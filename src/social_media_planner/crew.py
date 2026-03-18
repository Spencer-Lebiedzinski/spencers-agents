from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class SocialMediaPlanner:
    """SocialMediaPlanner crew"""

    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["research_agent"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def idea_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["idea_agent"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def writing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["writing_agent"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["planner_agent"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def media_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["media_agent"],  # type: ignore[index]
            verbose=True,
        )

    @task
    def research_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_analysis_task"],  # type: ignore[index]
        )

    @task
    def idea_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config["idea_generation_task"],  # type: ignore[index]
            context=[self.research_analysis_task()],
        )

    @task
    def writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["writing_task"],  # type: ignore[index]
            context=[self.idea_generation_task()],
        )

    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["planning_task"],  # type: ignore[index]
            context=[
                self.research_analysis_task(),
                self.idea_generation_task(),
                self.writing_task(),
            ],
        )

    @task
    def media_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["media_planning_task"],  # type: ignore[index]
            context=[
                self.idea_generation_task(),
                self.writing_task(),
                self.planning_task(),
            ],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SocialMediaPlanner crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
