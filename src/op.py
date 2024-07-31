import kopf
import kubernetes
import yaml

@kopf.on.create('example.com', 'v1', 'webapps')
def create_fn(spec, name, namespace, logger, **kwargs):
    # Create the Deployment
    dep = create_deployment(name, namespace, spec)
    kubernetes.config.load_incluster_config()
    api = kubernetes.client.AppsV1Api()
    api.create_namespaced_deployment(namespace, dep)
    logger.info(f"Deployment created for {name}")

    # Create the Service
    svc = create_service(name, namespace)
    api = kubernetes.client.CoreV1Api()
    api.create_namespaced_service(namespace, svc)
    logger.info(f"Service created for {name}")

@kopf.on.delete('example.com', 'v1', 'webapps')
def delete_fn(spec, name, namespace, logger, **kwargs):
    # Delete the Deployment
    api = kubernetes.client.AppsV1Api()
    try:
        api.delete_namespaced_deployment(name, namespace)
        logger.info(f"Deployment deleted for {name}")
    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            raise

    # Delete the Service
    api = kubernetes.client.CoreV1Api()
    try:
        api.delete_namespaced_service(name, namespace)
        logger.info(f"Service deleted for {name}")
    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            raise

def create_deployment(name, namespace, spec):
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': name,
            'namespace': namespace
        },
        'spec': {
            'replicas': spec.get('replicas', 1),
            'selector': {
                'matchLabels': {
                    'app': name
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': name
                    }
                },
                'spec': {
                    'containers': [{
                        'name': name,
                        'image': spec['image']
                    }]
                }
            }
        }
    }

def create_service(name, namespace):
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': name,
            'namespace': namespace
        },
        'spec': {
            'selector': {
                'app': name
            },
            'ports': [{
                'port': 80,
                'targetPort': 80
            }]
        }
    }