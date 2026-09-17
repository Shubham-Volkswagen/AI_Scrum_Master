from __future__ import annotations
import pandas as pd
from .capacity_service import adjusted_sprints
from .dependency_service import analyze_dependencies

LAYER_ORDER = {"Infrastructure": 1, "Identity": 2, "Data": 3, "Backend": 4, "Integrations": 5, "Frontend": 6, "QA": 7, "Security": 8, "Release": 9}
PRIORITY_ORDER = {"Highest": 1, "High": 2, "Medium": 3, "Low": 4}

def plan_sprints(data, configurable_count=None):
    backlog = data["Backlog"].copy()
    dep = analyze_dependencies(backlog, data["Dependencies"])
    if dep["cycles"]:
        raise ValueError(f"Cannot plan until dependency cycles are resolved: {dep['cycles']}")
    sprints = adjusted_sprints(data)
    sprints = sprints[sprints["Status"].isin(["Planned"])].copy()
    if configurable_count:
        sprints = sprints.head(int(configurable_count))
    remaining = dict(zip(sprints["SprintID"].astype(str), sprints["AvailablePts"].astype(float)))
    candidates = backlog[(backlog["Type"].isin(["Story", "Task", "Bug"])) & (~backlog["Status"].isin(["Done"])) & (backlog["SprintID"].isna())].copy()
    candidates["StoryPoints"] = pd.to_numeric(candidates["StoryPoints"], errors="coerce").fillna(0)
    candidates = candidates[candidates["StoryPoints"] > 0]
    candidates["rank"] = candidates["TicketID"].astype(str).map(dep["rank"]).fillna(10**9)
    candidates["layer_rank"] = candidates["Layer"].map(LAYER_ORDER).fillna(99)
    candidates["priority_rank"] = candidates["Priority"].map(PRIORITY_ORDER).fillna(99)
    candidates = candidates.sort_values(["rank", "layer_rank", "priority_rank", "TicketID"])
    assigned_sprint = {}
    rows, unresolved = [], []
    prereqs = {}
    for prereq, child in dep["graph"].edges():
        prereqs.setdefault(child, []).append(prereq)
    for _, row in candidates.iterrows():
        tid, pts = str(row["TicketID"]), float(row["StoryPoints"])
        earliest = 0
        for p in prereqs.get(tid, []):
            if p in assigned_sprint:
                earliest = max(earliest, list(remaining).index(assigned_sprint[p]))
        placed = False
        for idx, sid in enumerate(remaining):
            if idx >= earliest and remaining[sid] >= pts:
                before = remaining[sid]
                remaining[sid] -= pts
                assigned_sprint[tid] = sid
                rows.append({"TicketID": tid, "Title": row["Title"], "StoryPoints": pts, "SprintID": sid, "CapacityBefore": before, "CapacityAfter": remaining[sid], "PlacementReason": f"Dependency-safe rank {int(row['rank'])}; layer {row['Layer']}; priority {row['Priority']}"})
                placed = True
                break
        if not placed:
            unresolved.append({"TicketID": tid, "Title": row["Title"], "StoryPoints": pts, "Reason": "No remaining dependency-safe sprint capacity"})
    return pd.DataFrame(rows), pd.DataFrame(unresolved), sprints
