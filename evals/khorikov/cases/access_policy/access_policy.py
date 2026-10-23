"""Evaluate inherited role policies without clocks or external services."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Rule:
    """One allow or deny rule, optionally expiring at a caller-supplied tick."""

    role: str
    action: str
    effect: str
    expires_at: int | None = None

    def __post_init__(self):
        if not self.role or not self.action:
            raise ValueError("Rule role and action must be nonempty")
        if self.effect not in {"allow", "deny"}:
            raise ValueError("Rule effect must be allow or deny")


@dataclass(frozen=True)
class Scope:
    """A named resource scope and its directly attached rules."""

    name: str
    parent: str | None = None
    rules: tuple[Rule, ...] = ()
    inherit: bool = True

    def __post_init__(self):
        if not self.name:
            raise ValueError("Scope name must be nonempty")


@dataclass(frozen=True)
class Decision:
    """An access result; source is None for the default denial."""

    allowed: bool
    source: str | None


class PolicySet:
    """A reusable snapshot of an acyclic forest of resource policies.

    All graph validation happens at construction, so a later access request
    never encounters a dangling parent or a cycle. Inheritance barriers affect
    decisions but do not exempt the underlying graph from validation.
    """

    def __init__(self, scopes: Iterable[Scope]):
        indexed = {}
        for scope in scopes:
            if scope.name in indexed:
                raise ValueError("Duplicate scope: " + scope.name)
            indexed[scope.name] = Scope(
                name=scope.name,
                parent=scope.parent,
                rules=tuple(scope.rules),
                inherit=scope.inherit,
            )
        self._scopes = indexed
        self._validate_hierarchy()

    def _validate_hierarchy(self):
        for scope in self._scopes.values():
            if scope.parent is not None and scope.parent not in self._scopes:
                raise ValueError("Unknown parent: " + scope.parent)

        # Validate every component, including links behind inheritance barriers.
        complete = set()
        for name in self._scopes:
            trail = set()
            cursor = name
            while cursor is not None and cursor not in complete:
                if cursor in trail:
                    raise ValueError("Policy hierarchy contains a cycle")
                trail.add(cursor)
                cursor = self._scopes[cursor].parent
            complete.update(trail)

    def _lineage(self, name):
        current = self._scopes[name]
        while True:
            yield current
            if not current.inherit:
                return
            if current.parent is None:
                return
            current = self._scopes[current.parent]

    @staticmethod
    def _matches(rule, action, roles, now):
        if rule.expires_at is not None and now >= rule.expires_at:
            return False
        return (
            (rule.role == "*" or rule.role in roles)
            and (rule.action == "*" or rule.action == action)
        )

    def decide(
        self,
        scope: str,
        action: str,
        roles: Iterable[str],
        *,
        now: int,
    ) -> Decision:
        """Resolve the first scope with applicable rules, denying ties.

        The caller supplies time explicitly. An expired rule is absent from
        consideration, including at the expiration tick itself. Rules from
        different scopes never combine: the closest applicable scope decides.

        Everyone rules apply even when roles is empty. Duplicate input roles
        have no significance. A search with no applicable rule returns a denial
        without a source, distinguishing it from a configured deny rule.
        """
        if scope not in self._scopes:
            raise KeyError(scope)
        if not action or action == "*":
            raise ValueError("Requested action must be a concrete nonempty name")
        role_set = frozenset(roles)
        if "" in role_set:
            raise ValueError("Requested roles must be nonempty names")

        for current in self._lineage(scope):
            applicable = [
                rule for rule in current.rules
                if self._matches(rule, action, role_set, now)
            ]
            if applicable:
                denied = any(rule.effect == "deny" for rule in applicable)
                return Decision(not denied, current.name)

        return Decision(False, None)
