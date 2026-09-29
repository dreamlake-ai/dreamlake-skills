---
name: dreamlake-dataset-viz
description: Inspect a reachable dataset, author its .dreamrc, bind fields to views, and validate the result. Use when a DreamLake dataset needs visualization setup or repair; use dreamlake-source first if its data is not reachable.
---
# Configure Dataset Visualization

Write a `.dreamrc` for data already reachable through a DreamLake source or public storage. Inspect its root and use the matching reader and field names; start with [choose format and bind views](./references/choose-format-and-bind.md). For simulation trajectories, use [sim playback and conversion](./references/sim-playback-conversion.md). Validate the config and each binding with [validate and reference](./references/validate-and-reference.md). Fetch the linked official spec pages for option-level details instead of guessing keys.

If the data is not yet reachable, use [dreamlake-source](../dreamlake-source/SKILL.md) first.
