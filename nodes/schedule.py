import keyframed as kf
from functools import total_ordering
from sortedcontainers import SortedDict, SortedList
from .core import CATEGORY as RootCategory


CATEGORY=RootCategory + "/schedule"


@total_ordering
class ScheduleKeyframe(kf.Keyframe):
    def __lt__(self, other):
        return self.t < other


def update_schedule(schedule, keyframe):
    bl_idx = schedule.bisect_left(keyframe.t)
    try:
        if schedule[bl_idx].t == keyframe.t:
            #del schedule[bl_idx]
            schedule.pop(bl_idx)
    except IndexError:
        pass
    schedule.add(keyframe)
    return schedule


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
                "weight": ("FLOAT", {"default": 1}), # maybe i should hide this attribute
                "interpolation_method": (list(kf.interpolation.INTERPOLATORS.keys()),),
            },
        }
    
    def main(self, conditioning, time, weight, interpolation_method):
        keyframe = kf.Keyframe(t=time, value=weight, interpolation_method=interpolation_method)
        return (keyframe, conditioning)


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
    def main(keyframed_condition, schedule=None):
        #keyframe, kf_condition = keyframed_condition
        if schedule is None:
            schedule = SortedDict
        schedule = update_schedule(schedule, keyframed_condition)
        return (schedule,)


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
        bl_idx = schedule.bisect_left(time)
        left_kf, left_cond = schedule[bl_idx]
        if left_kf.t == time: # hit time exactly, return
            return (left_kf, left_cond)
        if bl_idx == len(schedule): # there's nothing to our right, return
            return (left_kf, left_cond)
        right_kf, right_cond = schedule[bl_idx+1]
        start, end = left_kf.t, right_kf.t
        interval_length = end - start
        elapsed = time-start
        perc_complete = elapsed / interval_length
        # TODO: use interpolation method on keyframe to compute transition weight
        # For now, simple lerp
        lerped_cond = perc_complete * right_cond + (1-perc_complete)*left_cond
        # TODO: we could also interpolate and return an associated weight
        return (lerped_cond,)


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