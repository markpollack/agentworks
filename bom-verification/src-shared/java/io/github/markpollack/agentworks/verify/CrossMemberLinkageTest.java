package io.github.markpollack.agentworks.verify;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.List;

import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;

/**
 * Cross-member LINKAGE gate for the agentworks BOM.
 *
 * <p><b>Why this exists.</b> The other scenarios prove <i>resolution</i> — that a coherent set of
 * versions can be selected. Resolution is not linkage. A member can resolve perfectly and still fail
 * at runtime because a type it compiled against has moved or been removed in a sibling the BOM has
 * since advanced.
 *
 * <p>That is not hypothetical. It shipped:
 *
 * <blockquote>
 * {@code agent-claude 0.23.0} pinned {@code journal 1.4.0} and imported
 * {@code io.github.markpollack.journal.claude.TraceContentMode}. Journal {@code 1.5.0} moved that
 * class to {@code io.github.markpollack.journal.trace}. BOM 1.12.0/1.13.0 then forced journal
 * {@code 1.6.0}, so any Spring Boot consumer trace-wiring a Claude client hit
 * {@code NoClassDefFoundError: …journal/claude/TraceContentMode}. Every gate was green: the member's
 * own CI passed because it built against the old sibling, and BOM verification passed because
 * resolution succeeded. Nothing loaded the two members together.
 * </blockquote>
 *
 * <p>Consequence for release policy: without this check, a drift waiver cannot be evidence-backed.
 * Waiving a BEHIND sibling pin is a claim that the gap is harmless, and a resolution-only gate has
 * no way to support or refute that claim.
 *
 * <p><b>How it works.</b> Loading a class is not enough — the JVM resolves referenced types lazily,
 * so {@code Class.forName} alone can succeed while a moved type is still missing. Reflecting over
 * declared methods, fields and constructors forces the JVM to resolve every type in those
 * signatures, which is where a moved or deleted sibling type surfaces as {@link NoClassDefFoundError}.
 *
 * <p><b>Maintenance.</b> When a member starts depending on a new sibling package, add it here. A
 * boundary this test does not name is a boundary this gate does not protect.
 */
class CrossMemberLinkageTest {

	/**
	 * Classes in {@code agent-client} that reference {@code agent-journal} types in their own
	 * signatures or bodies. These are the member boundaries the BOM actually has to hold together.
	 */
	private static final List<String> BOUNDARY_CLASSES = List.of(
			"io.github.markpollack.agents.claude.ClaudeAgentModel",
			"io.github.markpollack.agents.claude.ClaudeAgentSession",
			"io.github.markpollack.agents.claude.ClaudeAgentSessionRegistry");

	/**
	 * Every {@code agent-journal} type reached across the member boundary from {@code agent-claude}.
	 * {@code journal.trace.TraceContentMode} is the one that actually moved; the rest are the
	 * surface that would break the same way.
	 */
	private static final List<String> JOURNAL_TYPES_AT_THE_BOUNDARY = List.of(
			"io.github.markpollack.journal.Journal",
			"io.github.markpollack.journal.Run",
			"io.github.markpollack.journal.RunStatus",
			"io.github.markpollack.journal.claude.BaseRunRecorder",
			"io.github.markpollack.journal.claude.PhaseCapture",
			"io.github.markpollack.journal.claude.SessionLogParser",
			"io.github.markpollack.journal.event.JournalEvent",
			"io.github.markpollack.journal.event.LLMCallEvent",
			"io.github.markpollack.journal.event.ToolCallEvent",
			"io.github.markpollack.journal.storage.InMemoryStorage",
			"io.github.markpollack.journal.trace.TraceContentMode");

	/**
	 * Not every scenario puts both members on the classpath — {@code boot35} and {@code boot4}
	 * deliberately carry only the journal/SDK side. A boundary that a scenario does not assemble is
	 * not a boundary that scenario can violate, so those scenarios skip rather than fail. The
	 * {@code plain} scenario is the one that assembles both sides; it is where this gate bites.
	 */
	private static boolean boundaryIsOnThisClasspath(ClassLoader loader) {
		try {
			Class.forName(BOUNDARY_CLASSES.get(0), false, loader);
			return true;
		}
		catch (ClassNotFoundException ex) {
			return false;
		}
	}

	@Test
	@DisplayName("every agent-journal type reached across the member boundary is present")
	void journalTypesAtTheBoundaryArePresent() {
		ClassLoader loader = getClass().getClassLoader();
		Assumptions.assumeTrue(boundaryIsOnThisClasspath(loader),
				"this scenario does not assemble the agent-client side of the boundary");

		for (String type : JOURNAL_TYPES_AT_THE_BOUNDARY) {
			assertThatCode(() -> Class.forName(type, false, loader))
				.withFailMessage(
						"%s is referenced across the agent-client -> agent-journal member boundary but is "
								+ "absent from the resolved graph. A sibling type has moved or been removed; "
								+ "resolution succeeded and linkage did not. This is the 1.12.0/1.13.0 "
								+ "TraceContentMode failure mode.",
						type)
				.doesNotThrowAnyException();
		}
	}

	@Test
	@DisplayName("boundary-crossing classes fully resolve their signatures against the resolved siblings")
	void boundaryClassesResolveTheirSignatures() {
		ClassLoader loader = getClass().getClassLoader();
		Assumptions.assumeTrue(boundaryIsOnThisClasspath(loader),
				"this scenario does not assemble the agent-client side of the boundary");

		for (String className : BOUNDARY_CLASSES) {
			assertThatCode(() -> {
				Class<?> type = Class.forName(className, false, loader);
				// Force the JVM to resolve every type named in these signatures. A moved or deleted
				// sibling type surfaces here as NoClassDefFoundError; Class.forName alone would not
				// have noticed, because reference resolution is lazy.
				Method[] methods = type.getDeclaredMethods();
				Field[] fields = type.getDeclaredFields();
				Constructor<?>[] constructors = type.getDeclaredConstructors();
				assertThat(methods).isNotNull();
				assertThat(fields).isNotNull();
				assertThat(constructors).isNotNull();
			})
				.withFailMessage(
						"%s could not resolve its declared signatures against the versions this BOM "
								+ "selects. The member compiled against a different sibling than the one "
								+ "resolved here — the exact shape of the 1.12.0/1.13.0 regression.",
						className)
				.doesNotThrowAnyException();
		}
	}

	@Test
	@DisplayName("the boundary list is not silently empty")
	void theGateIsNotVacuous() {
		// A gate that checks nothing passes everything. If someone empties these lists to make a
		// failure go away, this test fails instead — the failure stays visible.
		assertThat(BOUNDARY_CLASSES).as("boundary classes under test").isNotEmpty();
		assertThat(JOURNAL_TYPES_AT_THE_BOUNDARY).as("cross-member types under test").hasSizeGreaterThan(5);
	}

}
