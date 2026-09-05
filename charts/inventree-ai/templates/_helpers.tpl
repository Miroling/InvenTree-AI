{{- define "inventree-ai.name" -}}
{{- printf "%s-inventree-ai" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "inventree-ai.selectorLabels" -}}
app.kubernetes.io/name: inventree-ai
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "inventree-ai.labels" -}}
{{ include "inventree-ai.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | quote }}
{{- end -}}
