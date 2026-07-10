#!/usr/bin/env python3
"""Code quality review -- error handling, debug artifacts, test coverage."""
import json, sys, re
from pathlib import Path

def review_file(path: str, content: str) -> list:
    findings = []
    ext = Path(path).suffix.lower()

    # Debug artifacts
    debug_patterns = [
        (r'(?:^|\n)\s*print\s*\(', "print() statement left in code"),
        (r'(?:^|\n)\s*console\.log\s*\(', "console.log() left in code"),
        (r'(?:^|\n)\s*debugger;?', "debugger statement left in code"),
        (r'(?:^|\n)\s*pdb\.set_trace\(\)', "pdb.set_trace() left in code"),
        (r'(?:^|\n)\s*byebug\b', "byebug left in code"),
    ]
    for pattern, msg in debug_patterns:
        if re.search(pattern, content, re.M):
            findings.append({"severity": "high", "category": "quality",
                             "file": path, "message": msg})
            break

    # TODO / FIXME / HACK
    todos = re.findall(r'\b(TODO|FIXME|HACK|XXX|WORKAROUND)\b', content)
    if todos:
        findings.append({"severity": "low", "category": "quality",
                         "file": path, "message": f"TODO/FIXME/HACK markers ({len(todos)} found) -- resolve before merge"})

    # Large files
    lines = content.split("\n")
    if len(lines) > 500:
        findings.append({"severity": "medium", "category": "quality",
                         "file": path, "message": f"Large file ({len(lines)} lines) -- consider splitting"})

    # Python error handling
    if ext == ".py":
        func_defs = re.findall(r'^def \w+', content, re.M)
        try_blocks = re.findall(r'\btry\b', content)
        if len(func_defs) > 3 and len(try_blocks) == 0:
            findings.append({"severity": "medium", "category": "quality",
                             "file": path, "message": "Multiple functions but no try/except -- add error handling"})
        bare_excepts = re.findall(r'\bexcept\s*:', content)
        if bare_excepts:
            findings.append({"severity": "high", "category": "quality",
                             "file": path, "message": "Bare 'except:' clause -- catches ALL exceptions including SystemExit"})

    # Hardcoded secrets
    secret_pat = re.compile(r'''(?:password|secret|api_key|token|private_key)\s*[:=]\s*["'][A-Za-z0-9_\-\.]{20,}["']''', re.I)
    if secret_pat.search(content):
        findings.append({"severity": "critical", "category": "quality",
                         "file": path, "message": "Possible hardcoded credential committed!"})

    # YAML indentation
    if ext in (".yaml", ".yml") and "kind: Deployment" in content:
        indents = re.findall(r'^(\s+)\S', content, re.M)
        mixed = [i for i in indents if i and len(i) % 2 != 0]
        if mixed:
            findings.append({"severity": "low", "category": "quality",
                             "file": path, "message": "Inconsistent YAML indentation -- use multiples of 2 spaces"})

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
