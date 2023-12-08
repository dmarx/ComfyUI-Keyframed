from .core import CATEGORY as ROOT_CATEGORY

import keyframed as kf

CATEGORY = ROOT_CATEGORY + "/sinusoidal"



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


NODE_CLASS_MAPPINGS = {
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

NODE_DISPLAY_NAME_MAPPINGS = {}