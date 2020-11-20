from ansible import context
from ansible.cli import CLI
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.plugins.callback import CallbackBase

from inspect import currentframe, getframeinfo

import os 
import uuid
import time


INVENTORY_FILE = '/etc/ansible/hosts'
PLAYBOOK_FILE = '/home/e2e/ansible_file/my_playbook.yml'

def test(arg):
    print(arg)

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

#    variable_manager = VariableManager(loader=loader, inventory=inventory)

    if extra_vars.items():
        print(f"[{frame_info.function}] extra_vars.items() is empty")
    else:
        variable_manager._extra_vars = extra_vars

    pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, 
                            variable_manager=variable_manager, loader=loader, passwords={})

#    pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords={})

    callback = SampleCallback()

    pbex._tqm._stdout_callback = callback
    return_code = pbex.run()
    results = callback.results

    return return_code, results


def ansible_main():
    frame_info = getframeinfo(currentframe())
    print(f"Start [{frame_info.function}]!")

    bind_key = str(uuid.uuid1())
    print(f"[{frame_info.function}] bind_key : {bind_key}")

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

    return
