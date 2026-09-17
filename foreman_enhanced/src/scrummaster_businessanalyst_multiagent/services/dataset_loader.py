from __future__ import annotations
import pandas as pd

REQUIRED = {
    "Teams": ["TeamID", "BaseVelocityPts"],
    "TeamMembers": ["MemberID", "TeamID", "AllocationPct"],
    "Sprints": ["SprintID", "TeamID", "StartDate", "EndDate", "WorkingDays", "PlannedCapacityPts", "CommittedPts", "Status"],
    "Holidays": ["Date", "ImpactedTeamID"],
    "SAD_Sections": ["SectionID"],
    "Backlog": ["TicketID", "Type", "Title", "ParentID", "SADSectionID", "StoryPoints", "SprintID", "HasAcceptanceCriteria", "HasDoD"],
    "Dependencies": ["FromTicketID", "ToTicketID (depends on)"],
    "ChangeRequests": ["CRID", "RawText"]
}

def load_workbook(source):
    book = pd.read_excel(source, sheet_name=None, engine="openpyxl")
    result = {}
    for sheet, cols in REQUIRED.items():
        if sheet not in book:
            raise ValueError(f"Required sheet missing: {sheet}")
        df = book[sheet].copy()
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise ValueError(f"{sheet} missing columns: {missing}")
        result[sheet] = df
    for name in ("Sprints", "Holidays"):
        for col in [c for c in result[name].columns if "Date" in c]:
            result[name][col] = pd.to_datetime(result[name][col], errors="coerce")
    return result
