# bom-verification fixtures

Synthetic inputs used to prove the release guards behave, not real Maven projects.

## Why these are not named `pom.xml`

The release workflow refuses to publish when it finds a SNAPSHOT in any `pom.xml`:

```bash
grep -r "SNAPSHOT" --include="pom.xml" . | grep -v "<!--" | grep -v "target/" | grep -v "src/main/resources/"
```

That check is blunt by design and cannot distinguish a real managed SNAPSHOT from a fixture that
contains one on purpose. `managed-snapshot/` exists precisely to carry
`example.synthetic:managed-snapshot:0.0.0-SNAPSHOT`, so while it was named `pom.xml` it matched the
guard and **blocked every release** — first observed on BOM 1.16.0, run 32545163740, which failed
20 seconds in with nothing published.

Fixture POMs therefore use the `pom-fixture.xml` suffix. Do not rename one back to `pom.xml`.

This is the second time `bom-verification` has tripped this guard: v1.6.0 was blocked because the
subtree itself carried a `-SNAPSHOT` version, fixed by pinning it to `1.0.0`.
