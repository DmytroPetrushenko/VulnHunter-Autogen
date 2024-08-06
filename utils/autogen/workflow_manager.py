from typing import List

from autogen import GroupChat, GroupChatManager, ConversableAgent


class WorkflowManager:
    def __init__(self,
                 main_input: str,
                 initializer: ConversableAgent,
                 agents_list: List[ConversableAgent],
                 state_transition,
                 llm_config_list: list,
                 max_round: int = 10
                 ):
        self._agents_list = agents_list
        self._initializer = initializer
        self._state_transition = state_transition
        self._max_round = max_round
        self._llm_config_list = llm_config_list
        self._main_input = main_input

    def start_workflow(self):
        """
        Start the workflow by creating a GroupChat and GroupChatManager, and initiating the chat.
        """

        groupchat = GroupChat(
            agents=self._agents_list,
            messages=[],
            max_round=self._max_round,
            allow_repeat_speaker=None,
            speaker_selection_method=self._state_transition,
            speaker_transitions_type="allowed"
        )

        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self._llm_config_list, "cache_seed": 1234567890},
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
            human_input_mode="NEVER"
        )

        self._initializer.initiate_chat(manager, message=f"{self._main_input}")
