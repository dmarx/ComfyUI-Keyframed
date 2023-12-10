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

 This one is probably why you are here. This workflow demonstrates how to use the `keyframed/schedule` nodes to achieve similar behavior as [FizzNodes'](https://github.com/FizzleDorf/ComfyUI_FizzNodes) **PromptSchedule** node, but implemented differently.

This schedule is essentailly a normal AnimateDiff workflow where several nodes have replaced the normal conditioning setup. Rather than a single `CLIP Text Encode` node, we can have multiple prompts which transition sequentially over time. For documentation detailing how this workflow works, see the `Nodes > Scheduling` section below.

## Prompt Interleaving (aka Prompt Entanglement, aka Prompt Superposition)

![Prompt Entanglement](examples/prompt-entanglement.png)

Which is the node equivalent for achieving this type of thing

![](https://pbs.twimg.com/media/Fqcdhe4agAEnJ-L?format=jpg&name=large)


## Simple Curved Parameter

![Simple Curved Parameter](examples/simple-curved-parameter.png)


## Multi-Prompt Transition With Manually Specified Curves

![Manual Prompt Transition](examples/manual-prompt-transition.png)


# Nodes

## Curve Constructors

### Curve From String

![Curve From String](assets/node_curve-from-string.png)


### Curve From YAML

![Curve From YAML](assets/node_curve-from-yaml.png)


### Constant-Valued Curve

![Curve From YAML](assets/node_constant-valued-curve.png)


### Entangled Curves

![Entangled Curves](assets/nodes_entangled.png)


## Curve Operators

### Evaluate Curve At T

![Evaluate Curve At T](assets/node_evaluate-curve-at-t.png)


### Apply Curve To Conditioning

![Apply Curve To Conditioning](assets/node_apply-curve-to-conditioning.png)


### Add Conditions

![Apply Curve To Conditioning](assets/node_add-conditions.png)


### Curve Arithmetic Operators

![Curve Arithmetic](assets/nodes_curve-arithmetic.png)

NB: the division operator is unreliable at the time of this writing (2023-12-09).


## Scheduling

### Keyframed Condition

![Keyframed Condition](assets/node_keyframed-condition.png)


### Set Keyframe

![Set Keyframe](assets/node_set-keyframe.png)

### Evaluate Schedule

![Evaluate Schedule](assets/nodes_evaluate-schedule.png)

