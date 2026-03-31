# Roadmap: AgentWorks Release Pipeline

> **Created**: 2026-03-25T14:00-04:00
> **Last updated**: 2026-03-25T14:00-04:00
> **Source plan**: `~/.claude/plans/composed-tickling-sunrise.md`

## Overview

The blog "I Read My Agent's Diary" references 14 Java projects, none of which are on Maven Central. Three repos return 404. Readers can't try anything. This roadmap fixes that end-to-end across 5 stages: fix broken links, rename agent-harness → agent-workflow, verify publishing infrastructure, release all projects to Maven Central in dependency order, and create an `agentworks` BOM.

> **Before every commit**: Verify ALL exit criteria for the current step are met — especially the standard items (learnings file, CLAUDE.md update, ROADMAP.md checkboxes). Do NOT remove exit criteria to mark a step complete — fulfill them.

---

## Stage 1: Fix Broken Repo Links

Three blog-referenced GitHub repos return 404. This is the highest-priority fix — it unblocks the blog.

### Step 1.0: Audit and Plan Review

**Entry criteria**:
- [ ] Read: `~/.claude/plans/composed-tickling-sunrise.md` — source plan

**Work items**:
- [ ] VERIFY agent-journal (`~/projects/agent-journal/`) remote, dirty state, secrets scan
- [ ] VERIFY agent-experiment (`~/projects/agent-experiment/`) remote, dirty state, secrets scan
- [ ] VERIFY code-coverage-experiment (`~/projects/code-coverage-experiment/`) remote, dirty state, secrets scan, LICENSE presence
- [ ] DOCUMENT any blockers discovered

**Exit criteria**:
- [ ] All three repos audited, blockers listed
- [ ] Create: `plans/learnings/step-1.0-audit.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 1.1: Fix and Push agent-journal

**Entry criteria**:
- [ ] Step 1.0 complete
- [ ] Read: `plans/learnings/step-1.0-audit.md`

**Work items**:
- [ ] COMMIT staged changes in `~/projects/agent-journal/` (LICENSE + 19 source files)
- [ ] PUSH to `git@github.com:markpollack/agent-journal.git`
- [ ] VERIFY repo accessible: `curl -s -o /dev/null -w "%{http_code}" https://github.com/markpollack/agent-journal` → 200
- [ ] VERIFY no secrets or tuvium references visible in public repo

**Exit criteria**:
- [ ] `https://github.com/markpollack/agent-journal` returns 200
- [ ] Create: `plans/learnings/step-1.1-agent-journal.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

**Deliverables**: Public agent-journal repo

---

### Step 1.2: Fix and Push agent-experiment

**Entry criteria**:
- [ ] Step 1.1 complete
- [ ] Read: `plans/learnings/step-1.1-agent-journal.md`

**Work items**:
- [ ] PUSH `~/projects/agent-experiment/` to GitHub
- [ ] VERIFY repo accessible: returns 200
- [ ] VERIFY clean (no secrets, no tuvium in code)

**Exit criteria**:
- [ ] `https://github.com/markpollack/agent-experiment` returns 200
- [ ] Create: `plans/learnings/step-1.2-agent-experiment.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

**Deliverables**: Public agent-experiment repo

---

### Step 1.3: Fix and Push code-coverage-experiment (v1)

**Entry criteria**:
- [ ] Step 1.2 complete
- [ ] Read: `plans/learnings/step-1.2-agent-experiment.md`

**Work items**:
- [ ] ADD LICENSE file (copy BSL 1.1 from `~/projects/agent-experiment/LICENSE`)
- [ ] UPDATE `CLAUDE.md` — replace `ai.tuvium` groupId with `io.github.markpollack`
- [ ] UPDATE `scripts/make_markov_analysis.py` — remove/update tuvium paths
- [ ] COMMIT all changes
- [ ] PUSH to GitHub
- [ ] VERIFY repo accessible: returns 200

**Exit criteria**:
- [ ] `https://github.com/markpollack/code-coverage-experiment` returns 200
- [ ] No `ai.tuvium` references in pushed code
- [ ] LICENSE file present
- [ ] Create: `plans/learnings/step-1.3-code-coverage-experiment.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

**Deliverables**: Public code-coverage-experiment repo

---

### Step 1.4: Stage 1 Consolidation

**Entry criteria**:
- [ ] All Stage 1 steps complete
- [ ] Read: all `plans/learnings/step-1.*` files

**Work items**:
- [ ] VERIFY all 3 URLs return 200
- [ ] VERIFY blog links resolve (re-run full blog link check)
- [ ] COMPACT learnings into `plans/learnings/LEARNINGS.md`
- [ ] UPDATE `CLAUDE.md` with distilled learnings

**Exit criteria**:
- [ ] All 3 blog-referenced repos publicly accessible
- [ ] `plans/learnings/LEARNINGS.md` updated
- [ ] Create: `plans/learnings/step-1.4-stage1-summary.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

## Stage 2: Rename agent-harness → agent-workflow

Per `~/projects/agent-harness/plans/ROADMAP.md` Stage 2.9. The git remote already points to `markpollack/agent-workflow`. Rename before first release so public names are correct from day one.

### Step 2.0: Stage 2 Entry — Context Load

**Entry criteria**:
- [ ] Stage 1 consolidation complete — Read: `plans/learnings/step-1.4-stage1-summary.md`
- [ ] Read: `plans/learnings/LEARNINGS.md`
- [ ] Read: `~/projects/agent-harness/plans/ROADMAP.md` — Stage 2.9 work items (lines 758-777)
- [ ] Read: `~/projects/agent-harness/plans/DESIGN.md` — target coordinates

**Work items**:
- [ ] REVIEW rename plan for completeness
- [ ] VERIFY 176 existing tests pass before rename: `cd ~/projects/agent-harness && ./mvnw test`
- [ ] DOCUMENT current module structure and target names

**Exit criteria**:
- [ ] Tests pass pre-rename
- [ ] Create: `plans/learnings/step-2.0-rename-context.md`
- [ ] Update `ROADMAP.md` checkboxes

---

### Step 2.1: Rename Modules and POMs

**Entry criteria**:
- [ ] Step 2.0 complete
- [ ] Read: `plans/learnings/step-2.0-rename-context.md`

**Work items**:
- [ ] RENAME module directories:
  - `harness-api` → `workflow-api`
  - `harness-patterns` → `workflow-core`
  - `agent-flows` → `workflow-flows`
  - `harness-tools` → `workflow-tools`
  - `harness-agents` → `workflow-agents`
  - `harness-examples` → `workflow-examples`
- [ ] UPDATE root `pom.xml` — artifactId, module references
- [ ] UPDATE all child `pom.xml` — artifactId, parent, dependency references
- [ ] VERIFY: `./mvnw compile` passes

**Exit criteria**:
- [ ] All POMs reference new names
- [ ] `./mvnw compile` passes
- [ ] Create: `plans/learnings/step-2.1-rename-modules.md`
- [ ] Update `ROADMAP.md` checkboxes

---

### Step 2.2: Rename Packages and Imports

**Entry criteria**:
- [ ] Step 2.1 complete
- [ ] Read: `plans/learnings/step-2.1-rename-modules.md`

**Work items**:
- [ ] RENAME all Java packages: `io.github.markpollack.harness.*` → `io.github.markpollack.workflow.*`
- [ ] UPDATE all `import` statements
- [ ] UPDATE `CLAUDE.md` module references
- [ ] VERIFY: `./mvnw test` — all 176 tests pass
- [ ] RENAME local directory: `~/projects/agent-harness` → `~/projects/agent-workflow`
- [ ] COMMIT and PUSH

**Exit criteria**:
- [ ] No references to `harness-*` remain in Java source or POM files
- [ ] All 176 tests pass
- [ ] `https://github.com/markpollack/agent-workflow` accessible
- [ ] Create: `plans/learnings/step-2.2-rename-packages.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

**Deliverables**: Fully renamed agent-workflow project

---

### Step 2.3: Stage 2 Consolidation

**Entry criteria**:
- [ ] All Stage 2 steps complete
- [ ] Read: all `plans/learnings/step-2.*` files

**Work items**:
- [ ] COMPACT learnings into `plans/learnings/LEARNINGS.md`
- [ ] UPDATE `CLAUDE.md` with rename learnings

**Exit criteria**:
- [ ] Create: `plans/learnings/step-2.3-stage2-summary.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

## Stage 3: Verify Publishing Infrastructure

### Step 3.0: Stage 3 Entry — Context Load

**Entry criteria**:
- [ ] Stage 2 consolidation complete — Read: `plans/learnings/step-2.3-stage2-summary.md`
- [ ] Read: `plans/learnings/LEARNINGS.md`

**Work items**:
- [ ] CHECK GitHub secrets on all spring-ai-community repos: agent-client, agent-judge, spring-testing-skills, claude-agent-sdk-java, agent-bench, agent-sandbox
- [ ] CHECK GitHub secrets on all markpollack repos: agent-journal, agent-experiment, agent-workflow, loopy
- [ ] Required secrets: `MAVEN_USERNAME`, `MAVEN_PASSWORD`, `GPG_SECRET_KEY`, `GPG_PASSPHRASE`
- [ ] VERIFY each repo has a GitHub Actions release workflow (`.github/workflows/release.yml` or similar)
- [ ] ADD release workflow to loopy (currently missing — copy from agent-journal pattern using `markpollack/build-tools`)
- [ ] ENUMERATE exact leaf artifactIds for multi-module projects:
  - agent-client submodules
  - claude-agent-sdk-java submodules
- [ ] VERIFY `agent-client` groupId `org.springaicommunity.agents` vs `org.springaicommunity` is intentional
- [ ] DOCUMENT all gaps found

**Exit criteria**:
- [ ] All repos have release workflows
- [ ] All repos have required secrets (or gaps documented with fix plan)
- [ ] Complete artifact inventory with exact GAVs for BOM
- [ ] Create: `plans/learnings/step-3.0-publishing-infra.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

**Deliverables**: Publishing readiness report, complete GAV inventory

---

## Stage 4: Release to Maven Central

Release in dependency order. Each step releases one tier.

### Step 4.0: Stage 4 Entry — Context Load

**Entry criteria**:
- [ ] Stage 3 complete — Read: `plans/learnings/step-3.0-publishing-infra.md`
- [ ] Read: `plans/learnings/LEARNINGS.md`
- [ ] All secrets and workflows confirmed

**Work items**:
- [ ] REVIEW dependency graph for release ordering
- [ ] VERIFY no circular SNAPSHOT dependencies between tiers

**Exit criteria**:
- [ ] Release order confirmed
- [ ] Create: `plans/learnings/step-4.0-release-planning.md`
- [ ] Update `ROADMAP.md` checkboxes

---

### Step 4.1: Release Tier 1 — No Internal Dependencies

**Entry criteria**:
- [ ] Step 4.0 complete
- [ ] Read: `plans/learnings/step-4.0-release-planning.md`

**Work items**:
For each project, run per-project release checklist:
- [ ] **claude-agent-sdk-java** → 1.0.0
  - [ ] `./mvnw verify` passes locally
  - [ ] Trigger GitHub Actions release workflow
  - [ ] Verify on Maven Central
- [ ] **agent-journal** → 0.1.0
  - [ ] `./mvnw verify` passes locally
  - [ ] Trigger release workflow
  - [ ] Verify on Maven Central
- [ ] **spring-testing-skills** → 0.2.0
  - [ ] `./mvnw verify` passes locally
  - [ ] Trigger release workflow
  - [ ] Verify on Maven Central
- [ ] **agent-judge** → 0.9.1
  - [ ] `./mvnw verify` passes locally
  - [ ] Trigger release workflow
  - [ ] Verify on Maven Central
- [ ] **agent-sandbox** → 0.9.1
  - [ ] `./mvnw verify` passes locally
  - [ ] Trigger release workflow
  - [ ] Verify on Maven Central

**Exit criteria**:
- [ ] All 5 Tier 1 artifacts findable on Maven Central
- [ ] Create: `plans/learnings/step-4.1-tier1-releases.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

**Deliverables**: 5 projects on Maven Central

---

### Step 4.2: Release Tier 2 — Depends on Tier 1

**Entry criteria**:
- [ ] Step 4.1 complete
- [ ] Read: `plans/learnings/step-4.1-tier1-releases.md`
- [ ] All Tier 1 artifacts indexed on Maven Central

**Work items**:
- [ ] UPDATE SNAPSHOT deps to released Tier 1 versions in each project
- [ ] **agent-client** → 0.10.0
  - [ ] Update claude-agent-sdk dep to 1.0.0
  - [ ] `./mvnw verify`, trigger release, verify
- [ ] **agent-bench** → 0.2.0
  - [ ] Update agent-judge dep to 0.9.1
  - [ ] `./mvnw verify`, trigger release, verify
- [ ] **agent-workflow** → 0.1.0
  - [ ] `./mvnw verify`, trigger release, verify

**Exit criteria**:
- [ ] All 3 Tier 2 artifacts on Maven Central
- [ ] Create: `plans/learnings/step-4.2-tier2-releases.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 4.3: Release Tier 3 — Depends on Tier 1+2

**Entry criteria**:
- [ ] Step 4.2 complete
- [ ] Read: `plans/learnings/step-4.2-tier2-releases.md`

**Work items**:
- [ ] UPDATE SNAPSHOT deps to released versions
- [ ] **agent-experiment** → 0.1.0
  - [ ] Update agent-journal, agent-client deps
  - [ ] `./mvnw verify`, trigger release, verify
- [ ] **loopy** → 0.3.0
  - [ ] Update agent-client, agent-journal deps
  - [ ] `./mvnw verify`, trigger release, verify

**Exit criteria**:
- [ ] All Tier 3 artifacts on Maven Central
- [ ] Create: `plans/learnings/step-4.3-tier3-releases.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 4.4: Stage 4 Consolidation

**Entry criteria**:
- [ ] All Stage 4 steps complete
- [ ] Read: all `plans/learnings/step-4.*` files

**Work items**:
- [ ] VERIFY all released artifacts searchable on Maven Central
- [ ] COMPACT learnings into `plans/learnings/LEARNINGS.md`
- [ ] DOCUMENT final GAV inventory with released versions

**Exit criteria**:
- [ ] Complete released GAV table
- [ ] Create: `plans/learnings/step-4.4-stage4-summary.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

## Stage 5: Create agentworks BOM

### Step 5.0: Stage 5 Entry — Context Load

**Entry criteria**:
- [ ] Stage 4 consolidation complete — Read: `plans/learnings/step-4.4-stage4-summary.md`
- [ ] Read: `plans/learnings/LEARNINGS.md`
- [ ] All suite artifacts on Maven Central

**Work items**:
- [ ] REVIEW final GAV inventory from Stage 4
- [ ] READ Spring AI BOM for reference: `~/.m2/repository/org/springframework/ai/spring-ai-bom/`

**Exit criteria**:
- [ ] BOM artifact list finalized
- [ ] Create: `plans/learnings/step-5.0-bom-planning.md`
- [ ] Update `ROADMAP.md` checkboxes

---

### Step 5.1: Create agentworks Repo and BOM POM

**Entry criteria**:
- [ ] Step 5.0 complete
- [ ] Read: `plans/learnings/step-5.0-bom-planning.md`

**Work items**:
- [ ] CREATE GitHub repo `markpollack/agentworks`
- [ ] CREATE `pom.xml` with:
  - `groupId: io.github.markpollack`
  - `artifactId: agentworks-bom`
  - `version: 1.0.0-SNAPSHOT`
  - `packaging: pom`
  - All leaf artifacts in `<dependencyManagement>` with released versions
- [ ] ADD release workflow (from `markpollack/build-tools`)
- [ ] ADD BSL 1.1 LICENSE
- [ ] ADD README with usage example
- [ ] CONFIGURE Maven Central secrets
- [ ] PUSH to GitHub

**Exit criteria**:
- [ ] Repo public at `https://github.com/markpollack/agentworks`
- [ ] BOM POM contains all suite artifacts with correct versions
- [ ] Create: `plans/learnings/step-5.1-bom-creation.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 5.2: Release BOM 1.0.0

**Entry criteria**:
- [ ] Step 5.1 complete
- [ ] Read: `plans/learnings/step-5.1-bom-creation.md`

**Work items**:
- [ ] TRIGGER release workflow for agentworks-bom 1.0.0
- [ ] VERIFY BOM on Maven Central
- [ ] TEST: create a sample project that imports the BOM and depends on journal-core — verify it resolves

**Exit criteria**:
- [ ] `agentworks-bom:1.0.0` on Maven Central
- [ ] Sample project builds successfully with BOM-managed versions
- [ ] Create: `plans/learnings/step-5.2-bom-release.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

**Deliverables**: Published agentworks BOM on Maven Central

---

### Step 5.3: Final Consolidation

**Entry criteria**:
- [ ] All stages complete
- [ ] Read: all `plans/learnings/step-5.*` files

**Work items**:
- [ ] FINAL verification: all blog links resolve, all artifacts on Maven Central, BOM works
- [ ] COMPACT all learnings into `plans/learnings/LEARNINGS.md`
- [ ] UPDATE blog with BOM usage example (if desired)
- [ ] UPDATE lab.pollack.ai docs with installation instructions

**Exit criteria**:
- [ ] Zero broken blog links
- [ ] Full agent suite on Maven Central
- [ ] BOM published and tested
- [ ] Create: `plans/learnings/step-5.3-final-summary.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

## Conventions

### Commit Convention
```
Step X.Y: Brief description of what was done
```

### Step Entry Criteria Convention
Every step's entry criteria must include:
```markdown
- [ ] Previous step complete
- [ ] Read: `plans/learnings/step-{PREV}-{topic}.md` — prior step learnings
```

### Step Exit Criteria Convention
Every step's exit criteria must include:
```markdown
- [ ] Create: `plans/learnings/step-X.Y-topic.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT
```

### Stage Consolidation Convention
Last step of each stage compacts per-step learnings into `plans/learnings/LEARNINGS.md`.

### Inter-Stage Gate Convention
First step of Stage N (N > 1) must gate on Stage N-1 consolidation.

---

## Revision History

| Timestamp | Change | Trigger |
|-----------|--------|---------|
| 2026-03-25T14:00-04:00 | Initial draft from plan | Blog release readiness audit |
