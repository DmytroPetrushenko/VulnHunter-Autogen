import os
import re
import time
from datetime import datetime
from typing import Optional, Tuple

from constants import *
from dao.sqlite.msf_sqlite import create_table, insert_data, create_connection, check_existing_record
from utils.msf.classes import CustomMsfRpcClient



def msf_console_scan_tool(module_category: str, module_name: str, rhosts: str, rport: Optional[str] = None,
                          ports: Optional[str] = None, threads: int = 50, target: Optional[int] = None,
                          payload: Optional[str] = None, lhost: Optional[str] = None,
                          lport: Optional[str] = None) -> str:
    """
    Execute a Metasploit module through the console interface and return the output.

    Args:
        module_category (str): The category of the Metasploit module (e.g., 'auxiliary', 'exploit').
        module_name (str): The name of the Metasploit module (e.g., 'scanner/http/http_version').
        rhosts (str): The target hosts to scan.
        rport (Optional[str]): The target port to scan.
        ports (Optional[str]): The target ports to scan.
        threads (int): The number of threads to use for scanning. Default is 50.
        target (Optional[int]): The specific target for the module.
        payload (Optional[str]): The payload to use with the module.
        lhost (Optional[str]): The local host for the payload.
        lport (Optional[str]): The local port for the payload.

    Returns:
        str: The output from the console after executing the module.

    Example:
        output = msf_console_scan_tool('auxiliary', 'scanner/http/http_version', '3.255.212.92')
        print(output)
    """

    # Create database connection and create database
    db_connection = create_connection()

    table_name, table_fields = get_table_name_and_fields()

    if not create_table(db_connection, table_name, table_fields):
        raise Exception('Table creation failed')

    if MOCK:
        record = check_existing_record(db_connection, table_name, f'{module_category}/{module_name}', rhosts,
                                       rport or '0', ports or '', threads)
        if record:
            print(f'The data was found in database for these parameters: {module_category}/{module_name}, {rhosts}, {rport}, {ports}, {threads}')
            return record[0]

    # Get values from environment variables if they are not provided
    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))
    ssl = os.getenv('SSL').lower() == 'true'

    # Create Metasploit RPC client
    client = CustomMsfRpcClient(password=password, host=host, port=port, ssl=ssl).get_client()

    # Create a new console
    console = client.consoles.console()
    console_id = console.cid

    try:
        commands = [
            f'use {module_category}/{module_name}',
            f'set RHOSTS {rhosts}',
            f'set THREADS {threads}'
        ]
        if rport:
            commands.append(f'set RPORT {rport}')
        if ports:
            commands.append(f'set PORTS {ports}')
        if target:
            commands.append(f'set TARGET {target}')
        if payload:
            commands.append(f'set PAYLOAD {payload}')
        if lhost:
            commands.append(f'set LHOST {lhost}')
        if lport:
            commands.append(f'set LPORT {lport}')
        commands.append('run')

        command_str = '\n'.join(commands) + '\n'
        client.consoles.console(console_id).write(command_str)

        # Record the start time
        start_time = time.time()

        output = ""
        while True:
            response = client.consoles.console(console_id).read()
            output += response['data']

            if any(keyword in output for keyword in KEYWORDS):
                break

            # Check for timeout
            if time.time() - start_time > TIMEOUT:
                timeout_message = '[TIMEOUT] "Time limit exceeded, exiting the loop."'
                output += timeout_message
                print(timeout_message)
                break

            time.sleep(1)
    finally:
        # Destroy the console
        client.consoles.console(console_id).destroy()

    # Split the output at the documentation line and take the part after it
    split_output = re.split(r'Metasploit Documentation: https://docs.metasploit.com/\n', output, maxsplit=1)
    if len(split_output) > 1:
        filtered_output = split_output[1]
    else:
        filtered_output = ""

    # Insert the result into the database
    table_values = {
        'module': f'{module_category}/{module_name}',
        'rhosts': rhosts,
        'rport': rport or '0',
        'ports': ports or '',
        'threads': threads,
        'output': filtered_output
    }
    insert_data(db_connection, table_name, table_values)

    return filtered_output


def get_table_name_and_fields() -> Tuple[str, dict]:
    """
    Generate the table name and define the table fields.

    Returns:
        tuple: A tuple containing the table name and a dictionary of table fields.
    """
    table_name = TABLE_NAME if TABLE_NAME else f'msf_console_{datetime.now().strftime("%Y_%m_%d")}'
    table_fields = {
        'id': ['INTEGER', 'PRIMARY KEY', 'AUTOINCREMENT'],
        'module': ['TEXT', 'NOT NULL'],
        'rhosts': ['TEXT', 'NOT NULL'],
        'rport': ['INTEGER'],
        'ports': ['TEXT'],
        'threads': ['INTEGER'],
        'output': ['TEXT']
    }
    return table_name, table_fields

