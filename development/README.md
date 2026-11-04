# Development snapshot publication

`publish-snapshot.yml` is manual-only and requires the independently reviewed exact
current `main` SHA. It has no push trigger, tag, stable release profile or signing step.
Existing `MAVEN_USERNAME` / `MAVEN_PASSWORD` references are used only for deployment.
Stable release guards and the plain / Boot 3.5 / Boot 4 runtime tests remain unchanged.

Publication is currently blocked. Final retained Client/Journal acceptance and the
complete published member bill are not available. No accepted-members manifest is
checked in and no workflow dispatch is warranted from this preparation.

Before publication, the owning Release steward must review and commit
`development/accepted-members.json`, obtain independent review and normal gates, and
promote that exact candidate non-forcibly. Every selected SNAPSHOT member needs an
actual owning acceptance receipt, current accepted-main source SHA and remote POM/JAR
checksums. Version strings alone do not establish source identity. Client/Journal
source promotion and workflows remain their owners' actions through Owner relay.

The manifest shape is `{"members": {"artifact-id": OFFER}}`. Each OFFER contains:

- `version`: selected base SNAPSHOT version;
- `sourceRepository`: repository name mapped from the BOM property;
- `sourceSha`: exact 40-character accepted current main SHA;
- `acceptanceReceipt`: immutable owning receipt reference reviewed by Release;
- `files`: `pom` and `jar` objects (only `pom` for POM-packaged modules), each with
  `version` set to its timestamped remote snapshot and `sha256` for those exact bytes.

The verifier requires the entire selected bill, checks current remote source mains,
compares each latest timestamped artifact with the accepted bytes, and records the
full bill. The workflow runs ordinary consumer gates and resolves every selected
member in an empty Maven repository, checks actual consumed POM/JAR hashes and remote
origins, and rechecks the offers immediately before deploy. It captures this run's
successful timestamped Maven upload coordinate, verifies that exact deployed BOM,
then repeats remote consumers and consumed-byte/origin checks in another empty
repository. The uploaded proof includes coordinates, hashes and test reports.
An interrupted or failed post-publication proof is a failed acceptance, even if a
snapshot was deployed; publication is not transactional. Repeated dispatch requires
a fresh Release disposition, never an automatic retry.

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

Import `io.github.markpollack:agentworks-bom:1.22.0-SNAPSHOT` only after the accepted
publication receipt supplies its exact timestamped coordinate and checksum. Local
installed fixtures are preparation evidence, not remote publication acceptance.
