import random
from typing import List, Dict

from autogen import ConversableAgent, UserProxyAgent

from utils.autogen.system_message import SystemMessage

EXECUTOR = 'executor'
INITIALIZER = 'initializer'
RANDOM_ALPHA = 1
RANDOM_OMEGA = 999_999_999


class AgentFactory:
    def __init__(self, llm_config_list: list, system_message: SystemMessage):
        self._common_llm_config = llm_config_list
        self._system_message = system_message
        self._seeds = self._generate_unique_seeds(len(system_message.get_agents_names()))
        self._executor = self._create_executor()
        self._initializer = self._create_initializer()

    def _generate_unique_seeds(self, count: int) -> List[float]:
        """
        Generate a list of unique random seeds.

        Args:
            count (int): Number of unique seeds to generate.

        Returns:
            List[float]: List of unique random seeds.
        """
        seeds = set()
        while len(seeds) < count:
            seeds.add(random.uniform(RANDOM_ALPHA, RANDOM_OMEGA))
        return list(seeds)

    def _create_executor(self) -> ConversableAgent:
        executor = ConversableAgent(
            name="Executor",
            llm_config=False,  # Turn off LLM for this agent.
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False
            },
            human_input_mode="NEVER",  # Never take human input for this agent for safety.
        )
        return executor

    def _create_initializer(self) -> ConversableAgent:
        return UserProxyAgent(
            name="Initializer",
            human_input_mode="NEVER",
        )

    def get_executor(self):
        return self._executor

    def get_initializer(self):
        return self._initializer

    def create_llm_agent(self, agent_name: str, user_seed: float = None, custom_llm_config: list = None):
        """
        Create and return an LLM agent with the specified name and optional seed.

        Args:
            agent_name (str): The name of the agent.
            user_seed (float, optional): A specific seed to use. If not provided, a seed from the list is used.

        Returns:
            ConversableAgent: The created LLM agent.
        """
        current_seed = user_seed if user_seed else (self._seeds.pop() if self._seeds else random.uniform(0, 1))
        current_llm_config = custom_llm_config if custom_llm_config else self._common_llm_config
        return ConversableAgent(
            name=agent_name,
            system_message=self._system_message.get_system_message(agent_name),
            llm_config={"config_list": current_llm_config, "cache_seed": current_seed}
        )

    def connect_tool(self, llm_agent, tools_list):
        for tool in tools_list:
            llm_agent.register_for_llm(name=tool.__name__, description=tool.__doc__)(tool)
            self._executor.register_for_execution(name=tool.__name__)(tool)
