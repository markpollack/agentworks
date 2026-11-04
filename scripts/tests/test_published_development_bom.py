import hashlib
import importlib.util
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock

script = Path(__file__).resolve().parents[1] / "verify-published-development-bom.py"
spec = importlib.util.spec_from_file_location("published", script)
published = importlib.util.module_from_spec(spec)
spec.loader.exec_module(published)


class PublishedBomTest(unittest.TestCase):
    base = "https://central.sonatype.com/repository/maven-snapshots/io/github/markpollack/agentworks-bom/1.22.0-SNAPSHOT"
    timestamp = "1.22.0-20261104.210000-7"

    def setUp(self):
        self.url = self.base + "/agentworks-bom-" + self.timestamp + ".pom"
        self.log = f"[INFO] Uploaded to central: {self.url} (38 kB at 30 kB/s)\n"
        self.digest = hashlib.sha256(b"reviewed").hexdigest()

    def metadata(self, version):
        return ET.fromstring(f"<metadata><versioning><snapshotVersions><snapshotVersion>"
            f"<extension>pom</extension><value>{version}</value></snapshotVersion>"
            f"</snapshotVersions></versioning></metadata>")

    def test_successful_upload_coordinate_is_required(self):
        self.assertEqual(published.deployment_url(self.log, self.base, "1.22.0-SNAPSHOT"), self.url)
        for log in ("", self.log.replace("Uploaded", "Uploading"), self.log+self.log):
            with self.assertRaises(ValueError): published.deployment_url(log, self.base, "1.22.0-SNAPSHOT")

    def test_old_identical_deployment_and_wrong_bytes_are_rejected(self):
        fetch = Mock(return_value=b"reviewed")
        with self.assertRaises(ValueError):
            published.verify_candidate(self.metadata("1.22.0-20261104.200000-6"), self.base, self.url, self.digest, fetch)
        fetch.assert_not_called()
        proof = published.verify_candidate(self.metadata(self.timestamp), self.base, self.url, self.digest, fetch)
        self.assertEqual(proof["sha256"], self.digest)
        with self.assertRaises(ValueError):
            published.verify_candidate(self.metadata(self.timestamp), self.base, self.url, self.digest, lambda _:b"wrong")


if __name__ == "__main__": unittest.main()
