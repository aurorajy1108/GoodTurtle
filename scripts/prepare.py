#!/usr/bin/env python3
"""Prepare local research assets. No network calls or model inference."""
import argparse
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = {"yes", "no", "yes and no"}
HOST_FIELDS = ("opening", "solution", "canonical_facts", "explicit_negatives", "unknown_details")


def release_scope():
    path = ROOT / "data/release_scope.json"
    return json.loads(path.read_text()) if path.exists() else None


def read_data():
    scope = release_scope()
    candidates_path = ROOT / "data/private/candidates.json"
    puzzles = json.loads(candidates_path.read_text()) if candidates_path.exists() else []
    if scope is not None:
        puzzles = [p for p in puzzles if p["puzzle_id"] in scope["puzzle_ids"]]
    if scope is not None and not scope["include_shared_demonstrations"]:
        examples = {"stories": [], "selection_order": []}
    else:
        examples = json.loads((ROOT / "data/host_examples.json").read_text())
    return puzzles, examples


def validate(puzzles, examples):
    errors = []
    scope = release_scope()
    if not puzzles and scope is None:
        errors.append("The candidate bank must not be empty.")
    ids = [p.get("puzzle_id") for p in puzzles]
    families = [p.get("family_id") for p in puzzles]
    if None in ids or len(set(ids)) != len(ids):
        errors.append("Puzzle IDs must be present and unique.")
    if None in families or len(set(families)) != len(families):
        errors.append("Draft candidate family IDs must be present and unique; human deduplication remains required.")
    required = set(HOST_FIELDS) | {"puzzle_id", "family_id", "curator_title", "language", "split", "rubric", "reference_path", "provenance", "human_review", "screening", "mechanism_tags", "surface_tags", "review_risk"}
    for puzzle in puzzles:
        pid = puzzle.get("puzzle_id", "<missing>")
        missing = required - puzzle.keys()
        if missing:
            errors.append(f"{pid}: missing {sorted(missing)}")
            continue
        if puzzle["language"] != "en":
            errors.append(f"{pid}: this release requires English stories.")
        for field in HOST_FIELDS:
            expected_type = str if field in {"opening", "solution"} else list
            value = puzzle[field]
            if not isinstance(value, expected_type) or not value:
                errors.append(f"{pid}: invalid {field}")
            elif isinstance(value, list) and any(not isinstance(v, str) or not v.strip() for v in value):
                errors.append(f"{pid}: invalid fact in {field}")
        if not puzzle["rubric"]:
            errors.append(f"{pid}: no rubric")
        elements = set()
        for element in puzzle["rubric"]:
            if not all(element.get(k) for k in ("element_id", "complete", "partial", "absent_or_incorrect")):
                errors.append(f"{pid}: incomplete rubric anchor")
            eid = element.get("element_id")
            if eid in elements:
                errors.append(f"{pid}: duplicate rubric element")
            elements.add(eid)
        if not puzzle["reference_path"]:
            errors.append(f"{pid}: missing reference path")
        for turn in puzzle["reference_path"]:
            if turn.get("label") not in LABELS or not turn.get("question"):
                errors.append(f"{pid}: invalid reference QA")
        screening = puzzle["screening"]
        if screening.get("status") == "not_run" and any(screening.get(k) is not None for k in ("direct_successes", "quick_successes", "interactive_successes", "decision")):
            errors.append(f"{pid}: unrun screening contains results")
    counts = Counter()
    case_ids = set()
    for story in examples["stories"]:
        if story["family_id"] in families:
            errors.append("A host demonstration overlaps a candidate family.")
        for case in story["cases"]:
            if case["case_id"] in case_ids:
                errors.append("Duplicate host example ID.")
            case_ids.add(case["case_id"])
            counts[case["expected_label"]] += 1
            if case["expected_label"] not in LABELS:
                errors.append("Invalid host demonstration label.")
            for turn in case["public_history"]:
                if turn["label"] not in LABELS:
                    errors.append("Invalid history label.")
    shared_disabled = scope is not None and not scope["include_shared_demonstrations"]
    if set(counts) != LABELS and not (shared_disabled and not counts):
        errors.append("Host examples must cover all three labels.")
    order = examples.get("selection_order", [])
    if len(order) != len(set(order)) or set(order) != case_ids:
        errors.append("selection_order must contain every example ID exactly once.")
    if errors:
        raise ValueError("\n".join(errors))
    return counts


def public_rows(puzzles):
    # Explicit allowlist: new private fields cannot leak through future additions.
    return [{"puzzle_id": p["puzzle_id"], "opening": p["opening"]} for p in puzzles]


def read_host_packs():
    packs = {}
    scope = release_scope()
    for path in sorted((ROOT / "data/host_packs").glob("*.json")):
        if scope is not None and path.stem not in scope["puzzle_ids"]:
            continue
        pack = json.loads(path.read_text())
        pid = pack["puzzle_id"]
        if path.stem != pid or pid in packs:
            raise ValueError(f"Invalid/duplicate host pack ID: {path.name}")
        for field in HOST_FIELDS:
            value = pack[field]
            expected = str if field in {"opening", "solution"} else list
            if not isinstance(value, expected) or (expected is str and not value.strip()):
                raise ValueError(f"{pid}: invalid {field}")
            if expected is list and any(not isinstance(v, str) or not v.strip() for v in value):
                raise ValueError(f"{pid}: invalid fact in {field}")
        seen_ids, seen_questions = set(), {}
        if not pack.get("host_examples"):
            raise ValueError(f"{pid}: empty host example bank")
        for case in pack["host_examples"]:
            if not case.get("case_id") or case["case_id"] in seen_ids:
                raise ValueError(f"{pid}: missing/duplicate case ID")
            seen_ids.add(case["case_id"])
            if not isinstance(case.get("question"), str) or not case["question"].strip() or case.get("answer") not in LABELS:
                raise ValueError(f"{pid}: invalid question/answer")
            history = case.get("public_history", [])
            for turn in history:
                if not turn.get("question") or turn.get("label") not in LABELS:
                    raise ValueError(f"{pid}: invalid example history")
            key = (case["question"].strip(), json.dumps(history, sort_keys=True))
            if key in seen_questions and seen_questions[key] != case["answer"]:
                raise ValueError(f"{pid}: conflicting labels for identical question and history")
            seen_questions[key] = case["answer"]
        packs[pid] = pack
    if scope is not None and set(packs) != set(scope["puzzle_ids"]):
        raise ValueError("Every puzzle in release_scope must have a host pack.")
    return packs


def host_messages(puzzle, examples, shots, question):
    by_id = {}
    for story in examples["stories"]:
        for case in story["cases"]:
            by_id[case["case_id"]] = {
                "example_story": {"opening": story["opening"], "solution": story["solution"]},
                "public_history": case["public_history"],
                "question": case["question"],
                "answer": case["expected_label"],
            }
    demonstrations = [by_id[case_id] for case_id in examples["selection_order"]]
    # None means the whole shared bank. Explicit counts remain available for
    # calibration; all conditions for the same puzzle use a frozen configuration.
    if shots is None:
        shots = len(demonstrations)
    if not 0 <= shots <= len(demonstrations):
        raise ValueError(f"shots must be between 0 and {len(demonstrations)}")
    target_examples = [{"question": case["question"], "answer": case["answer"],
                        "public_history": case.get("public_history", [])}
                       for case in puzzle.get("host_examples", [])]
    context = {"PROTOCOL_DEMONSTRATIONS": demonstrations[:shots],
               "TARGET_DEMONSTRATIONS": target_examples,
               "ACTIVE_PUZZLE": {key: puzzle[key] for key in HOST_FIELDS}}
    return [
        {"role": "system", "content": (ROOT / "prompts/host_system.txt").read_text()},
        {"role": "system", "content": "PROTOCOL_DEMONSTRATIONS use other stories. TARGET_DEMONSTRATIONS are designated answers for ACTIVE_PUZZLE; each example history is local to that example, not this game's history.\n" + json.dumps(context, ensure_ascii=False)},
        {"role": "user", "content": json.dumps({"public_history": [], "question": question}, ensure_ascii=False)},
    ]


def review_markdown(puzzles):
    lines = [f"# English candidate review — {len(puzzles)} drafts", "",
             "> SPOILERS: curator-only material. All stories are AI-assisted drafts; difficulty, novelty, human labels and release status remain unverified. Reference paths are illustrative, not empirical solver traces.", "",
             "每题末尾列出重点审查风险；不通过就替换，不能为了凑齐 20 题而保留。JSON 是数据源，运行 `python3 scripts/prepare.py review` 可重新生成此文档。", ""]
    for p in puzzles:
        lines += [f"## {p['puzzle_id']} — {p['curator_title']}", "", "**Opening (solver-visible)**", "", p["opening"], "",
                  "**Solution (private)**", "", p["solution"], "", "**Canonical facts**", ""]
        lines += [f"- {fact}" for fact in p["canonical_facts"]]
        lines += ["", "**Explicitly false**", ""] + [f"- {fact}" for fact in p["explicit_negatives"]]
        lines += ["", "**Unspecified**", ""] + [f"- {fact}" for fact in p["unknown_details"]]
        lines += ["", "**Required elements — 1 / 0.5 / 0**", ""]
        for e in p["rubric"]:
            lines.append(f"- {e['element_id']}: **1:** {e['complete']} **0.5:** {e['partial']} **0:** {e['absent_or_incorrect']}")
        lines += ["", "**Illustrative question path**", ""]
        lines += [f"- {qa['question']} → `{qa['label']}`" for qa in p["reference_path"]]
        lines += ["", f"**Mechanisms:** {', '.join(p['mechanism_tags'])}", "", f"**Review risk:** {p['review_risk']}", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "export", "review"):
        sub.add_parser(command)
    host = sub.add_parser("host")
    host.add_argument("puzzle_id")
    host.add_argument("--shots", type=int, default=None,
                      help="Number of shared demonstrations; default: entire bank")
    host.add_argument("--question", default="<REPLACE WITH ONE PLAYER QUESTION>")
    args = parser.parse_args()
    try:
        puzzles, examples = read_data()
        counts = validate(puzzles, examples)
        packs = read_host_packs()
        if args.command == "validate":
            print(f"Validated structure: {len(puzzles)} candidates; {sum(counts.values())} shared examples {dict(counts)}; {len(packs)} per-puzzle host packs. No model or human validation performed.")
        elif args.command == "export":
            destination = ROOT / "data/public/puzzles.jsonl"
            destination.parent.mkdir(parents=True, exist_ok=True)
            bank = {p["puzzle_id"]: p for p in puzzles}
            bank.update(packs)
            destination.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in public_rows(bank.values())))
            print(f"Exported {len(bank)} openings to {destination}")
        elif args.command == "review":
            if not puzzles:
                raise ValueError("No candidate drafts in this release; use the per-puzzle host packs and run audit reports. Existing review is unchanged.")
            destination = ROOT / "docs/candidate_review.md"
            destination.write_text(review_markdown(puzzles))
            print(f"Wrote curator review to {destination}")
        else:
            # An explicit pack is the versioned hosting source for this ID.
            puzzle = packs.get(args.puzzle_id)
            if puzzle is None:
                puzzle = next((p for p in puzzles if p["puzzle_id"] == args.puzzle_id), None)
            if puzzle is None:
                raise ValueError(f"Unknown puzzle ID: {args.puzzle_id}")
            print(json.dumps(host_messages(puzzle, examples, args.shots, args.question), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Invalid research assets or arguments: {exc}\n")


if __name__ == "__main__":
    main()
