import logging
import torch
import numpy as np


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CATEGORY="keyframed/debug"

# i could probably use icecream or something like that for this
def _inspect(item, depth=0):
    pad="\t"*depth
    if depth > 0:
        pad +="- "
    # NB: Linter says using f-strings in log statements can hinder performance
    logger.info(f"{pad}type: {type(item)}")
    log_item=True
    
    if hasattr(item, "shape"):
        logger.info(f"{pad}item.shape: {item.shape}")
        log_item=False
    elif hasattr(item, "size"):
        logger.info(f"{pad}item.shape: {item.size}")
        #logger.info(f"{pad}item.shape: {item.size()}")
        log_item=False

    # to do: be fancy and change to a match statement
    #if isinstance(item, dict):
    if hasattr(item, 'keys'):
        logger.info(f"{pad}item.keys(): {item.keys()}")
        if hasattr(item, 'items'):
            for k,v in item.items():
                logger.info(f"{pad}key: {k}")
                logger.info(f"{pad}value: {_inspect(v, depth=depth+1)}")
        log_item=False
    
    if isinstance(item, list):
        logger.info(f"{pad}len(item): {len(item)}")
        for entry in item:
            _inspect(entry, depth=depth+1)
        log_item=False

    if log_item:
        logger.info(f"{pad}item: {item}")


class KfDebug_Passthrough:
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    def main(self, item):
        _inspect(item)
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


class KfDebug_Cond(KfDebug_Passthrough):
    CATEGORY=CATEGORY
    FUNCTION = 'main'
    RETURN_TYPES = ("CONDITIONING",)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "item": ("CONDITIONING",{"forceInput": True,}),
            },
        }


NODE_CLASS_MAPPINGS = {
    #"KfDebug_Passthrough": KfDebug_Passthrough,
    "KfDebug_Float": KfDebug_Float,
    "KfDebug_Cond": KfDebug_Cond,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {k:k for k in NODE_CLASS_MAPPINGS}