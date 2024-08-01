from tools.msf_tools import msf_console_scan_tool
from workflows.workflow_teamlead_tasksupervisor_pentest.workflow_2 import start_workflow

# start_workflow()

filtered = msf_console_scan_tool(
    'auxiliary',
    'scanner/portscan/syn',
    '63.251.228.0/24',
    threads=500
)
print(filtered)
