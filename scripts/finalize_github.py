#!/usr/bin/env python3
"""Local administrative handoff. Dry run by default; never stores or prints credentials."""
import argparse
import json
import subprocess
import sys
from urllib.parse import quote

OWNER = "Neguchads"
AUDIT = "Audit workflow security"
CHECKS = {
    "starlight-bi": ["verificar", "quality / node-quality", AUDIT, "chromium", "Analyze (javascript-typescript)"],
    "ScriptForge": ["verificar", "quality / node-quality", AUDIT, "Analyze (javascript-typescript)"],
    "favorite-manager": ["test-and-build", "quality / node-quality", AUDIT, "chromium", "Analyze (javascript-typescript)"],
    "codex-config-universal": ["validate", AUDIT, "quality / docs-quality"],
    "ccod-xbox-recomp": ["python-syntax", "quality / python-quality", AUDIT, "source-only-tests", "Analyze (c-cpp)", "Analyze (python)"],
    "csotn-saturn-recomp": ["Python 3.11", "Python 3.13", "Publication and secrets", "Native runtime", "quality / python-quality", AUDIT, "Analyze (python)", "Analyze (c-cpp)"],
    "cdos-nintendods-recomp": ["Python & Manifest (windows-latest)", "Clean-Room Guard, Shell & Patch Lint", "Python & Manifest (ubuntu-latest)", "quality / python-quality", AUDIT, "Analyze (c-cpp)", "Analyze (python)"],
    "spec-to-proof": ["validate", AUDIT, "quality / docs-quality"],
}
RULESET = "Chad - protected default branch"
RELEASE_PLANNING = ("starlight-bi", "favorite-manager")

def gh(*args, body=None):
    command = ["gh", *args]
    output = subprocess.run(command, input=None if body is None else json.dumps(body),
                            text=True, check=True, stdout=subprocess.PIPE)
    return output.stdout

def api(path, method="GET", body=None):
    args = ["api", "--method", method, "-H", "Accept: application/vnd.github+json", path]
    if body is not None:
        args += ["--input", "-"]
    response = gh(*args, body=body)
    return json.loads(response) if response.strip() else None

def policy(branch, checks, approvals):
    return {
        "name": RULESET, "target": "branch", "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["refs/heads/" + branch], "exclude": []}},
        "rules": [
            {"type": "deletion"}, {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": approvals,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": False,
                "require_last_push_approval": False,
                "required_review_thread_resolution": True,
                "allowed_merge_methods": ["squash"],
            }},
            {"type": "required_status_checks", "parameters": {
                "strict_required_status_checks_policy": True,
                "required_status_checks": checks,
            }},
        ],
    }

def prepare(name, approvals):
    root = f"repos/{OWNER}/{name}"
    repo = api(root)
    if repo.get("private") or repo.get("fork") or repo.get("archived"):
        raise RuntimeError("Repository is no longer an eligible public original")
    if not repo.get("permissions", {}).get("admin"):
        raise RuntimeError("Local account has no administrative permission")
    branch = repo["default_branch"]
    existing = api(root + "/rulesets?per_page=100")
    if existing:
        raise RuntimeError("Existing rulesets detected; review manually rather than overwrite")
    if not repo.get("allow_squash_merge"):
        raise RuntimeError("Squash merge not enabled; review settings manually")
    info = api(root + "/branches/" + quote(branch, safe=""))
    if info.get("protected"):
        raise RuntimeError("Branch already protected; do not overlap policies automatically")
    sha = info["commit"]["sha"]
    records = api(root + "/commits/" + sha + "/check-runs?per_page=100&filter=latest")["check_runs"]
    checks = []
    for context in CHECKS[name]:
        matches = [r for r in records if r["name"] == context and
                   r.get("conclusion") == "success" and r.get("app", {}).get("slug") == "github-actions"]
        if not matches:
            raise RuntimeError(f"Missing successful GitHub Actions check on {sha[:8]}: {context}")
        checks.append({"context": context, "integration_id": matches[0]["app"]["id"]})
    return root, policy(branch, checks, approvals)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-rulesets", action="store_true", help="Create active rulesets after live checks")
    parser.add_argument("--approvals", choices=(0, 1), type=int, default=0,
                        help="Independent human reviewers required; 0 for solo development")
    parser.add_argument("--enable-release-planning", action="store_true",
                        help="Set RELEASE_PLEASE_ENABLED=true only; repo Actions PR permission must already be enabled")
    parser.add_argument("--repo", action="append", choices=CHECKS, help="Limit to named repositories")
    args = parser.parse_args()
    gh("auth", "status", "--hostname", "github.com")
    login = api("user")["login"]
    if login.lower() != OWNER.lower():
        raise SystemExit("Authenticate locally as Neguchads before proceeding")
    errors = []
    for name in args.repo or list(CHECKS):
        try:
            root, payload = prepare(name, args.approvals)
            print(name, json.dumps(payload, ensure_ascii=False, indent=2))
            if args.apply_rulesets:
                created = api(root + "/rulesets", "POST", payload)
                current = api(root + "/rulesets/" + str(created["id"]))
                if current["enforcement"] != "active":
                    raise RuntimeError("Ruleset not active after creation")
                print(f"ACTIVE ruleset {created['id']}")
        except (RuntimeError, subprocess.CalledProcessError, KeyError, ValueError) as exc:
            errors.append(name)
            print(f"SKIPPED {name}: {exc}", file=sys.stderr)
    if args.enable_release_planning:
        for name in RELEASE_PLANNING:
            if args.repo and name not in args.repo:
                continue
            try:
                root = f"repos/{OWNER}/{name}"
                permissions = api(root + "/actions/permissions/workflow")
                if permissions.get("can_approve_pull_request_reviews") is not True:
                    raise RuntimeError("Enable Actions-created PRs in Settings > Actions > General first")
                gh("variable", "set", "RELEASE_PLEASE_ENABLED", "--repo", OWNER + "/" + name, "--body", "true")
                print(f"RELEASE_PLANNING enabled: {name}")
            except (RuntimeError, subprocess.CalledProcessError, KeyError, ValueError) as exc:
                errors.append(name + ":release")
                print(f"SKIPPED {name}: {exc}", file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
