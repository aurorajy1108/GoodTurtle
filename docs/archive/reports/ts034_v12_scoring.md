# TS034 host-v12 and scoring clarification

TS034 host-v12 distinguishes the father's fear that both may be killed if his daughter arrives from an established unconditional killing plan or certain outcome. The active host binding changes; historical snapshots and scores remain unchanged.

`data/studies/ts034_v5.json` is a TS034-only dataset containing the local v5 grading clarification. The source story and weights are unchanged. General danger to the daughter and refusal can receive partial credit; an unsupported alternative motive does not establish witness elimination or protective self-sacrifice. This dataset must be specified explicitly and is not a replacement for the 50-puzzle default.

Selected prior checks: four persistent host calibration cases passed; two original submissions scored 75% and incomplete under the clarified persistent grader. Four compact grader calibration cases passed. These are not held-out estimates and do not guarantee stable model behavior. Results generated with v9 and old scoring must be reported separately.

For an API-free validation of the data and selected cases:

```sh
python3 scripts/check_host.py --dataset data/studies/ts034_v5.json --config configs/loop.deepseek.solo-json.json --cases tests/fixtures/ts034_host_v12.json --out /tmp/ts034-host-preflight --dry-run
python3 scripts/check_grader.py --dataset data/studies/ts034_v5.json --config configs/loop.deepseek.solo-json.json --cases tests/fixtures/ts034_grader_v5.json --out /tmp/ts034-grader-preflight --dry-run
```
