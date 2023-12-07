from .core import CATEGORY
import keyframed as kf
import numpy as np

class KfSinusoidalEntangledZeroOne:
    CATEGORY = CATEGORY + "/entangled [0-1]"
    FUNCTION = "main"
    #RETURN_TYPES = ("KEYFRAMED_CURVE", "SINUSOIDAL_CURVE")

    def main(self, n, **kargs):
        tau = 2*np.pi 
        floor=.001 # fully zeroing out conditions creates "sharp edges" in the traversal
        a = 1/n
        amplitude = a - floor/2

        
        #return [a+kf.SinusoidalCurve(phase=i/tau, amplitude=a, **kargs) for i in range(n)]
        return [amplitude+kf.SinusoidalCurve(phase=tau*(n-i-1)/n, amplitude=amplitude, **kargs) for i in range(n)]


class KfSinusoidalEntangledZeroOneFromWavelength(KfSinusoidalEntangledZeroOne):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "wavelength": ("FLOAT",{
                    "default": 12,
                    "step": 0.5,
                }),
            }
        }
    

class KfSinusoidalEntangledZeroOneFromWavelengthx2(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*2
    def main(self, wavelength):
        return super().main(n=2, wavelength=wavelength)

class KfSinusoidalEntangledZeroOneFromWavelengthx3(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*3
    def main(self, wavelength):
        return super().main(n=3, wavelength=wavelength)

class KfSinusoidalEntangledZeroOneFromWavelengthx4(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*4
    def main(self, wavelength):
        return super().main(n=4, wavelength=wavelength)

class KfSinusoidalEntangledZeroOneFromWavelengthx5(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*5
    def main(self, wavelength):
        return super().main(n=5, wavelength=wavelength)

class KfSinusoidalEntangledZeroOneFromWavelengthx6(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*6
    def main(self, wavelength):
        return super().main(n=6, wavelength=wavelength)

class KfSinusoidalEntangledZeroOneFromWavelengthx7(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*7
    def main(self, wavelength):
        return super().main(n=7, wavelength=wavelength)

class KfSinusoidalEntangledZeroOneFromWavelengthx8(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*8
    def main(self, wavelength):
        return super().main(n=8, wavelength=wavelength)

class KfSinusoidalEntangledZeroOneFromWavelengthx9(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*9
    def main(self, wavelength):
        return super().main(n=9, wavelength=wavelength)


###############################################################################################

class KfSinusoidalEntangledZeroOneFromFrequency(KfSinusoidalEntangledZeroOne):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                 "frequency": ("FLOAT",{
                    "default": 1/12,
                    "step": 0.01,
                }),
            }
        }


class KfSinusoidalEntangledZeroOneFromFrequencyx2(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*2
    def main(self, frequency):
        return super().main(n=2, frequency=frequency)

class KfSinusoidalEntangledZeroOneFromFrequencyx3(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*3
    def main(self, frequency):
        return super().main(n=3, frequency=frequency)

class KfSinusoidalEntangledZeroOneFromFrequencyx4(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*4
    def main(self, frequency):
        return super().main(n=4, frequency=frequency)

class KfSinusoidalEntangledZeroOneFromFrequencyx5(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*5
    def main(self, frequency):
        return super().main(n=5, frequency=frequency)

class KfSinusoidalEntangledZeroOneFromFrequencyx6(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*6
    def main(self, frequency):
        return super().main(n=6, frequency=frequency)

class KfSinusoidalEntangledZeroOneFromFrequencyx7(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*7
    def main(self, frequency):
        return super().main(n=7, frequency=frequency)
    
class KfSinusoidalEntangledZeroOneFromFrequencyx8(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*8
    def main(self, frequency):
        return super().main(n=8, frequency=frequency)

class KfSinusoidalEntangledZeroOneFromFrequencyx9(KfSinusoidalEntangledZeroOneFromWavelength):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)*9
    def main(self, frequency):
        return super().main(n=9, frequency=frequency)


###############################################################################################

NODE_CLASS_MAPPINGS = {
    "KfSinusoidalEntangledZeroOneFromWavelengthx2": KfSinusoidalEntangledZeroOneFromWavelengthx2,
    "KfSinusoidalEntangledZeroOneFromWavelengthx3": KfSinusoidalEntangledZeroOneFromWavelengthx3,
    "KfSinusoidalEntangledZeroOneFromWavelengthx4": KfSinusoidalEntangledZeroOneFromWavelengthx4,
    "KfSinusoidalEntangledZeroOneFromWavelengthx5": KfSinusoidalEntangledZeroOneFromWavelengthx5,
    "KfSinusoidalEntangledZeroOneFromWavelengthx6": KfSinusoidalEntangledZeroOneFromWavelengthx6,
    "KfSinusoidalEntangledZeroOneFromWavelengthx7": KfSinusoidalEntangledZeroOneFromWavelengthx7,
    "KfSinusoidalEntangledZeroOneFromWavelengthx8": KfSinusoidalEntangledZeroOneFromWavelengthx8,
    "KfSinusoidalEntangledZeroOneFromWavelengthx9": KfSinusoidalEntangledZeroOneFromWavelengthx9,

    "KfSinusoidalEntangledZeroOneFromFrequencyx2": KfSinusoidalEntangledZeroOneFromFrequencyx2,
    "KfSinusoidalEntangledZeroOneFromFrequencyx3": KfSinusoidalEntangledZeroOneFromFrequencyx3,
    "KfSinusoidalEntangledZeroOneFromFrequencyx4": KfSinusoidalEntangledZeroOneFromFrequencyx4,
    "KfSinusoidalEntangledZeroOneFromFrequencyx5": KfSinusoidalEntangledZeroOneFromFrequencyx5,
    "KfSinusoidalEntangledZeroOneFromFrequencyx6": KfSinusoidalEntangledZeroOneFromFrequencyx6,
    "KfSinusoidalEntangledZeroOneFromFrequencyx7": KfSinusoidalEntangledZeroOneFromFrequencyx7,
    "KfSinusoidalEntangledZeroOneFromFrequencyx8": KfSinusoidalEntangledZeroOneFromFrequencyx8,
    "KfSinusoidalEntangledZeroOneFromFrequencyx9": KfSinusoidalEntangledZeroOneFromFrequencyx9,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "KfSinusoidalEntangledZeroOneFromWavelengthx2": "2x Entangled Curves [0,1] (Wavelength)",
    "KfSinusoidalEntangledZeroOneFromWavelengthx3": "3x Entangled Curves [0,1] (Wavelength)",
    "KfSinusoidalEntangledZeroOneFromWavelengthx4": "4x Entangled Curves [0,1] (Wavelength)",
    "KfSinusoidalEntangledZeroOneFromWavelengthx5": "5x Entangled Curves [0,1] (Wavelength)",
    "KfSinusoidalEntangledZeroOneFromWavelengthx6": "6x Entangled Curves [0,1] (Wavelength)",
    "KfSinusoidalEntangledZeroOneFromWavelengthx7": "7x Entangled Curves [0,1] (Wavelength)",
    "KfSinusoidalEntangledZeroOneFromWavelengthx8": "8x Entangled Curves [0,1] (Wavelength)",
    "KfSinusoidalEntangledZeroOneFromWavelengthx9": "9x Entangled Curves [0,1] (Wavelength)",

    "KfSinusoidalEntangledZeroOneFromFrequencyx2": "2x Entangled Curves [0,1] (Frequency)",
    "KfSinusoidalEntangledZeroOneFromFrequencyx3": "3x Entangled Curves [0,1] (Frequency)",
    "KfSinusoidalEntangledZeroOneFromFrequencyx4": "4x Entangled Curves [0,1] (Frequency)",
    "KfSinusoidalEntangledZeroOneFromFrequencyx5": "5x Entangled Curves [0,1] (Frequency)",
    "KfSinusoidalEntangledZeroOneFromFrequencyx6": "6x Entangled Curves [0,1] (Frequency)",
    "KfSinusoidalEntangledZeroOneFromFrequencyx7": "7x Entangled Curves [0,1] (Frequency)",
    "KfSinusoidalEntangledZeroOneFromFrequencyx8": "8x Entangled Curves [0,1] (Frequency)",
    "KfSinusoidalEntangledZeroOneFromFrequencyx9": "9x Entangled Curves [0,1] (Frequency)",
}