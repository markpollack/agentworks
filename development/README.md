# Development snapshot publication

`publish-snapshot.yml` publishes `agentworks-bom` as a development SNAPSHOT on every push
to `main` (and on manual dispatch from `main`). Provenance is the `main` commit that
triggered the run. It has no tag, stable release profile or signing step. Existing
`MAVEN_USERNAME` / `MAVEN_PASSWORD` references are used only for deployment. Stable
release guards and the plain / Boot 3.5 / Boot 4 runtime tests remain unchanged.

Before deploying, the workflow runs the stable-release guard test, the script unit tests
and `scripts/verify-bom` from an empty Maven repository. It deploys only the BOM POM,
captures this run's timestamped upload coordinate, verifies the exact deployed bytes,
then reruns the bom-verification consumers against the published BOM from another empty
repository. Publication is not transactional: a failed post-publication check means a
snapshot may have been deployed and must be fixed forward on `main`. Runs are serialized
and never cancelled in progress.

Consumers must declare the snapshot repository themselves: importing a Maven BOM
does not import its `<repositories>` section.

```xml
<repositories>
  <repository>
    <id>central-snapshots</id>
    <url>https://central.sonatype.com/repository/maven-snapshots/</url>
    <releases><enabled>false</enabled></releases>
    <snapshots><enabled>true</enabled></snapshots>
  </repository>
</repositories>
```

Then import `io.github.markpollack:agentworks-bom:1.22.0-SNAPSHOT` with `scope=import`.
