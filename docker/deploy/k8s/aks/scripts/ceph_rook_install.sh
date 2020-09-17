#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd > /dev/null

echo "Creating dedicated node pool for Ceph pods..."
az aks nodepool add \
    --cluster-name ${AKS_CLUSTER_NAME} \
    --name ${CEPH_NODE_POOL_NAME} \
    --resource-group ${AKS_RESOURCE_GROUP} \
    --node-count ${CEPH_NODE_COUNT} \
    --node-taints storage-node=true:NoSchedule

COMMON_YAML_MODIFICATION_DATE=$(stat -c %y "ceph_rook_common.yaml")
echo "Applying common.yaml from the rook git repository (local copy of ${COMMON_YAML_MODIFICATION_DATE})..."
kubectl apply -f ceph_rook_common.yaml


echo "Applying operator..."
kubectl apply -f ceph_operator_cs.yaml


until echo "Waiting for ceph operator pod..." && kubectl get pods -n rook-ceph | grep -m 1 "operator" | grep "Running" | grep "1/1"; do sleep 5 ; done

echo "Applying cluster..."
kubectl apply -f ceph_cluster_cs.yaml

until echo "Waiting for ceph osd pods..." && kubectl get pods -n rook-ceph | grep -m 1 "osd-3" | grep "Running" | grep "1/1"; do sleep 5 ; done

echo "Applying ceph block pool..."
kubectl apply -f ceph_cephblockpool_cs.yaml

echo "Applying storage class..."
kubectl apply -f ceph_storageclass_cs.yaml

echo "Testing persistent volume claim..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  storageClassName: rook-ceph-block
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF



kubectl describe pvc test-pvc

