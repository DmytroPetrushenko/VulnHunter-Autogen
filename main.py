

from tools.msf_tools import msf_console_scan_tool
from workflows.workflow_t_ts_p.workflow_2 import start_workflow

start_workflow()


msf_console_scan_tool(
        'auxiliary',
        'scanner/portscan/ack',
        '63.251.228.70',
        threads=500
    )