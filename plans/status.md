# Status: agentworks

> **Period**: 2026-03-01 through 2026-03-31
> **Last updated**: 2026-03-31

## Summary

AgentWorks is the cross-project coordination repo for the agent suite — Maven BOM pinning all artifact versions across 14 Java projects spanning two groupIds (`io.github.markpollack` and `org.springaicommunity`). Version 1.0.0-SNAPSHOT. 4 commits total.

## What Was Accomplished

### 1. BOM Creation
- AgentWorks BOM 1.0.0-SNAPSHOT with all released agent suite artifacts
- Covers markpollack projects: journal-core (0.9.0), claude-code-capture (0.9.0), workflow-* (0.1.0), experiment-* (0.1.0), loopy (0.3.0)
- Covers spring-ai-community projects: spring-testing-skills (0.9.0), agent-judge-* (0.9.1), agent-sandbox-* (0.9.1), spring-ai-agent-utils (0.6.0), claude-code-sdk (1.0.0), agent-client-* (0.11.0)

### 2. Release Infrastructure
- Maven Central publishing via central-publishing-maven-plugin 0.10.0
- GPG signing, source + javadoc JARs for release profile
- Maven wrapper included

### 3. Agent-Client Update
- Updated agent-client artifacts to 0.11.0 with renamed artifactIds
- Added agent-client starters, advisor, and launcher to BOM

## Current State

### What's Working
- BOM with 30+ managed dependencies across the full agent suite
- Release profile configured for Maven Central
- Clean git status

### What's Next
- Publish BOM 1.0.0 to Maven Central
- Version alignment sweep (some projects have moved past BOM-pinned versions)
- Add new artifacts as projects ship (agent-bench, agent-experiment)
- lab.pollack.ai documentation site integration

## Where to Look for Details

| Document | Path | What It Contains |
|----------|------|-----------------|
| CLAUDE.md | `CLAUDE.md` | Build commands, project scope |
| POM | `pom.xml` | Full BOM with all managed dependencies |
