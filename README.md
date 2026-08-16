# AgentWorks BOM

The AgentWorks BOM coordinates compatible Maven versions across the nine public
AgentWorks `agent-*` projects. See the [AgentWorks project catalog](https://lab.pollack.ai/projects)
and the [BOM documentation](https://lab.pollack.ai/projects/agentworks-bom) for project details,
architecture, examples, and release notes.

The coordinated projects are [Agent Client](https://github.com/markpollack/agent-client),
[Agent Workflow](https://github.com/markpollack/agent-workflow),
[Agent Journal](https://github.com/markpollack/agent-journal),
[Agent Judge](https://github.com/markpollack/agent-judge),
[Agent Bench](https://github.com/markpollack/agent-bench),
[Agent Experiment](https://github.com/markpollack/agent-experiment),
[Agent Hooks](https://github.com/markpollack/agent-hooks),
[Agent Memory](https://github.com/markpollack/agent-memory), and
[Agent Sandbox](https://github.com/markpollack/agent-sandbox).

## Maven

Import the latest released BOM:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>io.github.markpollack</groupId>
            <artifactId>agentworks-bom</artifactId>
            <version>1.15.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

Member libraries can then be declared without individual versions.

## Build and verify

JDK 21 is used by CI. From a clean checkout, run the three-scenario consumer gate against the
current BOM:

```bash
./scripts/verify-bom
```

The command reads the version from the root POM, installs that exact BOM locally, and exercises
plain Java, Spring Boot 3.5, and Spring Boot 4 consumers. Member projects use independent version
lines; the BOM version identifies the tested combination.

## License

The current source is licensed under the [Business Source License 1.1](LICENSE).
