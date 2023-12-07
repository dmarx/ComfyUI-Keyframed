import keyframed as kf
from keyframed.dsl import curve_from_cn_string
import logging
import torch
from copy import deepcopy
#import warnings
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


CATEGORY = "keyframed"


class KfCurveFromString:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("KEYFRAMED_CURVE",)
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"chigozie_string": ("STRING", {
                    "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "0:(1)"
                }),
            },
        }
    
    def main(self, chigozie_string):
        curve = curve_from_cn_string(chigozie_string)
        return (curve,)


class KfCurveFromYAML:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("KEYFRAMED_CURVE",)
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"yaml": ("STRING", {
                    "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
                    # TO DO: replace this with kf.serializaiton.to_dict() # or whatever
                    "default": """curve:
- - 0
  - 0
  - linear
- - 1
  - 1
loop: false
bounce: false
duration: 1
label: foo"""
                }),
            },
        }
    
    def main(self, yaml):
        curve = kf.serialization.from_yaml(yaml)
        return (curve,)


class KfEvaluateCurveAtT:
    CATEGORY=CATEGORY # TODO: create a "utils" group
    FUNCTION = 'main'
    RETURN_TYPES = ("FLOAT","INT")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "t": ("INT",{"default":0})
            },
        }

    def main(self, curve, t):
        return curve[t], int(curve[t])


# class KfCurveToAcnLatentKeyframe:
#     CATEGORY=CATEGORY
#     FUNCTION = 'main'
#     RETURN_NAMES = ("LATENT_KF", )
#     RETURN_TYPES = ("LATENT_KEYFRAME",)
#     """Compatibility with Kosinkadink "Advanced Controlnet" AnimateDiff"""
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "curve": ("KEYFRAMED_CURVE",{"forceInput": True,}),
#             },
#         }
#     def main(self, curve):
#         warnings.warn("KfCurveToAcnLatentKeyframe not implemented")
#         return (curve,)


class KfApplyCurveToCond:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    #RETURN_TYPES = ("CONDITIONING","LATENT_KEYFRAME",)
    RETURN_TYPES = ("CONDITIONING",)
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("KEYFRAMED_CURVE", {"forceInput": True,}),
                "cond": ("CONDITIONING", {"forceInput": True,}),
            },
            "optional":{
                "latents": ("LATENT", {}),
                "start_t": ("INT", {"default":0, }),
                "n": ("INT", {}),
            },
        }
    def main(self, curve, cond, latents=None, start_t=0, n=0):
        #logger.info(f"latents: {latents}")
        logger.info(f"type(latents): {type(latents)}") # Latent is a dict that (presently) has one key, `samples`
        #device = 'cpu' # probably should be handling this some other way
        #if latents is not None:
        if isinstance(latents, dict):
            if 'samples' in latents:
                n = latents['samples'].shape[0] # batch dimension
                #device = latents['samples'].device
        #weights = [curve[start_t+i] for i in range(n)]
        #weights = torch.tensor(weights, device=device)
        cond_out = []
        for c_tensor, c_dict in cond:
            #weights.to(c_tensor.device)
            m=c_tensor.shape[0]
            if c_tensor.shape[0] == 1:
                c_tensor = c_tensor.repeat(n, 1, 1) # batch, n_tokens, embeding_dim
                m=n
            weights = [curve[start_t+i] for i in range(m)]
            weights = torch.tensor(weights, device=c_tensor.device)
            #logger.info(f"c_tensor.shape:{c_tensor.shape}")
            #logger.info(f"weights.shape:{weights.shape}")
            #logger.info(f"weights.shape:{weights.view(n,1,1).shape}")
            #c_tensor.mul_(weights)
            #c_tensor.mul_(weights.view(m,1,1)) # I think these in-place/mutating operations are messing things up
            c_tensor = c_tensor * weights.view(m,1,1)
            #c_tensor = c_tensor
            if "pooled_output" in c_dict:
                c_dict = deepcopy(c_dict) # hate this.
                pooled = c_dict['pooled_output']
                if pooled.shape[0] == 1:
                    pooled = pooled.repeat(m, 1) # batch, embeding_dim
                    #pooled.mul_(weights)
                c_dict['pooled_output'] = pooled * weights.view(m,1)
            cond_out.append((c_tensor, c_dict))
        return (cond_out,)

        #outv = torch.ones_like(latents) * torch.tensor(weights, device=latents.device)
        #return (cond, outv)


# TODO: Add Conds
#class ConditioningAverage:
class KfConditioningAdd:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("CONDITIONING",)

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"conditioning_1": ("CONDITIONING", ),
                             "conditioning_2": ("CONDITIONING", ),
                             }}

    def main(self, conditioning_1, conditioning_2):
        assert len(conditioning_1) == len(conditioning_2)

        outv = []
        for i, ((c1_tensor, c1_dict), (c2_tensor, c2_dict) ) in enumerate(zip(conditioning_1, conditioning_2)):
            c1_tensor += c2_tensor
            if ('pooled_output' in c1_dict) and ('pooled_output' in c2_dict):
                c1_dict['pooled_output'] += c2_dict['pooled_output']
            outv.append((c1_tensor, c1_dict))
        return (outv, )


# class KfCurveInverse:
#     CATEGORY = CATEGORY
#     FUNCTION = "main"
#     RETURN_TYPES = ("KEYFRAMED_CURVE",)

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "curve": ("KEYFRAMED_CURVE",{"forceInput": True,}),
#             },
#             "hidden": {
#                 "a": ("FLOAT", {"default": 0.0001}),
#             },
#         }
    
#     def main(self, curve, a=0.0001):
#         curve = curve + a
#         curve = 1/curve
#         return (curve,)


class KfCurveDraw:
    CATEGORY = f"{CATEGORY}/experimental"
    FUNCTION = "main"
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "curve": ("KEYFRAMED_CURVE",)
            }
        }

    def main(self, curve):
        """
        
        """
        # Create a figure and axes object
        fig, ax = plt.subplots()

        # Build the plot using the provided function
        #build_plot(ax)
        #curve.plot(ax=ax)
        curve.plot()
        width, height = 10, 5 #inches
        plt.figure(figsize=(width, height))

        # Save the plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)

        # Read the image into a numpy array, converting it to RGB mode
        pil_image = Image.open(buf).convert('RGB')
        plot_array = np.array(pil_image) #.astype(np.uint8)

        # Convert the array to the desired shape [batch, channels, width, height]
        #plot_array = np.transpose(plot_array, (2, 0, 1))  # Reorder to [channels, width, height]
        #plot_array = np.expand_dims(plot_array, axis=0)   # Add the batch dimension
        #plot_array = torch.tensor(plot_array) #.float()
        plot_array = torch.from_numpy(plot_array)
        return (plot_array,)

###########################################

# curve arithmetic

# TODO: Add Curves (to compute normalization)
class KfCurvesAdd:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve_1": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve_2": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
        }

    def main(self, curve_1, curve_2):
        return (curve_1 + curve_2, )


class KfCurvesSubtract:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve_1": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve_2": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
        }

    def main(self, curve_1, curve_2):
        return (curve_1 - curve_2, )


class KfCurvesMultiply:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve_1": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve_2": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
        }

    def main(self, curve_1, curve_2):
        return (curve_1 * curve_2, )


## This seems to not be working properly. I think the issue is upstream in Keyframed
# TODO: set as experimental?
class KfCurvesDivide:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve_1": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve_2": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
        }

    def main(self, curve_1, curve_2):
        return (curve_1 / curve_2, )


class KfCurveConstant:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("FLOAT", {"forceInput": True,})
                }}
    
    def main(self, value):
        curve = kf.Curve(value)
        return (curve,)


##################################################################

### TODO: Working with parameter groups


# Label curve
## inputs: curve, label (text widget)

# add curve(s) to parameter group
## inputs: pgroup, curve
## returns pgroup
## if pgroup not provided, new one created

# get curve from parameter group
## inputs: pgroup, label
## returns curve

# extract a time slice from the parameter group


##################################################################

### Sinusoidal

class KfSinusoidalWithFrequency:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE", "SINUSOIDAL_CURVE")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "frequency": ("FLOAT",{
                    "default": 1/12,
                    "step": 0.01,
                }),
                "phase": ("FLOAT", {
                    "default": 0.0,
                    #"min": 0.0,
                    #"max": 6.28318530718, # 2*pi
                    "step": 0.1308996939, # pi/24
                }),
                "amplitude": ("FLOAT",{
                    "default": 1,
                    "step": 0.01,
                }),
            },
        }

    def main(self, frequency, phase, amplitude):
        curve = kf.SinusoidalCurve(frequency=frequency, phase=phase, amplitude=amplitude)
        return (curve, curve)

class KfSinusoidalWithWavelength:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE", "SINUSOIDAL_CURVE")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "wavelength": ("FLOAT",{
                    "default": 12,
                    "step": 0.5,
                }),
                "phase": ("FLOAT", {
                    "default": 0.0,
                    #"min": 0.0,
                    #"max": 6.28318530718, # 2*pi
                    "step": 0.1308996939, # pi/24
                }),
                "amplitude": ("FLOAT",{
                    "default": 1,
                    "step": 0.01,
                }),
            },
        }

    def main(self, wavelength, phase, amplitude):
        curve = kf.SinusoidalCurve(wavelength=wavelength, phase=phase, amplitude=amplitude)
        return (curve, curve)


###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #


###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #

class KfSinusoidalAdjustWavelength:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE", "SINUSOIDAL_CURVE")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("SINUSOIDAL_CURVE",{"forceInput": True,}),
                "adjustment": ("FLOAT",{
                    "default": 0.0,
                    "step": 0.5,
                }),
            }}

    def main(self, curve, adjustment):
        wavelength, phase, amplitude = curve.wavelength, curve.phase, curve.amplitude 
        wavelength += adjustment
        curve = kf.SinusoidalCurve(wavelength=wavelength, phase=phase, amplitude=amplitude)
        return (curve, curve)


class KfSinusoidalAdjustPhase:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE", "SINUSOIDAL_CURVE")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("SINUSOIDAL_CURVE",{"forceInput": True,}),
                "adjustment": ("FLOAT", {
                    "default": 0.0,
                    "step": 0.1308996939, # pi/24
                }),
            }}
    
    def main(self, curve, adjustment):
        wavelength, phase, amplitude = curve.wavelength, curve.phase, curve.amplitude 
        phase += adjustment
        curve = kf.SinusoidalCurve(wavelength=wavelength, phase=phase, amplitude=amplitude)
        return (curve, curve)


class KfSinusoidalAdjustFrequency:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE", "SINUSOIDAL_CURVE")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("SINUSOIDAL_CURVE",{"forceInput": True,}),
                "adjustment": ("FLOAT",{
                    "default": 0,
                    "step": 0.01,
                }),
            }}

    def main(self, curve, adjustment):
        wavelength, phase, amplitude = curve.wavelength, curve.phase, curve.amplitude
        frequency = 1/wavelength
        frequency += adjustment
        wavelength = 1/frequency
        curve = kf.SinusoidalCurve(wavelength=wavelength, phase=phase, amplitude=amplitude)
        return (curve, curve)
    

class KfSinusoidalAdjustAmplitude:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE", "SINUSOIDAL_CURVE")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("SINUSOIDAL_CURVE",{"forceInput": True,}),
                "adjustment": ("FLOAT",{
                    "default": 0,
                    "step": 0.01,
                }),
            }}

    def main(self, curve, adjustment):
        wavelength, phase, amplitude = curve.wavelength, curve.phase, curve.amplitude 
        amplitude += adjustment
        curve = kf.SinusoidalCurve(wavelength=wavelength, phase=phase, amplitude=amplitude)
        return (curve, curve)


###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #   ###   #


class KfSinusoidalGetWavelength:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("FLOAT",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("SINUSOIDAL_CURVE",{"forceInput": True,}),
            }}

    def main(self, curve):
        return (curve.wavelength,)


class KfSinusoidalGetFrequency:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("FLOAT",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("SINUSOIDAL_CURVE",{"forceInput": True,}),
            }}

    def main(self, curve):
        return (1/curve.wavelength,)


class KfSinusoidalGetPhase:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("FLOAT",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("SINUSOIDAL_CURVE",{"forceInput": True,}),
            }}

    def main(self, curve):
        return (curve.phase,)


class KfSinusoidalGetAmplitude:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("FLOAT",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("SINUSOIDAL_CURVE",{"forceInput": True,}),
            }}

    def main(self, curve):
        return (curve.amplitude,)

##################################################################


# KfScheduleConditions:
#     """
#     Carry curve and cond together for Simplicity
#     """
#     CATEGORY = CATEGORY
#     FUNCTION = "main"
#     RETURN_TYPES = ("COND_SCHEDULE",)


# KfCombineWeightedConditions:

##################################################################

# TODO: 0-1 curves (low frequency oscillators)
# --> "1-X" operator

# TODO: pre-entangled curves

##################################################################

NODE_CLASS_MAPPINGS = {
    "KfCurveFromString": KfCurveFromString,
    "KfCurveFromYAML": KfCurveFromYAML,
    "KfEvaluateCurveAtT": KfEvaluateCurveAtT,
    "KfApplyCurveToCond": KfApplyCurveToCond,
    "KfConditioningAdd": KfConditioningAdd,
    #"KfCurveToAcnLatentKeyframe": KfCurveToAcnLatentKeyframe,
    #######################################
    #"KfCurveInverse": KfCurveInverse,
    "KfCurveDraw": KfCurveDraw,
    "KfCurvesAdd": KfCurvesAdd,
    "KfCurvesSubtract": KfCurvesSubtract,
    "KfCurvesMultiply": KfCurvesMultiply,
    "KfCurvesDivide": KfCurvesDivide,
    "KfCurveConstant": KfCurveConstant,
    #########################
    "KfSinusoidalWithFrequency": KfSinusoidalWithFrequency,
    "KfSinusoidalWithWavelength": KfSinusoidalWithWavelength,
    "KfSinusoidalAdjustWavelength": KfSinusoidalAdjustWavelength,
    "KfSinusoidalAdjustPhase": KfSinusoidalAdjustPhase,
    "KfSinusoidalAdjustFrequency": KfSinusoidalAdjustFrequency,
    "KfSinusoidalAdjustAmplitude": KfSinusoidalAdjustAmplitude,
    "KfSinusoidalGetWavelength": KfSinusoidalGetWavelength,
    "KfSinusoidalGetPhase": KfSinusoidalGetPhase,
    "KfSinusoidalGetAmplitude": KfSinusoidalGetAmplitude,
    "KfSinusoidalGetFrequency": KfSinusoidalGetFrequency,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "KfCurveFromString": "Curve From String",
    "KfCurveFromYAML": "Curve From YAML",
    "KfEvaluateCurveAtT": "Evaluate Curve At T",
    "KfApplyCurveToCond": "Apply Curve to Conditioning",
    "KfConditioningAdd": "Add Conditions",
    #"KfCurveToAcnLatentKeyframe": "Curve to ACN Latent Keyframe",
    "KfCurvesAdd": "Curve_1 + Curve_2",
    "KfCurvesSubtract": "Curve_1 - Curve_2",
    "KfCurvesMultiply": "Curve_1 * Curve_2",
    "KfCurvesDivide": "Curve_1 / Curve_2",
}