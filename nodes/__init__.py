
from .core import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from .debug import NODE_CLASS_MAPPINGS as ncm0, NODE_DISPLAY_NAME_MAPPINGS as ndnm0
from .entangled import NODE_CLASS_MAPPINGS as ncm1, NODE_DISPLAY_NAME_MAPPINGS as ndnm1
from .schedule import NODE_CLASS_MAPPINGS as ncm2, NODE_DISPLAY_NAME_MAPPINGS as ndnm2
from .sinusoidal import NODE_CLASS_MAPPINGS as ncm3, NODE_DISPLAY_NAME_MAPPINGS as ndnm3
from .pgroup import NODE_CLASS_MAPPINGS as ncm4, NODE_DISPLAY_NAME_MAPPINGS as ndnm4


# there's probably a cleaner, more-dummy-proof way to do this.
# feels like an accident waiting to happen. low risk though.
NODE_CLASS_MAPPINGS.update(ncm0)
NODE_CLASS_MAPPINGS.update(ncm1)
NODE_CLASS_MAPPINGS.update(ncm2)
NODE_CLASS_MAPPINGS.update(ncm3)
NODE_CLASS_MAPPINGS.update(ncm4)
NODE_DISPLAY_NAME_MAPPINGS.update(ndnm0)
NODE_DISPLAY_NAME_MAPPINGS.update(ndnm1)
NODE_DISPLAY_NAME_MAPPINGS.update(ndnm2)
NODE_DISPLAY_NAME_MAPPINGS.update(ndnm3)
NODE_DISPLAY_NAME_MAPPINGS.update(ndnm4)


__all__ =["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]