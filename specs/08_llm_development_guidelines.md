# Smart Thermostat

## LLM Development Guidelines

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines the mandatory development rules that every Large Language Model (LLM) shall follow while implementing the Smart Thermostat.

These rules are mandatory.

The LLM shall never violate them.

---

# 2. Documentation First

The project documentation is the single source of truth.

Implementation shall always follow the documentation.

The LLM shall never infer undocumented behaviour.

If documentation is incomplete or ambiguous, implementation shall stop.

---

# 3. No Assumptions

The LLM shall never assume undocumented requirements.

Whenever a requirement is missing, ambiguous or contradictory, the LLM shall stop and request clarification.

The LLM shall never invent missing behaviour.

---

# 4. No Architectural Decisions

The software architecture is frozen.

The LLM shall never:

- introduce new components;
- remove existing components;
- merge components;
- split components;
- modify component responsibilities.

Architecture is defined exclusively by:

- 03_architecture.md

---

# 5. No Functional Decisions

The functional behaviour is frozen.

The LLM shall never:

- introduce undocumented features;
- remove documented features;
- simplify documented behaviour;
- extend documented behaviour.

Functionality is defined exclusively by:

- 02_functional_specification.md

---

# 6. No State Machine Changes

The State Machine is frozen.

The LLM shall never:

- add states;
- remove states;
- bypass transitions;
- introduce hidden states.

The State Machine is defined exclusively by:

- 04_state_machine.md

---

# 7. No Algorithm Changes

The control algorithms are frozen.

The LLM shall never:

- replace algorithms;
- simplify algorithms;
- optimize algorithms;
- introduce alternative algorithms.

Algorithms are defined exclusively by:

- 05_control_algorithm.md
- 06_decision_rules.md

---

# 8. Respect Component Responsibilities

Every component has exactly one responsibility.

Responsibilities shall never be moved between components.

Business logic shall exist in exactly one location.

---

# 9. No Business Logic Duplication

Business logic shall never be duplicated.

Existing logic shall always be reused.

Duplicated implementations are forbidden.

---

# 10. No Hidden Behaviour

Every behaviour implemented by the LLM shall be explicitly documented.

Hidden rules, undocumented conditions and implicit behaviour are forbidden.

---

# 11. Home Assistant Best Practices

Implementation shall follow Home Assistant architecture.

The implementation shall:

- use asynchronous APIs;
- avoid blocking operations;
- respect ClimateEntity conventions;
- follow Home Assistant coding standards.

---

# 12. Simplicity

The simplest implementation satisfying the specification shall always be preferred.

Unnecessary abstractions are forbidden.

Complexity shall only be introduced when explicitly required.

---

# 13. Deterministic Behaviour

Implementation shall always be deterministic.

Given the same inputs and the same internal state, the implementation shall always produce the same outputs.

Random behaviour is forbidden.

---

# 14. Configuration

Only configuration parameters documented in:

- 07_configuration.md

may be implemented.

The LLM shall never introduce undocumented configuration options.

---

# 15. Error Handling

Errors shall always leave the thermostat in a valid operating state.

Unexpected situations shall never produce undefined behaviour.

---

# 16. Logging

Logging shall describe meaningful events.

Examples include:

- state transitions;
- rejected transitions;
- operating decisions;
- configuration errors.

Logging shall never implement business logic.

---

# 17. Code Quality

Implementation shall prioritize:

- readability;
- maintainability;
- simplicity;
- predictability.

Shorter code is not an objective.

Correct code is the objective.

---

# 18. Task Isolation

Only the current task shall be implemented.

The LLM shall never:

- anticipate future tasks;
- partially implement future functionality;
- prepare code for undocumented features.

---

# 19. No Premature Optimization

Correctness always has priority over performance.

Optimization shall only be performed when explicitly requested.

---

# 20. Testability

Every component shall be independently testable.

Component boundaries shall remain clearly identifiable.

---

# 21. Documentation Consistency

Whenever implementation and documentation differ:

the documentation is always correct.

The implementation shall be modified.

The documentation shall never be interpreted.

---

# 22. Frozen Documentation

Every document marked as "Frozen" shall be considered immutable.

The LLM shall never propose modifications unless explicitly requested by the user.

---

# 23. One Responsibility per Task

Every development task shall implement one objective only.

A task shall never contain multiple unrelated objectives.

---

# 24. No Refactoring Without Request

The LLM shall never refactor existing code unless explicitly requested.

Working code shall not be modified only for stylistic reasons.

---

# 25. Preserve Existing Behaviour

When implementing a new feature, the LLM shall preserve every previously implemented behaviour.

Regression of existing functionality is forbidden.

---

# 26. Source of Truth

The complete project documentation is the authoritative specification of the Smart Thermostat.

Whenever implementation differs from documentation, the documentation always prevails.