package io.github.markpollack.agentworks.verify;

import com.fasterxml.jackson.core.Version;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.markpollack.claude.agent.sdk.parsing.MessageParser;
import io.github.markpollack.claude.agent.sdk.types.Message;
import io.github.markpollack.journal.claude.PhaseCapture;
import io.github.markpollack.journal.claude.SessionLogParser;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Golden-path quality gate for the agentworks BOM.
 *
 * Guards against the agentworks-bom 1.5.0 regression where a consumer resolved a
 * MIXED Jackson set (databind 2.18.2 + core/annotations 2.17.2 + jsonSchema 2.20.1),
 * which failed at runtime with
 * {@code NoSuchMethodError: ParserMinimalBase.<init>(StreamReadConstraints)} on every
 * SDK message parse — the visible symptom being silent zero-byte TraceWriter files
 * and empty agent answers with retries.
 *
 * Three checks:
 *  1. Every Jackson 2 jar on the classpath reports the SAME version.
 *  2. The SDK message-parse path works end to end (the exact NoSuchMethodError site).
 *  3. SessionLogParser writes a NON-EMPTY trace file (the zero-byte symptom).
 */
class JacksonConvergenceTest {

    @Test
    @DisplayName("all Jackson 2 jars on the classpath resolve to a single version")
    void jacksonArtifactsConverge() throws Exception {
        List<String> seen = new ArrayList<>();

        Version core = com.fasterxml.jackson.core.json.PackageVersion.VERSION;
        Version databind = com.fasterxml.jackson.databind.cfg.PackageVersion.VERSION;
        seen.add("jackson-core=" + core);
        seen.add("jackson-databind=" + databind);

        assertThat(databind.toString())
                .as("jackson-databind must match jackson-core (mixed set => ParserMinimalBase NoSuchMethodError)")
                .isEqualTo(core.toString());

        // Optional modules — only checked when present on the classpath.
        for (String pkgVersionClass : new String[] {
                "com.fasterxml.jackson.datatype.jsr310.PackageVersion",
                "com.fasterxml.jackson.dataformat.yaml.PackageVersion",
                "com.fasterxml.jackson.module.jsonSchema.PackageVersion" }) {
            Version v = optionalVersion(pkgVersionClass);
            if (v != null) {
                seen.add(pkgVersionClass + "=" + v);
                assertThat(v.toString())
                        .as("%s must match jackson-core %s (full set: %s)", pkgVersionClass, core, seen)
                        .isEqualTo(core.toString());
            }
        }

        // Annotations versions as major.minor only since 2.21 — compare the prefix.
        String annotations = com.fasterxml.jackson.annotation.JsonProperty.class
                .getPackage().getImplementationVersion();
        if (annotations != null) {
            assertThat(core.toString())
                    .as("jackson-annotations (%s) must share major.minor with jackson-core", annotations)
                    .startsWith(annotations.split("\\.")[0] + "." + annotations.split("\\.")[1]);
        }
    }

    @Test
    @DisplayName("SDK message parse works (the ParserMinimalBase NoSuchMethodError site)")
    void sdkMessageParseSmokeTest() throws Exception {
        MessageParser parser = new MessageParser();

        Message user = parser.parseMessage(
                "{\"type\":\"user\",\"message\":{\"content\":\"hello\"}}");
        assertThat(user).isNotNull();

        Message assistant = parser.parseMessage(
                "{\"type\":\"assistant\",\"message\":{\"content\":[{\"type\":\"text\",\"text\":\"hi there\"}]}}");
        assertThat(assistant).isNotNull();

        // Plain databind round-trip exercises parser construction + StreamReadConstraints.
        ObjectMapper mapper = new ObjectMapper();
        JsonNode node = mapper.readTree("{\"a\":[1,2,3],\"b\":{\"c\":\"d\"}}");
        assertThat(mapper.writeValueAsString(node)).contains("\"c\":\"d\"");
    }

    @Test
    @DisplayName("TraceWriter produces a non-empty trace file (zero-byte regression)")
    void traceFileIsNotEmpty(@TempDir Path tmp) throws Exception {
        MessageParser parser = new MessageParser();
        Message assistant = parser.parseMessage(
                "{\"type\":\"assistant\",\"message\":{\"content\":[{\"type\":\"text\",\"text\":\"answer\"}]}}");

        Path traceFile = tmp.resolve("trace.jsonl");
        PhaseCapture capture = SessionLogParser.parse(
                List.of((io.github.markpollack.claude.agent.sdk.parsing.ParsedMessage)
                        io.github.markpollack.claude.agent.sdk.parsing.ParsedMessage.RegularMessage.of(assistant)).iterator(),
                "verify", "prompt text", traceFile);

        assertThat(capture).isNotNull();
        assertThat(Files.exists(traceFile))
                .as("trace file should have been created")
                .isTrue();
        assertThat(Files.size(traceFile))
                .as("trace file must not be zero bytes (the silent 1.5.0 failure symptom)")
                .isGreaterThan(0L);
    }

    private static Version optionalVersion(String className) {
        try {
            Class<?> clazz = Class.forName(className);
            return (Version) clazz.getField("VERSION").get(null);
        }
        catch (ClassNotFoundException e) {
            return null; // module not on this scenario's classpath — fine
        }
        catch (ReflectiveOperationException e) {
            throw new IllegalStateException("Cannot read " + className, e);
        }
    }
}
