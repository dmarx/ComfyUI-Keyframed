from .core import CATEGORY as RootCategory

from copy import deepcopy
import keyframed as kf
import logging
import numpy as np
import torch


logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CATEGORY=RootCategory + "/schedule"


class KfKeyframedCondition:
    """
    Attaches a condition to a keyframe
    """
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("KEYFRAMED_CONDITION",)
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", {}),
                "time": ("FLOAT", {"default": 0, "step": 1}), 
                #"weight": ("FLOAT", {"default": 1}), # maybe i should hide this attribute
                #"interpolation_method": (list(kf.interpolation.INTERPOLATORS.keys()),),
                "interpolation_method": (list(kf.interpolation.EASINGS.keys()), {"default":"linear"}),
            },
        }
    
    def main(self, conditioning, time, interpolation_method):

        # separately create keyframes for the parts that need interpolating, and carry around anything else
        # TODO: properly handle list of conds
        cond_tensor, cond_dict = conditioning[0] # uh... i have NO idea what to do if there are multiple condition entries here... map over them i guess?
        cond_tensor = cond_tensor.clone()
        kf_cond_t = kf.Keyframe(t=time, value=cond_tensor, interpolation_method=interpolation_method)

        cond_pooled = cond_dict.get("pooled_output")
        cond_dict = deepcopy(cond_dict)
        kf_cond_pooled = None
        if cond_pooled is not None:
            cond_pooled = cond_pooled.clone()
            kf_cond_pooled = kf.Keyframe(t=time, value=cond_pooled, interpolation_method=interpolation_method)
            cond_dict["pooled_output"] = cond_pooled
        
        return ({"kf_cond_t":kf_cond_t, "kf_cond_pooled":kf_cond_pooled, "cond_dict":cond_dict},)


def set_keyframed_condition(keyframed_condition, schedule=None):
    keyframed_condition = deepcopy(keyframed_condition)
    cond_dict = keyframed_condition.pop("cond_dict")
    #cond_dict = deepcopy(cond_dict)

    if schedule is None:
        # get a new copy of the tensor
        kf_cond_t = keyframed_condition["kf_cond_t"]
        #kf_cond_t.value = kf_cond_t.value.clone() # should be redundant with the deepcopy
        curve_tokenized = kf.Curve([kf_cond_t], label="kf_cond_t")
        curves = [curve_tokenized]
        if keyframed_condition["kf_cond_pooled"] is not None:
            kf_cond_pooled = keyframed_condition["kf_cond_pooled"]
            curve_pooled = kf.Curve([kf_cond_pooled], label="kf_cond_pooled")
            curves.append(curve_pooled)
        schedule = (kf.ParameterGroup(curves), cond_dict)
    else:
        schedule = deepcopy(schedule)
        schedule, old_cond_dict = schedule
        for k, v in keyframed_condition.items():
            if (v is not None):
                # for now, assume we already have a schedule for k.
                # Not sure how to handle new conditioning type appearing.
                schedule.parameters[k][v.t] = v
        old_cond_dict.update(cond_dict) # NB: mutating this is probably bad
        schedule = (schedule, old_cond_dict)
    return schedule


class KfKeyframedConditionWithText(KfKeyframedCondition):
    """
    Attaches a condition to a keyframe
    """
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("KEYFRAMED_CONDITION","CONDITIONING", "SCHEDULE")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                #"conditioning": ("CONDITIONING", {}),
                "clip": ("CLIP",),
                "text": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "time": ("FLOAT", {"default": 0, "step": 1}), 
                #"weight": ("FLOAT", {"default": 1}), # maybe i should hide this attribute
                #"interpolation_method": (list(kf.interpolation.INTERPOLATORS.keys()),),
                "interpolation_method": (list(kf.interpolation.EASINGS.keys()), {"default":"linear"}),
            },
            "optional": {
                "schedule": ("SCHEDULE", {}), 
            }
        }
    
    #def main(self, conditioning, time, interpolation_method):
    def main(self, clip, text, time, interpolation_method, schedule=None):
        tokens = clip.tokenize(text)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
        conditioning =  [[cond, {"pooled_output": pooled}]]
        keyframed_condition = super().main(conditioning, time, interpolation_method)[0]
        schedule = set_keyframed_condition(keyframed_condition, schedule)
        return (keyframed_condition, conditioning, schedule)


class KfSetKeyframe:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("SCHEDULE",)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "keyframed_condition": ("KEYFRAMED_CONDITION", {}),
            },
            "optional": {
                "schedule": ("SCHEDULE", {}), 
            }
        }
    def main(self, keyframed_condition, schedule=None):
        schedule = set_keyframed_condition(keyframed_condition, schedule)
        return (schedule,)


def evaluate_schedule_at_time(schedule, time):
    schedule = deepcopy(schedule)
    schedule, cond_dict = schedule
    #cond_dict = deepcopy(cond_dict)
    values = schedule[time]
    cond_t = values.get("kf_cond_t")
    cond_pooled = values.get("kf_cond_pooled")
    if cond_pooled is not None:
        #cond_dict = deepcopy(cond_dict)
        cond_dict["pooled_output"] = cond_pooled #.clone()
    #return [(cond_t.clone(), cond_dict)]
    return [(cond_t, cond_dict)]


class KfGetScheduleConditionAtTime:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("CONDITIONING",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "schedule": ("SCHEDULE",{}),
                "time": ("FLOAT",{}),
            }
        }
    
    def main(self, schedule, time):
        lerped_cond = evaluate_schedule_at_time(schedule, time)
        return (lerped_cond,)
        


class KfGetScheduleConditionSlice:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("CONDITIONING",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "schedule": ("SCHEDULE",{}),
                "start": ("FLOAT",{"default":0}),
                #"stop": ("FLOAT",{"default":0}),
                "step": ("FLOAT",{"default":1}),
                "n": ("INT", {"default":24}),
                #"endpoint": ("BOOL", {"default":True})
            }
        }
    
    #def main(self, schedule, start, stop, n, endpoint):
    def main(self, schedule, start, step, n):
        stop = start+n*step
        times = np.linspace(start=start, stop=stop, num=n, endpoint=True)
        conds = [evaluate_schedule_at_time(schedule, time)[0] for time in times]
        lerped_tokenized = [c[0] for c in conds]
        lerped_pooled = [c[1]["pooled_output"] for c in conds]
        lerped_tokenized_t = torch.cat(lerped_tokenized, dim=0)
        out_dict = deepcopy(conds[0][1])
        if isinstance(lerped_pooled[0], torch.Tensor) and isinstance(lerped_pooled[-1], torch.Tensor):
            out_dict['pooled_output'] =  torch.cat(lerped_pooled, dim=0)
        return [[(lerped_tokenized_t, out_dict)]] # uh... wrap it in lists until it doesn't complain?

###################################################################

NODE_CLASS_MAPPINGS = {
    "KfKeyframedCondition": KfKeyframedCondition,
    "KfKeyframedConditionWithText":KfKeyframedConditionWithText,
    "KfSetKeyframe": KfSetKeyframe,
    "KfGetScheduleConditionAtTime": KfGetScheduleConditionAtTime,
    "KfGetScheduleConditionSlice": KfGetScheduleConditionSlice,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KfKeyframedCondition": "Keyframed Condition",
    "KfKeyframedConditionWithText": "Schedule Prompt",
    "KfSetKeyframe": "Set Keyframe",
    "KfGetScheduleConditionAtTime": "Evaluate Schedule At T",
    "KfGetScheduleConditionSlice": "Evaluate Schedule At T (Batch)",
}