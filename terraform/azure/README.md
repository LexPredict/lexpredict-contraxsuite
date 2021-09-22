# AKS setup

## Requirments

- azure CLI
- terrafrom >=1.0
- helm
- kubeclt

## Resources

> NOTE Describe after first release

## First Install

### 1.Get Azure credentials

```bash
az login
az ad sp create-for-rbac --skip-assignment
```

### 2. Review and create var files

create `terraform.tfvars` file from `terraform.tfvars_example` with `appId` and`password` from previous step
create `rook-ceph-value.yaml` from `.rook-ceph/rook-ceph-values.yaml`

### 3. Create Azure resources

```bash
terraform init
terraform plan
terraform apply
# see valuse in terraform.tfvars
```

### 4. Connect to AKS Cluster to allow Terraform to

```sh
az aks get-credentials --resource-group {resource_group_name} --name {aks_dns_prefix}-aks
kubectl get no # test connection
```

### 5. Install required K8s resorses from helm charts

1. Check if cluster deployed seccesfully
2. Set "true" for helm charts you want to deploy in `terraform.tfvars` file. *Important!!!* Don't set `true` for ceph_cluster (see next)
3. Run review and apply changes with `terraform plan` and `terraform apply`

### 6. Deploy Rook Ceph Storage Resources

1. Set "true" for `ceph_storage_cluseter` module.
2. Run review and apply changes with `terraform plan` and `terraform apply`

---

## Administration

### Get external ingress IP

```bash
kubectl --namespace ingress get services ingress-ingress-nginx-controller
```

### Get grafana password

```bash
kubectl get secret prometheus-operator-grafana -o jsonpath=”{.data.admin-password}” | base64 --decode ; echo
```

### Control (Strat/Stop) cluster

```sh
az aks stop --resource-group {resource_group_name} --name {aks_dns_prefix}-aks
az aks start --resource-group {resource_group_name} --name {aks_dns_prefix}-aks
```

### Protect cluster with Allowed IP range

```sh
kubectl -n conrtaxsuite annotate ingress contrax-ingress nginx.ingress.kubernetes.io/whitelist-source-range="34.238.73.199/32"
```
