resource "helm_release" "kube_prometheus_stack" {
    count = var.install_monitoring ? 1 : 0
    repository = "https://prometheus-community.github.io/helm-charts"
    name       = "monitoring"
    chart      = "kube-prometheus-stack"
    timeout    = 600
    create_namespace = true
    namespace = "monitoring"
    #replace = true 
    set {
      name = "grafana.grafana\\.ini.server.domain"
      value = var.grafana_domain
    }
    
    set {
      name = "grafana.grafana\\.ini.server.root_url"
      value = "%(protocol)s://%(domain)s/grafana"
      #type = "string"
    }

    set {
      name = "grafana.grafana\\.ini.server.serve_from_sub_path"
      value = true
    }
    # TODO add configuration for default password change
}