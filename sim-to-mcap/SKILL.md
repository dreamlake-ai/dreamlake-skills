---
name: sim-to-mcap
description: Use a local Python simulation rollout to write an indexed MCAP with Foxglove transforms, robot geometry, and metrics. Use for embodied policy rollouts; dreamlake-source connects the output and dreamlake-dataset-viz configures its views.
---
# Convert a Simulation Rollout to MCAP

Use this local Python workflow when you have a trained policy and a physics simulator and need a DreamLake-playable MCAP. Install `foxglove-sdk`, adapt the [rollout writer](./references/write-rollout.md) to the simulator, and produce `/tf`, `/robot` and `/metrics` channels. Use [handoff and debug](./references/handoff-and-debug.md) to upload and bind the file.

This skill creates the local MCAP; [dreamlake-source](../dreamlake-source/SKILL.md) connects it and [dreamlake-dataset-viz](../dreamlake-dataset-viz/SKILL.md) configures its views. A numeric-only run without a body pose should use chart views instead.
