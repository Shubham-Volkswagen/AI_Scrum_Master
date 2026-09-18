import os
import streamlit as st
from .llmaas_auth import get_token
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from .models import BacklogPackage

@CrewBase
class ForemanBacklogCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        access_token = get_token()
        self.llm = LLM(
        model="gpt-4o",
        api_key=access_token,
        base_url="https://llmapi.ai.vwgroup.com",
        extra_headers={
            "X-LLM-API-CLIENT-ID":
                f"Bearer {st.secrets['LLMAAS_VIRTUAL_KEY']}"
        },
        temperature=0
    )
    
    @agent
    def intake_analyst(self):
        return Agent(config=self.agents_config["intake_analyst"], llm=self.llm, verbose=True)

    @agent
    def scrum_master(self):
        return Agent(config=self.agents_config["scrum_master"], llm=self.llm, verbose=True)

    @agent
    def business_analyst(self):
        return Agent(config=self.agents_config["business_analyst"], llm=self.llm, verbose=True)

    @task
    def intake_task(self):
        return Task(config=self.tasks_config["intake_task"], agent=self.intake_analyst())

    @task
    def decomposition_task(self):
        return Task(config=self.tasks_config["decomposition_task"], agent=self.scrum_master())

    @task
    def specification_task(self):
        return Task(config=self.tasks_config["specification_task"], agent=self.business_analyst(), output_pydantic=BacklogPackage)

    @crew
    def crew(self):
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)

# Backward-compatible name
ScrummasterBusinessanalystMultiagent = ForemanBacklogCrew
