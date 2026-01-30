# Golden Helm Chart

A comprehensive, production-ready Helm chart with best practices for Kubernetes deployments.

## Features

This golden Helm chart provides a complete solution for deploying applications on Kubernetes with:

- **Core Resources**: Deployments, Services, ConfigMaps, Secrets
- **Advanced Workloads**: CronJobs, Helm Hooks
- **High Availability**: Pod Disruption Budgets, Horizontal Pod Autoscalers
- **Networking**: Ingress, Network Policies
- **Service Mesh**: Full Istio support (Gateways, VirtualServices, DestinationRules, etc.)
- **Monitoring**: ServiceMonitors and PodMonitors for Prometheus Operator
- **Security**: RBAC, Pod Security Contexts, Network Policies
- **Storage**: Persistent Volume Claims
- **Flexibility**: Extra resources support for custom manifests

## Installation

### Basic Installation

```bash
helm install my-release ./golden-chart
```

### With Custom Values

```bash
helm install my-release ./golden-chart -f my-values.yaml
```

### With Namespace

```bash
helm install my-release ./golden-chart -n my-namespace --create-namespace
```

## Configuration

### Quick Start Example

Here's a minimal example to get started:

```yaml
deployments:
  api:
    enabled: true
    replicaCount: 2
    image:
      repository: my-org/my-api
      tag: "v1.0.0"
    ports:
      - name: http
        containerPort: 8080
    env:
      - name: APP_ENV
        value: production

services:
  api:
    enabled: true
    targetDeployment: api
    type: ClusterIP
    ports:
      - name: http
        port: 80
        targetPort: http
```

### Key Concepts

#### 1. Map-Based Configuration

Resources are organized as maps for easy overrides:

```yaml
deployments:
  api:      # Key becomes part of resource name: {release}-api
    enabled: true
    # ...
  worker:   # {release}-worker
    enabled: true
    # ...
```

#### 2. Defaults Inheritance

Set common defaults once, override when needed:

```yaml
defaults:
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"

deployments:
  api:
    resources: {}  # Uses defaults
  
  heavy-worker:
    resources:     # Overrides defaults
      requests:
        cpu: "1000m"
        memory: "2Gi"
```

#### 3. Security by Default

The chart includes secure defaults:

- Non-root containers
- Read-only root filesystem
- Dropped capabilities
- Network policies support
- RBAC resources

## Examples

### Example 1: Simple Web Application

```yaml
global:
  labels:
    app: my-app
    environment: production

deployments:
  web:
    enabled: true
    replicaCount: 3
    image:
      repository: my-org/web-app
      tag: "2.1.0"
    ports:
      - name: http
        containerPort: 8080
    env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: db-credentials
            key: url

services:
  web:
    enabled: true
    targetDeployment: web
    type: LoadBalancer
    ports:
      - name: http
        port: 80
        targetPort: http
```

### Example 2: Microservices with Istio

```yaml
istio:
  enabled: true
  
  gateways:
    main:
      enabled: true
      selector:
        istio: ingressgateway
      servers:
        - port:
            number: 443
            name: https
            protocol: HTTPS
          hosts:
            - "api.example.com"
          tls:
            mode: SIMPLE
            credentialName: api-tls-cert
  
  virtualServices:
    api:
      enabled: true
      hosts:
        - "api.example.com"
      gateways:
        - main
      http:
        - route:
            - destination:
                host: api
                port:
                  number: 80
          retries:
            attempts: 3
            perTryTimeout: 10s

deployments:
  api:
    enabled: true
    image:
      repository: my-org/api
      tag: "v1.0.0"

services:
  api:
    enabled: true
    targetDeployment: api
```

### Example 3: CronJob

```yaml
cronJobs:
  backup:
    enabled: true
    schedule: "0 2 * * *"
    timeZone: "UTC"
    image:
      repository: my-org/backup-job
      tag: "latest"
    command: ["/backup.sh"]
    env:
      - name: S3_BUCKET
        value: "my-backups"
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
```

## Values Reference

### Global Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.nameOverride` | Override chart name | `""` |
| `global.fullnameOverride` | Override full resource name | `""` |
| `global.labels` | Labels applied to all resources | `{}` |
| `global.annotations` | Annotations applied to all resources | `{}` |
| `global.imagePullSecrets` | Image pull secrets | `[]` |

### Defaults

| Parameter | Description | Default |
|-----------|-------------|---------|
| `defaults.image.repository` | Default image repository | `""` |
| `defaults.image.tag` | Default image tag | `"latest"` |
| `defaults.image.pullPolicy` | Default pull policy | `IfNotPresent` |
| `defaults.resources.requests.cpu` | Default CPU request | `"100m"` |
| `defaults.resources.requests.memory` | Default memory request | `"128Mi"` |
| `defaults.resources.limits.cpu` | Default CPU limit | `"500m"` |
| `defaults.resources.limits.memory` | Default memory limit | `"512Mi"` |

### Deployments

Each deployment supports the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `enabled` | Enable this deployment | `true` |
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | Required |
| `image.tag` | Image tag | Required |
| `ports` | Container ports | `[]` |
| `env` | Environment variables | `[]` |
| `resources` | Resource requests/limits | Uses defaults |
| `serviceAccount.create` | Create service account | `false` |
| `pdb.enabled` | Enable Pod Disruption Budget | `false` |
| `autoscaling.enabled` | Enable HPA | `false` |

See `values.yaml` for complete configuration options.

## Best Practices

1. **Always set resource limits**: Prevents resource exhaustion
2. **Use PodDisruptionBudgets**: Ensures availability during cluster maintenance
3. **Enable probes**: Improves reliability and zero-downtime deployments
4. **Use security contexts**: Runs containers as non-root
5. **Configure autoscaling**: Handles traffic spikes automatically
6. **Use separate values files**: Per environment (dev, staging, prod)

## Troubleshooting

### Check rendered templates

```bash
helm template my-release ./golden-chart -f my-values.yaml
```

### Dry run installation

```bash
helm install my-release ./golden-chart -f my-values.yaml --dry-run --debug
```

### Validate against cluster

```bash
helm install my-release ./golden-chart -f my-values.yaml --dry-run --debug --validate
```

## License

This chart is provided as-is for use in your projects.

## Contributing

Contributions are welcome! Please ensure:

1. Templates follow Helm best practices
2. Changes are backward compatible
3. Documentation is updated
4. Examples are provided for new features
