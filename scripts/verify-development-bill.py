#!/usr/bin/env python3
"""Verify reviewed accepted-main offers against the complete selected remote snapshot bill.

No credentials, local Maven artifacts, installs, or repository overrides are read.
The manifest is a reviewed input, not an automatically inferred source acceptance.
"""
import argparse
import hashlib
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {"m": "http://maven.apache.org/POM/4.0.0"}
REMOTE = "https://central.sonatype.com/repository/maven-snapshots"
OWNERS = {
    "agent-client.version": "agent-client",
    "agent-journal.version": "agent-journal",
    "agent-workflow.version": "agent-workflow",
    "agent-judge.version": "agent-judge",
    "agent-sandbox.version": "agent-sandbox",
    "agent-experiment.version": "agent-experiment",
    "claude-agent-sdk-java.version": "claude-agent-sdk-java",
}


def selection(pom):
    root = ET.parse(pom).getroot()
    props = {e.tag.split("}")[-1]: e.text for e in root.find("m:properties", NS)}
    selected = {}
    for d in root.findall("m:dependencyManagement/m:dependencies/m:dependency", NS):
        value = d.findtext("m:version", namespaces=NS)
        prop = value[2:-1] if value and value.startswith("${") else None
        version = props.get(prop, value)
        if not version.endswith("-SNAPSHOT"):
            continue
        if prop not in OWNERS or d.findtext("m:groupId", namespaces=NS) != "io.github.markpollack":
            raise ValueError("Unmapped snapshot member: source ownership must be reviewed")
        artifact = d.findtext("m:artifactId", namespaces=NS)
        if artifact in selected:
            raise ValueError(f"Duplicate managed member: {artifact}")
        selected[artifact] = {"version": version, "type": d.findtext("m:type", "jar", NS),
                              "sourceRepository": OWNERS[prop]}
    if not selected:
        raise ValueError("No selected development members")
    return root.findtext("m:version", namespaces=NS), selected


def validate(manifest, selected):
    members = manifest["members"]
    if set(members) != set(selected):
        raise ValueError(f"Accepted bill differs: missing={sorted(set(selected)-set(members))}; "
                         f"extra={sorted(set(members)-set(selected))}")
    for artifact, expected in selected.items():
        offer = members[artifact]
        for key in ("version", "sourceRepository"):
            if offer[key] != expected[key]:
                raise ValueError(f"{artifact}: wrong {key}")
        if not re.fullmatch(r"[0-9a-f]{40}", offer["sourceSha"]):
            raise ValueError(f"{artifact}: exact accepted-main source SHA required")
        if not offer.get("acceptanceReceipt"):
            raise ValueError(f"{artifact}: owning acceptance receipt required")
        extensions = {"pom"} if expected["type"] == "pom" else {"pom", "jar"}
        if set(offer["files"]) != extensions:
            raise ValueError(f"{artifact}: incomplete POM/JAR bill")
        for file in offer["files"].values():
            pattern = re.escape(expected["version"][:-9]) + r"-\d{8}\.\d{6}-\d+"
            if not re.fullmatch(pattern, file["version"]) or not re.fullmatch(r"[0-9a-f]{64}", file["sha256"]):
                raise ValueError(f"{artifact}: exact timestamped coordinate and SHA256 required")
    return members


def download(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def verify_remote(members):
    checked = set()
    for artifact, offer in sorted(members.items()):
        source = (offer["sourceRepository"], offer["sourceSha"])
        if source not in checked:
            refs = subprocess.check_output(["git", "ls-remote", "--exit-code",
                f"https://github.com/markpollack/{source[0]}.git", "refs/heads/main"], text=True)
            if refs.split()[0] != source[1]:
                raise ValueError(f"{source[0]}: accepted source is not current remote main")
            checked.add(source)
        base = f"{REMOTE}/io/github/markpollack/{artifact}/{offer['version']}"
        metadata = ET.fromstring(download(f"{base}/maven-metadata.xml"))
        for extension, file in offer["files"].items():
            versions = [v.findtext("value") for v in metadata.findall("versioning/snapshotVersions/snapshotVersion")
                        if v.findtext("extension") == extension and not v.findtext("classifier")]
            if versions != [file["version"]]:
                raise ValueError(f"{artifact}:{extension}: latest remote snapshot differs from accepted offer")
            data = download(f"{base}/{artifact}-{file['version']}.{extension}")
            if hashlib.sha256(data).hexdigest() != file["sha256"]:
                raise ValueError(f"{artifact}:{extension}: remote bytes differ from accepted offer")


def verify_consumed(members, repository, bom_version=None, bom_proof=None):
    """Tie the actual Maven consumer files and repository provenance to accepted bytes."""
    expected = [(artifact, offer["version"], extension, file["version"], file["sha256"])
                for artifact, offer in members.items() for extension, file in offer["files"].items()]
    if bom_version:
        expected.append(("agentworks-bom", bom_version, "pom", bom_proof["version"], bom_proof["sha256"]))
    for artifact, version, extension, timestamped, digest in expected:
        directory = repository / "io/github/markpollack" / artifact / version
        filename = f"{artifact}-{version}.{extension}"
        if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != digest:
            raise ValueError(f"{artifact}:{extension}: Maven consumed different bytes")
        remote_filename = f"{artifact}-{timestamped}.{extension}"
        if hashlib.sha256((directory / remote_filename).read_bytes()).hexdigest() != digest:
            raise ValueError(f"{artifact}:{extension}: Maven timestamped artifact differs")
        metadata = ET.parse(directory / "maven-metadata-central-snapshots.xml").getroot()
        versions = [v.findtext("value") for v in metadata.findall("versioning/snapshotVersions/snapshotVersion")
                    if v.findtext("extension") == extension and not v.findtext("classifier")]
        if versions != [timestamped]:
            raise ValueError(f"{artifact}:{extension}: Maven resolved a different timestamp")
        origins = [line.split(">", 1)[1].split("=", 1)[0]
                   for line in (directory / "_remote.repositories").read_text().splitlines()
                   if line.startswith(remote_filename + ">") or line.startswith(filename + ">")]
        if origins != ["central-snapshots"]:
            raise ValueError(f"{artifact}:{extension}: unexpected Maven origins {origins}")


def consumer(version, selected, path):
    root = ET.Element("project", xmlns=NS["m"])
    def add(parent, name, text):
        ET.SubElement(parent, name).text = text
    for k, v in {"modelVersion":"4.0.0", "groupId":"io.github.markpollack",
                 "artifactId":"development-bill-consumer", "version":"1"}.items():
        add(root, k, v)
    repository = ET.SubElement(ET.SubElement(root, "repositories"), "repository")
    add(repository, "id", "central-snapshots"); add(repository, "url", REMOTE)
    deps = ET.SubElement(ET.SubElement(root, "dependencyManagement"), "dependencies")
    bom = ET.SubElement(deps, "dependency")
    for k, v in {"groupId":"io.github.markpollack", "artifactId":"agentworks-bom",
                 "version":version, "type":"pom", "scope":"import"}.items(): add(bom, k, v)
    deps = ET.SubElement(root, "dependencies")
    for artifact, member in sorted(selected.items()):
        d = ET.SubElement(deps, "dependency")
        for k, v in {"groupId":"io.github.markpollack", "artifactId":artifact,
                     "type":member["type"]}.items(): add(d, k, v)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "development/accepted-members.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--consumer-pom", type=Path)
    parser.add_argument("--maven-repository", type=Path)
    parser.add_argument("--published-bom-proof", type=Path)
    args = parser.parse_args()
    version, selected = selection(ROOT / "pom.xml")
    if not version.endswith("-SNAPSHOT"):
        raise ValueError("Development publication requires a SNAPSHOT BOM")
    members = validate(json.loads(args.manifest.read_text()), selected)
    verify_remote(members)
    if args.published_bom_proof and not args.maven_repository:
        raise ValueError("Published BOM verification requires the consumed Maven repository")
    proof = json.loads(args.published_bom_proof.read_text()) if args.published_bom_proof else None
    if proof and proof["sha256"] != hashlib.sha256((ROOT / "pom.xml").read_bytes()).hexdigest():
        raise ValueError("Published BOM proof differs from reviewed source POM")
    if args.maven_repository:
        verify_consumed(members, args.maven_repository, version if proof else None, proof)
    args.output.write_text(json.dumps({"verifiedAt":datetime.now(timezone.utc).isoformat(),
        "bomVersion":version, "members":members,
        "consumedRepository":str(args.maven_repository) if args.maven_repository else None,
        "publishedBomVerified":bool(proof)}, indent=2) + "\n")
    if args.consumer_pom:
        consumer(version, selected, args.consumer_pom)
    print(f"Verified {len(members)} accepted-main remote snapshot members")


if __name__ == "__main__":
    main()
