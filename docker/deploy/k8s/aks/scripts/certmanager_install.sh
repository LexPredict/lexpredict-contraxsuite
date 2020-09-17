#!/bin/bash

set -e

kubectl create namespace cert-manager
kubectl apply -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.9/deploy/manifests/00-crds.yaml
helm repo add jetstack https://charts.jetstack.io
kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true
helm install --namespace cert-manager jetstack/cert-manager --version v0.9.0
