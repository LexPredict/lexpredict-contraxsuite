#!/bin/bash

kubectl create clusterrolebinding \
    kubernetes-dashboard \
    -n kube-system \
    --clusterrole=cluster-admin \
    --serviceaccount=kube-system:kubernetes-dashboard

