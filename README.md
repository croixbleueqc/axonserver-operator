# AxonIQ Axon Server Operator

Axon Server Operator to manage Application registration, contexts permissions and plugins



[TOC]

## Installation

### Developers

```bash
python -m venv --prompt axop .venv
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=$(pwd)
kopf run -m axop --liveness=http://0.0.0.0:5000/healthz -A --standalone # --peering=axoniq-operator
```

### Docker

```bash
docker build -t axop -f devops/Dockerfile .
```

### Kubernetes

```bash
# peering CRDs - used to start/pause operators
kubectl apply -f peering.yaml

# install operator with helm
# (eg with release/namespace set to axoniq-operator-nonprod)
helm upgrade --install --create-namespace axoniq-operator-nonprod devops/chart/ -n axoniq-operator-nonprod

# check if pods are running
kubectl -n axoniq-operator-nonprod get pod -w

# check peering status
kubectl get clusterkopfpeering axoniq-operator -o yaml

# check admission configuration
kubectl get validatingwebhookconfigurations admission.bleuelab.ca -o yaml
```

## Usage

### Instances

An instance is an object that refer to an Axon Server. You can have multiple instances.

Eg:

```yaml
apiVersion: axoniq.bleuelab.ca/v1
kind: Instance
metadata:
  name: axonserveree-nonprod
spec:
  http: https://axonserveree.domain.tld
  grpc: server1.ns.svc.cluster.local:8124,server2.ns.svc.cluster.local:8124,server3.ns.svc.cluster.local:8124
  token:
    hashicorpVault:
      addr: https://vault.domain.tld
      role: axoniq-operator-nonprod
      auth: kubernetes-nonprod
      path: teams/devops/axoniq/nonprod/server
      mount: bluecross
      field: axonserver.token
```

```bash
kubectl apply -f instances.yaml

# Cluster-wide instances
kubectl get instance.axoniq.bleuelab.ca
```

### Plugins

Axon Server EE support plugins to apply on contexts.

You can define which plugins are supported by your instances. It is possible to support the same plugin with multiple configurations.

We are using `io.axoniq.axon-server-plugin-data-protection` with `azure vault backend` as an example:

```yaml
apiVersion: axoniq.bleuelab.ca/v1
kind: Plugin
metadata:
  name: data-protection
spec:
  template:
    payload: |
      context: '{context}'
      name: io.axoniq.axon-server-plugin-data-protection
      version: '{version}'
      properties:
        'MetaModel configuration':
          metamodel: '{model}'
        'Vault storage configuration':
          vaultType: azure
          cacheEnabled: true
          prefix: '{context}'
          azureVaultUrl: 'https://{env}-myvault.vault.azure.net'
          azureServicePrincipalClientId:
            hashicorpVault:
              addr: https://vault.domain.tld
              role: axoniq-operator-nonprod
              auth: kubernetes-nonprod
              path: teams/devops/axoniq/keyvault/{env}
              mount: bluecross
              field: clientid
          azureServicePrincipalTenantId: 'your tenant id'
          azureServicePrincipalSecret:
            hashicorpVault:
              addr: https://vault.domain.tld
              role: axoniq-operator-nonprod
              auth: kubernetes-nonprod
              path: teams/devops/axoniq/keyvault/{env}
              mount: bluecross
              field: secret
    variables:
    - context # reserved
    - version # reserved
    - model
    - env

```

`variables` are used to know what should be replaced in the template payload. This is mainly what you will define in a context object under a plugin.

```bash
kubectl apply -f plugins.yaml

# Cluster-wide plugins
kubectl get plugin.axoniq.bleuelab.ca
```

### Contexts

This kind of objects are used to create a context and configure plugins associated to them.

Eg:

```yaml
apiVersion: axoniq.bleuelab.ca/v1
kind: Context
metadata:
  name: test
spec:
  instance: axonserveree-nonprod # should match a metadata.name instance object
  contexts:
  - context: myctx-dev
    plugins:
      data-protection: # should match a metadata.name plugin object
        version: 1.0.1 # version field is mandatory
        model: '{"config": []}' # everything else is free and depend on the plugin definition (and spec.template.variables)
        env: dev
  - context: myctx2-dev
```

```bash
kubectl -n myns apply -f contexts.yaml

kubectl -n myns get context.axoniq.bleuelab.ca
kubectl -n myns get all
```

### Apps

An application object permit to register an application, set permissions and get a token.

Eg:

```yaml
apiVersion: axoniq.bleuelab.ca/v1
kind: App
metadata:
  name: test
spec:
  instance: axonserveree-nonprod
  description: 'test'
  contexts:
  - context: myctx-dev
    roles:
    - ADMIN
    - CONTEXT_ADMIN
    - DISPATCH_COMMANDS
    - DISPATCH_QUERY
    - MONITOR
    - PUBLISH_EVENTS
    - READ
    - READ_EVENTS
    - SUBSCRIBE_COMMAND_HANDLER
    - SUBSCRIBE_QUERY_HANDLER
    - USE_CONTEXT
    - WRITE
```

Application will be registred with the kubernetes App object uid (metadata.uid).

```bash
kubectl -n myns apply -f apps.yaml

kubectl -n myns get app.axoniq.bleuelab.ca
kubectl -n myns get all

# token and connection string are available in a secret created by the operator
# the secret is named with the app object name
kubectl -n myns get secret test -o yaml
# token
kubectl -n myns get secret test -o json | jq -M -r .data.token | base64 -d
# url (from instance object in spec.grpc)
kubectl -n myns get secret test -o json | jq -M -r .data.url | base64 -d
```



## Limitation

### Vault

`axop` **only** support HashiCorp Vault backend to get some secrets. It is using the `hashicorpVault` key.

Your vault needs to be integrated with kubernetes as the service account credential of the pod will be used to connect on it.

## TODO

