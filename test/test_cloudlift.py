import os
import time

import boto3
import click
import requests
import urllib3
from mock import patch

from cloudlift.config import ServiceConfiguration
from cloudlift.deployment.service_creator import ServiceCreator
from cloudlift.deployment.service_updater import ServiceUpdater


def setup_module(module):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def mocked_service_config(cls, *args, **kwargs):
    return None

environment_name = 'staging'
service_name = 'dummy'

def test_cloudlift_can_deploy():
    cfn_client = boto3.client('cloudformation')
    stack_name = f'{service_name}-{environment_name}'
    cfn_client.delete_stack(StackName=stack_name)
    print("initiated delete")
    waiter = cfn_client.get_waiter('stack_delete_complete')
    waiter.wait(StackName=stack_name)
    print("completed delete")
    config_path = '/'.join([environment_name, service_name, 'env.properties'])
    os.chdir('./test/dummy')
    print("adding configuration to parameter store")
    ssm_client = boto3.client('ssm')
    ssm_client.put_parameter(
        Name=f"/{environment_name}/{service_name}/PORT",
        Value="80",
        Type="SecureString",
        KeyId='alias/aws/ssm', Overwrite=True
    )
    ssm_client.put_parameter(
        Name=f"/{environment_name}/{service_name}/LABEL",
        Value="Demo",
        Type="SecureString",
        KeyId='alias/aws/ssm',
        Overwrite=True
    )
    with patch.object(ServiceConfiguration, 'edit_config',
                      new=mocked_service_config):
        ServiceCreator(service_name, environment_name,).create()
    ServiceUpdater(service_name, environment_name, None).run()
    outputs = cfn_client.describe_stacks(
        StackName=stack_name
    )['Stacks'][0]['Outputs']
    service_url = [
        x for x in outputs if x["OutputKey"] == "DummyURL"
    ][0]['OutputValue']
    content_matched = wait_until(
        lambda: match_page_content(
            service_url,
            'This is dummy app. Label: Demo'
        ), 60)
    os.chdir('../../')
    assert content_matched


def match_page_content(service_url, content_expected):
    page_content = requests.get(service_url, verify=False).text
    print("page_content: " + str(page_content))
    return page_content == content_expected


def wait_until(predicate, timeout, period=1, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if predicate(*args, **kwargs):
            return True
        print("sleeping and gonna retry...")
        time.sleep(period)
    return False
