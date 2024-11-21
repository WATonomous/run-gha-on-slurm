import json
import os
import logging

POD_NAME = os.getenv('HOSTNAME', 'unknown-pod')
NAMESPACE = get_kubernetes_namespace()

def get_kubernetes_namespace():
    namespace_file = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    try:
        with open(namespace_file, "r") as f:
            namespace = f.read().strip()
        return namespace
    except FileNotFoundError:
        return "Namespace file not found"
    except Exception as e:
        return f"Error reading namespace: {e}"

class KubernetesLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "pod_name": POD_NAME,
            "namespace": NAMESPACE,
        }
        return json.dumps(log_record)