import unittest

from access_policy import Decision, PolicySet, Rule, Scope


class DecisionsTest(unittest.TestCase):
    def test_matching_deny_wins_in_either_rule_order(self):
        rules = (Rule("editor", "publish", "allow"), Rule("contractor", "publish", "deny"))
        for ordered in (rules, tuple(reversed(rules))):
            with self.subTest(ordered=ordered):
                policies = PolicySet([Scope("article", rules=ordered)])
                self.assertEqual(
                    policies.decide("article", "publish", ["contractor", "editor"], now=3),
                    Decision(False, "article"),
                )

    def test_nearer_allow_overrides_parent_deny(self):
        policies = PolicySet([
            Scope("organization", rules=(Rule("*", "*", "deny"),)),
            Scope("team", "organization", (Rule("member", "read", "allow"),)),
            Scope("document", "team"),
        ])
        self.assertEqual(policies.decide("document", "read", ["member"], now=0), Decision(True, "team"))

    def test_nearer_deny_overrides_parent_allow(self):
        policies = PolicySet([
            Scope("root", rules=(Rule("member", "read", "allow"),)),
            Scope("leaf", "root", (Rule("member", "read", "deny"),)),
        ])
        self.assertEqual(policies.decide("leaf", "read", ["member"], now=0), Decision(False, "leaf"))

    def test_nearer_wildcard_match_overrides_opposing_concrete_ancestor(self):
        for local_effect, ancestor_effect in (("allow", "deny"), ("deny", "allow")):
            for role, action in (("*", "*"), ("*", "read"), ("member", "*")):
                with self.subTest(local_effect=local_effect, role=role, action=action):
                    policies = PolicySet([
                        Scope("root", rules=(Rule("member", "read", ancestor_effect),)),
                        Scope("nearer", "root", (Rule(role, action, local_effect),)),
                        Scope("leaf", "nearer"),
                    ])
                    for requested_scope in ("nearer", "leaf"):
                        with self.subTest(requested_scope=requested_scope):
                            self.assertEqual(
                                policies.decide(requested_scope, "read", ["member"], now=0),
                                Decision(local_effect == "allow", "nearer"),
                            )

    def test_nonmatching_local_rules_leave_inheritance_available(self):
        policies = PolicySet([
            Scope("root", rules=(Rule("member", "read", "allow"),)),
            Scope("leaf", "root", (
                Rule("administrator", "read", "deny"),
                Rule("member", "write", "deny"),
            )),
        ])
        self.assertEqual(policies.decide("leaf", "read", ["member"], now=0), Decision(True, "root"))

    def test_expiration_boundary_falls_back_to_parent(self):
        policies = PolicySet([
            Scope("root", rules=(Rule("guest", "read", "deny"),)),
            Scope("leaf", "root", (Rule("guest", "read", "allow", expires_at=40),)),
        ])
        self.assertEqual(policies.decide("leaf", "read", ["guest"], now=39), Decision(True, "leaf"))
        self.assertEqual(policies.decide("leaf", "read", ["guest"], now=40), Decision(False, "root"))
        self.assertEqual(policies.decide("leaf", "read", ["guest"], now=41), Decision(False, "root"))
        self.assertEqual(policies.decide("leaf", "read", ["guest"], now=39), Decision(True, "leaf"))

    def test_expired_deny_does_not_defeat_active_allow(self):
        policies = PolicySet([Scope("root", rules=(
            Rule("member", "read", "deny", expires_at=0),
            Rule("member", "read", "allow"),
        ))])
        self.assertEqual(policies.decide("root", "read", ["member"], now=0), Decision(True, "root"))

    def test_requested_scope_barrier_still_evaluates_own_rules(self):
        policies = PolicySet([
            Scope("root", rules=(Rule("*", "*", "allow"),)),
            Scope("private", "root", (Rule("owner", "write", "allow"),), inherit=False),
        ])
        self.assertEqual(policies.decide("private", "write", ["owner"], now=0), Decision(True, "private"))
        self.assertEqual(policies.decide("private", "read", ["owner"], now=0), Decision(False, None))

    def test_ancestor_barrier_blocks_only_its_parent_search(self):
        policies = PolicySet([
            Scope("global", rules=(Rule("*", "*", "allow"),)),
            Scope("vault", "global", (Rule("auditor", "inspect", "allow"),), inherit=False),
            Scope("folder", "vault"),
            Scope("file", "folder"),
        ])
        self.assertEqual(policies.decide("file", "inspect", ["auditor"], now=0), Decision(True, "vault"))
        self.assertEqual(policies.decide("file", "download", ["auditor"], now=0), Decision(False, None))

    def test_everyone_rule_applies_without_roles(self):
        policies = PolicySet([Scope("public", rules=(Rule("*", "read", "allow"),))])
        self.assertEqual(policies.decide("public", "read", [], now=0), Decision(True, "public"))
        self.assertEqual(policies.decide("public", "write", [], now=0), Decision(False, None))

    def test_action_wildcard_still_requires_matching_role(self):
        policies = PolicySet([Scope("root", rules=(Rule("owner", "*", "allow"),))])
        for action in ("read", "rename", "delete"):
            with self.subTest(action=action):
                self.assertEqual(policies.decide("root", action, ["owner"], now=5), Decision(True, "root"))
                self.assertEqual(policies.decide("root", action, ["reader"], now=5), Decision(False, None))

    def test_specificity_does_not_override_same_scope_deny(self):
        policies = PolicySet([Scope("root", rules=(
            Rule("owner", "read", "allow"),
            Rule("*", "*", "deny"),
        ))])
        self.assertEqual(policies.decide("root", "read", ["owner"], now=1), Decision(False, "root"))

    def test_default_denial_differs_from_explicit_denial(self):
        policies = PolicySet([Scope("root", rules=(Rule("member", "write", "deny"),))])
        explicit = policies.decide("root", "write", ["member"], now=0)
        absent = policies.decide("root", "read", ["member"], now=0)
        self.assertFalse(explicit.allowed)
        self.assertFalse(absent.allowed)
        self.assertEqual(explicit.source, "root")
        self.assertIsNone(absent.source)
        self.assertNotEqual(explicit, absent)

    def test_roles_can_be_one_shot_iterable_and_duplicates_are_irrelevant(self):
        policies = PolicySet([
            Scope("root", rules=(Rule("reviewer", "approve", "allow"),)),
            Scope("leaf", "root", (Rule("admin", "approve", "deny"),)),
        ])
        for names in (["other", "reviewer", "reviewer"], ["reviewer", "other"]):
            with self.subTest(names=names):
                self.assertEqual(
                    policies.decide("leaf", "approve", (name for name in names), now=0),
                    Decision(True, "root"),
                )

    def test_matching_is_case_sensitive_and_preserves_whitespace(self):
        policies = PolicySet([Scope("Root", rules=(Rule("Member", "Read", "allow"),))])
        self.assertEqual(policies.decide("Root", "Read", ["Member"], now=0), Decision(True, "Root"))
        for action, roles in (("read", ["Member"]), ("Read", ["member"]), ("Read ", ["Member"]), ("Read", [" Member"])):
            with self.subTest(action=action, roles=roles):
                self.assertEqual(policies.decide("Root", action, roles, now=0), Decision(False, None))
        with self.assertRaises(KeyError):
            policies.decide("root", "Read", ["Member"], now=0)

    def test_unrelated_calls_do_not_retain_caller_or_action(self):
        policies = PolicySet([Scope("root", rules=(Rule("member", "read", "allow"),))])
        self.assertEqual(policies.decide("root", "read", ["member"], now=0), Decision(True, "root"))
        self.assertEqual(policies.decide("root", "read", [], now=0), Decision(False, None))
        self.assertEqual(policies.decide("root", "write", ["member"], now=0), Decision(False, None))
        self.assertEqual(policies.decide("root", "read", ["member"], now=0), Decision(True, "root"))


class ConfigurationTest(unittest.TestCase):
    def test_parent_reference_uses_exact_case_when_both_names_exist(self):
        policies = PolicySet([
            Scope("Archive", rules=(Rule("*", "read", "allow"),)),
            Scope("archive", rules=(Rule("*", "read", "deny"),)),
            Scope("document", "Archive"),
        ])
        self.assertEqual(policies.decide("document", "read", [], now=0), Decision(True, "Archive"))

    def test_differently_cased_parent_name_is_unknown(self):
        with self.assertRaises(ValueError):
            PolicySet([Scope("Archive"), Scope("document", "archive")])

    def test_empty_policy_set_is_valid_but_has_no_known_scope(self):
        policies = PolicySet([])
        with self.assertRaises(KeyError):
            policies.decide("missing", "read", [], now=0)

    def test_empty_scope_denies_by_default(self):
        self.assertEqual(PolicySet([Scope("root")]).decide("root", "read", [], now=0), Decision(False, None))

    def test_unordered_forest_and_generator_input_are_supported(self):
        scopes = [
            Scope("leaf", "root"),
            Scope("other", rules=(Rule("*", "read", "deny"),)),
            Scope("root", rules=(Rule("*", "read", "allow"),)),
        ]
        policies = PolicySet(scope for scope in scopes)
        self.assertEqual(policies.decide("leaf", "read", [], now=0), Decision(True, "root"))
        self.assertEqual(policies.decide("other", "read", [], now=0), Decision(False, "other"))

    def test_input_collections_are_snapshotted(self):
        rules = [Rule("member", "read", "allow")]
        scopes = [Scope("root", rules=rules)]
        policies = PolicySet(scopes)
        rules[:] = [Rule("member", "read", "deny")]
        scopes[:] = [Scope("replacement")]
        self.assertEqual(policies.decide("root", "read", ["member"], now=0), Decision(True, "root"))
        with self.assertRaises(KeyError):
            policies.decide("replacement", "read", [], now=0)

    def test_generator_rules_are_snapshotted_before_first_decision(self):
        for original_effect, replacement_effect in (("allow", "deny"), ("deny", "allow")):
            with self.subTest(original_effect=original_effect):
                rules = [Rule("member", "read", original_effect)]
                policies = PolicySet([
                    Scope("root", rules=(rule for rule in rules)),
                ])
                rules[:] = [Rule("member", "read", replacement_effect)]
                self.assertEqual(
                    policies.decide("root", "read", ["member"], now=0),
                    Decision(original_effect == "allow", "root"),
                )

    def test_invalid_graphs_are_rejected_at_construction(self):
        configurations = [
            [Scope("a"), Scope("a")],
            [Scope("a", "missing")],
            [Scope("a", "missing", inherit=False)],
            [Scope("a", "a")],
            [Scope("a", "b"), Scope("b", "c"), Scope("c", "a", inherit=False)],
            [Scope("valid"), Scope("x", "y"), Scope("y", "x")],
        ]
        for scopes in configurations:
            with self.subTest(scopes=scopes), self.assertRaises(ValueError):
                PolicySet(scopes)

    def test_invalid_rule_values_and_empty_scope_name_are_rejected(self):
        for role, action, effect in (("", "read", "allow"), ("member", "", "allow"), ("member", "read", "ALLOW"), ("member", "read", "")):
            with self.subTest(role=role, action=action, effect=effect), self.assertRaises(ValueError):
                Rule(role, action, effect)
        with self.assertRaises(ValueError):
            Scope("")

    def test_invalid_requests_are_rejected_even_if_scope_has_no_rules(self):
        policies = PolicySet([Scope("root")])
        for action in ("", "*"):
            with self.subTest(action=action), self.assertRaises(ValueError):
                policies.decide("root", action, [], now=0)
        with self.assertRaises(ValueError):
            policies.decide("root", "read", ["member", ""], now=0)

    def test_unknown_scope_precedes_other_invalid_request_fields(self):
        policies = PolicySet([Scope("root")])
        with self.assertRaises(KeyError):
            policies.decide("missing", "", [""], now=0)

    def test_public_values_prevent_field_reassignment(self):
        values = [(Rule("member", "read", "allow"), "effect", "deny"),
                  (Scope("root"), "name", "other"),
                  (Decision(True, "root"), "allowed", False)]
        for value, field, replacement in values:
            with self.subTest(value=value), self.assertRaises((AttributeError, TypeError)):
                setattr(value, field, replacement)


if __name__ == "__main__":
    unittest.main()
