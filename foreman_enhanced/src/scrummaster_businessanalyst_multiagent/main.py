import json, sys
from dotenv import load_dotenv
from .crew import ForemanBacklogCrew

def run():
    load_dotenv()
    if len(sys.argv) < 2:
        print("Usage: foreman <text-file>")
        return
    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()
    output = ForemanBacklogCrew().crew().kickoff(inputs={"transcript": text})
    if getattr(output, "pydantic", None):
        print(output.pydantic.model_dump_json(indent=2))
    else:
        print(getattr(output, "raw", str(output)))
