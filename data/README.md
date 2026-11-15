# Dataset and host references

[Public dataset on Hugging Face](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle) · [Dataset card](DATASET_CARD.md).

The public table contains 50 puzzles. Versioned annotations and host packs below are retained as reproducible runtime inputs.

| Content | Location |
| --- | --- |
| Current 50-puzzle dataset and unified scoring | `annotations/turtle50_v5/private.json` |
| Previous annotation versions | `annotations/turtle50_v2/` through `turtle50_v4/` |
| New human reference conversations | [Host-reference inbox](host_reference/inbox/README.md) |
| Registered sources and reviewed answers | [Host reference guide](host_reference/README.md) |
| Runtime host examples | [Host packs](host_packs/README.md), selected by `configs/host_bindings.json` |
| Prototype compatibility data | `public/`, `host_dev/`, `release_scope.json` |

“Private” means hidden from the player during gameplay. Host and grader inputs include the answer and scoring rules; players receive the opening and public feedback. Human reference sources belong here, while generated experimental games belong in `results/trajectories/` after publication. Retain the original language and provenance of source conversations.
