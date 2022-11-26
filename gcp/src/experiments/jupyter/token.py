import re
from kubernetes import client, config

config.load_kube_config()
namespace_name = input("Enter namespace name:")

def get_pods():
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace=namespace_name)
    return [pod.metadata.name for pod in pod_list.items][0]

pod_name = get_pods()

try:
    api = client.CoreV1Api()
    response = api.read_namespaced_pod_log(name=pod_name, namespace=namespace_name)
    match = re.search(r'token=([0-9a-z]*)', response)
    result = "token=" + match.group(1)
    print(result)
except Exception as e:
    print('Found exception in reading the logs:')
    print(e)