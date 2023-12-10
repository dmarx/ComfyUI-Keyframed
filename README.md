# Keyframed Nodes For ComfyUI

ComfyUI nodes to facilitate parameter/prompt keyframing using comfyui nodes for defining and manipulating parameter curves. Essentially provides a ComfyUI interface to the [keyframed](https://github.com/dmarx/keyframed) library.

Related project: https://github.com/FizzleDorf/ComfyUI_FizzNodes

---

<!--ts-->
* [ComfyUI-Keyframed](#comfyui-keyframed)
* [Overview](#overview)
* [Starter Workflows](#starter-workflows)
   * [Prompt Scheduling](#prompt-scheduling)
   * [Interleaving Multiple Prompts Simultaneously (aka Prompt Entanglement, aka Prompt Superposition)](#interleaving-multiple-prompts-simultaneously-aka-prompt-entanglement-aka-prompt-superposition)
   * [AnimateDiff Prompt Superposition - Complex Workflow](#animatediff-prompt-superposition---complex-workflow)
   * [Simple Curved Parameter](#simple-curved-parameter)
   * [Multi-Prompt Transition With Manually Specified Curves](#multi-prompt-transition-with-manually-specified-curves)
* [Nodes](#nodes)
   * [Curve Constructors](#curve-constructors)
      * [Curve From String](#curve-from-string)
      * [Curve From YAML](#curve-from-yaml)
      * [Constant-Valued Curve](#constant-valued-curve)
      * [Entangled Curves](#entangled-curves)
   * [Curve Operators](#curve-operators)
      * [Evaluate Curve At T](#evaluate-curve-at-t)
      * [Apply Curve To Conditioning](#apply-curve-to-conditioning)
      * [Add Conditions](#add-conditions)
      * [Curve Arithmetic Operators](#curve-arithmetic-operators)
   * [Scheduling](#scheduling)
      * [Keyframed Condition](#keyframed-condition)
         * [Interpolation Methods](#interpolation-methods)
      * [Set Keyframe](#set-keyframe)
      * [Evaluate Schedule](#evaluate-schedule)
<!--te-->


# Overview

**Philosophy**

* Treat curves/schedules and keyframes as objects that can be passed around, plugged and unplugged, interchanged, and manipulated atomically.
* Leverage nodes to facilitate modularity and flexibility.
* Facilitate fast iteration
* Provide convenience functions for most common use cases, and also low-leverl operators capable of reproducing the behavior of those convenience functions to permit user customization in "node space".


# Starter Workflows

## Prompt Scheduling

![Prompt Scheduling](examples/prompt-scheduling.png)

 This one is probably why you are here. This workflow demonstrates how to use the `keyframed/schedule` nodes to achieve similar behavior as [FizzNodes'](https://github.com/FizzleDorf/ComfyUI_FizzNodes) **PromptSchedule** node, but implemented differently.

This schedule is essentailly a normal AnimateDiff workflow where several nodes have replaced the normal conditioning setup. Rather than a single `CLIP Text Encode` node, we can have multiple prompts which transition sequentially over time. For documentation detailing how this workflow works, see the [`Nodes > Scheduling`](https://github.com/dmarx/ComfyUI-Keyframed/blob/dev/README.md#scheduling) section below.

## Interleaving Multiple Prompts Simultaneously (aka Prompt Entanglement, aka Prompt Superposition)

![Prompt Entanglement](examples/prompt-entanglement.png)

Which is the node equivalent for achieving this type of thing

![](https://pbs.twimg.com/media/Fqcdhe4agAEnJ-L?format=jpg&name=large)

For documentation detailing how this workflow works, see the [`Nodes > Entangled Curves`](https://github.com/dmarx/ComfyUI-Keyframed?tab=readme-ov-file#entangled-curves) section below.

## AnimateDiff Prompt Superposition - Complex Workflow

![Prompt Entanglement](examples/8x-interleaved-prompts_2phase-ad_loop-friendly-vfi_upscale.png)

Workflow output: https://twitter.com/DigThatData/status/1733416414864957484

* 8x Prompt superposition
* Second pass of AnimateDiff with denoise reduced to serve as a "refinement pass"
* FiLM Video Frame Interpolation (VFI) modified to interpolate looping videos correctly
* ESRGAN 2x Upscaling

## Simple Curved Parameter

![Simple Curved Parameter](examples/simple-curved-parameter.png)


## Multi-Prompt Transition With Manually Specified Curves

![Manual Prompt Transition](examples/manual-prompt-transition.png)

If you're feeling adventurous, this workflow demonstrates how you would use the curve objects directly to acheive the same thing as a schedule. Each prompt gets its own seaparate curve indicating the weight of the prompt at that time (you probably want the various conditionings weights to sum to 1 when combined. If you need to "fill" missing conditioning weight, try using an empty prompt).

# Nodes

## Curve Constructors

### Curve From String

![Curve From String](assets/node_curve-from-string.png)

Supports commonly used notation for curved parameter. See also Deforum, FizzNodes, https://www.chigozie.co.uk/keyframe-string-generator/

### Curve From YAML

![Curve From YAML](assets/node_curve-from-yaml.png)

Supports curved parameter notation used by https://github.com/dmarx/keyframed

### Constant-Valued Curve

![Curve From YAML](assets/node_constant-valued-curve.png)

Returns a curve which evaluates to the same value for all values of `t` (time). Especially useful for curve arithmetic.

### Entangled Curves

![Entangled Curves](assets/nodes_entangled.png)

Each output curve of the node is a sine wave that oscillates from `0` to `1` at the given frequency or wavelength. The outputs of a given node are phase-offset such that at any given time, the sum of the generated curves is `1`. 

Reference the [Prompt Interleaving Workflow](https://github.com/dmarx/ComfyUI-Keyframed/blob/dev/README.md#prompt-interleaving-aka-prompt-entanglement-aka-prompt-superposition) for a demonstrative example.

## Curve Operators

### Evaluate Curve At T

![Evaluate Curve At T](assets/node_evaluate-curve-at-t.png)


### Apply Curve To Conditioning

![Apply Curve To Conditioning](assets/node_apply-curve-to-conditioning.png)

Generates a batch of `n` conditionings multiplying each conditioning by th value of the curve at that conditioning's index within the batch. If a batch of latents is provided, `n` is ignored and the size of the latent batch is used. If the provided conditioning object has batch size > 1, the conditioning's batch size takes priority over the latent batch size and `n`.


### Add Conditions

![Apply Curve To Conditioning](assets/node_add-conditions.png)


### Curve Arithmetic Operators

![Curve Arithmetic](assets/nodes_curve-arithmetic.png)

NB: the division operator is unreliable at the time of this writing (2023-12-09).


## Scheduling

These nodes work together to facilitate transitioning through a sequence of conditionings (i.e. prompts). We'll call this sequence the "schedule" of the conditionings. The primary use case here is for manipulating the positive prompt, i.e. for building a "prompt schedule". Given a particular time (e.g. frame id) in an animation seuquence, we can query the prompt schedule at that time to get the appropriate conditioning to pass to the KSampler. 

Reference the [Prompt Scheduling Workflow](https://github.com/dmarx/ComfyUI-Keyframed/tree/dev?tab=readme-ov-file#prompt-scheduling) for a demonstrative example

### Keyframed Condition

![Keyframed Condition](assets/node_keyframed-condition.png)

This node attaches a `conditioning` to a `keyframe`. This let's us assign a time to the conditioning and set what interpolation method to use when we're between keyframes. 

#### Interpolation Methods

Consider three time points `a,b,c` such that `a<b<c`, and two keyframes `X,Y` such that `X.time = a` and `Y.time = c`. To interpolate a value at time `b`, we would use `X.interpolation_method` to "tween" the value between `X.value` and `Y.value`. 

* **`null`** - If the interpolation value is not set, the default interpolation is "previous".
* **`previous`** - `X.time`
* **`next`** - `Y.time`
* **`linear`** - normal linear lerp. Matches the behavior of Deforum and FizzNodes.
* **`sine_wave`** - sine function easing. slower close to terminal values, fastest at the middle of the transition.
* **`eased_lerp** - sin2 easing. similar to sine but starts and ends slower and the fastest part is faster.
* **`exp_decay`** - starts fast ends slow.

### Set Keyframe

![Set Keyframe](assets/node_set-keyframe.png)

Attaches a keyframe to a schedule. If you haven't created a schedule yet, pass your keyframe into this node to create one, then pass the output schedule to subsequent `Set Keyframe` nodes to attach additional keyframes to the schedule. The first keyframe in the schedule should always be at `time=0`.

### Evaluate Schedule

![Evaluate Schedule](assets/nodes_evaluate-schedule.png)

Evaluate the schedule at a time or time slice to extract a single conditioning or conditioning batch (respectively) to provide to e.g. a KSampler. The non-batch version gives the same kind of conditioning you'd get from a `CLIPTextConditioning` node. The intention of the batch version is to use with AnimateDiff to apply different conditionings per frame.

