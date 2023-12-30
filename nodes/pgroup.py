import keyframed as kf
import logging
from copy import deepcopy

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


CATEGORY = "keyframed/parameter group"


class KfAddCurveToPGroup:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    #RETURN_TYPES = ("KEYFRAMED_CURVE",)
    RETURN_TYPES = ("PARAMETER_GROUP",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
            "optional": {
                "parameter_group": ("PARAMETER_GROUP",{"forceInput": True,}),
            },
        }

    def main(self, curve, parameter_group=None):
        curve = deepcopy(curve)
        if parameter_group is None:
            #parameter_group = kf.ParameterGroup({curve.label:curve})
            parameter_group = kf.ParameterGroup([curve])
        else:
            parameter_group = deepcopy(parameter_group)
            parameter_group.parameters[curve.label] = curve
        return (parameter_group,)

class KfAddCurveToPGroupx10:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    #RETURN_TYPES = ("KEYFRAMED_CURVE",)
    RETURN_TYPES = ("PARAMETER_GROUP",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve0": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
            "optional": {
                "parameter_group": ("PARAMETER_GROUP",{"forceInput": True,}),
                "curve1": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve2": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve3": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve4": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve5": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve6": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve7": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve8": ("KEYFRAMED_CURVE",{"forceInput": True,}),
                "curve9": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
        }

    def main(self, parameter_group=None, **kwargs):
        if parameter_group is None:
            #parameter_group = kf.ParameterGroup({curve.label:curve})
            parameter_group = kf.ParameterGroup(kwargs)
        else:
            parameter_group = deepcopy(parameter_group)
            for curve in parameter_group.values():
                parameter_group.parameters[curve.label] = curve
        return (parameter_group,)


class KfGetCurveFromPGroup:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "curve_label": ("STRING",{"default": "My Curve",}),
                "parameter_group": ("PARAMETER_GROUP",{"forceInput": True,}),
            },
        }
    
    def main(self, curve_label, parameter_group):
        curve = parameter_group.parameters[curve_label]
        return (deepcopy(curve),)


##################################################################

# PGroup Arithmetic

class KfPGroupCurveAdd:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("PARAMETER_GROUP",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "parameter_group": ("PARAMETER_GROUP",{"forceInput": True,}),
                "curve": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
        }

    def main(self, parameter_group, curve):
        parameter_group = deepcopy(parameter_group)
        curve = deepcopy(curve)
        return (parameter_group + curve, )


class KfPGroupCurveMultiply:
    CATEGORY = CATEGORY
    FUNCTION = "main"
    RETURN_TYPES = ("PARAMETER_GROUP",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "parameter_group": ("PARAMETER_GROUP",{"forceInput": True,}),
                "curve": ("KEYFRAMED_CURVE",{"forceInput": True,}),
            },
        }

    def main(self, parameter_group, curve):
        parameter_group = deepcopy(parameter_group)
        curve = deepcopy(curve)
        return (parameter_group * curve, )


# not behaving as expected :(

class KfPGroupSum:
    #CATEGORY = CATEGORY
    CATEGORY = "keyframed/experimental"
    FUNCTION = "main"
    RETURN_TYPES = ("KEYFRAMED_CURVE",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "parameter_group": ("PARAMETER_GROUP",{"forceInput": True,}),
            },
        }

    def main(self, parameter_group):
        parameter_group = deepcopy(parameter_group)
        #curve = kf.Composition(parameter_group, reduction='sum')
        #curve = sum(parameter_group.parameters.values())
        outv = kf.Curve(0)
        for curve in parameter_group.parameters.values():
            outv += curve
        return (outv,)
        #return (curve,)

### broken
#class KfPGroupProd:
#    pass
#     CATEGORY = CATEGORY
#     FUNCTION = "main"
#     RETURN_TYPES = ("KEYFRAMED_CURVE",)

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "parameter_group": ("PARAMETER_GROUP",{"forceInput": True,}),
#             },
#         }

#     def main(self, parameter_group):
#         parameter_group = deepcopy(parameter_group)
#         curve = kf.Composition(parameter_group, reduction='prod')
#         return (curve,)

##################################################################

NODE_CLASS_MAPPINGS = {
    #"KfCurveDraw": KfCurveDraw,
    #"KfPGroupDraw": KfPGroupDraw,
    #"KfSetCurveLabel":KfSetCurveLabel,
    "KfAddCurveToPGroup": KfAddCurveToPGroup,
    "KfGetCurveFromPGroup": KfGetCurveFromPGroup,
    "KfAddCurveToPGroupx10": KfAddCurveToPGroupx10,
    "KfPGroupCurveAdd":KfPGroupCurveAdd,
    "KfPGroupCurveMultiply":KfPGroupCurveMultiply,
    "KfPGroupSum": KfPGroupSum,
    #"KfPGroupProd": KfPGroupProd,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    #"KfSetCurveLabel": "Set Curve Label",
    "KfAddCurveToPGroup": "Add Curve To Parameter Group",
    "KfGetCurveFromPGroup": "Get Curve From Parameter Group",
    "KfAddCurveToPGroupx10": "Add Curve To Parameter Group (x10)",
    "KfPGroupCurveAdd": "Parameter Group + Curve (addition)",
    "KfPGroupCurveMultiply": "Parameter Group * Curve (multiply)",
    "KfPGroupSum": "Sum Over Parameter Group",
    #"KfPGroupProd": "Product Over Parameter Group",
}
