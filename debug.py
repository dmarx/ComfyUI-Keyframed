import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CATEGORY="keyframed/debug"

class KfDebug_Passthrough:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    # RETURN_TYPES = ("FLOAT","INT")

    # @classmethod
    # def INPUT_TYPES(s):
    #     return {
    #         "required": {
    #             "curve": ("KEYFRAMED_CURVE",{"forceInput": True,}),
    #             "t": ("INT",{"default":0})
    #         },
    #     }

    def main(self, item):
        logger.info(f"type: {type(item)}")
        logger.info(f"item: {item}")
        return (item,) # pretty sure it's gotta be a tuple?

class KfDebug_Float(KfDebug_Passthrough):
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("FLOAT",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "item": ("FLOAT",{"forceInput": True,}),
            },
        }

NODE_CLASS_MAPPINGS = {
    #"KfDebug_Passthrough": KfDebug_Passthrough,
    "KfDebug_Float": KfDebug_Float,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {k:k for k in NODE_CLASS_MAPPINGS}