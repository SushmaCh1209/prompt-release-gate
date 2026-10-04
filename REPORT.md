# Prompt Release Safety Gate: Report

## Goal
Changing an AI prompt can quietly make an AI feature worse. This project builds a test that compares a new prompt against the current one on a fixed, hand-labeled test set and prints PASS or FAIL.

## Setup
- **Task:** turn a messy customer support note into JSON with `summary`, `sentiment`, `next_action` and `urgency`.
- **Model:** llama3.2:3b running locally with Ollama, temperature 0. The answer shape is enforced with a Pydantic schema.
- **Test set:** 30 notes I wrote by hand, with expected sentiment and urgency. They include spelling mistakes, angry customers, vague notes, mixed feelings, mixed Telugu-English, and calm notes that are actually urgent.
- **Metrics:** valid format %, sentiment correct %, urgency correct %, seconds per note.
- **Gate rule:** FAIL if valid format drops by more than 2 points, or sentiment or urgency accuracy drops by more than 5 points. One test note is worth 3.3 points, so 5 points is about 2 notes.

## Results

| Prompt | Valid format | Sentiment correct | Urgency correct | Seconds per note |
|---|---|---|---|---|
| v1 (basic instructions) | 100% | 60.0% | 70.0% | 19.97 |
| v2 (labeling rules + 3 examples) | 100% | 93.3% | 93.3% | 15.90 |
| v3 (deliberately bad) | 100% | 83.3% | 83.3% | 17.21 |

## v1 to v2: PASS
v2 added explicit rules for each label and three short examples. The examples were written separately and were not copied from the test notes. v2 fixed 11 sentiment answers and 7 urgency answers. One answer got worse (note 9's sentiment), so the net gain was 10 sentiment answers and 7 urgency answers. The full comparison is in `results/compare_v1_v2.txt`.

## v2 to v3: FAIL
To test the gate, I wrote v3 on purpose with a harmful rule: use "low" urgency unless the note says "urgent", and "neutral" sentiment unless the customer uses very angry words. Six answers got worse and none improved. The gate printed FAIL for both sentiment and urgency. The full comparison is in `results/compare_v2_v3.txt`.

The small model did not follow v3 consistently. Notes 8 and 10 got `high` urgency even though v3 said to use `low`. The gate measures outcomes, so it caught the drop either way.

## Where v2 is still wrong
- **Notes 9 and 16** (calm notes that report a problem): I labeled them `neutral`, but the v2 rule says a described problem counts as `negative`. This is a conflict between my labels and my prompt, not only a model mistake.
- **Note 9 urgency and note 26 urgency:** the model underestimated how soon action was needed.

## Limitations
- Only 30 test notes, so a one-note difference may be luck.
- I wrote both the labels and the v2 rules, so v2 is partly tuned to my own judgment.
- One small model and one task. Results may differ on a larger model.
- Summary quality is not scored.
- Valid format is 100% for every prompt because the schema is enforced when the answer is generated.
- Timing was measured on a laptop CPU with other programs open, so small speed differences are noise.
- I changed the rules and the examples at the same time, so I can't tell which one caused the improvement.

## What I learned
I learned that clear labeling rules and a few examples can make a prompt much more accurate (sentiment from 60% to 93%). The safety gate successfully detected when the deliberately bad prompt caused sentiment and urgency accuracy to drop. I also learned that some errors come from conflicts between the test labels and the prompt rules, not just from the model. Finally, a larger and more diverse test set would make the results more reliable.