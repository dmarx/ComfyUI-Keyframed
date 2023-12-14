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
        keyframed_condition["kf_cond_t"].label = text # attach prompt string as a label to the xattn keyframe for drawing
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

from toolz.itertoolz import sliding_window

def schedule_to_weight_curves(schedule):
    """
    Given a keyfrmaed curve, returns a curve for each keyframe giving the contribution
    of that keyframe to the schedule. Motivation here is to facilitate plotting
    """
    schedule, _ = schedule
    schedule = schedule.parameters["kf_cond_t"]
    schedule = deepcopy(schedule)
    curves = []
    keyframes = list(schedule._data.values())
    if len(keyframes) == 1:
        keyframe = keyframes[0]
        #curves = kf.ParameterGroup({kf.label: 1})
        curves = kf.ParameterGroup({keyframe.label: keyframe.Curve(1)})
        return curves
    for (frame_in, frame_curr, frame_out) in sliding_window(3, keyframes):
        frame_in.value, frame_curr.value, frame_out.value = 0,1,0
        c = kf.Curve({frame_in.t:frame_in, frame_curr.t:frame_curr, frame_out.t:frame_out}, 
                     label=frame_curr.label)
        c = deepcopy(c)
        curves.append(c)
    begin, end = keyframes[:2], keyframes[-2:]
    #outv = [begin]
    begin[0].value = 1
    begin[1].value = 0
    end[0].value = 0
    end[1].value = 1
    outv = [kf.Curve(begin, label=begin[0].label)]
    if len(keyframes) == 2:
        return outv
    outv += curves
    outv += [kf.Curve(end, label=end[1].label)]
    return kf.ParameterGroup(outv)

from .core import plot_curve

class KfDrawSchedule:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "schedule": ("SCHEDULE", {"forceInput": True,}),
                "n": ("INT", {"default": 64}),
                "show_legend": ("BOOLEAN", {"default": True}),
            }
        }

    def main(self, schedule, n, show_legend):
        curves = schedule_to_weight_curves(schedule)
        img_tensor = plot_curve(curves, n, show_legend, is_pgroup=True)
        return (img_tensor,)

###################################################################

NODE_CLASS_MAPPINGS = {
    "KfKeyframedCondition": KfKeyframedCondition,
    "KfKeyframedConditionWithText":KfKeyframedConditionWithText,
    "KfSetKeyframe": KfSetKeyframe,
    "KfGetScheduleConditionAtTime": KfGetScheduleConditionAtTime,
    "KfGetScheduleConditionSlice": KfGetScheduleConditionSlice,
    "KfDrawSchedule": KfDrawSchedule,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KfKeyframedCondition": "Keyframed Condition",
    "KfKeyframedConditionWithText": "Schedule Prompt",
    "KfSetKeyframe": "Set Keyframe",
    "KfGetScheduleConditionAtTime": "Evaluate Schedule At T",
    "KfGetScheduleConditionSlice": "Evaluate Schedule At T (Batch)",
}