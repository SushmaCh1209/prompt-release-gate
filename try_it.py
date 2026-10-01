from feature import load_prompt, process_note

prompt = load_prompt("prompts/v1.yaml")

notes = [
    "cust called angry!! app crashed 3 times today, wants refund asap",
    "thx for the quick help, all working now",
    "asked abt pricing for team plan, no rush, maybe next month",
]

for note in notes:
    print("NOTE:", note)
    print("RESULT:", process_note(note, prompt))
    print()