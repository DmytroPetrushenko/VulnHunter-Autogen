# VulnHunter Based on Autogen

## Overview

VulnHunter is an automated penetration testing framework designed to streamline the process of security testing by utilizing various agents. Each agent has a specific role and follows a set workflow to perform tasks efficiently. The project is based on the Autogen system to ensure robust and flexible operations.

## Agents

### Team Lead

The Team Lead agent is responsible for creating a penetration testing plan based on allowed Metasploit modules and generating a security report based on the results.

**Workflow:**
1. Create a pentest plan based on preliminary Metasploit modules.
   - Request the preliminary modules list from the Pentest agent.
   - Create preliminary pentesting tasks based on the list.
   - Send the task to the Pentest agent for execution.

2. Create a pentest plan based on identified findings and auxiliary Metasploit modules.
   - Request the auxiliary modules list from the Pentest agent.
   - Classify the findings and create focused pentesting tasks.
   - Send the plan to the Pentest agent for execution.
   - Analyze results and create additional tasks if needed.

3. Create a security report.
   - Compile all results into a security report.
   - Ask the Pentest agent to write the report to a file.

**Related Files:**
- `agents_prompts/team_lead#1.txt`
- `agents_prompts/team_lead#2.txt`

### Pentest Agent

The Pentest agent conducts testing according to the tasks received from the Team Lead.

**Workflow:**
1. Receive a task from the Team Lead.
2. Execute the task, using default or generated values for missing parameters.
3. Receive the result from the Executor and format the message for the Task Supervisor.
4. Rework the task if required by the Task Supervisor.

**Related Files:**
- `agents_prompts/pentest.txt`
- `agents_prompts/pentest#2.txt`

### Task Supervisor

The Task Supervisor checks the results provided by the Pentest agent and ensures they meet the assigned tasks.

**Workflow:**
1. Receive the result from the Executor.
2. Compare the result with the assigned task.
3. Approve the result or request rework from the Pentest agent.
4. If the Pentest agent has reworked the task twice, approve it despite multiple attempts.

**Related Files:**
- `agents_prompts/task_supervisor#1.txt`
- `agents_prompts/task_supervisor#2.txt`

## Usage

1. **Set up the environment:**
   - Ensure you have Python and the necessary dependencies installed.
   - Set up Metasploit and any other required tools.

2. **Run the workflows:**
   - Execute the Python scripts to start the agents and follow the workflows:
     - `workflows/workflow_teamlead_tasksupervisor_pentest/workflow_1.py`
     - `workflows/workflow_teamlead_tasksupervisor_pentest/workflow_1_claude.py`
     - `workflows/workflow_teamlead_tasksupervisor_pentest/workflow_2.py`
   - Monitor the output and logs to ensure tasks are performed correctly.

3. **Generate reports:**
   - Once the tasks are completed, compile the results into a security report.
   - Use the provided templates and instructions to format the report.

**Utility Scripts:**
- `tools/common_tools.py`
- `tools/msf_tools.py`
- `utils/msf/classes.py`

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
