import concurrent.futures
from typing import List

from tools.msf_tools import msf_console_scan_tool
from utils.task_time_logger import enable_logging_task_time


def scan_module(module_name: str) -> str:
    """
    Executes a scan using the specified Metasploit module.
    """
    return msf_console_scan_tool(
        'auxiliary',
        module_name,
        '63.251.228.70',
        threads=500
    )


def main():
    enable_logging_task_time() # Logs the duration of a process with the module name and message.

    module_names = [
        'scanner/portscan/tcp',
        'scanner/portscan/ack',
        'scanner/portscan/syn',
        'scanner/portscan/xmas'
    ]

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_module = {executor.submit(scan_module, module_name): module_name for module_name in module_names}
        for future in concurrent.futures.as_completed(future_to_module):
            module_name = future_to_module[future]
            try:
                result = future.result()
                results.append((module_name, result))
                print(f"Module {module_name} completed successfully.")
            except Exception as exc:
                print(f"Module {module_name} generated an exception: {exc}")

    # Process results
    for module_name, result in results:
        print(f"Results for {module_name}:\n{result}")


if __name__ == "__main__":
    main()
