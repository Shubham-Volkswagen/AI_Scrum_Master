from __future__ import annotations
import os, requests
from requests.auth import HTTPBasicAuth

def _adf(text):
    return {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": str(text)[:32000]}]}]}

def raw_create_jira_ticket(summary, description, issue_type, parent_key=None, story_points=None):
    domain = os.getenv("JIRA_DOMAIN", "").rstrip("/")
    auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))
    fields = {"project": {"key": os.getenv("JIRA_PROJECT_KEY")}, "summary": summary, "description": _adf(description), "issuetype": {"name": issue_type}}
    if parent_key:
        fields["parent"] = {"key": parent_key}
    response = requests.post(f"{domain}/rest/api/3/issue", json={"fields": fields}, headers={"Accept": "application/json", "Content-Type": "application/json"}, auth=auth, timeout=30)
    if response.status_code == 201:
        return {"ok": True, "key": response.json().get("key"), "status": 201}
    return {"ok": False, "status": response.status_code, "error": response.text}

def create_issue_link(inward_key, outward_key, link_type="Blocks"):
    domain = os.getenv("JIRA_DOMAIN", "").rstrip("/")
    auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))
    payload = {"type": {"name": link_type}, "inwardIssue": {"key": inward_key}, "outwardIssue": {"key": outward_key}}
    r = requests.post(f"{domain}/rest/api/3/issueLink", json=payload, headers={"Accept": "application/json", "Content-Type": "application/json"}, auth=auth, timeout=30)
    return {"ok": r.status_code in (200, 201, 204), "status": r.status_code, "error": "" if r.status_code in (200, 201, 204) else r.text}

def publish_backlog(items):
    key_map, results = {}, []
    type_order = {"Epic": 0, "Feature": 1, "Story": 2, "Task": 2, "Bug": 2}
    for item in sorted(items, key=lambda x: type_order.get(x.get("issue_type"), 9)):
        parent = key_map.get(item.get("parent_local_id"))
        description = item.get("description", "") + "\n\nAcceptance Criteria:\n" + "\n".join(item.get("acceptance_criteria", [])) + "\n\nDefinition of Done:\n" + "\n".join(item.get("definition_of_done", []))
        result = raw_create_jira_ticket(item["summary"], description, item["issue_type"], parent, item.get("story_points"))
        results.append({"local_id": item["local_id"], **result})
        if result.get("ok"):
            key_map[item["local_id"]] = result["key"]
    return key_map, results
