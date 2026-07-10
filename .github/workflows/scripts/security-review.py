#!/usr/bin/env python3
"""Security review - Docker, K8s, Terraform, CI/CD patterns."""
import json, sys, re
from pathlib import Path

def review_file(path: str, content: str) -> list:
    findings = []
    ext = Path(path).suffix.lower()
    name = Path(path).name.lower()

    # Docker checks
    if ext in (".dockerfile",) or name == "dockerfile" or "docker-compose" in name:
        if re.search(r'FROM\s+\S+', content) and not re.search(r'FROM\s+\S+@sha256:', content):
            findings.append({"severity": "medium", "category": "security",
                             "file": path, "message": "Unpinned base image -- use digest pinning (@sha256:...)"})
        if re.search(r'USER\s+root\b', content, re.I):
            findings.append({"severity": "high", "category": "security",
                             "file": path, "message": "Container runs as root -- add runAsNonRoot: true + USER nonroot"})
        if re.search(r'ENV\s+(?:\w*(SECRET|KEY|PASSWORD|TOKEN|API_KEY)\w*)\s*=', content, re.I):
            findings.append({"severity": "critical", "category": "security",
                             "file": path, "message": "Secrets in ENV -- use docker secrets or --secret flag"})
        if re.search(r'ADD\s+', content) and not re.search(r'ADD\s+.*\.(tar|gz|bz2|xz)', content):
            findings.append({"severity": "low", "category": "security",
                             "file": path, "message": "Prefer COPY over ADD for local files"})

    # Kubernetes checks
    if ext in (".yaml", ".yml") and any(k in content for k in ["kind: Deployment", "kind: Pod", "kind: StatefulSet", "apiVersion: apps"]):
        if "securityContext" not in content:
            findings.append({"severity": "medium", "category": "security",
                             "file": path, "message": "Missing securityContext on pod/deployment spec"})
        if "runAsNonRoot" not in content:
            findings.append({"severity": "high", "category": "security",
                             "file": path, "message": "Missing runAsNonRoot: true in securityContext"})
        if "allowPrivilegeEscalation: false" not in content:
            findings.append({"severity": "high", "category": "security",
                             "file": path, "message": "Missing allowPrivilegeEscalation: false"})
        if "readOnlyRootFilesystem: true" not in content:
            findings.append({"severity": "medium", "category": "security",
                             "file": path, "message": "Missing readOnlyRootFilesystem: true"})
        if re.search(r'capabilities:\s*\n\s+add:\s*\[\s*ALL\s*\]', content):
            findings.append({"severity": "critical", "category": "security",
                             "file": path, "message": "Container granted ALL capabilities -- drop all and add only needed"})

    # Terraform checks
    if ext == ".tf":
        if "backend" not in content:
            findings.append({"severity": "high", "category": "security",
                             "file": path, "message": "No Terraform backend configured -- state not remote/encrypted"})
        if re.search(r'(?:password|secret|private_key|token|api_key)\s*=\s*["\'][^"\']+["\']', content, re.I):
            findings.append({"severity": "critical", "category": "security",
                             "file": path, "message": "Possible hardcoded secret in Terraform -- use variables + sensitive"})

    # CI/CD checks
    if ".github/workflows" in path or (ext == ".yml" and "name:" in content and "on:" in content):
        if re.search(r'pull_request_target', content):
            findings.append({"severity": "high", "category": "security",
                             "file": path, "message": "pull_request_target used -- ensure no checkout of PR code in untrusted context"})
        if re.search(r'github\.event.*\b(run:|run:\s*\|)', content):
            findings.append({"severity": "critical", "category": "security",
                             "file": path, "message": "Possible script injection -- avoid ${{ github.event.* }} in run: steps"})

    return findings

def main():
    changed_files = sys.argv[1:]
    all_findings = []
    for fp in changed_files:
        try:
            content = Path(fp).read_text()
            all_findings.extend(review_file(fp, content))
        except FileNotFoundError:
            all_findings.append({"severity": "warning", "category": "security",
                                 "file": fp, "message": "File not found for review"})
    print(json.dumps({"status": "completed", "findings": all_findings, "count": len(all_findings)}))

if __name__ == "__main__":
    main()
