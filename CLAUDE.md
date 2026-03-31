# AgentWorks

Cross-project coordination repo for the AgentWorks suite — Maven BOM, release pipeline, and shared infrastructure.

## Execution Tracking

`plans/ROADMAP.md` is the source of truth for implementation progress. Each step should be executed individually with learnings captured in `plans/learnings/`.

## Build Commands

```bash
./mvnw verify    # Once BOM pom.xml exists
```

## Project Scope

This repo will contain:
- `agentworks-bom` — Maven BOM pinning all agent suite artifact versions
- Release coordination across 14 Java projects spanning two groupIds:
  - `org.springaicommunity` (community projects)
  - `io.github.markpollack` (personal projects)

## Related Projects

See `plans/ROADMAP.md` Stage 4 for the complete project inventory with GAVs and release versions.
