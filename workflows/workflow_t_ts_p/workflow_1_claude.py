import os
import re

import autogen

from constants import *
from tools.common_tools import read_from_file, write_to_file
from tools.msf_tools import msf_console_scan_tool
from utils.autogen.agent_factory import AgentFactory
from utils.autogen.system_message import SystemMessage
from utils.autogen.workflow_manager import WorkflowManager


def start_workflow():
    # Load LLM configurations
    config_list_claude = [
        {
            # Choose your model name.
            "model": "claude-3-5-sonnet-20240620",
            # You need to provide your API key here.
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "api_type": "anthropic",
        }
    ]

    llm_config_gpt = autogen.config_list_from_json(
        env_or_file="OAI_CONFIG_LIST",
        filter_dict={"model": ["gpt-4-turbo-2024-04-09"]}
    )

    # Define agent names
    agents_names = [
        f'{TEAM_LEAD}#2',
        f'{TASK_SUPERVISOR}#1',
        PENTEST,
        'executor',
        'initializer'
    ]

    # Define seeds for agents
    team_lead_seed = 0.12345
    pentest_seed = 0.67890
    task_supervisor_seed = 0.54321

    # Define key phrases
    pentest_agent_keywords = re.compile(r'Pentest Agent, rework required', re.IGNORECASE)
    team_lead_keywords = re.compile(r'Team Lead, task completed satisfactorily', re.IGNORECASE)

    # Main input for the workflow
    main_input = "Please investigate 63.251.228.0/24"

    # Initialize and load system messages
    system_message = SystemMessage()
    system_message.load_messages(agents_names)

    # Create agent factory
    agent_factory = AgentFactory(config_list_claude, system_message)

    # Create agents
    team_lead = agent_factory.create_llm_agent(TEAM_LEAD, user_seed=team_lead_seed)
    pentest = agent_factory.create_llm_agent(PENTEST, user_seed=pentest_seed)
    task_supervisor = agent_factory.create_llm_agent(TASK_SUPERVISOR, user_seed=task_supervisor_seed, custom_llm_config=llm_config_gpt)
    executor = agent_factory.get_executor()
    initializer = agent_factory.get_initializer()

    # Connect necessary tools to pentest agent
    pentest_tools = [msf_console_scan_tool, read_from_file, write_to_file]
    agent_factory.connect_tool(pentest, pentest_tools)

    # Custom state transition function to determine the next agent to speak
    def state_transition(last_speaker, groupchat):
        messages = groupchat.messages
        last_message = messages[-1]['content']

        if last_speaker is initializer:
            return team_lead
        if last_speaker is team_lead:
            return pentest
        if last_speaker is pentest:
            if 'tool_calls' in messages[-1].keys():
                return executor
            return task_supervisor
        if last_speaker is executor:
            return task_supervisor
        if last_speaker is task_supervisor:
            if pentest_agent_keywords.search(last_message):
                return pentest
            if team_lead_keywords.search(last_message):
                return team_lead
            return task_supervisor


    # Initialize and start the workflow
    workflow_manager = WorkflowManager(
        main_input=main_input,
        initializer=initializer,
        agents_list=[initializer, team_lead, pentest, executor, task_supervisor],
        state_transition=state_transition,
        llm_config_list=config_list_claude,
        max_round=50
    )
    workflow_manager.start_workflow()
