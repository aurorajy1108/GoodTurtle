# Experiment records on Hugging Face

The published puzzle collection is [COMP1110-20261A-Group50/GoodTurtle](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle).
Its 50 rows contain `id`, `question`, `answer`, `source` and `rubric`.

Full experiment records are published in `COMP1110-20261A-Group50/GoodTurtle-experiments`.
A publication is complete after uploading and downloading the pinned release, checking the full archive,
and writing a verification receipt. This release has completed upload and pinned-download verification; GitHub retains compact summaries and a remote descriptor.

## Data layout

| File | Contents |
| --- | --- |
| `data/games.jsonl` | One row per canonical game, with settings, outcome and usage information |
| `data/turns.jsonl` | Questions, answer attempts and recorded public feedback |
| `data/messages.jsonl` | Shared messages and private draft/review notes, explicitly labelled |
| `results.tar.gz` | Complete original published results tree, including frozen settings and text records |
| `archive_manifest.json` | File inventory for download verification |
| `release.json` | Counts, source code version and archive information |
| `README.md` | HF dataset card with three independently browsable configurations |

The proposed snapshot has 206 games, 20,076 submissions and 4,937 shared/reflection messages.
New live experiments are not included until finished and registered. Original host answers, scores,
completion decisions and source labels remain unchanged.

## Prepare and verify locally

In a lightweight code checkout, run `python3 scripts/fetch_results.py` first to restore the full results tree before exporting a new version. The core preparation/download tools use the Python standard library. Choose new output directories:

```bash
python3 scripts/export_hf_results.py --out /path/outside/repo/hf-bundle
python3 scripts/fetch_results.py --source /path/outside/repo/hf-bundle \
  --root /path/outside/repo/restore-check
```

`--source` verifies a local prepared bundle without network access. It restores original records and
checks the complete catalog. Existing conflicting files are never overwritten. The lightweight
GitHub results README and summaries are preserved when restoring into a code checkout.

## Publish (maintainers)

Publishing additionally requires `huggingface_hub` and an HF account/token with write access to the
organization. Store `HF_TOKEN` in the environment or an ignored local environment file; never commit it.
Then, in a shell with that environment loaded:

```bash
python3 scripts/publish_hf_results.py --folder /path/outside/repo/hf-bundle \
  --repo-id COMP1110-20261A-Group50/GoodTurtle-experiments \
  --verification-dir /path/outside/repo/remote-check \
  --receipt /path/outside/repo/verified-remote.json
```

The command uploads the prepared dataset, downloads its exact revision, verifies the archive and original
records, and writes the receipt only after success. Do not use another personal namespace as a substitute
for the project organization.

## GitHub migration after successful publication

Keep code, configurations, prompts, tests, small summary tables and final paper figures on GitHub.
Pin the verified receipt as `results/remote.json`, document its HF link and provide:

```bash
python3 scripts/fetch_results.py
```

Once the pinned download has been independently verified, remove the full `results/trajectories/`,
review payloads, redundant inventories and detailed analysis exports from the release branch.
The downloader restores the original directory structure when full analysis is needed.
Update catalog/release checks to accept a lightweight checkout and require restored files for full validation.

Versioned runtime annotations and active host packs remain part of reproducible code inputs. The public
HF puzzle table does not replace a historical run's frozen settings. Keep the existing HF puzzle release
unchanged while publishing experiment records separately.
