import json
import sys

# Gate rules (percentage points). One test note is worth about 3.3 points.
FAIL_IF_FORMAT_DROPS_MORE_THAN = 2.0
FAIL_IF_LABEL_ACCURACY_DROPS_MORE_THAN = 5.0

old_name = sys.argv[1] if len(sys.argv) > 2 else "v1"
new_name = sys.argv[2] if len(sys.argv) > 2 else "v2"

with open("evals/test_cases.jsonl", encoding="utf-8") as f:
    cases = {c["id"]: c for c in (json.loads(l) for l in f if l.strip())}


def load(version):
    with open(f"results/{version}.jsonl", encoding="utf-8") as f:
        rows = {r["id"]: r for r in (json.loads(l) for l in f if l.strip())}
    with open(f"results/{version}_scores.json", encoding="utf-8") as f:
        scores = json.load(f)
    return rows, scores


def is_right(row, case, field):
    p = row["parsed"]
    return bool(p) and p[field] == case["expected_" + field]


def short(row):
    p = row["parsed"]
    return f"{p['sentiment']}/{p['urgency']}" if p else "INVALID"


old_rows, old = load(old_name)
new_rows, new = load(new_name)

print(f"=== Scores: {old_name} (old) vs {new_name} (new) ===")
metrics = [
    ("valid_format_pct", "Valid format"),
    ("sentiment_correct_pct", "Sentiment correct"),
    ("urgency_correct_pct", "Urgency correct"),
    ("avg_seconds", "Seconds per note"),
]
for key, label in metrics:
    diff = round(new[key] - old[key], 1)
    print(f"{label:20} old: {old[key]:>6}   new: {new[key]:>6}   change: {diff:+}")

print()
regressions, improvements = [], []
for cid, case in cases.items():
    if cid not in old_rows or cid not in new_rows:
        continue
    for field in ("sentiment", "urgency"):
        before = is_right(old_rows[cid], case, field)
        after = is_right(new_rows[cid], case, field)
        item = (cid, field, case, old_rows[cid], new_rows[cid])
        if before and not after:
            regressions.append(item)
        elif after and not before:
            improvements.append(item)


def show(title, items):
    print(f"=== {title}: {len(items)} ===")
    for cid, field, case, o, n in items:
        expected = f"{case['expected_sentiment']}/{case['expected_urgency']}"
        print(f"Note {cid} ({field}): {case['note'][:70]}")
        print(f"   expected: {expected}   old: {short(o)}   new: {short(n)}")
    print()


show("Got WORSE in new", regressions)
show("Got BETTER in new", improvements)

reasons = []
if old["valid_format_pct"] - new["valid_format_pct"] > FAIL_IF_FORMAT_DROPS_MORE_THAN:
    reasons.append("valid format dropped too much")
for key, label in (("sentiment_correct_pct", "sentiment"), ("urgency_correct_pct", "urgency")):
    if old[key] - new[key] > FAIL_IF_LABEL_ACCURACY_DROPS_MORE_THAN:
        reasons.append(f"{label} accuracy dropped too much")

print("=== GATE RESULT ===")
if reasons:
    print("FAIL: " + "; ".join(reasons))
else:
    print(f"PASS: {new_name} did not get worse beyond the allowed limits.")