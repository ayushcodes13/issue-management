import os
from pathlib import Path

from lib.checks import run_checks
from lib.ai import analyze_flagged_issues
from lib.linear import fetch_active_issues
from lib.report import write_reports


def main():
    mode = os.environ.get("AUDIT_MODE", "manual-preview")
    out_dir = Path(os.environ.get("AUDIT_OUT_DIR", "results"))

    print("Fetching active Linear issues...")
    issues = fetch_active_issues()
    print(f"Fetched {len(issues)} active issues.")

    print("Running deterministic hygiene checks...")
    findings = run_checks(issues)
    flagged_issue_count = len({item["issueId"] for item in findings if item.get("issueId") != "owner-summary"})
    print(f"Flagged {flagged_issue_count} issues for review.")

    print("Generating suggestions...")
    analysis = analyze_flagged_issues(issues, findings)

    print("Writing results...")
    team_summary = write_reports(out_dir, issues, findings, analysis, mode)

    print(team_summary)
    print(f"\nWrote results to {out_dir}")
    print(f"Analysis source: {analysis.get('source')}")
    if analysis.get("fallbackReason"):
        print(f"Fallback reason: {analysis.get('fallbackReason')}")


if __name__ == "__main__":
    main()
