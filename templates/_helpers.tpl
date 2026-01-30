{{/*
Expand the name of the chart.
*/}}
{{- define "golden-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "golden-chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "golden-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "golden-chart.labels" -}}
helm.sh/chart: {{ include "golden-chart.chart" . }}
{{ include "golden-chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "golden-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "golden-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "golden-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "golden-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate resource name with component key
Usage: include "golden-chart.resourceName" (dict "context" $ "component" "api")
*/}}
{{- define "golden-chart.resourceName" -}}
{{- $fullname := include "golden-chart.fullname" .context -}}
{{- printf "%s-%s" $fullname .component | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Generate namespace
*/}}
{{- define "golden-chart.namespace" -}}
{{- default .Release.Namespace .Values.namespaceOverride -}}
{{- end }}

{{/*
Service selector labels for targeting specific deployments
Usage: include "golden-chart.serviceSelectorLabels" (dict "context" $ "targetDeployment" "api" "extraLabels" {...})
*/}}
{{- define "golden-chart.serviceSelectorLabels" -}}
app.kubernetes.io/name: {{ include "golden-chart.name" .context }}
app.kubernetes.io/instance: {{ .context.Release.Name }}
app.kubernetes.io/component: {{ .targetDeployment }}
{{- with .extraLabels }}
{{- toYaml . }}
{{- end }}
{{- end }}

{{/*
Resolve service name from service key
*/}}
{{- define "golden-chart.serviceName" -}}
{{ include "golden-chart.resourceName" (dict "context" .context "component" .serviceKey) }}
{{- end }}

{{/*
Resolve Istio gateway name
*/}}
{{- define "golden-chart.istioGatewayName" -}}
{{ include "golden-chart.resourceName" (dict "context" .context "component" .gatewayKey) }}
{{- end }}

{{/*
Resolve gateway reference - handles both string names and objects
*/}}
{{- define "golden-chart.resolveGateway" -}}
{{- if kindIs "string" .gateway -}}
{{ .gateway }}
{{- else -}}
{{ include "golden-chart.istioGatewayName" (dict "context" .context "gatewayKey" .gateway) }}
{{- end -}}
{{- end }}

{{/*
Image pull secrets
*/}}
{{- define "golden-chart.imagePullSecrets" -}}
{{- with .Values.imagePullSecrets }}
imagePullSecrets:
  {{- toYaml . | nindent 2 }}
{{- end }}
{{- end }}

{{/*
Image helper
Usage: include "golden-chart.image" (dict "image" $image)
*/}}
{{- define "golden-chart.image" -}}
{{- $repository := .image.repository | default "nginx" -}}
{{- $tag := .image.tag | default "latest" -}}
{{- printf "%s:%s" $repository $tag -}}
{{- end }}

{{/*
Pod security context
*/}}
{{- define "golden-chart.podSecurityContext" -}}
{{- with .podSecurityContext }}
{{- toYaml . }}
{{- end }}
{{- end }}

{{/*
Container security context
*/}}
{{- define "golden-chart.containerSecurityContext" -}}
{{- with .securityContext }}
{{- toYaml . }}
{{- end }}
{{- end }}
