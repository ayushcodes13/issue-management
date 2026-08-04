import os
from pathlib import Path

from lib.checks import run_checks
from lib.linear_client import fetch_active_issues
from lib.openai_analysis import analyze_flagged_issues
from lib.reports import write_reports


def main():
    mode = os.environ.get("AUDIT_MODE", "manual-preview")
    out_dir = Path(os.environ.get("AUDIT_OUT_DIR", "results"))

    issues = fetch_active_issues()
    findings = run_checks(issues)
    analysis = analyze_flagged_issues(issues, findings)
    team_summary = write_reports(out_dir, issues, findings, analysis, mode)

    print(team_summary)
    print(f"\nWrote artifacts to {out_dir}")
    print(f"Analysis source: {analysis.get('source')}")
    if analysis.get("fallbackReason"):
        print(f"Fallback reason: {analysis.get('fallbackReason')}")


if __name__ == "__main__":
    main()
