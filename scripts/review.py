import os
from pathlib import Path

from lib.ai import findings_from_analysis, review_issues_with_ai
from lib.linear import fetch_active_issues
from lib.report import write_reports
from lib.state import load_history


def main():
    mode = os.environ.get("AUDIT_MODE", "manual-preview")
    out_dir = Path(os.environ.get("AUDIT_OUT_DIR", "results"))

    print("Fetching active Linear issues...")
    issues = fetch_active_issues()
    print(f"Fetched {len(issues)} active issues.")

    print("Reviewing all active issues against the local SOP with Azure OpenAI...")
    analysis = review_issues_with_ai(issues)
    findings = findings_from_analysis(issues, analysis)
    suggestion_count = len({item["issueId"] for item in findings if item.get("issueId") != "owner-summary"})
    print(f"Generated suggestions for {suggestion_count} issues.")

    print("Writing results...")
    history = load_history()
    team_summary = write_reports(out_dir, issues, findings, analysis, mode, history)

    print(team_summary)
    print(f"\nWrote results to {out_dir}")
    print(f"Analysis source: {analysis.get('source')}")
    if analysis.get("fallbackReason"):
        print(f"Fallback reason: {analysis.get('fallbackReason')}")


if __name__ == "__main__":
    main()
