from tools.msf_tools import msf_console_scan_tool
from workflows.workflow_teamlead_tasksupervisor_pentest.workflow_2 import start_workflow

start_workflow()

# filtered = msf_console_scan_tool(
#     'auxiliary',
#     'scanner/portscan/tcp',
#     '63.251.228.0/24',
#     ports='1-65535'
# )
# print(filtered)
