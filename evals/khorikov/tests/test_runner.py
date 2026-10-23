"""Behavioral checks for the evaluator; fixtures here are independent of its cases.

These checks run real unittest submissions in disposable directories. They never
invoke an AI agent or inspect the benchmark's hidden scenarios.
"""
import contextlib
import copy
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import textwrap
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch


EVALUATOR_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("khorikov_evaluator", EVALUATOR_ROOT / "runner.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


PRODUCTION = """def _double(value):
    return value * 2


def total(value):
    return _double(value)
"""
CONTRACT_TEST = """import unittest
from subject import total

class TotalTests(unittest.TestCase):
    def test_total_contains_two_equal_parts(self):
        self.assertEqual(6, total(3))
"""


class EvaluatorFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="evaluator-behavior-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.root = self.directory / "evaluator"
        self.root.mkdir()
        for name in ("runner.py", "test_host.py"):
            shutil.copy2(EVALUATOR_ROOT / name, self.root / name)
        self.skill = self.directory / "skill"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("---\nname: sample\ndescription: Test observable behavior.\n---\nAssert the public result.\n")
        configs = []
        for case_id, split in (("sample", "development"), ("sealed_sample", "holdout")):
            case = self.root / "cases" / case_id
            case.mkdir(parents=True)
            (case / "subject.py").write_text(PRODUCTION)
            (case / "task.md").write_text("Test that total(value) returns two equal parts.\n")
            (case / "reference_tests.py").write_text(CONTRACT_TEST)
            runner.write_json(case / "grader.json", {
                "mutants": [{"id": "extra-part", "invariant": "Exactly two equal parts are included",
                             "source": "subject.py", "before": "return value * 2", "after": "return value * 3"}],
                "refactors": [{"id": "inline-helper", "source": "subject.py", "before": PRODUCTION,
                               "after": "def total(value):\n    return value + value\n"}],
            })
            configs.append({"id": case_id, "split": split, "files": ["subject.py", "task.md"]})
        runner.write_json(self.root / "suite.json", {"cases": configs})
        root_patch = patch.object(runner, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.sequence = 0

    def submission(self, source=CONTRACT_TEST):
        self.sequence += 1
        workspace = runner.prepare("sample", self.skill, self.directory / f"submission-{self.sequence}")
        (workspace / "tests" / "test_subject.py").write_text(textwrap.dedent(source))
        return workspace

    def grade(self, workspace, **kwargs):
        self.sequence += 1
        return runner.grade("sample", workspace, self.directory / f"grade-{self.sequence}", **kwargs)

    def run_submission(self, source, operation=None, timeout=5):
        workspace = self.submission(source)
        self.sequence += 1
        return runner.run_tests("sample", workspace / "tests", self.directory / f"run-{self.sequence}",
                                operation=operation, timeout=timeout)


class SubmissionGradingTests(EvaluatorFixture):
    def test_observable_assertion_kills_a_regression_and_survives_helper_inlining(self):
        grade = self.grade(self.submission())

        self.assertTrue(grade["eligible"])
        self.assertEqual((1, 1, 1), (grade["tests"], grade["killed"], grade["total_mutants"]))
        self.assertTrue(grade["refactors"][0]["passed"])
        mutant = grade["mutants"][0]["result"]
        self.assertTrue(mutant["failures"])
        self.assertFalse(mutant["errors"])

    def test_variant_directory_names_cannot_be_used_as_a_mutation_oracle(self):
        # This submission deliberately asserts only metadata. It must earn no kills.
        source = """from pathlib import Path
import sys
import unittest

class MetadataOnlyTests(unittest.TestCase):
    def test_execution_metadata_does_not_identify_a_mutant(self):
        visible_paths = [str(Path.cwd()), __file__, *sys.argv]
        self.assertFalse(any('mutant-' in path for path in visible_paths))
"""
        grade = self.grade(self.submission(source))

        self.assertTrue(grade["eligible"])
        self.assertEqual(0, grade["killed"])
        self.assertFalse(grade["mutants"][0]["killed"])

    def test_test_filename_without_discovered_tests_is_ineligible(self):
        grade = self.grade(self.submission("def helper():\n    return True\n"))

        self.assertFalse(grade["eligible"])
        self.assertTrue(all(run["found"] == 0 for run in grade["baseline"]))
        self.assertNotIn("mutants", grade)

    def test_skipped_baseline_is_ineligible_even_when_its_other_assertion_passes(self):
        source = CONTRACT_TEST + "\n    @unittest.skip('not implemented')\n    def test_missing_contract(self):\n        pass\n"
        grade = self.grade(self.submission(source))

        self.assertFalse(grade["eligible"])
        self.assertTrue(grade["baseline"][0]["skipped"])
        self.assertNotIn("mutants", grade)

    def test_expected_failure_does_not_make_a_baseline_eligible(self):
        source = CONTRACT_TEST + "\n    @unittest.expectedFailure\n    def test_known_gap(self):\n        self.assertEqual(0, 1)\n"
        grade = self.grade(self.submission(source))

        self.assertFalse(grade["eligible"])
        self.assertEqual(1, grade["baseline"][0]["expected_failures"])

    def test_broken_import_or_syntax_cannot_earn_mutation_credit(self):
        for source in ("import dependency_that_does_not_exist\n", "def invalid(:\n"):
            with self.subTest(source=source):
                result = self.run_submission(source)
                self.assertFalse(runner.healthy(result))
                self.assertFalse(runner.killed(result, expected_count=1))
                self.assertTrue(result.get("errors") or result.get("host_error"))

    def test_production_runtime_error_is_not_a_detected_behavior_regression(self):
        operation = {"id": "broken-import", "source": "subject.py", "before": "return value * 2",
                     "after": "return dependency_that_does_not_exist"}
        result = self.run_submission(CONTRACT_TEST, operation)

        self.assertFalse(runner.killed(result, expected_count=1))
        self.assertTrue(result["errors"])
        self.assertFalse(result["failures"])

    def test_assertion_detected_regression_still_counts_when_another_test_also_errors(self):
        source = CONTRACT_TEST + "\n    def test_zero_parts_remain_zero(self):\n        self.assertEqual(0, total(0))\n"
        operation = {"id": "fault-with-domain-error", "source": "subject.py", "before": "return value * 2",
                     "after": "return value * 3 if value else 1 / 0"}

        result = self.run_submission(source, operation)

        self.assertEqual((2, 2), (result["found"], result["run"]))
        self.assertEqual(1, len(result["failures"]))
        self.assertEqual(1, len(result["errors"]))
        self.assertTrue(runner.killed(result, expected_count=2))

    def test_timeout_is_not_a_detected_behavior_regression(self):
        source = """import time
import unittest

class SlowTests(unittest.TestCase):
    def test_never_finishes_within_the_budget(self):
        time.sleep(30)
"""
        result = self.run_submission(source, timeout=0.1)

        self.assertTrue(result["process"]["timed_out"])
        self.assertFalse(runner.healthy(result))
        self.assertFalse(runner.killed(result, expected_count=1))

    def test_failure_of_a_behavior_preserving_refactor_rejects_all_mutation_credit(self):
        source = CONTRACT_TEST + """
    def test_internal_helper_still_exists(self):
        import subject
        self.assertTrue(hasattr(subject, '_double'))
"""
        grade = self.grade(self.submission(source))

        self.assertEqual(1, grade["killed"])
        self.assertFalse(grade["eligible"])
        self.assertFalse(grade["refactors"][0]["passed"])

    def test_production_tampering_is_rejected_even_if_the_submission_manifest_is_rewritten(self):
        workspace = self.submission()
        (workspace / "subject.py").write_text("def total(value):\n    return 6\n")
        manifest = runner.read_json(workspace / "submission.json")
        manifest["protected"]["subject.py"] = runner.digest(workspace / "subject.py")
        runner.write_json(workspace / "submission.json", manifest)

        grade = self.grade(workspace)

        self.assertFalse(grade["eligible"])
        self.assertNotIn("baseline", grade)

    def test_prepared_workspace_has_public_inputs_and_skill_but_no_evaluator_material(self):
        workspace = runner.prepare("sample", self.skill, self.directory / "public-workspace")

        self.assertEqual(PRODUCTION, (workspace / "subject.py").read_text())
        self.assertEqual((self.skill / "SKILL.md").read_bytes(), (workspace / "skill" / "SKILL.md").read_bytes())
        for hidden in ("grader.json", "reference_tests.py", "test_host.py", "suite.json", "runner.py"):
            with self.subTest(hidden=hidden):
                self.assertEqual([], list(workspace.rglob(hidden)))
        self.assertTrue((workspace / "tests").is_dir())


    def test_agent_cannot_replace_the_supplied_skill_and_still_get_an_eligible_evaluation(self):
        def changed_skill(workspace, prompt, evidence, budget, timeout=600):
            budget.consume()
            (Path(workspace) / "tests" / "test_subject.py").write_text(CONTRACT_TEST)
            (Path(workspace) / "skill" / "SKILL.md").write_text("Replacement instructions")

        with patch.object(runner, "agent", side_effect=changed_skill), contextlib.redirect_stdout(io.StringIO()):
            result = runner.evaluate(self.skill, ["sample"], self.directory / "evaluation", 1,
                                     runner.AgentBudget(1), 5)

        self.assertFalse(result["eligible"])
        self.assertFalse(result["records"][0]["grade"]["eligible"])


class ComparisonTests(unittest.TestCase):
    @staticmethod
    def healthy_run(count=1):
        return {"found": count, "run": count, "failures": [], "errors": [], "skipped": [],
                "expected_failures": 0, "unexpected_successes": 0,
                "process": {"exit_code": 0, "timed_out": False}}

    @classmethod
    def failed_run(cls, count=1):
        result = cls.healthy_run(count)
        result["failures"] = [{"test": "observable_contract", "trace": "AssertionError"}]
        result["process"]["exit_code"] = 1
        return result

    @classmethod
    def evaluation(cls, outcomes, repeats=2):
        """outcomes maps case IDs to one mutant-result dictionary per repeat."""
        return {"case_ids": list(outcomes), "repeats": repeats, "eligible": True,
                "variants": {case: {"mutants": list(samples[0]), "refactors": ["behavior-preserving"]}
                             for case, samples in outcomes.items()},
                "records": [{"case": case, "repeat": index,
                             "grade": {"eligible": True, "baseline": [cls.healthy_run(), cls.healthy_run()],
                                       "mutants": [{"id": mutant, "invariant": "Observable result: " + mutant,
                                                    "killed": killed, "result": cls.failed_run() if killed else cls.healthy_run()}
                                                   for mutant, killed in values.items()],
                                       "refactors": [{"id": "behavior-preserving", "passed": True, "result": cls.healthy_run()}]}}
                            for case, samples in outcomes.items() for index, values in enumerate(samples)]}

    @classmethod
    def fail_refactor(cls, evaluation):
        evaluation["eligible"] = False
        grade = evaluation["records"][0]["grade"]
        grade["eligible"] = False
        grade["refactors"][0].update(passed=False, result=cls.failed_run())

    def setUp(self):
        self.old = self.evaluation({"sample": [{"first": True, "second": False},
                                               {"first": True, "second": False}]})
        self.better = self.evaluation({"sample": [{"first": True, "second": True},
                                                  {"first": True, "second": True}]})

    def test_complete_repeated_evidence_with_an_improvement_is_accepted(self):
        self.assertTrue(runner.improvement(self.old, self.better))

    def test_aggregate_gain_cannot_hide_a_regression_in_one_invariant(self):
        old = self.evaluation({"sample": [{"first": True, "second": False, "third": False}] * 2})
        new = self.evaluation({"sample": [{"first": False, "second": True, "third": True}] * 2})

        self.assertFalse(runner.improvement(old, new))

    def test_equivalent_complete_results_are_accepted_only_for_a_non_strict_gate(self):
        self.assertFalse(runner.improvement(self.old, copy.deepcopy(self.old)))
        self.assertTrue(runner.improvement(self.old, copy.deepcopy(self.old), strict=False))

    def test_unequal_repeat_budgets_are_not_comparable(self):
        new = self.evaluation({"sample": [{"first": True, "second": True}]}, repeats=1)
        self.assertFalse(runner.improvement(self.old, new))

    def test_missing_repeat_is_not_comparable(self):
        new = copy.deepcopy(self.better)
        new["records"].pop()
        self.assertFalse(runner.improvement(self.old, new))

    def test_duplicate_repeat_is_not_independent_evidence(self):
        new = copy.deepcopy(self.better)
        new["records"][1]["repeat"] = 0
        self.assertFalse(runner.improvement(self.old, new))

    def test_missing_mutant_in_one_repeat_is_not_comparable(self):
        new = copy.deepcopy(self.better)
        new["records"][0]["grade"]["mutants"].pop()
        self.assertFalse(runner.improvement(self.old, new))

    def test_duplicate_mutant_cannot_reweight_one_repeat(self):
        new = copy.deepcopy(self.better)
        new["records"][0]["grade"]["mutants"].append(copy.deepcopy(new["records"][0]["grade"]["mutants"][0]))
        self.assertFalse(runner.improvement(self.old, new))

    def test_expected_case_missing_from_both_results_is_still_incomplete(self):
        old, new = copy.deepcopy(self.old), copy.deepcopy(self.better)
        old["case_ids"].append("unrun-case")
        new["case_ids"].append("unrun-case")
        self.assertFalse(runner.improvement(old, new))

    def test_empty_evaluations_cannot_pass_the_holdout_gate(self):
        empty = self.evaluation({}, repeats=2)
        self.assertFalse(runner.improvement(empty, empty, strict=False))

    def test_record_ineligibility_cannot_be_overridden_by_the_summary_flag(self):
        new = copy.deepcopy(self.better)
        new["records"][0]["grade"]["eligible"] = False
        self.assertFalse(runner.improvement(self.old, new))


class SurvivalComparisonTests(unittest.TestCase):
    @staticmethod
    def make_error(evaluation, mutant_id):
        for record in evaluation["records"]:
            for mutant in record["grade"]["mutants"]:
                if mutant["id"] == mutant_id:
                    run = mutant["result"]
                    run["failures"] = []
                    run["errors"] = [{"test": "observable_contract", "trace": "DomainError"}]
                    run["process"]["exit_code"] = 1
                    mutant["killed"] = False

    def test_error_to_assertion_accounting_gain_is_not_a_new_detection(self):
        old = ComparisonTests.evaluation({"sample": [{"fault": False}]}, repeats=1)
        self.make_error(old, "fault")
        new = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)

        self.assertEqual({"sample/fault": 0.0}, runner.comparison_evidence(old)["healthy_survival_rates"])
        self.assertEqual({"sample/fault": 0.0}, runner.comparison_evidence(new)["healthy_survival_rates"])
        self.assertFalse(runner.improvement(old, new))
        self.assertTrue(runner.improvement(old, new, strict=False))

    def test_error_to_healthy_survivor_is_a_regression_even_with_unchanged_assertion_credit(self):
        old = ComparisonTests.evaluation({"sample": [{"fault": False}]}, repeats=1)
        self.make_error(old, "fault")
        new = ComparisonTests.evaluation({"sample": [{"fault": False}]}, repeats=1)

        self.assertEqual(runner.rates(old), runner.rates(new))
        self.assertEqual({"sample/fault": 1.0}, runner.comparison_evidence(new)["healthy_survival_rates"])
        self.assertFalse(runner.improvement(old, new, strict=False))

    def test_credited_gain_and_reduced_survival_must_belong_to_the_same_invariant(self):
        old = ComparisonTests.evaluation({"sample": [{"already_detected": False, "survivor": False}]}, repeats=1)
        self.make_error(old, "already_detected")
        new = ComparisonTests.evaluation({"sample": [{"already_detected": True, "survivor": False}]}, repeats=1)
        self.make_error(new, "survivor")

        self.assertFalse(runner.improvement(old, new))

    def test_refactor_repair_cannot_hide_a_new_healthy_survivor(self):
        old = ComparisonTests.evaluation({"sample": [{"fault": False}]}, repeats=1)
        self.make_error(old, "fault")
        ComparisonTests.fail_refactor(old)
        new = ComparisonTests.evaluation({"sample": [{"fault": False}]}, repeats=1)

        self.assertFalse(runner.improvement(old, new))

    def test_healthy_to_assertion_improvement_still_advances(self):
        old = ComparisonTests.evaluation({"sample": [{"fault": False}]}, repeats=1)
        new = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)

        self.assertEqual({"sample/fault": 1.0}, runner.comparison_evidence(old)["healthy_survival_rates"])
        self.assertEqual({"sample/fault": 0.0}, runner.comparison_evidence(new)["healthy_survival_rates"])
        self.assertTrue(runner.improvement(old, new))


class EligibilityRepairTests(EvaluatorFixture):
    def wrap_grade(self, grade):
        rules = runner.read_json(self.root / "cases" / "sample" / "grader.json")
        return {"case_ids": ["sample"], "repeats": 1, "eligible": grade["eligible"],
                "variants": {"sample": {kind: [item["id"] for item in rules[kind]] for kind in ("mutants", "refactors")}},
                "records": [{"case": "sample", "repeat": 0, "grade": grade}]}

    def test_real_refactor_coupling_repair_can_advance_without_changing_fault_detection(self):
        coupled = CONTRACT_TEST + "\n    def test_private_helper_exists(self):\n        import subject\n        self.assertTrue(hasattr(subject, '_double'))\n"
        old = self.wrap_grade(self.grade(self.submission(coupled)))
        new = self.wrap_grade(self.grade(self.submission()))

        self.assertFalse(old["eligible"])
        self.assertTrue(new["eligible"])
        self.assertEqual(old["records"][0]["grade"]["killed"], new["records"][0]["grade"]["killed"])
        self.assertTrue(runner.improvement(old, new))
        self.assertIsNone(runner.rates(old))  # The ordinary public rate gate stays conservative.

    def test_baseline_failure_with_absent_measurements_cannot_be_zero_filled(self):
        old = self.wrap_grade(self.grade(self.submission(CONTRACT_TEST.replace('self.assertEqual(6', 'self.assertEqual(7'))))
        new = self.wrap_grade(self.grade(self.submission()))

        self.assertFalse(runner.improvement(old, new))

    def test_missing_baseline_does_not_authorize_a_refactor_repair(self):
        old = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)
        ComparisonTests.fail_refactor(old)
        new = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)
        old["records"][0]["grade"].pop("baseline")

        self.assertFalse(runner.improvement(old, new))

    def test_repair_with_fault_detection_regression_is_rejected(self):
        old = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)
        ComparisonTests.fail_refactor(old)
        new = ComparisonTests.evaluation({"sample": [{"fault": False}]}, repeats=1)

        self.assertFalse(runner.improvement(old, new))

    def test_incomplete_refactor_or_mutant_measurements_cannot_establish_repair(self):
        for missing_kind in ("mutants", "refactors"):
            with self.subTest(missing_kind=missing_kind):
                old = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)
                ComparisonTests.fail_refactor(old)
                new = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)
                old["records"][0]["grade"][missing_kind].clear()
                self.assertFalse(runner.improvement(old, new))

    def test_mutant_omitted_from_every_record_cannot_shrink_the_declared_universe(self):
        old = ComparisonTests.evaluation({"sample": [{"first": False, "second": False}]}, repeats=1)
        new = ComparisonTests.evaluation({"sample": [{"first": True, "second": False}]}, repeats=1)
        for evaluation in (old, new):
            evaluation["records"][0]["grade"]["mutants"].pop()
        self.assertFalse(runner.improvement(old, new))

    def test_missing_measured_mutant_execution_cannot_establish_repair(self):
        old = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)
        ComparisonTests.fail_refactor(old)
        new = ComparisonTests.evaluation({"sample": [{"fault": True}]}, repeats=1)
        old["records"][0]["grade"]["mutants"][0].pop("result")
        self.assertFalse(runner.improvement(old, new))


class ReviewGateTests(EvaluatorFixture):
    def review(self, response, edit=None):
        self.sequence += 1
        output = self.directory / f"review-{self.sequence}"
        submission = self.submission()
        evaluation = {"records": [{"case": "sample", "repeat": 0, "submission": str(submission)}]}

        def reviewer(workspace, prompt, evidence, budget, timeout):
            budget.consume()
            for label in ("incumbent", "candidate"):
                self.assertTrue((Path(workspace) / "submissions" / label / "sample-0" / "tests" / "test_subject.py").is_file())
            if edit:
                edit(Path(workspace))
            runner.write_json(Path(workspace) / "review.json", response)

        with patch.object(runner, "agent", side_effect=reviewer):
            return runner.review_candidate(self.skill, self.skill, evaluation, evaluation, output, runner.AgentBudget(1), 1)

    def test_explicit_complete_approval_with_unchanged_inputs_passes(self):
        result = self.review({"approve": True, "evidence": ["Both suites assert the independent public result."], "concerns": []})
        self.assertTrue(result["approved"])

    def test_material_concern_or_explicit_rejection_prevents_approval(self):
        for approve, concerns in ((True, ["Private helper coupling remains."]), (False, [])):
            with self.subTest(approve=approve, concerns=concerns):
                result = self.review({"approve": approve, "evidence": ["Inspected tests."], "concerns": concerns})
                self.assertFalse(result["approved"])

    def test_malformed_review_is_rejected_instead_of_treating_missing_fields_as_clear(self):
        invalid = [
            {"approve": True, "evidence": ["Observed behavior."]},
            {"approve": True, "evidence": ["Observed behavior."], "concerns": [], "approved": True},
            {"approve": 1, "evidence": ["Observed behavior."], "concerns": []},
            {"approve": True, "evidence": [17], "concerns": []},
            {"approve": True, "evidence": ["Observed behavior."], "concerns": [False]},
            {"approve": True, "evidence": "Observed behavior.", "concerns": []},
            {"approve": True, "evidence": ["Observed behavior."], "concerns": None},
            {"approve": True, "evidence": [], "concerns": []},
            {"approve": True, "evidence": ["   "], "concerns": []},
        ]
        for response in invalid:
            with self.subTest(response=response), self.assertRaises(ValueError):
                self.review(response)

    def test_review_of_edited_added_or_removed_inputs_cannot_authorize_promotion(self):
        edits = [
            lambda workspace: (workspace / "candidate-skill" / "SKILL.md").write_text("Different candidate."),
            lambda workspace: (workspace / "submissions" / "candidate" / "sample-0" / "tests" / "test_subject.py").unlink(),
            lambda workspace: (workspace / "submissions" / "incumbent" / "sample-0" / "tests" / "test_added.py").write_text("New evidence"),
        ]
        for index, edit in enumerate(edits):
            with self.subTest(edit=index), self.assertRaisesRegex(ValueError, "changed supplied artifacts"):
                self.review({"approve": True, "evidence": ["Observed behavior."], "concerns": []}, edit)

    def test_symlink_replacement_of_a_supplied_tree_is_rejected_even_with_equal_bytes(self):
        def replace(workspace):
            target = workspace / "candidate-skill"
            shutil.rmtree(target)
            target.symlink_to(self.skill, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.review({"approve": True, "evidence": ["Observed behavior."], "concerns": []}, replace)


class FeedbackAccountingTests(unittest.TestCase):
    def test_healthy_survivor_is_missed_but_runtime_error_is_only_uncredited(self):
        evaluation = ComparisonTests.evaluation({"sample": [{"survivor": False, "exception": False, "assertion": True}]}, repeats=1)
        error_run = evaluation["records"][0]["grade"]["mutants"][1]["result"]
        error_run["errors"] = [{"test": "domain_exception", "trace": "InsufficientStock"}]
        error_run["process"]["exit_code"] = 1

        feedback = runner.feedback(evaluation)["cases"][0]
        self.assertEqual(["Observable result: survivor"], feedback["missed_contracts"])
        self.assertEqual([{"invariant": "Observable result: exception", "reason": "test errors"}], feedback["uncredited_outcomes"])

    def test_timeout_is_not_described_as_an_undetected_contract(self):
        evaluation = ComparisonTests.evaluation({"sample": [{"hung": False}]}, repeats=1)
        run = evaluation["records"][0]["grade"]["mutants"][0]["result"]
        run["process"].update(exit_code=-15, timed_out=True)

        feedback = runner.feedback(evaluation)["cases"][0]
        self.assertEqual([], feedback["missed_contracts"])
        self.assertEqual("execution timed out", feedback["uncredited_outcomes"][0]["reason"])


class ParallelEvaluationTests(EvaluatorFixture):
    def test_two_workers_overlap_and_preserve_canonical_evidence_order(self):
        cases = ["sealed_sample", "sample"]  # Deliberately differs from alphabetical order.
        rendezvous = threading.Barrier(2)
        published = {case: threading.Event() for case in cases}
        lock = threading.Lock()
        active = 0
        maximum_active = 0
        original_grade, original_write = runner.grade, runner.write_json
        first_published = {}

        def controlled_agent(workspace, prompt, evidence, budget, timeout=600):
            nonlocal active, maximum_active
            budget.consume()
            with lock:
                active += 1
                maximum_active = max(maximum_active, active)
            try:
                rendezvous.wait(timeout=5)  # A serial evaluator cannot satisfy this rendezvous.
                (Path(workspace) / "tests" / "test_subject.py").write_text(CONTRACT_TEST)
            finally:
                with lock:
                    active -= 1

        def out_of_order_grade(case_id, submission, output, timeout=20):
            result = original_grade(case_id, submission, output, timeout)
            repeat = int(Path(submission).parent.name.rsplit("-", 1)[1])
            if repeat == 0 and not published[case_id].wait(timeout=5):
                raise AssertionError("The second repeat was not independently published")
            return result

        def observe_publication(path, value):
            original_write(path, value)
            if Path(path).name == "partial.json":
                for record in value["records"]:
                    case_id = record["case"]
                    first_published.setdefault(case_id, record["repeat"])
                    if record["repeat"] == 1:
                        published[case_id].set()

        output = self.directory / "parallel-evaluation"
        budget = runner.AgentBudget(4)
        with patch.object(runner, "agent", side_effect=controlled_agent), \
                patch.object(runner, "grade", side_effect=out_of_order_grade), \
                patch.object(runner, "write_json", side_effect=observe_publication), \
                contextlib.redirect_stdout(io.StringIO()):
            result = runner.evaluate(self.skill, cases, output, 2, budget, 5, workers=2)

        self.assertEqual(2, maximum_active)
        self.assertEqual(4, budget.used)
        self.assertEqual({case: 1 for case in cases}, first_published)
        expected = [(case, repeat) for case in cases for repeat in range(2)]
        self.assertEqual(expected, [(record["case"], record["repeat"]) for record in result["records"]])
        self.assertEqual(result, runner.read_json(output / "evaluation.json"))
        self.assertEqual(result["records"], runner.read_json(output / "partial.json")["records"])
        self.assertEqual(cases, result["case_ids"])
        self.assertEqual({case: {"mutants": ["extra-part"], "refactors": ["inline-helper"]} for case in cases}, result["variants"])
        self.assertEqual({case + "/extra-part": 1.0 for case in cases}, runner.rates(result))


class MaintenanceEvaluationTests(EvaluatorFixture):
    def starting_tests(self, repeats=1, source=CONTRACT_TEST):
        self.sequence += 1
        root = self.directory / f"starting-{self.sequence}"
        for repeat in range(repeats):
            tests = root / f"sample-{repeat}" / "tests"
            tests.mkdir(parents=True)
            (tests / "test_subject.py").write_text(source)
        return root

    def evaluate(self, starting, agent, repeats=1, output=None):
        self.sequence += 1
        output = output or self.directory / f"maintenance-{self.sequence}"
        with patch.object(runner, "agent", side_effect=agent), contextlib.redirect_stdout(io.StringIO()):
            return runner.evaluate(self.skill, ["sample"], output, repeats,
                                   runner.AgentBudget(repeats), 5, starting_tests=starting)

    @staticmethod
    def maintain(workspace, prompt, evidence, budget, timeout=600):
        budget.consume()
        (Path(workspace) / "tests" / "test_subject.py").write_text(CONTRACT_TEST)

    def test_existing_tests_can_be_repaired_with_exact_starting_provenance(self):
        coupled = CONTRACT_TEST + "\n    def test_private_helper_exists(self):\n        import subject\n        self.assertTrue(hasattr(subject, '_double'))\n"
        starting = self.starting_tests(source=coupled)
        source = starting / "sample-0" / "tests"
        (source / "__pycache__").mkdir()
        (source / "__pycache__" / "initial.bin").write_bytes(b"Every supplied file is captured.")
        initial = runner.tree_hashes(source, include_cache=True)
        output = self.directory / "repair"

        def repair(workspace, prompt, evidence, budget, timeout=600):
            budget.consume()
            self.assertEqual(coupled, (Path(workspace) / "tests" / "test_subject.py").read_text())
            for instruction in ("supplied tests are editable", "retained", "replaced", "justifiably removed"):
                self.assertIn(instruction, prompt)
            (Path(workspace) / "tests" / "test_subject.py").write_text(CONTRACT_TEST)
            (Path(workspace) / "report.md").write_text(
                "Retained: public total scenario. Justifiably removed: helper existence is not a contract.\n")

        result = self.evaluate(starting, repair, output=output)

        self.assertTrue(result["eligible"])
        record = result["records"][0]
        self.assertEqual((1, 1), (record["grade"]["tests"], record["grade"]["killed"]))
        self.assertTrue(record["grade"]["refactors"][0]["passed"])
        provenance = record["starting_tests"]
        self.assertEqual(initial, provenance["initial_test_hashes"])
        self.assertEqual(str(source), provenance["source"])
        self.assertEqual(str(output / "starting-tests" / "sample-0" / "tests"), provenance["snapshot"])
        self.assertIn("__pycache__/initial.bin", provenance["initial_test_hashes"])
        self.assertEqual(initial, runner.tree_hashes(provenance["snapshot"], include_cache=True))
        self.assertEqual(initial, runner.tree_hashes(source, include_cache=True))
        self.assertNotEqual(initial, record["grade"]["test_hashes"])
        self.assertEqual(provenance, result["starting_tests"]["inputs"]["sample-0"])
        self.assertEqual(result["starting_tests"], runner.read_json(output / "starting-tests" / "provenance.json"))
        self.assertEqual(result, runner.read_json(output / "evaluation.json"))

    def test_two_arms_and_repeats_use_independent_copies_of_the_same_inputs(self):
        starting = self.starting_tests(repeats=2)
        initial = runner.tree_hashes(starting)
        workspaces = []
        rendezvous = threading.Barrier(2)

        def edit(workspace, prompt, evidence, budget, timeout=600):
            budget.consume()
            workspace = Path(workspace)
            label = workspace.parent.name
            editable = workspace / "tests" / "test_subject.py"
            snapshot = workspace.parent.parent / "starting-tests" / label / "tests" / "test_subject.py"
            source = starting / label / "tests" / "test_subject.py"
            self.assertEqual(CONTRACT_TEST, editable.read_text())
            self.assertFalse(editable.samefile(source))
            self.assertFalse(editable.samefile(snapshot))
            self.assertFalse(snapshot.samefile(source))
            rendezvous.wait(timeout=5)
            editable.write_text(CONTRACT_TEST + "\n# Maintained in " + str(workspace) + "\n")
            workspaces.append(workspace)

        old = self.evaluate(starting, edit, repeats=2)
        new = self.evaluate(starting, edit, repeats=2)

        self.assertEqual(4, len(set(workspaces)))
        self.assertEqual(initial, runner.tree_hashes(starting))
        self.assertTrue(runner.improvement(old, new, strict=False))
        self.assertEqual([record["starting_tests"]["initial_test_hashes"] for record in old["records"]],
                         [record["starting_tests"]["initial_test_hashes"] for record in new["records"]])
        self.assertEqual(4, len({record["starting_tests"]["snapshot"]
                                 for result in (old, new) for record in result["records"]}))

    def test_missing_later_input_is_rejected_before_any_agent_starts(self):
        starting = self.starting_tests()
        budget = runner.AgentBudget(2)
        with patch.object(runner, "agent") as agent, self.assertRaisesRegex(ValueError, "real directories"):
            runner.evaluate(self.skill, ["sample"], self.directory / "missing-input", 2, budget, 5,
                            starting_tests=starting)
        agent.assert_not_called()
        self.assertEqual(0, budget.used)

    def test_empty_or_non_test_input_is_rejected_before_any_agent_starts(self):
        for filename, contents in (("test_subject.py", ""), ("helper.py", CONTRACT_TEST)):
            with self.subTest(filename=filename):
                starting = self.starting_tests(source="")
                tests = starting / "sample-0" / "tests"
                (tests / "test_subject.py").unlink()
                (tests / filename).write_text(contents)
                with patch.object(runner, "agent") as agent, self.assertRaisesRegex(ValueError, "nonempty test_"):
                    runner.evaluate(self.skill, ["sample"], self.directory / filename, 1,
                                    runner.AgentBudget(1), 5, starting_tests=starting)
                agent.assert_not_called()

    def test_symlink_inputs_are_rejected_before_any_agent_starts(self):
        for target in ("root", "case", "tests", "file", "nested", "dangling"):
            with self.subTest(target=target):
                starting = self.starting_tests()
                tests = starting / "sample-0" / "tests"
                if target in ("nested", "dangling"):
                    (tests / target).symlink_to(self.directory / "absent" if target == "dangling" else self.skill,
                                               target_is_directory=True)
                else:
                    path = {"root": starting, "case": tests.parent, "tests": tests,
                            "file": tests / "test_subject.py"}[target]
                    saved = self.directory / ("saved-" + target)
                    path.rename(saved)
                    path.symlink_to(saved, target_is_directory=target != "file")
                with patch.object(runner, "agent") as agent, self.assertRaisesRegex(ValueError, "[Ss]ymlink"):
                    runner.evaluate(self.skill, ["sample"], self.directory / ("linked-" + target), 1,
                                    runner.AgentBudget(1), 5, starting_tests=starting)
                agent.assert_not_called()

    def test_source_or_snapshot_tampering_fails_closed(self):
        for target in ("source", "snapshot", "manifest", "snapshot-symlink", "snapshot-cache"):
            with self.subTest(target=target):
                starting = self.starting_tests()
                output = self.directory / ("tampered-" + target)
                cache = starting / "sample-0" / "tests" / "__pycache__"
                cache.mkdir()
                (cache / "initial.bin").write_bytes(b"Captured initial bytes")

                def tamper(workspace, prompt, evidence, budget, timeout=600):
                    self.maintain(workspace, prompt, evidence, budget, timeout)
                    snapshot = output / "starting-tests" / "sample-0" / "tests"
                    if target == "manifest":
                        runner.write_json(output / "starting-tests" / "provenance.json", {"inputs": {}})
                    elif target == "snapshot-symlink":
                        shutil.rmtree(snapshot)
                        snapshot.symlink_to(starting / "sample-0" / "tests", target_is_directory=True)
                    elif target == "snapshot-cache":
                        (snapshot / "__pycache__" / "initial.bin").write_bytes(b"Changed bytes")
                    else:
                        tests = starting / "sample-0" / "tests" if target == "source" else snapshot
                        (tests / "test_subject.py").write_text(CONTRACT_TEST + "\n# Tampered\n")

                with self.assertRaises(ValueError):
                    self.evaluate(starting, tamper, output=output)
                self.assertFalse((output / "evaluation.json").exists())

    def test_initial_hash_mismatch_in_either_copy_prevents_agent_calls(self):
        original_copy = runner.shutil.copytree
        for target in ("source", "snapshot", "editable"):
            with self.subTest(target=target):
                starting = self.starting_tests()
                output = self.directory / ("mismatched-" + target)
                snapshot = output / "starting-tests" / "sample-0" / "tests"
                editable = output / "sample-0" / "submission" / "tests"

                def broken_copy(source, destination, *args, **kwargs):
                    result = original_copy(source, destination, *args, **kwargs)
                    destination = Path(destination)
                    if destination.resolve() == (editable if target == "editable" else snapshot).resolve():
                        changed = Path(source) if target == "source" else destination
                        (changed / "test_subject.py").write_text(CONTRACT_TEST + "\n# Changed during copy\n")
                    return result

                with patch.object(runner.shutil, "copytree", side_effect=broken_copy), \
                        patch.object(runner, "agent") as agent, self.assertRaisesRegex(ValueError, "initial"):
                    runner.evaluate(self.skill, ["sample"], output, 1, runner.AgentBudget(1), 5,
                                    starting_tests=starting)
                agent.assert_not_called()
                self.assertFalse((output / "evaluation.json").exists())

    def test_tampering_after_grading_is_detected_before_final_publication(self):
        starting = self.starting_tests()
        output = self.directory / "late-tamper"
        original_grade = runner.grade

        def grade_then_tamper(*args, **kwargs):
            result = original_grade(*args, **kwargs)
            (starting / "sample-0" / "tests" / "test_subject.py").write_text("# Changed after grading\n")
            return result

        with patch.object(runner, "grade", side_effect=grade_then_tamper), self.assertRaisesRegex(ValueError, "source changed"):
            self.evaluate(starting, self.maintain, output=output)
        self.assertFalse((output / "evaluation.json").exists())

    def test_maintenance_keeps_source_task_and_skill_protected(self):
        for name in ("subject.py", "task.md", "skill/SKILL.md"):
            with self.subTest(name=name):
                starting = self.starting_tests()

                def tamper(workspace, prompt, evidence, budget, timeout=600):
                    self.maintain(workspace, prompt, evidence, budget, timeout)
                    path = Path(workspace) / name
                    path.write_text(path.read_text() + "\n# Changed protected input\n")

                result = self.evaluate(starting, tamper)
                self.assertFalse(result["eligible"])
                self.assertFalse(result["records"][0]["grade"]["eligible"])

    def test_greenfield_evaluation_keeps_original_prompt_and_empty_test_directory(self):
        def generate(workspace, prompt, evidence, budget, timeout=600):
            self.assertEqual([], list((Path(workspace) / "tests").iterdir()))
            self.assertEqual(runner.generation_prompt(), prompt)
            self.assertIn("Preserve all supplied files", prompt)
            self.maintain(workspace, prompt, evidence, budget, timeout)

        result = self.evaluate(None, generate)

        self.assertTrue(result["eligible"])
        self.assertNotIn("starting_tests", result)
        self.assertNotIn("starting_tests", result["records"][0])

    def test_cli_accepts_starting_tests_and_runs_the_real_harness(self):
        starting = self.starting_tests()
        output = self.directory / "cli-maintenance"
        arguments = ["runner.py", "evaluate", "--skill", str(self.skill), "--output", str(output),
                     "--repeats", "1", "--starting-tests", str(starting)]
        with patch.object(runner.sys, "argv", arguments), patch.object(runner, "agent", side_effect=self.maintain), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, runner.main())
        result = runner.read_json(output / "evaluation.json")
        self.assertTrue(result["eligible"])
        self.assertEqual(str(starting), result["starting_tests"]["source_root"])

    def test_cli_default_call_budgets_cover_the_expanded_suite(self):
        arguments = ["runner.py", "evaluate", "--skill", str(self.skill), "--output", str(self.directory / "unused")]
        with patch.object(runner.sys, "argv", arguments), patch.object(runner, "evaluate") as evaluate:
            self.assertEqual(0, runner.main())
        self.assertEqual(18, evaluate.call_args.args[4].maximum)
        arguments[1] = "research"
        with patch.object(runner.sys, "argv", arguments), patch.object(runner, "research") as research:
            self.assertEqual(0, runner.main())
        self.assertEqual(61, research.call_args.args[0].max_agent_calls)


class AgentBudgetTests(EvaluatorFixture):
    def test_exhausted_budget_prevents_starting_an_agent_process(self):
        budget = runner.AgentBudget(1)
        budget.consume()
        evidence = self.directory / "never-started"

        with patch.object(runner, "run_process") as process:
            with self.assertRaises(RuntimeError):
                runner.agent(self.directory, "A task", evidence, budget)

        process.assert_not_called()
        self.assertEqual(1, budget.used)
        self.assertFalse(evidence.exists())

    def test_simultaneous_consumers_cannot_exceed_the_shared_call_budget(self):
        callers, allowance = 16, 5
        rendezvous = threading.Barrier(callers)
        budget = runner.AgentBudget(allowance)

        def consume_once(_):
            rendezvous.wait(timeout=5)
            try:
                budget.consume()
                return True
            except RuntimeError:
                return False

        with ThreadPoolExecutor(max_workers=callers) as pool:
            admitted = list(pool.map(consume_once, range(callers)))

        self.assertEqual(allowance, sum(admitted))
        self.assertEqual(callers - allowance, admitted.count(False))
        self.assertEqual(allowance, budget.used)

    def test_research_budget_stop_preserves_evidence_without_promoting_a_candidate(self):
        started = []

        def controlled_agent(workspace, prompt, evidence, budget, timeout=600):
            budget.consume()
            started.append(Path(workspace))
            (Path(workspace) / "tests" / "test_subject.py").write_text(CONTRACT_TEST)

        args = SimpleNamespace(output=self.directory / "campaign", skill=self.skill, max_agent_calls=1,
                               repeats=1, rounds=2, agent_timeout=5, workers=1)
        with patch.object(runner, "agent", side_effect=controlled_agent), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError):
                runner.research(args)

        state = runner.read_json(args.output / "campaign.json")
        self.assertEqual("incomplete", state["status"])
        self.assertEqual(1, state["agent_calls"])
        self.assertEqual(1, len(started))
        self.assertTrue((args.output / "baseline" / "evaluation.json").is_file())
        self.assertFalse((args.output / "accepted-skill").exists())


class RejectedDevelopmentHistoryTests(EvaluatorFixture):
    def test_second_proposal_receives_prior_change_and_rejected_development_evidence(self):
        observed = []
        evaluated_splits = []

        def proposer(workspace, prompt, evidence, budget, timeout=600):
            budget.consume()
            workspace = Path(workspace)
            observed.append({"history": runner.read_json(workspace / "rejected-development-history.json"),
                             "incumbent_feedback": runner.read_json(workspace / "development-feedback.json")})
            number = len(observed)
            (workspace / "hypothesis.md").write_text(f"Hypothesis {number}: clarify observable outcomes.\n")
            skill = workspace / "skill" / "SKILL.md"
            skill.write_text(skill.read_text() + ("\nClarify.\n" if number == 1 else "\nObserve.\n"))

        def evaluation(skill, cases, output, repeats, budget, timeout, workers=1):
            evaluated_splits.append(list(cases))
            values = {"retained": Path(output).name == "baseline", "missing": False}
            return ComparisonTests.evaluation({case: [values] * repeats for case in cases}, repeats)

        args = SimpleNamespace(output=self.directory / "history-campaign", skill=self.skill,
                               max_agent_calls=10, repeats=1, rounds=2, agent_timeout=5, workers=1)
        with patch.object(runner, "agent", side_effect=proposer), \
                patch.object(runner, "evaluate", side_effect=evaluation), \
                patch.object(runner, "review_candidate") as review, \
                contextlib.redirect_stdout(io.StringIO()):
            runner.research(args)

        self.assertEqual(2, len(observed))
        self.assertEqual([], observed[0]["history"])
        self.assertEqual(observed[0]["incumbent_feedback"], observed[1]["incumbent_feedback"])
        self.assertEqual(1, len(observed[1]["history"]))
        previous = observed[1]["history"][0]
        self.assertEqual({"round", "hypothesis", "skill_markdown_changes", "development_feedback", "decision"}, set(previous))
        self.assertEqual(1, previous["round"])
        self.assertEqual("Hypothesis 1: clarify observable outcomes.\n", previous["hypothesis"])
        self.assertEqual(["SKILL.md"], [item["path"] for item in previous["skill_markdown_changes"]])
        self.assertIn("+Clarify.", previous["skill_markdown_changes"][0]["diff"])
        self.assertNotIn("Observe.", previous["skill_markdown_changes"][0]["diff"])
        self.assertEqual(["Observable result: retained", "Observable result: missing"],
                         previous["development_feedback"]["cases"][0]["missed_contracts"])
        self.assertFalse(previous["decision"]["development_improved"])
        self.assertFalse(previous["decision"]["accepted"])
        self.assertTrue(previous["decision"]["reason"])
        self.assertEqual([["sample"], ["sample"], ["sample"]], evaluated_splits)
        self.assertEqual({"sample"}, {item["case"] for item in previous["development_feedback"]["cases"]})
        review.assert_not_called()
        self.assertFalse((args.output / "accepted-skill").exists())

    def test_holdout_use_ends_proposals_even_when_holdout_or_quality_review_rejects(self):
        for index, (holdout_passes, review_approves) in enumerate(((False, None), (True, False), (True, True))):
            with self.subTest(holdout_passes=holdout_passes, review_approves=review_approves):
                proposals = []
                evaluation_names = []

                def proposer(workspace, prompt, evidence, budget, timeout=600):
                    budget.consume()
                    workspace = Path(workspace)
                    proposals.append(workspace)
                    self.assertEqual([], runner.read_json(workspace / "rejected-development-history.json"))
                    (workspace / "hypothesis.md").write_text("Improve observable expectations.\n")
                    skill = workspace / "skill" / "SKILL.md"
                    skill.write_text(skill.read_text() + "\nClarify.\n")

                def evaluation(skill, cases, output, repeats, budget, timeout, workers=1):
                    name = Path(output).name
                    evaluation_names.append(name)
                    detected = name != "baseline" and (name != "holdout-candidate" or holdout_passes)
                    return ComparisonTests.evaluation({case: [{"fault": detected}] * repeats for case in cases}, repeats)

                args = SimpleNamespace(output=self.directory / f"holdout-stop-{index}", skill=self.skill,
                                       max_agent_calls=10, repeats=1, rounds=3, agent_timeout=5, workers=1)
                with patch.object(runner, "agent", side_effect=proposer), \
                        patch.object(runner, "evaluate", side_effect=evaluation), \
                        patch.object(runner, "review_candidate", return_value={"approved": review_approves}) as review, \
                        contextlib.redirect_stdout(io.StringIO()):
                    runner.research(args)

                self.assertEqual(1, len(proposals))
                self.assertEqual(["baseline", "development", "holdout-incumbent", "holdout-candidate"], evaluation_names)
                self.assertFalse((args.output / "round-2").exists())
                state = runner.read_json(args.output / "campaign.json")
                self.assertEqual("completed", state["status"])
                self.assertEqual(1, len(state["rounds"]))
                self.assertEqual(bool(holdout_passes and review_approves), state["rounds"][0]["accepted"])
                if holdout_passes:
                    review.assert_called_once()
                else:
                    review.assert_not_called()


class CampaignIntegrityTests(EvaluatorFixture):
    def test_changed_evaluator_cannot_leave_a_promoted_skill_artifact(self):
        def proposal(workspace, prompt, evidence, budget, timeout=600):
            budget.consume()
            skill = Path(workspace) / "skill" / "SKILL.md"
            skill.write_text(skill.read_text() + "\nClarify.\n")

        def evaluation(skill, cases, output, repeats, budget, timeout, workers=1):
            improved = Path(output).name != "baseline"
            if Path(output).name == "holdout-candidate":
                evaluator = self.root / "runner.py"
                evaluator.write_text(evaluator.read_text() + "\n# Changed during the campaign.\n")
            return ComparisonTests.evaluation({case: [{"regression": improved}] * repeats for case in cases}, repeats)

        args = SimpleNamespace(output=self.directory / "changed-evaluator", skill=self.skill, max_agent_calls=10,
                               repeats=2, rounds=1, agent_timeout=5, workers=1)
        with patch.object(runner, "agent", side_effect=proposal), patch.object(runner, "evaluate", side_effect=evaluation):
            with self.assertRaisesRegex(RuntimeError, "Evaluator changed"):
                runner.research(args)

        self.assertEqual("incomplete", runner.read_json(args.output / "campaign.json")["status"])
        self.assertFalse((args.output / "accepted-skill").exists())


if __name__ == "__main__":
    unittest.main()
