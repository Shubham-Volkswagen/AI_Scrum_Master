from __future__ import annotations
import pandas as pd
from .capacity_service import adjusted_sprints, allocation_issues
from .dependency_service import analyze_dependencies
from .similarity_service import similarity

def finding(category, severity, record, evidence, recommendation):
    return {"Category": category, "Severity": severity, "Record": record, "Evidence": evidence, "Recommendation": recommendation}

def run_health_checks(data):
    b = data["Backlog"].copy()
    findings = []
    ids = set(b["TicketID"].dropna().astype(str))
    sad_ids = set(data["SAD_Sections"]["SectionID"].dropna().astype(str))
    for _, r in allocation_issues(data).iterrows():
        findings.append(finding("OVER_ALLOCATION", "High", r["MemberID"], f"Allocation is {r['AllocationPct']}%", "Review and cap effective allocation at 100%."))
    for _, r in adjusted_sprints(data).iterrows():
        if float(r["CommittedPts"]) > float(r["AdjustedCapacityPts"]):
            findings.append(finding("OVER_COMMITTED_SPRINT", "High", r["SprintID"], f"Committed {r['CommittedPts']} vs adjusted capacity {r['AdjustedCapacityPts']}", "Rebalance unstarted work after human approval."))
        if r["HolidayCount"] and float(r["PlannedCapacityPts"]) == float(data["Sprints"].loc[data["Sprints"]["SprintID"] == r["SprintID"], "PlannedCapacityPts"].iloc[0]):
            findings.append(finding("HOLIDAY_CAPACITY_IMPACT", "Medium", r["SprintID"], f"{r['HolidayCount']} holiday(s) occur within the sprint", "Use holiday-adjusted capacity for forecast."))
    work = b[b["Type"].isin(["Story", "Task", "Bug"])]
    for _, r in work[pd.to_numeric(work["StoryPoints"], errors="coerce").fillna(0) <= 0].iterrows():
        findings.append(finding("ZERO_ESTIMATE", "High", r["TicketID"], "Story points are zero or blank", "Estimate before sprint commitment."))
    for _, r in b.iterrows():
        parent = r.get("ParentID")
        if pd.notna(parent) and str(parent).strip() and str(parent) not in ids:
            findings.append(finding("ORPHAN_PARENT", "High", r["TicketID"], f"Parent {parent} does not exist", "Repair the parent link."))
        sad = r.get("SADSectionID")
        if pd.notna(sad) and str(sad).strip() and str(sad) not in sad_ids:
            findings.append(finding("INVALID_SAD_REFERENCE", "High", r["TicketID"], f"S-AD section {sad} does not exist", "Map to a valid S-AD section or remove unapproved scope."))
        if r.get("HasAcceptanceCriteria") == "N":
            findings.append(finding("MISSING_ACCEPTANCE_CRITERIA", "Medium", r["TicketID"], "Acceptance criteria flag is N", "Refine before commitment."))
        if r.get("HasDoD") == "N":
            findings.append(finding("MISSING_DOD", "Medium", r["TicketID"], "Definition of Done flag is N", "Add Definition of Done."))
    dep = analyze_dependencies(b, data["Dependencies"])
    for e in dep["orphan_edges"]:
        findings.append(finding("ORPHAN_DEPENDENCY", "High", e["dependent"], f"Dependency references missing ticket {e['prerequisite']}", "Repair or remove the dependency edge."))
    for cycle in dep["cycles"]:
        findings.append(finding("DEPENDENCY_CYCLE", "Critical", " -> ".join(cycle), "Circular dependency prevents valid sequencing", "Break the cycle through human review."))
    sprint_num = {str(x): i for i, x in enumerate(data["Sprints"]["SprintID"].astype(str), 1)}
    sprint_by_ticket = dict(zip(b["TicketID"].astype(str), b["SprintID"].astype(str)))
    for _, r in data["Dependencies"].iterrows():
        a, p = str(r["FromTicketID"]), str(r["ToTicketID (depends on)"])
        if a in sprint_by_ticket and p in sprint_by_ticket and sprint_by_ticket[a] in sprint_num and sprint_by_ticket[p] in sprint_num and sprint_num[sprint_by_ticket[a]] < sprint_num[sprint_by_ticket[p]]:
            findings.append(finding("DEPENDENCY_INVERSION", "High", a, f"Scheduled before prerequisite {p}", "Move only after human approval."))
    titles = list(b["Title"].fillna("").astype(str))
    for i, title in enumerate(titles):
        candidates = titles[i+1:]
        if candidates:
            best = similarity(title, candidates)[0]
            if best[1] >= 0.82:
                other = b.iloc[i+1+candidates.index(best[0])]["TicketID"]
                findings.append(finding("POSSIBLE_DUPLICATE", "Medium", b.iloc[i]["TicketID"], f"Similar to {other}; score {best[1]:.2f}", "Confirm whether to merge."))
    return pd.DataFrame(findings), adjusted_sprints(data), dep
