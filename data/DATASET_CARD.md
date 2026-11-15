# GoodTurtle dataset card

## Contents and intended use

GoodTurtle contains 50 English Turtle Soup puzzles with 161 weighted scoring checkpoints. It supports research on interactive questioning, story reconstruction, prior experience and cooperation. A puzzle consists of an opening, hidden answer, weighted rubric and available host reference material. See the [dataset guide](README.md) for file locations.

## Preparation

The five project members collected ten puzzle candidates each. The team checked English wording, trialled candidates, prepared scoring annotations and reviewed uncertain host replies. Reference material includes original human conversations, model-generated games and later review decisions. Source identity and review status are retained in the reference records. Version-specific annotation notes describe subsequent changes.

The release preserves source wording and original conversations. Dated records may include Chinese explanations or review notes; the playable openings and project entry documentation are English.

## Evaluation boundary

The host and grader may read the hidden answer and rubric. The player may read only its opening, permitted prior experience and public feedback. Avoid exposing `private.json`, host packs or grader output to the player. Here, “private” describes gameplay visibility rather than repository access.

New experiments default to `annotations/turtle50_v5/private.json`. Older versions remain available for historical comparisons. Questions in the reference inbox do not enter the host automatically: activation follows review and the binding configuration.

## Interpretation

Reference review and model evaluation are recorded separately from original human annotations. Story scoring includes judgment about paraphrases and causal coverage. Repeated model runs can differ, and this puzzle collection does not estimate performance across all reasoning tasks.

## Sources and rights

Puzzle and conversation provenance is retained where available in the dataset and host-reference sources. The collection includes adapted third-party stories; this repository does not assign a new license to those underlying stories. No project-wide software license has been selected by the authors in this release. Cite the repository and relevant original sources when describing the work.
