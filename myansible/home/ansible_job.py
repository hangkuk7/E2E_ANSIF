from ansible import constants
from ansible import context
from ansible.cli import CLI
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.plugins.callback import CallbackBase

from inspect import currentframe, getframeinfo
from home import DatabaseManager

import os 
import uuid
import time

import configparser
import sys
import json
import pymysql


INVENTORY_FILE = '/etc/ansible/hosts'
PLAYBOOK_FILE = '/home/e2e/ansible_file/my_playbook.yml'

DB_INFO = {'host': '192.168.1.132', 'port': 3306, 'passwd': 'Dlxndl@123', 'user': 'e2e', 'db': 'e2edb'}

def test(arg):
    print(arg)

def run_sql(sql_string, raw_data=None):
    try:
        conn = pymysql.connect(host=DB_INFO['host'], user=DB_INFO['user'], password=DB_INFO['passwd'], 
                               db=DB_INFO['db'], 
                               charset='utf8')
        curs = conn.cursor()

        if raw_data:
            curs.execute(query=sql_string, args=(raw_data))
        else:
            curs.execute(sql_string)

        conn.commit()

    except Exception as e:
        print(e)
    finally:
        conn.close()


def select_sql(sql_string):
    result = None
    try:
        conn = pymysql.connect(host=DB_INFO['host'], user=DB_INFO['user'], password=DB_INFO['passwd'], 
                               db=DB_INFO['db'], 
                               charset='utf8')
        curs = conn.cursor()
        curs.execute(sql_string)
        result = curs.fetchall()
    except Exception as e:
        print(e)
    finally:
        conn.close()

    return result


class SampleCallback(CallbackBase):
    """Sample callback"""

    def __init__(self):
        super(SampleCallback, self).__init__()
        # store all results
        self.results = []

    def v2_runner_on_ok(self, result, **kwargs):
        """Save result instead of printing it"""
        self.results.append(result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.results.append(result)

    def v2_runner_on_unreachable(self, result):
        self.results.append(result)


def ansible_run(loader, inventory, playbook_path, extra_vars):
    frame_info = getframeinfo(currentframe())
    print(f"Start [{frame_info.function}]!")

    variable_manager = VariableManager(loader=loader, inventory=inventory, version_info=CLI.version_info(gitinfo=False))

    if extra_vars.items():
        print(f"[{frame_info.function}] extra_vars.items() is empty")
    else:
        variable_manager._extra_vars = extra_vars

    pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, 
                            variable_manager=variable_manager, loader=loader, passwords={})

    callback = SampleCallback()

    pbex._tqm._stdout_callback = callback
    return_code = pbex.run()
    results = callback.results

    return return_code, results


def ansible_main():
    frame_info = getframeinfo(currentframe())
    print(f"Start [{frame_info.function}]!")

    workflow_id = str(uuid.uuid1())
    print(f"[{frame_info.function}] bind_key : {workflow_id}")

    now_time = time.strftime('%Y-%m-%d_%H:%M:%S')
    print(f"[{frame_info.function}] now_time : {now_time}")

    # Check files
    if not os.path.exists(INVENTORY_FILE):
        print(f"[{frame_info.function}] Errror. File not exist. {INVENTORY_FILE}):")
        sys.exit()
    else:
        print(f"[{frame_info.function}] INVENTORY_FILE : {INVENTORY_FILE}")

    if not os.path.exists(PLAYBOOK_FILE):
        print(f"[{frame_info.function}] Errror. File not exist. {PLAYBOOK_FILE}):")
        sys.exit()
    else: 
        print(f"[{frame_info.function}] PLAYBOOK_FILE : {PLAYBOOK_FILE}")

    # Code for Ansible execute 
    context.CLIARGS = ImmutableDict(
        # connection='local',
        # timeout=3,
        # module_path=['/data1/e2e/flexconf_venv/lib/python3.6/site-packages/ansible-2.9.9-py3.6.egg/ansible'],
        # forks=10, check=False, diff=False,
        syntax=False, start_at_task=None, verbosity=3,
        # extra_vars=test_extra_vars
        # host_key_checking=False,
        )

    loader = DataLoader()

    inventory = InventoryManager(loader=loader, sources=(INVENTORY_FILE,))
    list_hosts = inventory.list_hosts()

    idx = 0
    for host in list_hosts:
        idx = idx + 1
        host = str(host)
        print(f"[{frame_info.function}] ({idx}) th, host : {host}")

    ansible_run_start_time = time.time() 
    print(f"[{frame_info.function}] ansible_run_start_time : {ansible_run_start_time}")

    extra_vars = {}

    return_code, results = ansible_run(loader, inventory, PLAYBOOK_FILE, extra_vars)
    
    print("[{frame_info.function}] return_code : ", return_code)
    print("[{frame_info.function}] results : ")

    print(results)
    if return_code == 0:
        for result in results:
            if 'ansible_raw_data' in result._result.keys():
#                result_msg = result._result
#                print(result_msg)
                system_id = str(result._host)
                print(system_id)
#                raw_stdout_lines = result._result["ansible_raw_data"]["stdout_lines"]
#                print(raw_stdout_lines)
                raw_ansible_facts = result._result["ansible_raw_data"]["ansible_facts"]
                print(f"raw_ansible_facts : {raw_ansible_facts}")
                raw_changed = result._result["ansible_raw_data"]["changed"]
                print(f"raw_changed : {raw_changed}")
                raw_cmd = result._result["ansible_raw_data"]["cmd"]
                print(f"raw_cmd : {raw_cmd}")
                raw_start = result._result["ansible_raw_data"]["start"]
                print(f"raw_start : {raw_start}")
                raw_end = result._result["ansible_raw_data"]["end"]
                print(f"raw_end : {raw_end}")

    else:
        for result in results:
            result_msg = result._result
            print(f"Error : {result_msg}")

    split_lines = result._result["ansible_raw_data"]["stdout_lines"]
    line_num = len(split_lines)
    print(f"line_num = {line_num}")

    print(f"===================================== Result =======================================")
    i = 1
    for split_line in split_lines:
        tmp_line = split_line.split('  ', 2)
        proto = tmp_line[0]
        ref_cnt = tmp_line[1]

        tmp_line = tmp_line[2].split('     ', 2)
        if 'ACC' in tmp_line[0]:
            flags = 'ACC'
        else:
            flags = ''
        
        types = tmp_line[1].lstrip()

        tmp_line = tmp_line[2].split('    ')
        state = tmp_line[0].strip()

        if len(tmp_line) < 3:
            i_node = -1
            path = ""
        elif len(tmp_line) == 3:
            if len(tmp_line[1].lstrip()) < 1:
                temp_data = tmp_line[2].lstrip()
                if temp_data.isalpha() == True:
                    i_node = -1
                    path = temp_data
                else:
                    i_node = int(temp_data) 
                    path = ""
            else:
                temp_data = tmp_line[1].lstrip()
                if temp_data.isalpha() == True:
                    i_node = -1
                    path = temp_data
                else:
                    i_node = int(temp_data)
                    path = tmp_line[2].lstrip()

        elif len(tmp_line) == 4:
            temp_data = tmp_line[2].lstrip()
            if temp_data.isalpha() == True:
                i_node = -1
                path = temp_data
            else:
                if len(temp_data) > 1:
                    temp_val = tmp_line[3].lstrip()
                    if temp_val.isalpha() == True:
                        i_node = -1
                        path = temp_val 
                    else:
                        i_node = int(temp_val)
                        path = ""
                else:
                    i_node = -1
                    path = ""

        elif len(tmp_line) == 5:
            temp_data = tmp_line[3].lstrip()
            if temp_data.isalpha() == True:
                i_node = -1
                path = temp_data
            else:
                if len(temp_data) > 1:
                    temp_val = tmp_line[4].lstrip()
                    if temp_val.isalpha() == True:
                        i_node = -1
                        path = temp_val
                    else:
                        if len(temp_val) > 1 and temp_val.isalpha() == True:
                            i_node = -1 
                            path = temp_val 
                        else:
                            i_node = -1 
                            path = ""
                else:
                    i_node = -1
                    path = ""

        else:
            print(f"Error. unknow tmp_line, tmp_line_len={len(tmp_line)}")

        sql_insert = "INSERT INTO tb_e2eo_ansible_result_raw(workflow_id, system_id, requested_at, result_idx, protocol, ref_cnt, flags, types, state, i_node, path) VALUES " \
"('" + workflow_id + "','" + host + "', NOW(), " + str(i) + ", '" + proto + "', " + str(ref_cnt) + ", '" + flags + "', '" + types + "', '" + state + "', \
" + str(i_node) + ", '" + path + "');"

        run_sql(sql_insert)

#        print(f"{i} th, sql_insert={sql_insert}")
        print(f"{i} th, proto={proto}, ref_cnt={ref_cnt}, flags={flags}, types={types}, state={state}, i_node={i_node}, path={path}")

        i = i +1
    print(f"=======================================================================================")

    return
