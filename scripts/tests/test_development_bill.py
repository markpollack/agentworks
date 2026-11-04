import copy
import importlib.util
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

script = Path(__file__).resolve().parents[1] / "verify-development-bill.py"
spec = importlib.util.spec_from_file_location("bill", script)
bill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bill)


class DevelopmentBillTest(unittest.TestCase):
    def setUp(self):
        self.selected = {"agent-client-core": {"version":"0.32.1-SNAPSHOT", "type":"jar", "sourceRepository":"agent-client"}}
        self.offer = {"version":"0.32.1-SNAPSHOT", "sourceRepository":"agent-client", "sourceSha":"a"*40,
                      "acceptanceReceipt":"owning immutable receipt", "files":{
                          ext:{"version":"0.32.1-20261104.120000-1", "sha256":bill.hashlib.sha256(b"accepted").hexdigest()}
                          for ext in ["pom", "jar"]}}
        self.manifest = {"members":{"agent-client-core":self.offer}}

    def test_exact_full_bill_accepted(self):
        self.assertEqual(bill.validate(self.manifest, self.selected), self.manifest["members"])

    def test_incomplete_extra_and_unaccepted_bills_rejected(self):
        for mutation in (lambda m:m["members"].clear(),
                         lambda m:m["members"].update(extra=self.offer),
                         lambda m:m["members"]["agent-client-core"].update(sourceSha="main"),
                         lambda m:m["members"]["agent-client-core"].update(acceptanceReceipt=""),
                         lambda m:m["members"]["agent-client-core"]["files"].pop("pom"),
                         lambda m:m["members"]["agent-client-core"]["files"]["jar"].update(version="0.32.1-SNAPSHOT")):
            bad = copy.deepcopy(self.manifest); mutation(bad)
            with self.assertRaises(ValueError): bill.validate(bad, self.selected)

    def metadata(self, version="0.32.1-20261104.120000-1"):
        return ("<metadata><versioning><snapshotVersions>" + "".join(
            f"<snapshotVersion><extension>{e}</extension><value>{version}</value></snapshotVersion>"
            for e in ["pom", "jar"]) + "</snapshotVersions></versioning></metadata>").encode()

    def test_remote_exact_and_stale_source_metadata_or_bytes(self):
        members = self.manifest["members"]
        with patch.object(bill.subprocess, "check_output", return_value="a"*40+"\trefs/heads/main\n"):
            with patch.object(bill, "download", side_effect=[self.metadata(), b"accepted", b"accepted"]):
                bill.verify_remote(members)
            for responses in ([self.metadata("0.32.1-20261104.130000-2")], [self.metadata(), b"different"]):
                with patch.object(bill, "download", side_effect=responses), self.assertRaises(ValueError):
                    bill.verify_remote(members)
        with patch.object(bill.subprocess, "check_output", return_value="b"*40+"\trefs/heads/main\n"), self.assertRaises(ValueError):
            bill.verify_remote(members)

    def test_complete_current_source_selection(self):
        version, selected = bill.selection(bill.ROOT / "pom.xml")
        self.assertEqual(version, "1.22.0-SNAPSHOT")
        self.assertEqual(len(selected), 76)
        self.assertEqual(selected["agent-journal-parent"]["type"], "pom")
        self.assertNotIn("journal-core", selected)

    def test_consumed_bytes_and_remote_origins_are_mandatory(self):
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            directory = repository / "io/github/markpollack/agent-client-core/0.32.1-SNAPSHOT"
            directory.mkdir(parents=True)
            prefix = "agent-client-core-0.32.1-SNAPSHOT"
            for ext in ("pom", "jar"): (directory / f"{prefix}.{ext}").write_bytes(b"accepted")
            timestamped = "agent-client-core-0.32.1-20261104.120000-1"
            for ext in ("pom", "jar"): (directory / f"{timestamped}.{ext}").write_bytes(b"accepted")
            (directory / "maven-metadata-central-snapshots.xml").write_bytes(self.metadata())
            origins = directory / "_remote.repositories"
            # Real Maven 3.9.10 remote layout uses timestamped keys; local installs use base keys.
            origins.write_text("".join(f"{timestamped}.{ext}>central-snapshots=\n" for ext in ("pom", "jar")))
            bill.verify_consumed(self.manifest["members"], repository)
            (directory / f"{prefix}.jar").write_bytes(b"stale")
            with self.assertRaises(ValueError): bill.verify_consumed(self.manifest["members"], repository)
            (directory / f"{prefix}.jar").write_bytes(b"accepted")
            origins.write_text("".join(f"{prefix}.{ext}>=\n" for ext in ("pom", "jar")))
            with self.assertRaises(ValueError): bill.verify_consumed(self.manifest["members"], repository)


if __name__ == "__main__": unittest.main()
