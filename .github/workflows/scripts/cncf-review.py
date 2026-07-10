#!/usr/bin/env python3
"""CNCF / Cloud Native best practices review."""
import json, sys, re
from pathlib import Path

def review_file(path: str, content: str) -> list:
    findings = []
    ext = Path(path).suffix.lower()

    if ext not in (".yaml", ".yml"):
        return findings

    # Resource limits
    if re.search(r'kind:\s*(Deployment|StatefulSet|DaemonSet|Job|Pod)', content):
        if "resources:" not in content:
            findings.append({"severity": "high", "category": "cncf",
                             "file": path, "message": "Missing resource limits/requests -- required by CNCF best practices"})
        elif "limits:" not in content:
            findings.append({"severity": "medium", "category": "cncf",
                             "file": path, "message": "resources defined but no limits -- set both requests and limits"})

    # Probes
    has_container = "containers:" in content
    has_liveness = "livenessProbe:" in content
    has_readiness = "readinessProbe:" in content
    has_startup = "startupProbe:" in content

    if has_container and not has_liveness and not has_startup:
        findings.append({"severity": "medium", "category": "cncf",
                         "file": path, "message": "No liveness/startup probe -- pod won't auto-restart on deadlock"})
    if has_container and not has_readiness:
        findings.append({"severity": "medium", "category": "cncf",
                         "file": path, "message": "No readiness probe -- traffic may route to unready pods"})

    # Graceful shutdown
    if "preStop:" not in content and ("kind: Deployment" in content or "kind: StatefulSet" in content):
        findings.append({"severity": "low", "category": "cncf",
                         "file": path, "message": "No preStop hook -- connections may drop on shutdown"})

    # Recommended labels
    has_labels = any(k in content for k in [
        "app.kubernetes.io/name", "app.kubernetes.io/instance",
        "app.kubernetes.io/version", "app.kubernetes.io/managed-by"
    ])
    if "kind: Deployment" in content and not has_labels:
        findings.append({"severity": "low", "category": "cncf",
                         "file": path, "message": "Missing recommended k8s labels (app.kubernetes.io/*)"})

    # PodDisruptionBudget
    if "kind: Deployment" in content and "PodDisruptionBudget" not in content:
        findings.append({"severity": "low", "category": "cncf",
                         "file": path, "message": "No PodDisruptionBudget for HA workloads"})

    # Topology spread
    if "kind: Deployment" in content and "topologySpreadConstraints" not in content:
        findings.append({"severity": "low", "category": "cncf",
                         "file": path, "message": "No topologySpreadConstraints -- pods may colocate on same node"})

    # Literal env values
    if re.search(r'env:\s*\n\s+-\s+name:\s+\w+\s*\n\s+value:\s+"', content):
        findings.append({"severity": "low", "category": "cncf",
                         "file": path, "message": "Literal env values -- consider ConfigMaps/Secrets instead"})

    return findings

def main():
    changed_files = sys.argv[1:]
    all_findings = []
    for fp in changed_files:
        try:
            content = Path(fp).read_text()
            all_findings.extend(review_file(fp, content))
        except FileNotFoundError:
            pass
    print(json.dumps({"status": "completed", "findings": all_findings, "count": len(all_findings)}))

if __name__ == "__main__":
    main()
