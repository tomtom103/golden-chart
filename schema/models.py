"""
Pydantic models for Golden Helm Chart values.yaml
This provides type checking and generates JSON schema for LSP support
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# ============================================================================
# Common/Shared Models
# ============================================================================


class ImageConfig(BaseModel):
    """Container image configuration"""

    repository: Optional[str] = None
    tag: Optional[str] = None
    pullPolicy: Optional[str] = Field(None, pattern="^(Always|Never|IfNotPresent)$")


class EnvVar(BaseModel):
    """Environment variable configuration"""

    name: str
    value: Optional[str] = None
    valueFrom: Optional[Dict[str, Any]] = None


class ResourceRequirements(BaseModel):
    """CPU and memory resource requirements"""

    requests: Optional[Dict[str, str]] = None
    limits: Optional[Dict[str, str]] = None


class SecurityContext(BaseModel):
    """Security context for containers and pods"""

    runAsNonRoot: Optional[bool] = None
    runAsUser: Optional[int] = None
    runAsGroup: Optional[int] = None
    fsGroup: Optional[int] = None
    readOnlyRootFilesystem: Optional[bool] = None
    allowPrivilegeEscalation: Optional[bool] = None
    capabilities: Optional[Dict[str, List[str]]] = None
    seccompProfile: Optional[Dict[str, str]] = None


class ProbeConfig(BaseModel):
    """Health probe configuration"""

    enabled: Optional[bool] = None
    httpGet: Optional[Dict[str, Any]] = None
    exec_: Optional[Dict[str, Any]] = Field(None, alias="exec")
    tcpSocket: Optional[Dict[str, Any]] = None
    grpc: Optional[Dict[str, Any]] = None
    initialDelaySeconds: Optional[int] = None
    periodSeconds: Optional[int] = None
    timeoutSeconds: Optional[int] = None
    successThreshold: Optional[int] = None
    failureThreshold: Optional[int] = None

    class Config:
        populate_by_name = True


class ContainerPort(BaseModel):
    """Container port configuration"""

    name: str
    containerPort: int
    protocol: Optional[str] = "TCP"


# ============================================================================
# Defaults
# ============================================================================


class Defaults(BaseModel):
    """Default values inherited by all resources"""

    image: Optional[ImageConfig] = None
    replicas: Optional[int] = None
    resources: Optional[ResourceRequirements] = None
    securityContext: Optional[SecurityContext] = None
    env: Optional[List[EnvVar]] = None
    annotations: Optional[Dict[str, str]] = None
    labels: Optional[Dict[str, str]] = None


# ============================================================================
# Deployment
# ============================================================================


class DeploymentConfig(BaseModel):
    """Configuration for a Kubernetes Deployment"""

    enabled: Optional[bool] = Field(None, description="Set to false to disable")
    image: Optional[ImageConfig] = None
    replicas: Optional[int] = None
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    ports: Optional[List[ContainerPort]] = None
    env: Optional[List[EnvVar]] = None
    resources: Optional[ResourceRequirements] = None
    securityContext: Optional[SecurityContext] = None
    livenessProbe: Optional[ProbeConfig] = None
    readinessProbe: Optional[ProbeConfig] = None
    startupProbe: Optional[ProbeConfig] = None
    volumeMounts: Optional[List[Dict[str, Any]]] = None
    volumes: Optional[List[Dict[str, Any]]] = None
    lifecycle: Optional[Dict[str, Any]] = None
    annotations: Optional[Dict[str, str]] = None
    podAnnotations: Optional[Dict[str, str]] = None


# ============================================================================
# Service
# ============================================================================


class ServicePort(BaseModel):
    """Service port configuration"""

    name: Optional[str] = None
    port: int
    targetPort: Optional[Any] = None  # Can be int or string
    protocol: Optional[str] = "TCP"


class ServiceConfig(BaseModel):
    """Configuration for a Kubernetes Service"""

    enabled: Optional[bool] = None
    type: Optional[str] = Field(None, pattern="^(ClusterIP|NodePort|LoadBalancer)$")
    targetDeployment: Optional[str] = Field(
        None, description="Deployment key to target"
    )
    ports: Optional[List[ServicePort]] = None
    annotations: Optional[Dict[str, str]] = None


# ============================================================================
# ConfigMap and Secret
# ============================================================================


class ConfigMapConfig(BaseModel):
    """Configuration for ConfigMap"""

    enabled: Optional[bool] = None
    data: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None


class SecretConfig(BaseModel):
    """Configuration for Secret"""

    enabled: Optional[bool] = None
    type: Optional[str] = "Opaque"
    data: Optional[Dict[str, str]] = None
    stringData: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None


# ============================================================================
# PVC
# ============================================================================


class PVCConfig(BaseModel):
    """Configuration for PersistentVolumeClaim"""

    enabled: Optional[bool] = None
    accessModes: Optional[List[str]] = None
    resources: Optional[Dict[str, Any]] = None
    storageClassName: Optional[str] = None


# ============================================================================
# HPA
# ============================================================================


class HPAConfig(BaseModel):
    """Configuration for HorizontalPodAutoscaler"""

    enabled: Optional[bool] = None
    targetDeployment: str = Field(..., description="Deployment key to target")
    minReplicas: Optional[int] = 2
    maxReplicas: Optional[int] = 10
    metrics: Optional[List[Dict[str, Any]]] = None
    behavior: Optional[Dict[str, Any]] = None


# ============================================================================
# CronJob
# ============================================================================


class CronJobConfig(BaseModel):
    """Configuration for CronJob"""

    enabled: Optional[bool] = None
    schedule: str
    image: Optional[ImageConfig] = None
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    env: Optional[List[EnvVar]] = None
    resources: Optional[ResourceRequirements] = None
    restartPolicy: Optional[str] = "OnFailure"


# ============================================================================
# Hook
# ============================================================================


class HookConfig(BaseModel):
    """Configuration for Helm hooks"""

    enabled: Optional[bool] = None
    types: str  # Helm hook types: pre-install, post-install, pre-upgrade, etc.
    weight: Optional[str] = None
    deletePolicy: Optional[str] = None
    backoffLimit: Optional[int] = None
    activeDeadlineSeconds: Optional[int] = None
    ttlSecondsAfterFinished: Optional[int] = None
    image: Optional[ImageConfig] = None
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    env: Optional[List[EnvVar]] = None
    envFrom: Optional[List[Dict[str, Any]]] = None
    volumeMounts: Optional[List[Dict[str, Any]]] = None
    volumes: Optional[List[Dict[str, Any]]] = None
    resources: Optional[ResourceRequirements] = None
    podSecurityContext: Optional[SecurityContext] = None
    containerSecurityContext: Optional[SecurityContext] = None
    nodeSelector: Optional[Dict[str, str]] = None
    tolerations: Optional[List[Dict[str, Any]]] = None
    affinity: Optional[Dict[str, Any]] = None
    restartPolicy: Optional[str] = None
    serviceAccount: Optional[Dict[str, Any]] = None
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None
    podLabels: Optional[Dict[str, str]] = None
    podAnnotations: Optional[Dict[str, str]] = None


# ============================================================================
# Istio (Simplified - Gateway, VirtualService, DestinationRule only)
# ============================================================================


class IstioGatewayConfig(BaseModel):
    """Istio Gateway configuration"""

    enabled: Optional[bool] = None
    servers: Optional[List[Dict[str, Any]]] = None
    selector: Optional[Dict[str, str]] = None


class IstioVirtualServiceConfig(BaseModel):
    """Istio VirtualService configuration"""

    enabled: Optional[bool] = None
    hosts: Optional[List[str]] = None
    gateways: Optional[List[str]] = None
    http: Optional[List[Dict[str, Any]]] = None


class IstioDestinationRuleConfig(BaseModel):
    """Istio DestinationRule configuration"""

    enabled: Optional[bool] = None
    targetService: Optional[str] = None
    trafficPolicy: Optional[Dict[str, Any]] = None


class IstioConfig(BaseModel):
    """Istio service mesh configuration (simplified)"""

    enabled: bool = False
    gateways: Optional[Dict[str, IstioGatewayConfig]] = None
    virtualServices: Optional[Dict[str, IstioVirtualServiceConfig]] = None
    destinationRules: Optional[Dict[str, IstioDestinationRuleConfig]] = None


# ============================================================================
# ServiceAccount
# ============================================================================


class ServiceAccountConfig(BaseModel):
    """Configuration for ServiceAccount"""

    create: bool = True
    name: Optional[str] = None
    annotations: Optional[Dict[str, str]] = None


# ============================================================================
# Root Values Model
# ============================================================================


class HelmValues(BaseModel):
    """Root model for all Helm chart values"""

    # Global settings
    nameOverride: Optional[str] = Field(None, description="Override the chart name")
    fullnameOverride: Optional[str] = Field(
        None, description="Override the full resource name"
    )

    # Defaults
    defaults: Optional[Defaults] = Field(
        None, description="Default values inherited by all resources"
    )

    # Core resources
    deployments: Optional[Dict[str, DeploymentConfig]] = Field(
        None, description="Map of deployments"
    )
    services: Optional[Dict[str, ServiceConfig]] = Field(
        None, description="Map of services"
    )

    # Configuration
    configMaps: Optional[Dict[str, ConfigMapConfig]] = Field(
        None, description="Map of configmaps"
    )
    secrets: Optional[Dict[str, SecretConfig]] = Field(
        None, description="Map of secrets"
    )
    persistentVolumeClaims: Optional[Dict[str, PVCConfig]] = Field(
        None, description="Map of PVCs"
    )

    # Scaling
    horizontalPodAutoscalers: Optional[Dict[str, HPAConfig]] = Field(
        None, description="Map of HPAs"
    )

    # Jobs
    cronjobs: Optional[Dict[str, CronJobConfig]] = Field(
        None, description="Map of cronjobs"
    )
    hooks: Optional[Dict[str, HookConfig]] = Field(None, description="Map of hooks")

    # Service mesh
    istio: Optional[IstioConfig] = Field(None, description="Istio configuration")

    # ServiceAccount
    serviceAccount: Optional[ServiceAccountConfig] = Field(
        None, description="ServiceAccount configuration"
    )

    # Image pull secrets
    imagePullSecrets: Optional[List[Dict[str, str]]] = Field(
        None, description="Image pull secrets"
    )

    class Config:
        extra = "allow"
