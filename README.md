# ComfyUI-Keyframed

🚧 Work In Progress 🚧 - ComfyUI nodes to facilitate value keyframing by providing an interface for using [keyframed](https://github.com/dmarx/keyframed) in ComfyUI workflows.


...Open question: if I make this, what will differentiate it from https://github.com/FizzleDorf/ComfyUI_FizzNodes ?

* easier curve composition
* easier to change interpolators/easing functions

# Philosophy

Treat curves/schedules and keyframes as objects that can be passed around, plugged and unplugged, interchanged, and manipulated atomically.

# Starter Workflows

## Prompt Scheduling

![Prompt Scheduling](examples/prompt-scheduling.png)

## Prompt Interleaving (aka Prompt Entanglement, aka Prompt Superposition)

![Prompt Entanglement](examples/prompt-entanglement.png)

Which is the node equivalent for achieving this type of thing

![](https://pbs.twimg.com/media/Fqcdhe4agAEnJ-L?format=jpg&name=large)

## Simple Curved Parameter

![Simple Curved Parameter](examples/simple-curved-parameter.png)

## Multi-Prompt Transition With Manually Specified Curves

![Manual Prompt Transition](examples/manual-prompt-transition.png)

