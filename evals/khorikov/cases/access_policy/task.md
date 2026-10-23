# Regression tests for inherited access policies

Add standard-library `unittest` tests under `tests/test_*.py` for `access_policy.py`.
Preserve the supplied module and this task. The module is pure Python and has no
external dependencies. Use deterministic data and explicit `now` values. Run your
tests and write an English `report.md` describing the contract evidence, actual
commands and results, and any limitations.

The public API consists of `Rule`, `Scope`, `Decision`, and `PolicySet`. Test
observable access decisions and invalid configuration through these APIs. Internal
helpers and storage layout are not part of the contract.

## Data and construction

- `Rule(role, action, effect, expires_at=None)` is an immutable value. `role` and
  `action` are nonempty, case-sensitive strings. `effect` is exactly `"allow"` or
  `"deny"`. Empty role/action or another effect raises `ValueError`. A policy rule
  may use `"*"` for its role, its action, or both.
- `Scope(name, parent=None, rules=(), inherit=True)` is a record whose fields cannot
  be reassigned. It names a resource scope. `name` is a nonempty, case-sensitive
  string; an empty name raises
  `ValueError`. `parent` is another scope's name or `None`. `rules` is an iterable
  of `Rule` values; its default is empty. `inherit` is a boolean.
- `PolicySet(scopes)` consumes an iterable of scopes once. It snapshots both the
  collection of scopes and each scope's rules. Subsequent changes to an input
  collection do not affect its decisions. It accepts an empty collection and
  multiple independent roots. Input order does not matter.
- The complete parent graph must be a forest. Duplicate names, unknown parents,
  self-parenting, and longer cycles raise `ValueError` during `PolicySet`
  construction, even if an `inherit=False` scope lies on an invalid link or the
  invalid component would never be queried. Exception messages are unspecified.

## Decisions

Call `policies.decide(scope, action, roles, now=integer)`:

1. `scope` must name a configured scope; otherwise raise `KeyError`. `action` must
   be a nonempty concrete string, not `"*"`; otherwise raise `ValueError`. `roles`
   is an iterable of role names, and an empty role name raises `ValueError`.
   An empty iterable means the caller has no roles. Duplicate roles and their
   order have no effect. These checks precede evaluation; if the scope is unknown,
   `KeyError` takes precedence over invalid action or role input.
2. A rule is active when `expires_at` is `None`, or when `now < expires_at`. Both
   time values are integer logical ticks supplied by the caller. There is no
   system-clock lookup. A rule is already inactive at its expiration tick.
3. An active rule matches when **both** its role and its action match. A concrete
   role matches membership in `roles`. A role of `"*"` matches everyone, including
   callers with no roles. A concrete action matches exactly; an action of `"*"`
   matches every valid requested action. No whitespace trimming or case folding
   is performed.
4. Consider the requested scope first, then its parent, then successive ancestors.
   The first scope containing at least one active matching rule decides. A scope
   containing only inactive or nonmatching rules does not decide. Applicable rules
   at more distant ancestors cannot change a nearer scope's decision.
5. At that deciding scope, any matching deny wins over any matching allow,
   regardless of rule order or whether either match used a wildcard. Return
   `Decision(allowed=False, source=that_scope_name)` for a denial, otherwise
   `Decision(allowed=True, source=that_scope_name)`.
6. An `inherit=False` scope still evaluates its own rules, but evaluation never
   traverses from that scope to its parent. This boundary applies whether it is
   the requested scope or an ancestor.
7. If the search ends without any active matching rule, return
   `Decision(allowed=False, source=None)`. This differs observably from an explicit
   deny, whose `source` is the scope that denied access.

`Decision` is an immutable value with public `allowed` and `source` fields and
value equality. Calls do not alter policy state; one `PolicySet` can be reused
across callers, actions, and ticks. Inputs of types other than those specified
above are outside this task's contract.
