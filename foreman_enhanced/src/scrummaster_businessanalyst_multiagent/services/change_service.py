from __future__ import annotations
from .similarity_service import similarity

def analyze_change(raw_text, data, threshold=0.72):
    backlog = data["Backlog"]
    changes = data["ChangeRequests"]
    pool = list(backlog["Title"].fillna("").astype(str)) + list(changes["RawText"].fillna("").astype(str))
    ranked = similarity(raw_text, pool)
    best_text, score = ranked[0] if ranked else ("", 0.0)
    duplicate_id = None
    if score >= threshold:
        if best_text in set(backlog["Title"].astype(str)):
            duplicate_id = str(backlog.loc[backlog["Title"].astype(str) == best_text, "TicketID"].iloc[0])
        else:
            duplicate_id = str(changes.loc[changes["RawText"].astype(str) == best_text, "CRID"].iloc[0])
    return {"raw_text": raw_text, "duplicate_id": duplicate_id, "similarity_score": round(score, 3), "matched_text": best_text, "explanation": "Probable duplicate; human confirmation required." if duplicate_id else "No strong duplicate found. Create/refine a new item and place it only after capacity review.", "requires_human_confirmation": True}
