import os
import re

import agentops
import autogen

from constants import *
from tools.common_tools import read_from_file, write_to_file
from tools.msf_tools import msf_console_scan_tool
from utils.autogen.agent_factory import AgentFactory
from utils.autogen.system_message import SystemMessage
from utils.autogen.workflow_manager import WorkflowManager


def start_workflow():
    """
        Workflow Description:
        This workflow involves three key roles: Team Lead, Pentest Agent, and Task Supervisor, all powered by GPT-4 Turbo.

        - Team Lead: Creates and assigns pentesting tasks to the Pentest Agent.
        - Pentest Agent: Executes tasks assigned by the Team Lead and collaborates with the Executor for task execution.
        - Task Supervisor: Reviews the results provided by the Pentest Agent and decides whether to approve them or request rework.

        Workflow Communication:
        - Team Lead assigns tasks to the Pentest Agent.
        - Pentest Agent collaborates with the Executor for executing tasks and then submits the results to the Task Supervisor.
        - Task Supervisor reviews the results and decides to either approve them and send them to the Team Lead, or request rework from the Pentest Agent.
    """

    # When initializing AgentOps, you can pass in optional tags to help filter sessions
    agentops.init(api_key=os.getenv('agent_ops_api'))

    # Load LLM configurations
    llm_config_gpt = autogen.config_list_from_json(
        env_or_file="OAI_CONFIG_LIST",
        filter_dict={"model": ["gpt-4-turbo-2024-04-09"]}
    )

    # Define agent names
    agents_names = [
        f'{TEAM_LEAD}#3',
        f'{TASK_SUPERVISOR}#2',
        f'{PENTEST}#3',
        f'{HELPER}#1',
        'executor',
        'initializer'
    ]

    # Define seeds for agents
    team_lead_seed = 0.12345
    pentest_seed = 0.67890
    task_supervisor_seed = 0.54321
    helper_seed = 0.72591

    # Main input for the workflow
    main_input = "Please investigate 192.168.56.101"

    # Initialize and load system messages
    system_message = SystemMessage()
    system_message.load_messages(agents_names)

    # Create agent factory
    agent_factory = AgentFactory(llm_config_gpt, system_message)

    # Create agents
    team_lead = agent_factory.create_llm_agent(TEAM_LEAD, user_seed=team_lead_seed)
    pentest = agent_factory.create_llm_agent(PENTEST, user_seed=pentest_seed)
    task_supervisor = agent_factory.create_llm_agent(TASK_SUPERVISOR, user_seed=task_supervisor_seed)
    helper = agent_factory.create_llm_agent(HELPER, user_seed=helper_seed)
    executor = agent_factory.get_executor()
    initializer = agent_factory.get_initializer()

    # Connect necessary tools to pentest agent
    pentest_tools = [msf_console_scan_tool]
    common_tools = [read_from_file, write_to_file]
    agent_factory.connect_tool(pentest, pentest_tools)
    agent_factory.connect_tool(helper, common_tools)

    # Define key phrases
    pentest_agent_keywords = re.compile(r'Pentest', re.IGNORECASE)
    team_lead_keywords = re.compile(r'Team Lead', re.IGNORECASE)
    task_supervisor_keywords = re.compile(r'Task Supervisor', re.IGNORECASE)
    helper_keywords = re.compile(r'Helper agent', re.IGNORECASE)

    # Custom state transition function to determine the next agent to speak
    def state_transition(last_speaker, groupchat):
        messages = groupchat.messages
        last_message = messages[-1]['content']

        if last_speaker is initializer:
            return team_lead
        if last_speaker is team_lead:
            if helper_keywords.search(last_message):
                return helper
            if pentest_agent_keywords.search(last_message):
                return pentest
            return team_lead
        if last_speaker is helper:
            if 'tool_calls' in messages[-1].keys():
                return executor
            return team_lead
        if last_speaker is pentest:
            if 'tool_calls' in messages[-1].keys():
                return executor
            if task_supervisor_keywords.search(last_message):
                return task_supervisor
            return pentest
        if last_speaker is executor:
            if 'helper' in messages[-2]['name']:
                return team_lead
            return pentest
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
        agents_list=[initializer, team_lead, pentest, task_supervisor, helper, executor],
        state_transition=state_transition,
        llm_config_list=llm_config_gpt,
        max_round=50
    )
    workflow_manager.start_workflow()

    # Close your AgentOps session to indicate that it completed.
    agentops.end_session("Success")
