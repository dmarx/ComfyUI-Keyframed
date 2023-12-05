import logging
import torch
import numpy as np
from PIL.Image import Image

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CATEGORY="keyframed/debug"

# maybe use icecream here instead?
# https://github.com/gruns/icecream
def _inspect(item, depth=0):
    pad="\t"*depth
    if depth > 0:
        pad +="- "
    # NB: Linter says using f-strings in log statements can hinder performance
    logger.info(f"{pad}type: {type(item)}")
    log_item=True
    
    # maybe a bit overengineered. whatever.
    if hasattr(item, "shape"):
        logger.info(f"{pad}item.shape: {item.shape}")
        log_item=False
    elif hasattr(item, "size"):
        try:
            logger.info(f"{pad}item.shape: {item.size()}")
        except TypeError:
            logger.info(f"{pad}item.shape: {item.size}")
        log_item=False
    
    if isinstance(item, Image):
        logger.info(f"{pad}item.mode: {item.mode}")


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
    OUTPUT_NODE=True

    _FORCED_INPUT = {"label": ("STRING", {
                    "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "debugging passthrough"})}

    @classmethod
    def INPUT_TYPES(cls):
        outv = {
            "required": {
                "item": (cls.RETURN_TYPES[0],{"forceInput": True,}),
            },
        }
        outv["required"].update(cls._FORCED_INPUT)
        return outv

    def main(self, item, label):
        #if label:
        logger.info(f"label: {label}")
        _inspect(item)
        return (item,) # pretty sure it's gotta be a tuple?


# class KfDebug_DummyOutput(KfDebug_Passthrough):
#     OUTPUT_NODE=True
#     _FORCED_INPUT = {"label": ("STRING", {
#                     "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
#                     "default": "dummy output"})}

###########################

### Built-in Types


# there should be a way to create a type-agnostic passthrough node

class KfDebug_Clip(KfDebug_Passthrough):
    RETURN_TYPES = ("CLIP",)


class KfDebug_Cond(KfDebug_Passthrough):
    RETURN_TYPES = ("CONDITIONING",)


class KfDebug_Float(KfDebug_Passthrough):
    RETURN_TYPES = ("FLOAT",)


class KfDebug_Image(KfDebug_Passthrough):
    RETURN_TYPES = ("IMAGE",)


class KfDebug_Int(KfDebug_Passthrough):
    RETURN_TYPES = ("INT",)


class KfDebug_Latent(KfDebug_Passthrough):
    RETURN_TYPES = ("LATENT",)


class KfDebug_Model(KfDebug_Passthrough):
    RETURN_TYPES = ("MODEL",)


class KfDebug_String(KfDebug_Passthrough):
    RETURN_TYPES = ("STRING",)


class KfDebug_Vae(KfDebug_Passthrough):
    RETURN_TYPES = ("VAE",)


##############################################

### Custom Node Types


class KfDebug_Segs(KfDebug_Passthrough):
    RETURN_TYPES = ("SEGS",)


class KfDebug_Curve(KfDebug_Passthrough):
    RETURN_TYPES = ("KEYFRAMED_CURVE",)


# ###########################


NODE_CLASS_MAPPINGS = {
    #"KfDebug_Passthrough": KfDebug_Passthrough,
    "KfDebug_Float": KfDebug_Float,
    "KfDebug_Cond": KfDebug_Cond,
    "KfDebug_Curve": KfDebug_Curve,
    "KfDebug_Latent": KfDebug_Latent,
    "KfDebug_Model": KfDebug_Model,
    "KfDebug_Vae": KfDebug_Vae,
    "KfDebug_Clip": KfDebug_Clip,
    "KfDebug_Image": KfDebug_Image,
    "KfDebug_Int": KfDebug_Int,
    "KfDebug_String": KfDebug_String,
    "KfDebug_Segs": KfDebug_Segs,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {k:k for k in NODE_CLASS_MAPPINGS}