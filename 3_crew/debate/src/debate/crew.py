import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

safe_gpt5 = LLM(
    model="openai/gpt-5",
    drop_params=True,
    additional_drop_params=["stop", "temperature"],
)


@CrewBase
class Debate:
    """Debate crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def proposer(self) -> Agent:
        config = dict(self.agents_config["proposer"])

        override_llm = os.getenv("PROPOSER_LLM")

        # Choose override LLM if specified; otherwise, use safe_gpt5
        chosen_llm = override_llm or safe_gpt5
        config["llm"] = chosen_llm

        return Agent(config=config, verbose=True)

    @agent
    def opposer(self) -> Agent:
        config = dict(self.agents_config["opposer"])
        override_llm = os.getenv("OPPOSER_LLM")
        
        # Choose override LLM if specified; otherwise, use safe_gpt5
        chosen_llm = override_llm or safe_gpt5
        config["llm"] = chosen_llm

        return Agent(config=config, verbose=True)

    @agent
    def judge(self) -> Agent:
        config = dict(self.agents_config["judge"])
        override_llm = os.getenv("JUDGE_LLM")
        
        # Choose override LLM if specified; otherwise, use safe_gpt5
        chosen_llm = override_llm or safe_gpt5
        config["llm"] = chosen_llm

        return Agent(config=config, verbose=True)

    @task
    def propose(self) -> Task:
        return Task(
            config=self.tasks_config["propose"],
        )

    @task
    def oppose(self) -> Task:
        return Task(
            config=self.tasks_config["oppose"],
        )

    @task
    def decide(self) -> Task:
        return Task(
            config=self.tasks_config["decide"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Debate crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
