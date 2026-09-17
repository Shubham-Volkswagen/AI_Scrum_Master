from __future__ import annotations
import pandas as pd

def adjusted_sprints(data):
    sprints = data["Sprints"].copy()
    holidays = data["Holidays"].copy()
    rows = []
    for _, sprint in sprints.iterrows():
        matches = holidays[(holidays["ImpactedTeamID"] == sprint["TeamID"]) & (holidays["Date"] >= sprint["StartDate"]) & (holidays["Date"] <= sprint["EndDate"])]
        nominal = max(float(sprint["WorkingDays"]), 1.0)
        effective = max(nominal - len(matches), 0.0)
        adjusted = float(sprint["PlannedCapacityPts"]) * effective / nominal
        row = sprint.to_dict()
        row.update({"HolidayCount": len(matches), "EffectiveWorkingDays": effective, "AdjustedCapacityPts": round(adjusted, 2), "AvailablePts": round(max(adjusted - float(sprint["CommittedPts"]), 0), 2)})
        rows.append(row)
    return pd.DataFrame(rows)

def allocation_issues(data):
    members = data["TeamMembers"]
    return members[members["AllocationPct"] > 100].copy()
