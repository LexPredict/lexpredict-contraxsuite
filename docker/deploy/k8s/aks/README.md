# Creating a New Kubernetes Cluster in Azure

Use the scripts in "scripts" folder for running the following steps.

1. Install Azure CLI - no script, https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-apt?view=azure-cli-latest
2. az login
3. Create the cluster. Check available k8s versions if az says the requested version is wrong.
4. Connect kubectl to the cluster.
5. Create cluster role binding for the dashboard - can appear required not only for the dashboard but for something else.
6. Install Helm on the local machine.
6.1. If helm is not yet initialized on the cluster - init helm with creating service account.
7. Install kubeapps.
7.1. Retrieve token for kubeapps.
7.2. Login to kubeapps and enter the token (one time action).
8. Install Cert Manager (manages letsencrypt certificates) - needed for Prometheus/Grafana/Contraxsuite certs.
9. Install Prometheus/Grafana
10. Install rook/ceph