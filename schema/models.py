"""
Pydantic models for Golden Helm Chart values.yaml
Provides type checking and generates JSON schema for LSP support.

Every field here maps to a field actually read by a template in templates/.
The descriptions on each field flow into values.schema.json and appear as
hover documentation in IDEs with YAML language server support.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# ============================================================================
# Common/Shared Models
# ============================================================================


class ImageConfig(BaseModel):
    """Container image reference. When used inside 'defaults', these values
    are inherited by every deployment, cronjob, and hook that does not
    specify its own image."""

    repository: Optional[str] = Field(
        None,
        description="Container image repository, e.g. 'data-platform/api' or 'metabase/metabase'.",
    )
    tag: Optional[str] = Field(
        None,
        description="Image tag or digest. Prefer pinned versions like 'v2.1.0' over 'latest'.",
    )
    pullPolicy: Optional[str] = Field(
        None,
        pattern="^(Always|Never|IfNotPresent)$",
        description="Kubernetes image pull policy. Use 'Never' for local dev with pre-loaded images, "
        "'IfNotPresent' for production, or 'Always' to force re-pull.",
    )


class EnvVar(BaseModel):
    """A single environment variable injected into a container.
    Mirrors the Kubernetes EnvVar spec: set a literal 'value' or use
    'valueFrom' to reference a Secret/ConfigMap/field."""

    name: str = Field(description="Environment variable name.")
    value: Optional[str] = Field(
        None,
        description="Literal string value. Mutually exclusive with 'valueFrom'.",
    )
    valueFrom: Optional[Dict[str, Any]] = Field(
        None,
        description="Reference to a Secret key, ConfigMap key, or field path. "
        "Example: {secretKeyRef: {name: db-credentials, key: url}}.",
    )


class ResourceRequirements(BaseModel):
    """CPU and memory resource requests/limits for a container.
    Always set requests to guarantee scheduling; set limits to prevent
    noisy-neighbor issues on shared nodes."""

    requests: Optional[Dict[str, str]] = Field(
        None,
        description="Minimum resources guaranteed to the container, e.g. {cpu: '250m', memory: '256Mi'}.",
    )
    limits: Optional[Dict[str, str]] = Field(
        None,
        description="Maximum resources the container can use, e.g. {cpu: '1000m', memory: '1Gi'}.",
    )


class SecurityContext(BaseModel):
    """Container or pod-level security settings. The chart defaults enforce
    non-root, read-only root filesystem, and dropped capabilities.
    Override per-deployment only when the workload genuinely requires it."""

    runAsNonRoot: Optional[bool] = Field(
        None,
        description="Require the container to run as a non-root user. Should almost always be true.",
    )
    runAsUser: Optional[int] = Field(
        None,
        description="UID to run the container process as. Common convention is 1000 or 1001.",
    )
    runAsGroup: Optional[int] = Field(
        None,
        description="GID to run the container process as.",
    )
    fsGroup: Optional[int] = Field(
        None,
        description="GID applied to all files in mounted volumes. Useful for shared storage.",
    )
    readOnlyRootFilesystem: Optional[bool] = Field(
        None,
        description="Mount the container's root filesystem as read-only. "
        "Use emptyDir volumes for /tmp or cache directories if the app needs to write.",
    )
    allowPrivilegeEscalation: Optional[bool] = Field(
        None,
        description="Whether the process can gain more privileges than its parent. Should be false.",
    )
    capabilities: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Linux capabilities to add or drop. Default drops ALL: {drop: ['ALL']}.",
    )
    seccompProfile: Optional[Dict[str, str]] = Field(
        None,
        description="Seccomp profile to apply, e.g. {type: RuntimeDefault}.",
    )


class ProbeConfig(BaseModel):
    """Health check probe configuration. The chart only renders the probe
    when 'enabled' is true, so probes defined in defaults are opt-in.
    At least one of httpGet, exec, tcpSocket, or grpc must be set."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to true to enable this probe. When false or omitted, the probe is not rendered.",
    )
    httpGet: Optional[Dict[str, Any]] = Field(
        None,
        description="HTTP GET check, e.g. {path: '/health', port: 'http'}.",
    )
    exec_: Optional[Dict[str, Any]] = Field(
        None,
        alias="exec",
        description="Command-based check, e.g. {command: ['pg_isready']}.",
    )
    tcpSocket: Optional[Dict[str, Any]] = Field(
        None,
        description="TCP socket check, e.g. {port: 6379}.",
    )
    grpc: Optional[Dict[str, Any]] = Field(
        None,
        description="gRPC health check, e.g. {port: 50051}.",
    )
    initialDelaySeconds: Optional[int] = Field(
        None,
        description="Seconds to wait after container start before probing.",
    )
    periodSeconds: Optional[int] = Field(
        None,
        description="How often (in seconds) to perform the probe.",
    )
    timeoutSeconds: Optional[int] = Field(
        None,
        description="Seconds after which the probe times out.",
    )
    successThreshold: Optional[int] = Field(
        None,
        description="Consecutive successes required to mark the probe as passing.",
    )
    failureThreshold: Optional[int] = Field(
        None,
        description="Consecutive failures required to mark the probe as failing. "
        "For startupProbe, this controls the total startup budget: failureThreshold * periodSeconds.",
    )

    class Config:
        populate_by_name = True


class ContainerPort(BaseModel):
    """A port exposed by a container. The 'name' is used to reference the port
    in Service targetPort and probe definitions (e.g. 'http', 'metrics')."""

    name: str = Field(description="Port name, referenced by services and probes (e.g. 'http').")
    containerPort: int = Field(description="Port number the container listens on.")
    protocol: Optional[str] = Field("TCP", description="Protocol: TCP (default) or UDP.")


class ServiceAccountRef(BaseModel):
    """Service account to use for a job or cronjob pod. When 'create' is true,
    a dedicated service account is created with the same name as the job resource."""

    create: Optional[bool] = Field(
        None,
        description="Create a dedicated service account for this job.",
    )
    name: Optional[str] = Field(
        None,
        description="Use an existing service account by name instead of creating one.",
    )


# ============================================================================
# Defaults
# ============================================================================


class Defaults(BaseModel):
    """Default values inherited by all workloads. For deployments, these are
    deep-merged (deployment values win). For hooks and cronjobs, individual
    fields fall back to these defaults when not set on the resource itself.

    Only set values here that genuinely apply to every workload in the release.
    Per-workload overrides belong in the individual deployment/cronjob/hook config."""

    image: Optional[ImageConfig] = Field(
        None,
        description="Default image config. Useful for setting a shared pullPolicy across all workloads.",
    )
    replicas: Optional[int] = Field(
        None,
        description="Default replica count for deployments.",
    )
    resources: Optional[ResourceRequirements] = Field(
        None,
        description="Default CPU/memory requests and limits. Applied to deployments via merge, "
        "to hooks and cronjobs via fallback.",
    )
    securityContext: Optional[SecurityContext] = Field(
        None,
        description="Default container security context. Merged into deployments; "
        "not applied to hooks/cronjobs automatically (use podSecurityContext/containerSecurityContext there).",
    )
    nodeSelector: Optional[Dict[str, str]] = Field(
        None,
        description="Default node selector labels. Pods will only schedule on nodes matching all labels.",
    )
    tolerations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Default tolerations. Allows pods to schedule on tainted nodes.",
    )
    affinity: Optional[Dict[str, Any]] = Field(
        None,
        description="Default affinity rules (nodeAffinity, podAffinity, podAntiAffinity).",
    )


# ============================================================================
# Deployment (deployment.yaml)
# ============================================================================


class DeploymentConfig(BaseModel):
    """Configuration for a Kubernetes Deployment. Each key in the 'deployments'
    map becomes a separate Deployment resource named '<release>-<key>'.

    Example: deployments.data-api creates a Deployment named 'myrelease-golden-chart-data-api'.

    Fields not set here inherit from 'defaults' via deep merge."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this deployment. Enabled by default.",
    )
    image: Optional[ImageConfig] = Field(
        None,
        description="Container image. Overrides defaults.image.",
    )
    replicas: Optional[int] = Field(
        None,
        description="Number of pod replicas. Ignored when an HPA targets this deployment.",
    )
    strategy: Optional[Dict[str, Any]] = Field(
        None,
        description="Deployment rollout strategy. Example: "
        "{type: RollingUpdate, rollingUpdate: {maxSurge: 1, maxUnavailable: 0}}.",
    )
    command: Optional[List[str]] = Field(
        None,
        description="Override the container entrypoint (Docker ENTRYPOINT).",
    )
    args: Optional[List[str]] = Field(
        None,
        description="Arguments to the entrypoint (Docker CMD).",
    )
    ports: Optional[List[ContainerPort]] = Field(
        None,
        description="Ports the container exposes. Typically 'http' (app) and 'metrics' (Prometheus).",
    )
    env: Optional[List[EnvVar]] = Field(
        None,
        description="Environment variables injected into the main container.",
    )
    envFrom: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Bulk environment injection from ConfigMaps or Secrets. "
        "Example: [{configMapRef: {name: app-config}}].",
    )
    resources: Optional[ResourceRequirements] = Field(
        None,
        description="CPU/memory requests and limits. Overrides defaults.resources.",
    )
    securityContext: Optional[SecurityContext] = Field(
        None,
        description="Container-level security context. Overrides defaults.securityContext.",
    )
    livenessProbe: Optional[ProbeConfig] = Field(
        None,
        description="Liveness probe. Restarts the container when it fails. "
        "Must set 'enabled: true' to render.",
    )
    readinessProbe: Optional[ProbeConfig] = Field(
        None,
        description="Readiness probe. Removes the pod from Service endpoints when it fails. "
        "Must set 'enabled: true' to render.",
    )
    startupProbe: Optional[ProbeConfig] = Field(
        None,
        description="Startup probe. Delays liveness/readiness checks until the app is ready. "
        "Use for slow-starting apps (e.g. JVM, large model loading). Must set 'enabled: true' to render.",
    )
    lifecycle: Optional[Dict[str, Any]] = Field(
        None,
        description="Container lifecycle hooks. Common pattern: "
        "{preStop: {exec: {command: ['/bin/sh', '-c', 'sleep 15']}}} for graceful shutdown.",
    )
    volumeMounts: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Volume mounts for the main container. "
        "Example: [{name: tmp, mountPath: /tmp}].",
    )
    volumes: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Pod volumes. Example: [{name: tmp, emptyDir: {sizeLimit: 100Mi}}].",
    )
    initContainers: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Init containers that run before the main container. "
        "Use for migrations, config rendering, or waiting on dependencies.",
    )
    sidecarContainers: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Additional containers that run alongside the main container. "
        "Common uses: log forwarders, proxy sidecars, debug containers.",
    )
    nodeSelector: Optional[Dict[str, str]] = Field(
        None,
        description="Node selector labels. Overrides defaults.nodeSelector.",
    )
    tolerations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Tolerations for node taints. Overrides defaults.tolerations.",
    )
    affinity: Optional[Dict[str, Any]] = Field(
        None,
        description="Affinity/anti-affinity rules. Overrides defaults.affinity.",
    )
    topologySpreadConstraints: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Topology spread constraints for HA. Distributes pods across zones/nodes. "
        "Example: [{maxSkew: 1, topologyKey: 'topology.kubernetes.io/zone', "
        "whenUnsatisfiable: DoNotSchedule}].",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels added to the Deployment metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations added to the Deployment metadata.",
    )
    podLabels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels added to the Pod template metadata.",
    )
    podAnnotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations added to the Pod template metadata. "
        "Common use: Prometheus scrape annotations, Istio sidecar config.",
    )


# ============================================================================
# Service (service.yaml)
# ============================================================================


class ServicePort(BaseModel):
    """A port exposed by a Kubernetes Service. Maps an external port to a
    container port or named port on the target pods."""

    name: Optional[str] = Field(
        None,
        description="Port name. Must match when using named targetPort references.",
    )
    port: int = Field(description="Port number the Service exposes.")
    targetPort: Optional[Any] = Field(
        None,
        description="Container port or named port to route traffic to (e.g. 8080 or 'http').",
    )
    protocol: Optional[str] = Field("TCP", description="Protocol: TCP (default) or UDP.")


class ServiceConfig(BaseModel):
    """Configuration for a Kubernetes Service. Each key in the 'services' map
    creates a Service named '<release>-<key>'.

    Use 'targetDeployment' to set up label selectors that route traffic to
    the matching deployment's pods (matched via app.kubernetes.io/component)."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this service.",
    )
    type: Optional[str] = Field(
        None,
        pattern="^(ClusterIP|NodePort|LoadBalancer|ExternalName)$",
        description="Service type. ClusterIP for internal, LoadBalancer for external access, "
        "NodePort for development.",
    )
    targetDeployment: Optional[str] = Field(
        None,
        description="Key of the deployment to target (must match a key in 'deployments'). "
        "Sets the app.kubernetes.io/component selector label.",
    )
    ports: Optional[List[ServicePort]] = Field(
        None,
        description="Ports exposed by the service.",
    )
    clusterIP: Optional[str] = Field(
        None,
        description="Explicit cluster IP. Set to 'None' for headless services.",
    )
    loadBalancerIP: Optional[str] = Field(
        None,
        description="Static IP for LoadBalancer services (cloud-provider dependent).",
    )
    loadBalancerSourceRanges: Optional[List[str]] = Field(
        None,
        description="CIDR ranges allowed to access a LoadBalancer service.",
    )
    externalTrafficPolicy: Optional[str] = Field(
        None,
        description="'Local' preserves client source IP but may cause imbalanced traffic. "
        "'Cluster' (default) distributes evenly.",
    )
    sessionAffinity: Optional[str] = Field(
        None,
        description="'ClientIP' to enable sticky sessions, 'None' (default) for round-robin.",
    )
    sessionAffinityConfig: Optional[Dict[str, Any]] = Field(
        None,
        description="Session affinity settings, e.g. {clientIP: {timeoutSeconds: 10800}}.",
    )
    extraSelectorLabels: Optional[Dict[str, str]] = Field(
        None,
        description="Additional labels added to the Service's pod selector beyond the defaults.",
    )
    nodePorts: Optional[Dict[str, int]] = Field(
        None,
        description="Map of port name to static NodePort number. Only used when type is NodePort. "
        "Example: {http: 30080}.",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the Service metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the Service metadata. "
        "Common use: cloud load balancer configuration.",
    )


# ============================================================================
# ConfigMap (configmap.yaml)
# ============================================================================


class ConfigMapConfig(BaseModel):
    """Configuration for a Kubernetes ConfigMap. Stores non-sensitive
    configuration data (config files, environment variables, etc.).

    Mount into pods via volumeMounts or inject via envFrom."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this ConfigMap.",
    )
    data: Optional[Dict[str, str]] = Field(
        None,
        description="Key-value pairs stored as UTF-8 strings. "
        "Can hold config files using YAML block scalars: 'config.yaml: |\\n  key: value'.",
    )
    binaryData: Optional[Dict[str, str]] = Field(
        None,
        description="Key-value pairs stored as base64-encoded binary data.",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the ConfigMap metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the ConfigMap metadata.",
    )


# ============================================================================
# Secret (secret.yaml)
# ============================================================================


class SecretConfig(BaseModel):
    """Configuration for a Kubernetes Secret. Stores sensitive data like
    API keys, database credentials, and TLS certificates.

    Prefer external secret managers (e.g. AWS Secrets Manager, Vault) for
    production. This is useful for dev/test or bootstrap secrets."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this Secret.",
    )
    type: Optional[str] = Field(
        "Opaque",
        description="Secret type: 'Opaque' (default), 'kubernetes.io/tls', "
        "'kubernetes.io/dockerconfigjson', etc.",
    )
    data: Optional[Dict[str, str]] = Field(
        None,
        description="Base64-encoded key-value pairs.",
    )
    stringData: Optional[Dict[str, str]] = Field(
        None,
        description="Plain-text key-value pairs (automatically base64-encoded by Kubernetes).",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the Secret metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the Secret metadata.",
    )


# ============================================================================
# PVC (pvc.yaml)
# ============================================================================


class PVCConfig(BaseModel):
    """Configuration for a PersistentVolumeClaim. Requests durable storage
    that survives pod restarts.

    Reference the PVC in a deployment's volumes list:
    volumes: [{name: data, persistentVolumeClaim: {claimName: '<release>-<key>'}}]"""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this PVC.",
    )
    accessModes: Optional[List[str]] = Field(
        None,
        description="Access modes: ReadWriteOnce (single node), ReadOnlyMany (multi-node read), "
        "ReadWriteMany (multi-node read/write).",
    )
    resources: Optional[Dict[str, Any]] = Field(
        None,
        description="Storage resource requests. Example: {requests: {storage: '10Gi'}}.",
    )
    storageClassName: Optional[str] = Field(
        None,
        description="Storage class name. Empty string '' means default class; "
        "set to a specific class for SSD, regional, etc.",
    )
    selector: Optional[Dict[str, Any]] = Field(
        None,
        description="Label selector to bind to a specific PersistentVolume.",
    )
    volumeName: Optional[str] = Field(
        None,
        description="Name of a specific PersistentVolume to bind to (static provisioning).",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the PVC metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the PVC metadata.",
    )


# ============================================================================
# HPA (hpa.yaml)
# ============================================================================


class HPAConfig(BaseModel):
    """Configuration for a HorizontalPodAutoscaler. Automatically scales the
    target deployment's replica count based on CPU, memory, or custom metrics.

    When an HPA is active, do not set 'replicas' on the target deployment
    (the HPA's minReplicas takes over)."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this HPA.",
    )
    targetDeployment: str = Field(
        ...,
        description="Key of the deployment to scale (must match a key in 'deployments').",
    )
    minReplicas: Optional[int] = Field(
        2,
        description="Minimum replica count. Set >= 2 for HA.",
    )
    maxReplicas: Optional[int] = Field(
        10,
        description="Maximum replica count. Set based on your capacity budget.",
    )
    metrics: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Scaling metrics. Example for CPU-based: "
        "[{type: Resource, resource: {name: cpu, target: {type: Utilization, averageUtilization: 70}}}].",
    )
    behavior: Optional[Dict[str, Any]] = Field(
        None,
        description="Scale-up and scale-down behavior policies. Use stabilizationWindowSeconds "
        "to prevent flapping. Example: {scaleDown: {stabilizationWindowSeconds: 300}}.",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the HPA metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the HPA metadata.",
    )


# ============================================================================
# CronJob (cronjob.yaml)
# ============================================================================


class CronJobConfig(BaseModel):
    """Configuration for a Kubernetes CronJob. Runs a container on a cron
    schedule for batch processing, ETL, data quality checks, cleanup, etc.

    Each key in the 'cronjobs' map creates a CronJob named '<release>-<key>'.
    Image defaults fall back to 'defaults.image'."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this CronJob.",
    )
    schedule: str = Field(
        description="Cron schedule expression, e.g. '0 */2 * * *' (every 2 hours). "
        "Use https://crontab.guru to validate.",
    )
    timeZone: Optional[str] = Field(
        None,
        description="IANA time zone for the schedule, e.g. 'America/New_York'. "
        "Requires Kubernetes >= 1.27.",
    )
    concurrencyPolicy: Optional[str] = Field(
        None,
        description="What to do if a job is still running when the next run is due. "
        "'Forbid' (skip), 'Replace' (kill and restart), or 'Allow' (run concurrently).",
    )
    failedJobsHistoryLimit: Optional[int] = Field(
        None,
        description="Number of failed job runs to keep for debugging. Default: 1.",
    )
    successfulJobsHistoryLimit: Optional[int] = Field(
        None,
        description="Number of successful job runs to keep. Default: 3.",
    )
    startingDeadlineSeconds: Optional[int] = Field(
        None,
        description="Seconds after which a missed schedule is considered failed.",
    )
    suspend: Optional[bool] = Field(
        None,
        description="Set to true to pause the CronJob without deleting it.",
    )
    backoffLimit: Optional[int] = Field(
        None,
        description="Number of retries before marking the job as failed.",
    )
    activeDeadlineSeconds: Optional[int] = Field(
        None,
        description="Maximum runtime in seconds before the job is killed.",
    )
    ttlSecondsAfterFinished: Optional[int] = Field(
        None,
        description="Seconds to keep completed job pods before garbage collection.",
    )
    completions: Optional[int] = Field(
        None,
        description="Number of successful completions required. Default: 1.",
    )
    parallelism: Optional[int] = Field(
        None,
        description="Maximum number of pods running in parallel. Default: 1.",
    )
    image: Optional[ImageConfig] = Field(
        None,
        description="Container image. Falls back to defaults.image if not set.",
    )
    command: Optional[List[str]] = Field(
        None,
        description="Override the container entrypoint.",
    )
    args: Optional[List[str]] = Field(
        None,
        description="Arguments to the entrypoint.",
    )
    env: Optional[List[EnvVar]] = Field(
        None,
        description="Environment variables for the job container.",
    )
    envFrom: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Bulk environment injection from ConfigMaps or Secrets.",
    )
    resources: Optional[ResourceRequirements] = Field(
        None,
        description="CPU/memory requests and limits. Falls back to defaults.resources.",
    )
    podSecurityContext: Optional[SecurityContext] = Field(
        None,
        description="Pod-level security context (applies to all containers in the pod).",
    )
    containerSecurityContext: Optional[SecurityContext] = Field(
        None,
        description="Container-level security context for the job container.",
    )
    volumeMounts: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Volume mounts for the job container.",
    )
    volumes: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Pod volumes available to mount.",
    )
    nodeSelector: Optional[Dict[str, str]] = Field(
        None,
        description="Node selector labels. Falls back to defaults.nodeSelector.",
    )
    tolerations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Tolerations for node taints. Falls back to defaults.tolerations.",
    )
    affinity: Optional[Dict[str, Any]] = Field(
        None,
        description="Affinity rules. Falls back to defaults.affinity.",
    )
    restartPolicy: Optional[str] = Field(
        "OnFailure",
        description="Pod restart policy: 'OnFailure' (default) or 'Never'.",
    )
    serviceAccount: Optional[ServiceAccountRef] = Field(
        None,
        description="Service account for the job pods.",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the CronJob metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the CronJob metadata.",
    )
    podLabels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the job Pod template.",
    )
    podAnnotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the job Pod template.",
    )


# ============================================================================
# Hook (hook.yaml)
# ============================================================================


class HookConfig(BaseModel):
    """Configuration for a Helm hook job. Hooks run at specific points in the
    Helm lifecycle (install, upgrade, delete, etc.) and are commonly used for
    database migrations, cache warming, or validation checks.

    Each key in the 'hooks' map creates a Job named '<release>-hook-<key>'."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this hook.",
    )
    types: str = Field(
        description="Comma-separated Helm hook types: 'pre-install', 'post-install', "
        "'pre-upgrade', 'post-upgrade', 'pre-delete', 'post-delete', 'pre-rollback', 'post-rollback'. "
        "Example: 'pre-install,pre-upgrade'.",
    )
    weight: Optional[str] = Field(
        None,
        description="Hook execution order (lower runs first). Use negative values (e.g. '-5') "
        "to run before other hooks.",
    )
    deletePolicy: Optional[str] = Field(
        None,
        description="When to delete the hook resource. "
        "Default: 'before-hook-creation,hook-succeeded'. "
        "Add 'hook-failed' to also clean up on failure.",
    )
    backoffLimit: Optional[int] = Field(
        None,
        description="Number of retries before marking the job as failed.",
    )
    activeDeadlineSeconds: Optional[int] = Field(
        None,
        description="Maximum runtime in seconds. The hook is killed if it exceeds this.",
    )
    ttlSecondsAfterFinished: Optional[int] = Field(
        None,
        description="Seconds to keep completed hook pods before garbage collection.",
    )
    image: Optional[ImageConfig] = Field(
        None,
        description="Container image. Falls back to defaults.image if not set.",
    )
    command: Optional[List[str]] = Field(
        None,
        description="Override the container entrypoint, e.g. ['alembic', 'upgrade', 'head'].",
    )
    args: Optional[List[str]] = Field(
        None,
        description="Arguments to the entrypoint.",
    )
    env: Optional[List[EnvVar]] = Field(
        None,
        description="Environment variables for the hook container.",
    )
    envFrom: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Bulk environment injection from ConfigMaps or Secrets.",
    )
    resources: Optional[ResourceRequirements] = Field(
        None,
        description="CPU/memory requests and limits. Falls back to defaults.resources.",
    )
    podSecurityContext: Optional[SecurityContext] = Field(
        None,
        description="Pod-level security context.",
    )
    containerSecurityContext: Optional[SecurityContext] = Field(
        None,
        description="Container-level security context for the hook container.",
    )
    volumeMounts: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Volume mounts for the hook container.",
    )
    volumes: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Pod volumes available to mount.",
    )
    nodeSelector: Optional[Dict[str, str]] = Field(
        None,
        description="Node selector labels. Falls back to defaults.nodeSelector.",
    )
    tolerations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Tolerations for node taints. Falls back to defaults.tolerations.",
    )
    affinity: Optional[Dict[str, Any]] = Field(
        None,
        description="Affinity rules. Falls back to defaults.affinity.",
    )
    restartPolicy: Optional[str] = Field(
        None,
        description="Pod restart policy. Default: 'Never' (hooks should not restart).",
    )
    serviceAccount: Optional[ServiceAccountRef] = Field(
        None,
        description="Service account for the hook pod.",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the hook Job metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the hook Job metadata (in addition to helm.sh/hook).",
    )
    podLabels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the hook Pod template.",
    )
    podAnnotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the hook Pod template.",
    )


# ============================================================================
# Istio (gateway.yaml, virtualservice.yaml, destinationrule.yaml)
# ============================================================================


class IstioGatewayConfig(BaseModel):
    """Istio Gateway configuration. Defines a load balancer at the edge of
    the mesh that receives incoming HTTP/TCP connections. The Gateway binds
    to an Istio ingress gateway workload via the 'selector' field.

    Pair with a VirtualService that references this gateway to route traffic
    to your services."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this Gateway.",
    )
    selector: Optional[Dict[str, str]] = Field(
        None,
        description="Label selector for the Istio ingress gateway workload, "
        "e.g. {istio: ingressgateway}.",
    )
    servers: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Server specifications defining ports, hosts, and TLS settings. "
        "Example: [{port: {number: 443, name: https, protocol: HTTPS}, "
        "hosts: ['api.example.com'], tls: {mode: SIMPLE, credentialName: my-cert}}].",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the Gateway metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the Gateway metadata.",
    )


class IstioVirtualServiceConfig(BaseModel):
    """Istio VirtualService configuration. Defines traffic routing rules
    for requests arriving through a Gateway or from within the mesh.

    Route destinations reference service keys from the 'services' map —
    the chart automatically resolves them to fully-qualified service names."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this VirtualService.",
    )
    hosts: Optional[List[str]] = Field(
        None,
        description="Hostnames this VirtualService applies to, e.g. ['api.example.com'].",
    )
    gateways: Optional[List[str]] = Field(
        None,
        description="Gateway keys from 'istio.gateways' to bind to. "
        "Use 'mesh' for mesh-internal routing.",
    )
    exportTo: Optional[List[str]] = Field(
        None,
        description="Namespaces this VirtualService is visible to. "
        "Use ['.'] to restrict to the current namespace.",
    )
    http: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="HTTP routing rules. Each rule can match on URI, headers, etc. "
        "and route to one or more destinations with weights. "
        "Supports retries, timeouts, fault injection, and rewrites.",
    )
    tcp: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="TCP routing rules for non-HTTP traffic.",
    )
    tls: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="TLS routing rules for passthrough or terminated TLS traffic.",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the VirtualService metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the VirtualService metadata.",
    )


class IstioDestinationRuleConfig(BaseModel):
    """Istio DestinationRule configuration. Defines traffic policies
    (load balancing, connection pools, outlier detection) applied after
    routing to a specific service.

    The 'host' field must reference a service key from the 'services' map."""

    enabled: Optional[bool] = Field(
        None,
        description="Set to false to skip rendering this DestinationRule.",
    )
    host: Optional[str] = Field(
        None,
        description="Service key from the 'services' map to apply this rule to. "
        "Resolved to the full service name automatically.",
    )
    trafficPolicy: Optional[Dict[str, Any]] = Field(
        None,
        description="Traffic policy with load balancing, connection pools, and outlier detection. "
        "Example: {loadBalancer: {simple: LEAST_REQUEST}, "
        "outlierDetection: {consecutiveErrors: 5, interval: 30s}}.",
    )
    subsets: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Named subsets for version-based routing (canary, blue-green). "
        "Each subset defines labels to match a pod subset.",
    )
    exportTo: Optional[List[str]] = Field(
        None,
        description="Namespaces this DestinationRule is visible to.",
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Extra labels on the DestinationRule metadata.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Extra annotations on the DestinationRule metadata.",
    )


class IstioConfig(BaseModel):
    """Istio service mesh configuration. When 'enabled' is true, the chart
    renders Istio networking resources (Gateway, VirtualService, DestinationRule).

    Requires Istio to be installed in the cluster. All Istio resources are
    namespaced and use the networking.istio.io/v1beta1 API."""

    enabled: bool = Field(
        False,
        description="Enable Istio resource rendering. Set to true when deploying to an Istio-enabled cluster.",
    )
    gateways: Optional[Dict[str, IstioGatewayConfig]] = Field(
        None,
        description="Map of Istio Gateways. Each key becomes part of the resource name.",
    )
    virtualServices: Optional[Dict[str, IstioVirtualServiceConfig]] = Field(
        None,
        description="Map of Istio VirtualServices for HTTP/TCP routing rules.",
    )
    destinationRules: Optional[Dict[str, IstioDestinationRuleConfig]] = Field(
        None,
        description="Map of Istio DestinationRules for traffic policies (LB, circuit breaking, etc.).",
    )


# ============================================================================
# ServiceAccount (serviceaccount.yaml)
# ============================================================================


class ServiceAccountConfig(BaseModel):
    """Configuration for a Kubernetes ServiceAccount. Created once per release
    and shared by all deployments. Use annotations to bind to cloud IAM roles
    (e.g. AWS IRSA, GCP Workload Identity)."""

    create: bool = Field(
        True,
        description="Create a ServiceAccount. Set to false to use the 'default' account.",
    )
    name: Optional[str] = Field(
        None,
        description="Override the ServiceAccount name. Defaults to the release fullname.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Annotations on the ServiceAccount. Common use: "
        "{'eks.amazonaws.com/role-arn': 'arn:aws:iam::123456789012:role/my-role'} for AWS IRSA.",
    )
    automountServiceAccountToken: Optional[bool] = Field(
        None,
        description="Whether to auto-mount the ServiceAccount token into pods. "
        "Set to false if the workload doesn't need Kubernetes API access.",
    )


# ============================================================================
# Global
# ============================================================================


class GlobalConfig(BaseModel):
    """Global labels and annotations applied to all resources in the chart.
    Use for org-wide metadata like cost-center tags, team ownership, or
    environment identifiers."""

    labels: Optional[Dict[str, str]] = Field(
        None,
        description="Labels added to every resource's metadata. "
        "Example: {'team': 'data-platform', 'cost-center': 'engineering'}.",
    )
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description="Annotations added to every resource's metadata.",
    )


# ============================================================================
# Root Values Model
# ============================================================================


class HelmValues(BaseModel):
    """Root model for all Golden Chart Helm values.

    This chart uses a map-based configuration model: each major resource type
    (deployments, services, cronjobs, etc.) is a map where the key becomes
    part of the Kubernetes resource name.

    Example:
      deployments:
        data-api:       # creates Deployment '<release>-data-api'
          image: ...
        celery-worker:  # creates Deployment '<release>-celery-worker'
          image: ...
    """

    nameOverride: Optional[str] = Field(
        None,
        description="Override the chart name used in resource names. "
        "Default is the chart name ('golden-chart').",
    )
    fullnameOverride: Optional[str] = Field(
        None,
        description="Fully override the resource name prefix. "
        "When set, all resources are named '<fullnameOverride>-<key>'.",
    )
    namespaceOverride: Optional[str] = Field(
        None,
        description="Override the target namespace. "
        "By default, resources use the namespace from 'helm install -n <ns>'.",
    )
    imagePullSecrets: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Image pull secrets for private registries, applied to all pods. "
        "Example: [{name: 'my-registry-secret'}].",
    )

    global_: Optional[GlobalConfig] = Field(
        None,
        alias="global",
        description="Global labels and annotations applied to all resources.",
    )

    defaults: Optional[Defaults] = Field(
        None,
        description="Default values inherited by all workloads. "
        "Deployments deep-merge with these; hooks and cronjobs use them as fallbacks.",
    )

    deployments: Optional[Dict[str, DeploymentConfig]] = Field(
        None,
        description="Map of Kubernetes Deployments. "
        "Each key creates a Deployment named '<release>-<key>'.",
    )
    services: Optional[Dict[str, ServiceConfig]] = Field(
        None,
        description="Map of Kubernetes Services. "
        "Use 'targetDeployment' to route traffic to a specific deployment.",
    )
    configMaps: Optional[Dict[str, ConfigMapConfig]] = Field(
        None,
        description="Map of ConfigMaps for non-sensitive configuration data.",
    )
    secrets: Optional[Dict[str, SecretConfig]] = Field(
        None,
        description="Map of Secrets for sensitive data. "
        "Consider external secret managers for production.",
    )
    persistentVolumeClaims: Optional[Dict[str, PVCConfig]] = Field(
        None,
        description="Map of PersistentVolumeClaims for durable storage.",
    )
    horizontalPodAutoscalers: Optional[Dict[str, HPAConfig]] = Field(
        None,
        description="Map of HPAs for auto-scaling deployments based on metrics.",
    )
    cronjobs: Optional[Dict[str, CronJobConfig]] = Field(
        None,
        description="Map of CronJobs for scheduled batch processing "
        "(e.g. dbt runs, data quality checks, cleanup tasks).",
    )
    hooks: Optional[Dict[str, HookConfig]] = Field(
        None,
        description="Map of Helm hook jobs that run during install/upgrade lifecycle "
        "(e.g. database migrations, cache warming).",
    )

    istio: Optional[IstioConfig] = Field(
        None,
        description="Istio service mesh configuration (Gateway, VirtualService, DestinationRule).",
    )
    serviceAccount: Optional[ServiceAccountConfig] = Field(
        None,
        description="ServiceAccount configuration shared by all deployments in the release.",
    )

    extraResources: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Arbitrary Kubernetes manifests rendered as-is. "
        "Escape hatch for resources the chart doesn't natively support.",
    )

    class Config:
        extra = "allow"
        populate_by_name = True
