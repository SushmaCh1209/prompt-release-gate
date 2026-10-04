import argparse
import json
import os
import time

from feature import load_prompt, call_model
from schema import NoteResult

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", required=True)
args = parser.parse_args()

prompt = load_prompt(args.prompt)
version = prompt["version"]

with open("evals/test_cases.jsonl", encoding="utf-8") as f:
    cases = [json.loads(line) for line in f if line.strip()]
by_id = {c["id"]: c for c in cases}

os.makedirs("results", exist_ok=True)
out_path = f"results/{version}.jsonl"

# Load answers saved by earlier runs, so nothing is called twice
done = {}
if os.path.exists(out_path):
    with open(out_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                done[r["id"]] = r

for case in cases:
    if case["id"] in done:
        continue
    start = time.time()
    try:
        raw = call_model(case["note"], prompt)
    except Exception as e:
        msg = str(e)
        print(f"Case {case['id']}: call failed: {msg[:120]}")
        if "429" in msg:
            print("Quota used up. Run again later to continue.")
            break
        continue
    seconds = round(time.time() - start, 2)
    try:
        parsed = NoteResult.model_validate_json(raw).model_dump()
    except Exception:
        parsed = None
    record = {"id": case["id"], "raw": raw, "parsed": parsed, "seconds": seconds}
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    done[case["id"]] = record
    print(f"Case {case['id']} done ({seconds}s)")

# Score everything saved so far
results = [r for r in done.values() if r["id"] in by_id]
n = len(results)
if n == 0:
    print("No results yet.")
else:
    valid = sum(1 for r in results if r["parsed"])
    sent = sum(1 for r in results if r["parsed"]
               and r["parsed"]["sentiment"] == by_id[r["id"]]["expected_sentiment"])
    urg = sum(1 for r in results if r["parsed"]
              and r["parsed"]["urgency"] == by_id[r["id"]]["expected_urgency"])
    avg = sum(r["seconds"] for r in results) / n
    scores = {
        "version": version,
        "cases_scored": n,
        "valid_format_pct": round(100 * valid / n, 1),
        "sentiment_correct_pct": round(100 * sent / n, 1),
        "urgency_correct_pct": round(100 * urg / n, 1),
        "avg_seconds": round(avg, 2),
    }
    with open(f"results/{version}_scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)
    print()
    print(f"{version}: scored {n} of {len(cases)} cases")
    print(f"  valid format:      {scores['valid_format_pct']}%")
    print(f"  sentiment correct: {scores['sentiment_correct_pct']}%")
    print(f"  urgency correct:   {scores['urgency_correct_pct']}%")
    print(f"  average time:      {scores['avg_seconds']}s per note")