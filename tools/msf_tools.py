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
    start_time_point = datetime.now()
    print(f'Timestamp 1: {start_time_point.strftime("%H:%M:%S")}')

    db_connection = create_connection()
    print(f'Timestamp 2: {(datetime.now() - start_time_point).total_seconds()} seconds')

    table_name, table_fields = get_table_name_and_fields()
    if not create_table(db_connection, table_name, table_fields):
        raise Exception('Table creation failed')
    print(f'Timestamp 3: {(datetime.now() - start_time_point).total_seconds()} seconds')

    if MOCK:
        record = check_existing_record(db_connection, f'{module_category}/{module_name}', rhosts)
        if record:
            print(f'The data was found in database for these parameters: {module_category}/{module_name}, {rhosts}')
            return record[0]

    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))
    ssl = os.getenv('SSL').lower() == 'true'
    print(f'Timestamp 4: {(datetime.now() - start_time_point).total_seconds()} seconds')

    rpc_start_time = datetime.now()
    client = CustomMsfRpcClient(password=password, host=host, port=port, ssl=ssl).get_client()
    rpc_end_time = datetime.now()
    print(f'Timestamp 5: Start RPC Client creation: {rpc_start_time.strftime("%H:%M:%S")}')
    print(f'Timestamp 5: End RPC Client creation: {rpc_end_time.strftime("%H:%M:%S")}')
    print(f'Timestamp 5: RPC Client creation duration: {(rpc_end_time - rpc_start_time).total_seconds()} seconds')

    current_console = client.consoles.console()

    try:
        commands = [
            f'use {module_category}/{module_name}',
            f'set RHOSTS {rhosts}',
            f'set THREADS {threads}'
        ]
        if 'scanner/portscan/tcp' in module_name:
            commands.append(f'set CONCURRENCY 100')
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


        current_console.write(command_str)
        print(f'Timestamp 6: {(datetime.now() - start_time_point).total_seconds()} seconds')

        start_time = time.time()
        output = ""
        while True:
            response = current_console.read()
            current_output = response['data']
            print(current_output)
            output += current_output

            if any(keyword in output for keyword in KEYWORDS):
                break

            if time.time() - start_time > 60:
                timeout_message = '[TIMEOUT] "Time limit exceeded, exiting the loop."'
                output += timeout_message
                print(timeout_message)

                # Stop the task in Metasploit
                current_console.write('exit\n')

                break

            time.sleep(1)
    finally:
        current_console.destroy()

    split_output = re.split(r'Metasploit Documentation: https://docs.metasploit.com/\n', output, maxsplit=1)
    filtered_output = split_output[1] if len(split_output) > 1 else ""

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
