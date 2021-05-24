# AKS setup

## Requirments

- azure CLI
- terrafrom >=14.8
- helm
- kubeclt

## Resources

## First Install

### Get Azure credentials

```bash
az login
az ad sp create-for-rbac --skip-assignment
```

### Create files

create `terraform.tfvars` file from `terraform.tfvars_example` with `appId` and`password` from previous step
create `rook-ceph-value.yaml` from `.rook-ceph/rook-ceph-values.yaml`

### Create Azure resources

```bash
terraform init
terraform plan
terraform apply
# see valuse in terraform.tfvars
az aks get-credentials --resource-group {resource_group_name} --name {aks_dns_prefix}-aks
kubectl get no
```

### Install required helm charts

1. Check if cluster deployed seccesfully
2. Set "true" for helm charts you want to deploy in helm module
3. Run review and apply changes with `terraform plan` and `terraform apply`

### Deploy Rook Ceph Cluster Configuration

1. Set "true" for `ceph_storage_cluseter` module.
2. Run review and apply changes with `terraform plan` and `terraform apply`

### Get external ingress IP

```bash
kubectl --namespace ingress get services ingress-nginx-ingress-controller
```

### Get grafana password

```bash
kubectl get secret prometheus-operator-grafana -o jsonpath=”{.data.admin-password}” | base64 --decode ; echo
```

## Development

### Control cluster

```sh
az aks stop --resource-group {resource_group_name} --name {aks_dns_prefix}-aks
az aks start --resource-group {resource_group_name} --name {aks_dns_prefix}-aks
```

### Protect cluster with Allowed IP range

```sh
kubectl -n conrtaxsuite annotate ingress contrax-ingress nginx.ingress.kubernetes.io/whitelist-source-range="34.238.73.199/32"
```
