from __future__ import absolute_import
from __future__ import unicode_literals
from testinfra.utils.ansible_runner import AnsibleRunner
import os
import pytest
import logging
import testinfra.utils.ansible_runner
import collections


logging.basicConfig(level=logging.DEBUG)
# DEFAULT_HOST = 'all'
VAR_FILE = "../../../../../ansible-bootstrap-workstation/defaults.yml"

TESTINFRA_HOSTS = testinfra.utils.ansible_runner.AnsibleRunner(
        os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
inventory = os.environ['MOLECULE_INVENTORY_FILE']
runner = AnsibleRunner(inventory)
# runner.get_hosts(DEFAULT_HOST)


@pytest.fixture
def ansible_variables(host):
    variables = runner.run(
        TESTINFRA_HOSTS,
        'include_vars',
        VAR_FILE
    )
    return variables['ansible_facts']


def converttostr(data):
    if isinstance(data, str):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(list(map(converttostr, iter(data.items()))))
    elif isinstance(data, collections.Iterable):
        return type(data)(list(map(converttostr, data)))
    else:
        return data


def test_group(host, ansible_variables):
    dict_variables = converttostr(ansible_variables)
    mygroup = dict_variables['system_group']
    mygid = dict_variables['system_gid']
    assert host.group(mygroup).exists
    assert host.group(mygroup).gid == mygid


def test_username(host, ansible_variables):
    dict_variables = converttostr(ansible_variables)
    myuser = dict_variables['system_username']
    myuid = dict_variables['system_uid']
    mygid = dict_variables['system_gid']
    myshell = dict_variables['system_username_shell']
    mypassword = dict_variables['system_username_password']

    assert host.user(myuser).exists
    assert host.user(myuser).uid == myuid
    assert host.user(myuser).gid == mygid
    assert host.user(myuser).shell == myshell
    assert host.user(myuser).password == mypassword


def test_groups(host, ansible_variables):
    dict_variables = converttostr(ansible_variables)
    myuser = dict_variables['system_username']
    mygroups = dict_variables['system_default_groups']
    myactualgroups = host.user(myuser).groups
    myactualgroups.remove(myuser)

    mygroups.sort()
    myactualgroups.sort()

    assert mygroups == myactualgroups


def test_sudo_form_root(host, ansible_variables):
    dict_variables = converttostr(ansible_variables)
    myuser = dict_variables['system_username']
    assert host.check_output("whoami") == "root"
    with host.sudo("luis7238"):
        assert host.user(myuser).name == myuser
        assert host.check_output("whoami") == myuser
        assert host.check_output("sudo -l | grep '(ALL) NOPASSWD: ALL' ")
    assert host.check_output("whoami") == "root"


# def test_sudo_from_root(host, ansible_variables):
#     dict_variables = converttostr(ansible_variables)
#     myuser = dict_variables['system_username']
#     assert host.user().name == "root"
#     with host.sudo(myuser):
#         assert host.user().name == myuser
#     assert host.user().name == "root"


# def test_sudo_fail_from_root(host, ansible_variables):
#     dict_variables = converttostr(ansible_variables)
#     myuser = dict_variables['system_username']
#     #assert host.user().name == "root"
#     with pytest.raises(AssertionError) as exc:
#         with host.sudo(myuser):
#             assert host.user(myuser).name == myuser
#             host.check_output('ls /root/invalid')
#         assert str(exc.value).startswith('Unexpected exit code')
#     #with host.sudo():
#     #    assert host.user().name == "root"
