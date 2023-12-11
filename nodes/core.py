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

import torchvision.transforms as TT


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
        curve = deepcopy(curve)
        cond = deepcopy(cond)
        #logger.info(f"latents: {latents}")
        #logger.info(f"type(latents): {type(latents)}") # Latent is a dict that (presently) has one key, `samples`
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
        conditioning_1 = deepcopy(conditioning_1)
        conditioning_2 = deepcopy(conditioning_2)
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
                "curve": ("KEYFRAMED_CURVE", {"forceInput": True,}),
                "n": ("INT", {"default": 64}),
            }
        }

    def main(self, curve, n):
        """
        
        """
        # Create a figure and axes object
        fig, ax = plt.subplots()

        # Build the plot using the provided function
        #build_plot(ax)
        #curve.plot(ax=ax)
        #curve.plot(n=n)

        eps:float=1e-9
        # value to be subtracted from keyframe to produce additional points for plotting.
        # Plotting these additional values is important for e.g. visualizing step function behavior.

        m=3
        if n < m:
            n = self.duration + 1
            n = max(m, n)
        
        
        xs_base = list(range(int(n))) + list(curve.keyframes)
        logger.debug(f"xs_base:{xs_base}")
        xs = set()
        for x in xs_base:
            xs.add(x)
            xs.add(x-eps)
        
        xs = [x for x in list(set(xs)) if (x >= 0)]
        xs.sort()
        ys = [curve[x] for x in xs]

        width, height = 12,8 #inches
        plt.figure(figsize=(width, height))
        #line = plt.plot(xs, ys, *args, **kargs)
        line = plt.plot(xs, ys)
        kfx = curve.keyframes
        kfy = [curve[x] for x in kfx]
        plt.scatter(kfx, kfy, color=line[0].get_color())




        #width, height = 10, 5 #inches
        #plt.figure(figsize=(width, height))

        # Save the plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close() # no idea if this makes a difference
        buf.seek(0)

        # Read the image into a numpy array, converting it to RGB mode
        pil_image = Image.open(buf).convert('RGB')
        #plot_array = np.array(pil_image) #.astype(np.uint8)

        # Convert the array to the desired shape [batch, channels, width, height]
        #plot_array = np.transpose(plot_array, (2, 0, 1))  # Reorder to [channels, width, height]
        #plot_array = np.expand_dims(plot_array, axis=0)   # Add the batch dimension
        #plot_array = torch.tensor(plot_array) #.float()
        #plot_array = torch.from_numpy(plot_array)

        img_tensor = TT.ToTensor()(pil_image)
        img_tensor = img_tensor.unsqueeze(0)
        img_tensor = img_tensor.permute([0, 2, 3, 1])
        return (img_tensor,)
        #return (plot_array,)

#  buffer_io = BytesIO()
#             plt.savefig(buffer_io, format='png', bbox_inches='tight')
#             plt.close()

#             buffer_io.seek(0)
#             img = Image.open(buffer_io)

#             img_tensor = TT.ToTensor()(img)
        
#             img_tensor = img_tensor.unsqueeze(0)
            
#             img_tensor = img_tensor.permute([0, 2, 3, 1])

#             return (img_tensor,)

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
        curve_1 = deepcopy(curve_1)
        curve_2 = deepcopy(curve_2)
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
        curve_1 = deepcopy(curve_1)
        curve_2 = deepcopy(curve_2)
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
        curve_1 = deepcopy(curve_1)
        curve_2 = deepcopy(curve_2)
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
        curve_1 = deepcopy(curve_1)
        curve_2 = deepcopy(curve_2)
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
    "KfCurveConstant": "Constant-Valued Curve",
}