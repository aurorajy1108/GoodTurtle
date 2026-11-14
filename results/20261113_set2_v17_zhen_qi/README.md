# Set 2 v17: Zhen Qi's five-repeat archive

[中文](README.zh-CN.md) · [Browse all trajectories](index.html) · [Runs CSV](runs.csv) · [35-game chart](figures/your_35.pdf) · [Cross-batch comparison](figures/comparison_53.pdf)

This release publishes **35 completed TS034 target games and the three fixed source games** used by Zhen Qi's experiments. Target conditions are a shared direct baseline and answer-only/session transfer from TS033, TS035 and TS012, with five independent target starts per condition. Restored copies represent the same logical game, never additional repeats. All original final scores and public/model responses are retained; none of the 35 target games met the complete-solution criterion.

| Source A | Direct baseline | Answer-only | Full source session |
|---|---:|---:|---:|
| TS033, negative hypothesis | 55.5% (shared) | 66.5% | 27.0% |
| TS035, positive hypothesis | 55.5% (shared) | 23.0% | 41.0% |
| TS012, irrelevant hypothesis | 55.5% (shared) | 33.0% | 56.0% |

These are original **final partial-score means**, not success rates. Direct is five games total, not five new games for each row. Each transfer cell has five games conditioned on one fixed source experience; this is not replication across five source examples or five target puzzles. The relation labels are prior hypotheses, not established effects.

## Frozen conditions

- Target: TS034, Host `host-v17-ts034-witness-timeline-20261112`, scoring `ts034-scoring-v6-aligned-20261111`, `coverage-v2` with opt-in `rubric_aligned_v1` completion. This archive does **not** claim to use main's later unified-v3 defaults.
- Player: `deepseek-flash`, thinking disabled, max output 8,192; Host/Grader: `deepseek-v4-pro`, thinking enabled/high, max output 32,768. Prompts, actual configs, puzzle/rubric and Host context are saved per game.
- Target weights: identity/call roles 45%, conditional witness-killing fear 30%, protective refusal/communication/personal risk 20%, wealthy daughter 2%, only family 3%.
- Session transfer inherits the complete fixed A Player-message prefix and reveals the official source solution at the boundary. B receives a new 100-slot budget and its own Host/Grader. `transfer_boundary.json` records the boundary and inherited prefix hash; `sources/` contains each A trajectory. TS012's official reveal includes its frozen Host's supplementary setting and is longer than its base dataset answer. Answer-only uses the same official reveal, without the source dialogue.

## Recoveries and protocol interventions

Every game exhausted its 100-slot budget. A slot is not necessarily a question or an executed action. TS012 answer-only R3 contains one invalid slot (#44); TS033 answer-only R3 contains three (#67, #76, #87). Those four replies consumed budget but were **not executed and received no Host/Grader label**. Their original text and explicit controller notices remain in the trajectory. They are marked in `runs.csv` and the chart; excluding these two games is a separate sensitivity analysis, not the main result.

Network and format-only continuations retain observed replies and earlier records. Direct R5's saved Chinese `最终` header was recovered as FINAL at slot95; its body, including the wrong amount, was not translated or corrected. Runtime/controller hashes vary across recovery implementations; common task/Host/Grader/prompt hashes do not imply byte-identical engine code. The release is an immutable outcome archive, not a resumable runtime.

Historical `format_repair` auxiliary calls, including any `codex_cli / gpt-6.1-sol` calls, remain in the API audits. They are format assistance, not evidence of an additional puzzle-solving agent. Per-game counts and failed attempts are retained. Unknown costs are not zero; `target_costs.json` gives the known API-equivalent subtotal and unknown counts, not an actual invoice.

## Files, verification and review

Each game contains the complete public trajectory (JSONL, Markdown, HTML), raw final result, actual config/prompts, private puzzle/rubric, Host context, review templates, usage/cost files and `verification.json`. Verification covers counters, feedback for executed actions, weighted scores, completion consistency, final-answer text, cost-call counts, source answer boundaries and published-byte hashes. Structural verification is distinct from semantic correctness.

`api_audit.jsonl.gz` preserves **every recorded response, error, usage and accounting entry** in order. Repeated request bodies and inherited-session bodies remain local; the publication includes their deterministic hashes plus the source log hash. These compact audits cannot reconstruct full HTTP requests. `manifest.json` reports the omitted raw log volume. API keys, environment files and unrelated working files are not part of this archive.

[Offline review](analysis.zh-CN.md) covers all new R4/R5 records structurally and selected Host/Grader cases semantically. `review/` stores the assistant's suggested adjudications separately, including the earlier context review. They are **not user-confirmed human gold** and do not overwrite the original labels or scores. Format recovery, semantic intervention, score disputes and zero-score games are all disclosed rather than filtered out.

The comparison figure incorporates 18 already published teammate target games from pinned main `25f4cc4`; `comparison_53_records.json` contains their original scores and fixed GitHub links, not duplicate trajectory archives. Different Host/scoring versions remain separate. Direct controls are repeated visually across source panels for readability, but counted once. No pooled cross-version mean or significance claim is made.

## Offline verification and reproduction

From the repository root, without API calls:

```bash
python3 scripts/publish_set2_v17_archive.py \
  --out results/20261113_set2_v17_zhen_qi --verify-only
```

To export from full local originals, supply a JSON manifest with `targets` (35 entries) and `sources` (three entries). Each entry names `run_dir`, `run_id`, `source`, `condition` and `repeat`; directories refer to the authoritative completed continuation, not an earlier stopped copy. Use a new `--out` directory. The exporter verifies before finalizing an atomic publication and never imports an API client.

The comparison can be regenerated with Matplotlib and NumPy:

```bash
GOODTURTLE_CHINESE_FONT=/path/to/chinese-font.ttc \
  python3 results/20261113_set2_v17_zhen_qi/render_comparison.py
```

The original 35-game chart is preserved verbatim. Its plotted data are available in `review/combined_35_runs.csv`; historical local paths in provenance identify origin records and are not runtime dependencies. This PR publishes results only and does not change active Host, Grader or Player defaults.
