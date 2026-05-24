import os
os.environ["CREWAI_DISABLE_PROMPT_CACHE"] = "true"
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OPENAI_API_KEY"] = "fake"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"
os.environ["GROQ_API_BASE"] = "https://api.groq.com/openai/v1"

# ── Patch LiteLLM directement ─────────────────────────────
import litellm
litellm.drop_params = True  # ← supprime cache_breakpoint !

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from tiksafe_crewai.tools.custom_tool import (
    ContentClassificationTool,
    AlertTool
)

load_dotenv()

from crewai import LLM
llm = LLM(
    model="cerebras/llama3.1-8b",  # ← nom exact !
    api_key=os.getenv("CEREBRAS_API_KEY")
)



@CrewBase
class TiksafeCrewai():

    agents_config = 'config/agents.yaml'
    tasks_config  = 'config/tasks.yaml'

    classify_tool = ContentClassificationTool()
    alert_tool    = AlertTool()

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'],
            tools=[self.classify_tool],
            llm=llm,
            verbose=True,
            max_retry_limit=3
        )

    @agent
    def supervisor(self) -> Agent:
        return Agent(
            config=self.agents_config['supervisor'],
            tools=[],
            llm=llm,
            verbose=True,
            max_retry_limit=3
        )

    @agent
    def alerter(self) -> Agent:
        return Agent(
            config=self.agents_config['alerter'],
            tools=[self.alert_tool],
            llm=llm,
            verbose=True,
            max_retry_limit=3
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task']
        )

    @task
    def verification_task(self) -> Task:
        return Task(
            config=self.tasks_config['verification_task']
        )

    @task
    def alert_task(self) -> Task:
        return Task(
            config=self.tasks_config['alert_task'],
            output_file='output/result.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )