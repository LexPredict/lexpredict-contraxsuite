#!/bin/bash



echo "Opening kubeapps dashboard..."
export POD_NAME=$(kubectl get pods -n kubeapps -l "app=kubeapps,release=kubeapps" -o jsonpath="{.items[0].metadata.name}")
echo "Visit http://127.0.0.1:8080 in your browser to access the Kubeapps Dashboard"
kubectl port-forward -n kubeapps $POD_NAME 8080:8080
