
### First install
```bash
az login
az ad sp create-for-rbac --skip-assignment
```

create .tfvars file with `appId` and`password`

```bash
terraform init
terraform plan
terraform apply
az aks get-credentials --resource-group dev-contraxuite-cluster --name dev-contraxuite-cluster-aks
kubectl get no
```

##### Get external ingress IP
```bash
kubectl --namespace ingress get services ingress-nginx-ingress-controller
```

##### Get grafana password
```bash
kubectl get secret prometheus-operator-grafana -o jsonpath=”{.data.admin-password}” | base64 --decode ; echo
```