#!/usr/bin/env python3
"""Bounded remote proof of this run's exact POM upload, without Maven installation."""
import argparse
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


def deployment_url(log, base, version):
    pattern = re.escape(base + "/agentworks-bom-" + version[:-9]) + r"-\d{8}\.\d{6}-\d+\.pom"
    uploaded = re.findall(r"Uploaded to central: (" + pattern + r")\s", log)
    if len(uploaded) != 1:
        raise ValueError("Deploy log must identify exactly one successful timestamped BOM POM upload")
    return uploaded[0]


def verify_candidate(metadata, base, deployed_url, expected, download):
    snapshots = [e.findtext("value") for e in metadata.findall("versioning/snapshotVersions/snapshotVersion")
                 if e.findtext("extension") == "pom" and not e.findtext("classifier")]
    if len(snapshots) != 1:
        raise ValueError("Missing or ambiguous remote BOM POM")
    url = f"{base}/agentworks-bom-{snapshots[0]}.pom"
    if url != deployed_url:
        raise ValueError("Latest remote coordinate is not this workflow's successful deployment")
    digest = hashlib.sha256(download(url)).hexdigest()
    if digest != expected:
        raise ValueError("Published BOM bytes differ from this reviewed source POM")
    return {"url":url, "version":snapshots[0], "sha256":digest}


def download(url):
    with urllib.request.urlopen(url, timeout=15) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deploy-log", type=Path, required=True)
    args = parser.parse_args()
    pom = Path(__file__).resolve().parent.parent / "pom.xml"
    version = ET.parse(pom).getroot().findtext("{http://maven.apache.org/POM/4.0.0}version")
    if not version.endswith("-SNAPSHOT"):
        raise ValueError("Expected a development SNAPSHOT")
    expected = hashlib.sha256(pom.read_bytes()).hexdigest()
    base = f"https://central.sonatype.com/repository/maven-snapshots/io/github/markpollack/agentworks-bom/{version}"
    deployed_url = deployment_url(args.deploy_log.read_text(), base, version)
    for attempt in range(20):
        try:
            metadata = ET.fromstring(download(f"{base}/maven-metadata.xml"))
            proof = verify_candidate(metadata, base, deployed_url, expected, download)
            run = os.environ.get("GITHUB_RUN_ID")
            repository = os.environ.get("GITHUB_REPOSITORY")
            proof.update(sourceSha=os.environ.get("GITHUB_SHA"), workflowRun=run,
                         workflowAttempt=os.environ.get("GITHUB_RUN_ATTEMPT"),
                         workflowUrl=f"https://github.com/{repository}/actions/runs/{run}")
            args.output.write_text(json.dumps(proof, indent=2)+"\n")
            print(f"Published exact BOM: {deployed_url} SHA256 {expected}")
            return
        except (urllib.error.URLError, ValueError):
            pass
        if attempt == 19:
            raise SystemExit("Exact deployed BOM was not visible within the bounded polling window")
        time.sleep(15)


if __name__ == "__main__":
    main()
