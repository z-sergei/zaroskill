# Working on Zaroskill

This repository is the editable source of four personal skills and two pinned Matt Pocock dependencies. Installed skill directories are deployment copies. Read `README.md` for the catalog and `docs/workflow.md` when choosing how to combine them.

- Keep personal skills self-contained and stack-independent. Project paths, build commands and company-specific workflow maps belong in the consuming project.
- Put conditional reasoning in a referenced file with a specific trigger. Preserve the requested task boundary and independent business expectations. Use `writing-for-agents` and `skill-creator` when available for substantial instruction changes.
- `vendor/mattpocock/` is an unchanged licensed snapshot. Record an intentional version update in `provenance.json`, including the source revision, hashes and license; make local experiments separately.
- For a behavioral change, use realistic tasks plus correct controls, preserve raw outputs and distinguish executed evidence from an unexecuted proposal. An independent fresh-context pass is appropriate for complex instruction changes. Blind the reviewer to version identity when comparing outputs. State the number of runs and limitations; wording preference alone is not a measured gain.
- Run `python3 -B scripts/check.py` and relevant installation tests after packaging changes. Use `evals/khorikov/README.md` for its separate fixture checks. Launch model-backed campaigns only within the task's authorized scope and budget; the local smoke checks do not start them.
- Keep generated campaigns and local scratch data in `.eval-runs/` or outside the repository. Keep small reviewed evidence under `evals/`. Exposed evaluation cases are development material; retain fresh cases for later comparison.

A change is ready when the affected package and necessary checks are valid, the behavioral evidence matches its claim, and the diff preserves unrelated skills and user files. Publishing a remote or changing a consuming application's code is a separate task.
