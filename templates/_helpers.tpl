{{- define "golden-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

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

{{- define "golden-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "golden-chart.labels" -}}
helm.sh/chart: {{ include "golden-chart.chart" . }}
{{ include "golden-chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "golden-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "golden-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "golden-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "golden-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Usage: include "golden-chart.resourceName" (dict "context" $ "component" "api")
*/}}
{{- define "golden-chart.resourceName" -}}
{{- $fullname := include "golden-chart.fullname" .context -}}
{{- printf "%s-%s" $fullname .component | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "golden-chart.namespace" -}}
{{- default .Release.Namespace .Values.namespaceOverride -}}
{{- end }}

{{/*
Usage: include "golden-chart.serviceSelectorLabels" (dict "context" $ "targetDeployment" "api" "extraLabels" {...})
*/}}
{{- define "golden-chart.serviceSelectorLabels" -}}
app.kubernetes.io/name: {{ include "golden-chart.name" .context }}
app.kubernetes.io/instance: {{ .context.Release.Name }}
app.kubernetes.io/component: {{ .targetDeployment }}
{{- with .extraLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{- define "golden-chart.serviceName" -}}
{{ include "golden-chart.resourceName" (dict "context" .context "component" .serviceKey) }}
{{- end }}

{{- define "golden-chart.istioGatewayName" -}}
{{ include "golden-chart.resourceName" (dict "context" .context "component" .gatewayKey) }}
{{- end }}

{{- define "golden-chart.resolveGateway" -}}
{{- if kindIs "string" .gateway -}}
{{ .gateway }}
{{- else -}}
{{ include "golden-chart.istioGatewayName" (dict "context" .context "gatewayKey" .gateway) }}
{{- end -}}
{{- end }}

{{- define "golden-chart.imagePullSecrets" -}}
{{- with .Values.imagePullSecrets }}
imagePullSecrets:
  {{- toYaml . | nindent 2 }}
{{- end }}
{{- end }}
