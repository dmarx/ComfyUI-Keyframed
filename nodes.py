import keyframed as kf
from keyframed.dsl import curve_from_cn_string
import warnings

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
                    "default": "0: 1"
                }),
            },
        }
    
    def main(self, chigozie_string):
        return curve_from_cn_string(chigozie_string)


class KfCurveFromYAML:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("KEYFRAMED_CURVE",)
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"yaml": ("STRING", {
                    "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
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
        return kf.serialization.from_yaml(yaml)


class KfEvaluateCurveAtT:
    CATEGORY=CATEGORY
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


class KfCurveToAcnLatentKeyframe:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_NAMES = ("LATENT_KF", )
    RETURN_TYPES = ("LATENT_KEYFRAME",)
    """Compatibility with Kosinkadink "Advanced Controlnet" AnimateDiff"""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
        }
    def main(self, curve):
        warnings.warn("KfCurveToAcnLatentKeyframe not implemented")
        return curve


NODE_CLASS_MAPPINGS = {
    "KfCurveFromString": KfCurveFromString,
    "KfCurveFromYAML": KfCurveFromYAML,
    "KfEvaluateCurveAtT": KfEvaluateCurveAtT,
     "KfCurveToAcnLatentKeyframe": KfCurveToAcnLatentKeyframe,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "KfCurveFromString": "Curve From String",
    "KfCurveFromYAML": "Curve From YAML",
    "KfEvaluateCurveAtT": "EvaluateCurveAtT",
    "KfCurveToAcnLatentKeyframe": "Curve to ACN Latent Keyframe",
}