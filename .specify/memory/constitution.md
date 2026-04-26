<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 (uninitialized template) → 1.0.0
Bump type: MAJOR — inaugural ratification; all placeholder tokens replaced with concrete governance content.

Principles established:
  NEW → I. Code Quality First
  NEW → II. Test-First Development (NON-NEGOTIABLE)
  NEW → III. Consistent User Experience
  NEW → IV. Performance by Design
  NEW → V. Continuous Integration & Quality Gates

Sections established:
  NEW → Performance Standards
  NEW → Development Workflow & Quality Gates

Templates requiring updates:
  ✅ .specify/templates/plan-template.md — Constitution Check gates align with principles I–V
  ✅ .specify/templates/spec-template.md — Success Criteria section covers SC metrics matching Principle IV
  ✅ .specify/templates/tasks-template.md — Test tasks (Phase tests) align with Principle II; Polish phase covers Principle I and IV
  ⚠  .specify/templates/commands/ — no command files found at expected path; no action taken

Deferred items:
  None — all fields resolved.
-->

# AI Notes Constitution

## Core Principles

### I. Code Quality First

Every line of code MUST be written to be read by humans, not just executed by machines.

- Code MUST follow the Single Responsibility Principle: each module, class, and function has exactly one reason to change.
- Code MUST be DRY (Don't Repeat Yourself): duplication is only permitted when abstraction would increase complexity more than it reduces it — and that trade-off MUST be documented.
- Dead code (unreachable branches, commented-out blocks, unused imports) MUST NOT be committed.
- All public APIs MUST be documented with purpose, parameters, return values, and known edge cases.
- Cyclomatic complexity per function MUST NOT exceed 10 without explicit justification in a complexity tracking table.
- Code review is MANDATORY for every change; no self-merges are permitted except on personal development branches.

**Rationale**: In an AI-assisted notes application, the codebase evolves rapidly. Maintaining high code quality from the outset prevents compounding technical debt and ensures the system remains understandable and maintainable as AI integrations deepen.

### II. Test-First Development (NON-NEGOTIABLE)

Tests MUST be written before implementation code. No exceptions.

- The Red-Green-Refactor cycle is strictly enforced: write a failing test → confirm it fails → implement the minimum code to pass → refactor.
- Unit test coverage MUST be ≥ 80% for all new code; coverage MUST NOT decrease across any PR.
- Integration tests MUST cover every public contract (API endpoint, service interface, data schema boundary).
- Tests MUST be deterministic: flaky tests MUST be fixed or quarantined within one sprint of detection; they MUST NOT be merged.
- Test naming MUST follow the pattern: `test_<unit>_<scenario>_<expected_result>` (or equivalent for the project language).
- Mocks MUST NOT replace real behavior in integration tests; only in unit tests where isolation is the explicit goal.

**Rationale**: AI notes features — retrieval, summarization, tagging — are complex and stateful. Test-first discipline is the only reliable way to verify correctness before user impact, especially for non-deterministic AI components where behavioural contracts must be pinned explicitly.

### III. Consistent User Experience

The user interface MUST feel like a single, coherent product across all features and surfaces.

- A shared design token system (colors, typography, spacing, elevation) MUST be defined and MUST be the only source of styling values; hard-coded style literals are forbidden.
- Every interactive element MUST meet WCAG 2.1 Level AA accessibility standards (contrast ratio ≥ 4.5:1 for text, keyboard navigability, ARIA labels where required).
- User-facing error messages MUST be written in plain language, state what went wrong, and offer a next action; technical stack traces MUST NOT be exposed.
- New UI patterns introduced by a feature MUST be documented in the component library before the feature is merged.
- User flows that span multiple screens or steps MUST have an end-to-end acceptance scenario written in the feature spec (Given/When/Then).
- Visual regressions MUST be caught by automated snapshot or pixel-comparison tests before release.

**Rationale**: Note-taking is a flow-state activity. Inconsistencies in UI patterns, terminology, or interaction models break concentration and erode trust. A constitution-level commitment to UX consistency ensures every feature team contributes to the product's coherence rather than fragmenting it.

### IV. Performance by Design

Performance requirements MUST be defined before implementation begins, not discovered after.

- Every feature spec MUST declare its performance goals in the Technical Context section of `plan.md` (e.g., p95 latency, time-to-interactive, memory budget).
- The following application-wide budgets are non-negotiable:
  - **API response time**: p95 ≤ 300 ms for read operations; p95 ≤ 500 ms for write operations under nominal load.
  - **Time-to-Interactive (TTI)**: ≤ 2 s on a mid-tier device on a 4G connection for the main notes view.
  - **Memory footprint**: Client-side heap MUST NOT exceed 150 MB during normal usage sessions.
  - **AI inference latency**: On-device or proxied AI operations MUST complete within 3 s for interactive features; background operations are exempt.
- Performance regressions (>10% degradation in any metric above) MUST block the PR and be resolved before merge.
- Optimization work MUST be evidence-driven: profiling data MUST be attached to the PR that introduces the optimization.
- No premature optimization: code MUST NOT be made complex in anticipation of performance problems that have not been measured.

**Rationale**: Users adopt note-taking apps as daily-driver tools. Sluggish response times directly reduce the perceived intelligence of AI features and increase abandonment. Defining budgets upfront ensures performance is a first-class citizen of every design decision.

### V. Continuous Integration & Quality Gates

Every commit to a shared branch MUST pass all automated quality gates before merge.

- The CI pipeline MUST run, in order: static analysis → unit tests → integration tests → coverage check → build.
- A PR MUST NOT be merged if any gate fails; bypassing CI requires two senior approvals and MUST be documented as a tech-debt item.
- Static analysis (linting, type-checking) MUST be configured to zero-warning tolerance; warnings are treated as errors.
- Dependency updates MUST be reviewed for security advisories (CVEs); known HIGH or CRITICAL vulnerabilities MUST be resolved within 7 days.
- Every release artifact MUST be produced by the CI pipeline; no manual build deployments are permitted.
- Branch protection rules MUST enforce: ≥ 1 required reviewer, CI passing, and up-to-date with base branch before merge.

**Rationale**: Continuous integration catches regressions at the lowest cost point — before code reaches shared branches. Strict quality gates make the pipeline the single source of truth for production readiness, removing subjectivity from release decisions.

## Performance Standards

The following concrete benchmarks define the performance baseline for the AI Notes application. These MUST be updated whenever the system architecture materially changes.

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Note list load (cold) | ≤ 1.5 s TTI | Lighthouse CI in CI pipeline |
| Note save (local + sync) | ≤ 200 ms perceived | User-facing timestamp delta |
| Full-text search results | ≤ 500 ms p95 | Backend instrumentation |
| AI summary generation | ≤ 3 s p95 | AI service span in traces |
| AI tagging (background) | ≤ 10 s | Background job metrics |
| Offline → online sync | ≤ 5 s for ≤ 100 notes delta | Integration test harness |
| App startup (warm) | ≤ 800 ms | Device profiler in CI |

Performance tests MUST run in the CI pipeline on every PR targeting the main branch. Results MUST be compared to the baseline from the previous release tag; regressions above the 10% threshold MUST block merge.

## Development Workflow & Quality Gates

The following workflow is MANDATORY for all feature development.

### Feature Lifecycle

1. **Spec** (`/speckit-specify`): Feature spec with user stories, requirements, and success criteria (including performance goals).
2. **Plan** (`/speckit-plan`): Technical plan passing Constitution Check against all five principles.
3. **Tasks** (`/speckit-tasks`): Dependency-ordered task list; test tasks MUST precede implementation tasks.
4. **Implement** (`/speckit-implement`): Red-Green-Refactor; commit after each passing task.
5. **Review**: PR opened; CI passes all gates; ≥ 1 reviewer approves.
6. **Merge**: Squash merge to keep history clean; feature branch deleted after merge.

### Quality Gates (MUST pass before merge)

- [ ] All unit tests pass with ≥ 80% coverage
- [ ] All integration tests pass
- [ ] Static analysis: zero warnings
- [ ] Performance benchmarks: no regression > 10%
- [ ] Visual regression tests: no unreviewed snapshots
- [ ] Code review: ≥ 1 approval
- [ ] Security scan: no HIGH/CRITICAL CVEs in new dependencies
- [ ] WCAG 2.1 AA: validated for any new UI components

### Amendment Process

Amendments to this constitution MUST follow:

1. Author opens a PR with the proposed change and rationale.
2. Amendment is announced to the full team with a 48-hour comment window.
3. ≥ 2 senior contributors MUST approve; no single author may approve their own amendment.
4. The `CONSTITUTION_VERSION` MUST be incremented following semantic versioning (see Governance).
5. All affected templates and docs MUST be updated in the same PR.

## Governance

This constitution supersedes all informal conventions, legacy patterns, and individual preferences. Where conflict exists between this document and any other project artifact, the constitution takes precedence — unless a formal amendment is in progress.

- All PRs MUST include a "Constitution Check" section (in `plan.md`) verifying compliance with Principles I–V.
- Complexity violations (e.g., cyclomatic complexity > 10, coverage < 80%) MUST be justified in the Complexity Tracking table of `plan.md`; unjustified violations block merge.
- `CONSTITUTION_VERSION` follows semantic versioning:
  - **MAJOR**: Removal or redefinition of a core principle; backward-incompatible governance change.
  - **MINOR**: New principle, new section, or materially expanded guidance added.
  - **PATCH**: Clarifications, wording refinements, typo corrections.
- Compliance reviews MUST occur at the start of each development cycle (sprint or milestone); findings MUST be logged as tech-debt tasks.
- The authoritative runtime development guidance for agents is `.specify/memory/constitution.md` (this file).

**Version**: 1.0.0 | **Ratified**: 2026-04-26 | **Last Amended**: 2026-04-26
