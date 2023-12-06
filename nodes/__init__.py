
from .core import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from .debug import NODE_CLASS_MAPPINGS as ncm0, NODE_DISPLAY_NAME_MAPPINGS as ndnm0
from .entangled import NODE_CLASS_MAPPINGS as ncm1, NODE_DISPLAY_NAME_MAPPINGS as ndnm1

# there's probably a cleaner, more-dummy-proof way to do this.
# feels like an accident waiting to happen. low risk though.
NODE_CLASS_MAPPINGS.update(ncm0)
NODE_CLASS_MAPPINGS.update(ncm1)
NODE_DISPLAY_NAME_MAPPINGS.update(ndnm0)
NODE_DISPLAY_NAME_MAPPINGS.update(ndnm1)


__all__ =["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]