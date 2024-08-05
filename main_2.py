from tools.msf_tools import msf_console_scan_tool
from workflows.workflow_teamlead_tasksupervisor_pentest.workflow_1_claude import start_workflow

# start_workflow()


filtered = msf_console_scan_tool(
    'auxiliary',
    'scanner/portscan/syn',
    '63.251.228.70',
    threads=500
)
print(filtered)

# from line_profiler import LineProfiler
#
# def profile_msf_tool():
#     filtered = msf_console_scan_tool(
#         'auxiliary',
#         'scanner/portscan/tcp',
#         '63.251.228.0/24',
#         threads=500
#     )
#     return filtered
#
# lp = LineProfiler()
# lp_wrapper = lp(profile_msf_tool)
# lp_wrapper()
# lp.print_stats()