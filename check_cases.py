import json

ok_sentiment = {"positive", "neutral", "negative"}
ok_urgency = {"low", "medium", "high"}
ok_difficulty = {"easy", "medium", "hard"}

with open("evals/test_cases.jsonl", encoding="utf-8") as f:
    lines = f.read().splitlines()

problems = 0
seen_ids = set()
for n, line in enumerate(lines, 1):
    if not line.strip():
        print(f"Line {n}: blank line, delete it")
        problems += 1
        continue
    try:
        case = json.loads(line)
    except Exception as e:
        print(f"Line {n}: not valid JSON ({e})")
        problems += 1
        continue
    if case.get("expected_sentiment") not in ok_sentiment:
        print(f"Line {n}: bad expected_sentiment")
        problems += 1
    if case.get("expected_urgency") not in ok_urgency:
        print(f"Line {n}: bad expected_urgency")
        problems += 1
    if case.get("difficulty") not in ok_difficulty:
        print(f"Line {n}: bad difficulty")
        problems += 1
    if case.get("id") in seen_ids:
        print(f"Line {n}: duplicate id {case.get('id')}")
        problems += 1
    seen_ids.add(case.get("id"))

print(f"Checked {len(lines)} lines, {problems} problem(s) found.")