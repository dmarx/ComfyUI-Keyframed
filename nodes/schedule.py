import keyframed as kf
#from keyframed.interpolation import bisect_left_keyframe, bisect_right_keyframe

from functools import total_ordering
from sortedcontainers import SortedDict, SortedList
from .core import CATEGORY as RootCategory

from numbers import Number

import torch
from copy import deepcopy
import logging

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CATEGORY=RootCategory + "/schedule"




# @total_ordering
# class ScheduleKeyframe(kf.Keyframe):
#     def __lt__(self, other):
#         return self.t < other


# def update_schedule(schedule, keyframe):
#     bl_idx = schedule.bisect_left(keyframe.t)
#     try:
#         if schedule[bl_idx].t == keyframe.t:
#             #del schedule[bl_idx]
#             schedule.pop(bl_idx)
#     except IndexError:
#         pass
#     schedule.add(keyframe)
#     return schedule





# # scavenged from Keyframed...

# def bisect_left_keyframe(k: Number, curve:SortedList, *args, **kargs) -> ScheduleKeyframe:
#     """
#     finds the value of the keyframe in a sorted dictionary to the left of a given key, i.e. performs "previous" interpolation
#     """
#     right_index = curve.bisect_right(k)
#     left_index = right_index - 1
#     #if right_index > 0:
#     if right_index >= 0:
#         #_, left_value = self._data.peekitem(left_index)
#         left_value = curve[left_index]
#     else:
#         raise RuntimeError(
#             "The return value of bisect_right should always be greater than zero, "
#             f"however self._data.bisect_right({k}) returned {right_index}."
#             "You should never see this error. Please report the circumstances to the library issue tracker on github."
#             )
#     return left_value


# def bisect_right_keyframe(k: Number, curve:SortedList, *args, **kargs) -> ScheduleKeyframe:
#     """
#     finds the value of the keyframe in a sorted dictionary to the right of a given key, i.e. performs "next" interpolation
#     """
#     right_index = curve.bisect_right(k)
#     #if right_index > 0:
#     if right_index >= 0:
#         #_, right_value = curve.peekitem(right_index)
#         right_value = curve[right_index]
#     else:
#         raise RuntimeError(
#             "The return value of bisect_right should always be greater than zero, "
#             f"however self._data.bisect_right({k}) returned {right_index}."
#             "You should never see this error. Please report the circumstances to the library issue tracker on github."
#             )
#     return right_value



# schedule = SortedList()

# x0 = ScheduleKeyframe(t=0, value="a")
# x1 = ScheduleKeyframe(t=5, value="b")
# x2 = ScheduleKeyframe(t=5, value="c")
# x3 = ScheduleKeyframe(t=6, value="d")



# schedule = update_schedule(schedule, x0)
# schedule = update_schedule(schedule, x3) # 
# schedule = update_schedule(schedule, x2)
# schedule = update_schedule(schedule, x1)
# schedule



###################################################################################



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
                "time": ("FLOAT", {"default": 0}), 
                #"weight": ("FLOAT", {"default": 1}), # maybe i should hide this attribute
                "interpolation_method": (list(kf.interpolation.INTERPOLATORS.keys()),),
            },
        }
    
    def main(self, conditioning, time, interpolation_method):
        #keyframe = kf.Keyframe(t=time, value=weight, interpolation_method=interpolation_method)
        #keyframe = ScheduleKeyframe(t=time, value=weight, interpolation_method=interpolation_method)
        #return (keyframe, conditioning)
        #kf_cond = ScheduleKeyframe(t=time, value=conditioning, interpolation_method=interpolation_method)
        #return (kf_cond,)
        ###########################

        # separately create keyframes for the parts that need interpolating, and carry around anything else
        cond_tensor, cond_dict = conditioning[0] # uh... i have NO idea what to do if there are multiple condition entries here... map over them i guess?
        #cond_tensor = deepcopy(cond_tensor)
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
        #keyframe, kf_condition = keyframed_condition
        cond_dict = keyframed_condition.pop("cond_dict")
        cond_dict = deepcopy(cond_dict)

        if schedule is None:
            curve_tokenized = kf.Curve([keyframed_condition["kf_cond_t"]], label="kf_cond_t")
            curves = [curve_tokenized]
            if keyframed_condition["kf_cond_pooled"] is not None:
                curve_pooled = kf.Curve([keyframed_condition["kf_cond_pooled"]], label="kf_cond_pooled")
                curves.append(curve_pooled)
            schedule = (kf.ParameterGroup(curves), cond_dict)
            #schedule = kf.ParameterGroup(keyframed_condition) #parameters
            #schedule = SortedList() #SortedDict
            #schedule = kf.Curve([keyframed_condition])
            #schedule = kf.Curve({keyframed_condition.t: keyframed_condition})
        else:
            schedule, old_cond_dict = schedule
            for k, v in keyframed_condition.items():
                if (v is not None):
                    # for now, assume we already have a schedule for k.
                    # Not sure how to handle new conditioning type appearing.
                    schedule.parameters[k][v.t] = v
            #schedule[keyframed_condition.t] = keyframed_condition
            #schedule._data[keyframed_condition.t] = keyframed_condition
            old_cond_dict.update(cond_dict) # NB: mutating this is probably bad
            schedule = (schedule, old_cond_dict)

        #schedule = update_schedule(schedule, keyframed_condition)
        return (schedule,)

def evaluate_schedule_at_time(schedule, time):
    #schedule, cond_dict = schedule
    schedule, cond_dict = schedule
    #cond_dict = deepcopy(cond_dict)
    values = schedule[time]
    cond_t = values.get("kf_cond_t")
    cond_pooled = values.get("kf_cond_pooled")
    if cond_pooled is not None:
        #cond_dict = deepcopy(cond_dict)
        cond_dict["pooled_output"] = cond_pooled.clone()
    logger.debug(f"type(cond_t):{type(cond_t)}")
    logger.debug(f"type(cond_pooled):{type(cond_pooled)}")
    logger.debug(f"type(cond_dict):{type(cond_dict)}")
    return [(cond_t.clone(), cond_dict)]


# def evaluate_schedule_at_time__OLD2(schedule, time):
#     kf_cond_left, kf_cond_right = bisect_left_keyframe(time, schedule), bisect_right_keyframe(time, schedule)
#     logger.debug(f"kf_cond_left: {kf_cond_left}")
#     #return (kf_cond_left.value,)

#     kf_tokenized_left = deepcopy(kf_cond_left)
#     #kf_pooled_left = deepcopy(kf_cond_left)
#     kf_tokenized_left.value = kf_cond_left.value[0]
#     #kf_pooled_left.value = kf_cond_left.value[1].get("pooled_output")

#     kf_tokenized_right = deepcopy(kf_cond_right)
#     #kf_pooled_right = deepcopy(kf_cond_right)
#     kf_tokenized_right.value = kf_cond_right.value[0]
#     #kf_pooled_right.value = kf_cond_right.value[1].get("pooled_output")

#     curve_tokenized = kf.Curve([kf_tokenized_left, kf_tokenized_right])
#     #curve_pooled = kf.Curve([kf_pooled_left, kf_pooled_right])

#     lerped_tokenized = curve_tokenized[time]
#     logger.debug(lerped_tokenized)
#     #lerped_pooled = curve_pooled[time]

#     #out_dict = deepcopy(kf_cond_left.value[1])
#     #out_dict["pooled_output"] = lerped_pooled
#     out_dict={}

#     return (lerped_tokenized, out_dict)


def evaluate_schedule_at_time__OLD(schedule, time):
    bl_idx = schedule.bisect_left(time)
    logger.debug(f"bl_idx:{bl_idx}")
    print(f"bl_idx:{bl_idx}")
    #left_kf, left_cond = schedule[bl_idx]
    left_kf = schedule[bl_idx]
    left_cond = left_kf.value
    if left_kf.t == time: # hit time exactly, return
        #return (left_kf, left_cond)
        return left_cond
    if bl_idx == len(schedule): # there's nothing to our right, return
        #return (left_kf, left_cond)
        return left_cond
    #right_kf, right_cond = schedule[bl_idx+1]
    right_kf = schedule[bl_idx+1]
    right_cond = right_kf.value
    logger.info(f"type(right_kf):{type(right_kf)}")
    logger.info(f"type(right_cond):{type(right_cond)}")
    start, end = left_kf.t, right_kf.t
    interval_length = end - start
    elapsed = time-start
    perc_complete = elapsed / interval_length
    # TODO: use interpolation method on keyframe to compute transition weight
    # For now, simple lerp

    # TODO: This isn't a proper cond object. need to separately lerp the cond and the pooled output
    #lerped_cond = perc_complete * right_cond + (1-perc_complete)*left_cond
    right_tokenized, right_dict = right_cond
    right_pooled = right_dict.get["pooled_output"]
    logger.info(f"type(right_tokenized):{type(right_tokenized)}")
    logger.info(f"type(right_pooled):{type(right_pooled)}")

    left_tokenized, left_dict = left_cond
    left_pooled = left_dict.get["pooled_output"]
    logger.info(f"type(left_tokenized):{type(left_tokenized)}")
    logger.info(f"type(left_pooled):{type(left_pooled)}")

    lerped_tokenized = perc_complete * right_tokenized + (1-perc_complete)*left_tokenized
    
    # TODO: simplify this
    if (right_pooled is not None) and (left_pooled is not None):
        lerped_pooled = perc_complete * right_pooled + (1-perc_complete)*left_pooled
    else:
        if right_pooled is not None:
            lerped_pooled = perc_complete * right_pooled
        elif left_pooled is not None:
            lerped_pooled = (1-perc_complete) * left_pooled
    logger.info(f"type(lerped_pooled):{type(lerped_pooled)}")
    out_dict = deepcopy(left_dict)
    if lerped_pooled is not None:
        out_dict['pooled_output'] = lerped_pooled

    logger.info("type(lerped_tokenized):{type(lerped_tokenized)}")
    # TODO: we could also interpolate and return an associated weight
    return (lerped_tokenized, out_dict)


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
                "stop": ("FLOAT",{"default":0}),
                "n": ("INTEGER", {"default":1}),
                "endpoint": ("BOOL", {"default":True})
            }
        }
    
    def main(self, schedule, start, stop, n, endpoint):
        times = np.linspace(start=start, stop=stop, num=n, endpoint=endpoint)
        conds = [evaluate_schedule_at_time(schedule, time) for time in times]
        lerped_tokenized = [c[0] for c in conds]
        lerped_pooled = [c[1]["pooled_output"] for c in conds]
        lerped_tokenized_t = torch.cat(lerped_tokenized)
        logger.info(f"lerped_tokenized_t.shape: {lerped_tokenized_t.shape}")
        out_dict = deepcopy(conds[0][1])
        if isinstance(lerped_pooled[0], torch.Tensor) and isinstance(lerped_pooled[-1], torch.Tensor):
            out_dict['pooled_output'] =  torch.cat(lerped_pooled)
        return (lerped_conds, out_dict)

###################################################################

NODE_CLASS_MAPPINGS = {
    "KfKeyframedCondition": KfKeyframedCondition,
    "KfSetKeyframe": KfSetKeyframe,
    "KfGetScheduleConditionAtTime": KfGetScheduleConditionAtTime,
}

NODE_DISPLAY_NAME_MAPPINGS = {}


###################################################################################

# class KfSetKeyframe:
#     CATEGORY=CATEGORY
#     FUNCTION = 'main'
#     RETURN_TYPES = ("SCHEDULE",)
    
#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "keyframed_condition": ("KEYFRAMED_CONDITION", {}),
#             },
#             "optional": {
#                 "schedule": ("SCHEDULE", {}), 
#             }
#         }
#     def main(keyframed_condition, schedule=None):
#         keyframe, kf_condition = keyframed_condition
#         if schedule is None:
#             schedule = SortedDict
#         schedule[keyframe.t] = keyframed_condition
#         return (schedule,)

# class KfGetScheduleConditionAtTime:
#     CATEGORY=CATEGORY
#     FUNCTION = 'main'
#     RETURN_TYPES = ("KEYFRAME",)

#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "schedule": ("SCHEDULE",{}),
#                 "time": ("FLOAT",{}),
#             }
#         }
    
#     def main(self, schedule, time):
        
#         # right_index = self._data.bisect_right(k)
#         # left_index = right_index - 1
#         # if right_index > 0:
#         #     _, left_value = self._data.peekitem(left_index)
#         # else: