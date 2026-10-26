from pathlib import Path
import argparse, json, shutil
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "blind-judge"
EVALUATION = ROOT / "evaluation" if (ROOT / "evaluation").is_dir() else ROOT
parser = argparse.ArgumentParser()
parser.add_argument("--pair", choices=["R3"], required=True)
args = parser.parse_args()
PAIRS = {"R3": ["birch", "cedar"]}
if (OUT / args.pair).exists():
    raise SystemExit("Do not replace an existing blind pair.")
for label in PAIRS[args.pair]:
    assert (ROOT / "results" / (label + ".json")).is_file(), label
OUT.mkdir(exist_ok=True)
ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
if not (OUT / "original-cases").exists():
    shutil.copytree(EVALUATION / "cases", OUT / "original-cases", ignore=ignore)
shutil.copyfile(EVALUATION / "grading/rubric.md", OUT / "rubric.md")
shutil.copyfile(ROOT / "judge-instructions.txt", OUT / "instructions.txt")
index = json.loads((OUT / "index.json").read_text()) if (OUT / "index.json").exists() else {}
for pair, labels in [(args.pair, PAIRS[args.pair])]:
    for letter, label in zip(["A", "B"], labels):
        source = ROOT / "runs" / label
        target = OUT / pair / letter
        shutil.copytree(source / "work", target, ignore=ignore)
        for name in ["execution.md", "summary.json"]:
            if (source / name).is_file():
                shutil.copyfile(source / name, target / name)
        if (source / "probes").exists():
            shutil.copytree(source / "probes", target / "probes", ignore=ignore)
        shutil.copyfile(ROOT / "results" / (label + ".json"), target / "mechanical.json")
        # Neutralize folder labels in evidence copies, retaining all commands/outcomes.
        for file in target.rglob("*"):
            if not file.is_file():
                continue
            try:
                text = file.read_text()
            except UnicodeDecodeError:
                continue
            text = text.replace(str(source), "<run>" ).replace(str(EVALUATION / "grading"), "<independent-grader>")
            file.write_text(text)
        index[f"{pair}/{letter}"] = {"cases": "cases/", "mechanical": "mechanical.json", "notes": "Participant execution records are supplied evidence, not judge executions."}
(OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n")
print("Prepared blind judge inputs; no version map or skill instructions included.")
