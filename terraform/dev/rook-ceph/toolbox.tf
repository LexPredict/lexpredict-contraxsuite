resource "kubernetes_manifest" "deployment_rook_ceph_tools" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "apps/v1"
    "kind" = "Deployment"
    "metadata" = {
      "labels" = {
        "app" = "rook-ceph-tools"
      }
      "name" = "rook-ceph-tools"
      "namespace" = "rook-ceph"
    }
    "spec" = {
      "replicas" = 1
      "selector" = {
        "matchLabels" = {
          "app" = "rook-ceph-tools"
        }
      }
      "template" = {
        "metadata" = {
          "labels" = {
            "app" = "rook-ceph-tools"
          }
        }
        "spec" = {
          "containers" = [
            {
              "args" = [
                "-g",
                "--",
                "/usr/local/bin/toolbox.sh",
              ]
              "command" = [
                "/tini",
              ]
              "env" = [
                {
                  "name" = "ROOK_CEPH_USERNAME"
                  "valueFrom" = {
                    "secretKeyRef" = {
                      "key" = "ceph-username"
                      "name" = "rook-ceph-mon"
                    }
                  }
                },
                {
                  "name" = "ROOK_CEPH_SECRET"
                  "valueFrom" = {
                    "secretKeyRef" = {
                      "key" = "ceph-secret"
                      "name" = "rook-ceph-mon"
                    }
                  }
                },
              ]
              "image" = "rook/ceph:master"
              "imagePullPolicy" = "IfNotPresent"
              "name" = "rook-ceph-tools"
              "volumeMounts" = [
                {
                  "mountPath" = "/etc/ceph"
                  "name" = "ceph-config"
                },
                {
                  "mountPath" = "/etc/rook"
                  "name" = "mon-endpoint-volume"
                },
              ]
            },
          ]
          "dnsPolicy" = "ClusterFirstWithHostNet"
          "tolerations" = [
            {
              "effect" = "NoExecute"
              "key" = "node.kubernetes.io/unreachable"
              "operator" = "Exists"
              "tolerationSeconds" = 5
            },
          ]
          "volumes" = [
            {
              "configMap" = {
                "items" = [
                  {
                    "key" = "data"
                    "path" = "mon-endpoints"
                  },
                ]
                "name" = "rook-ceph-mon-endpoints"
              }
              "name" = "mon-endpoint-volume"
            },
            {
              "emptyDir" = {}
              "name" = "ceph-config"
            },
          ]
        }
      }
    }
  }
}
