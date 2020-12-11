resource "kubernetes_manifest" "cephcluster_rook_ceph" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "ceph.rook.io/v1"
    "kind" = "CephCluster"
    "metadata" = {
      "name" = "rook-ceph"
      "namespace" = "rook-ceph"
    }
    "spec" = {
      "cephVersion" = {
        "allowUnsupported" = false
        "image" = "ceph/ceph:v15.2.5"
      }
      "dashboard" = {
        "enabled" = true
        "ssl" = true
      }
      "dataDirHostPath" = "/var/lib/rook"
      "disruptionManagement" = {
        "machineDisruptionBudgetNamespace" = "openshift-machine-api"
        "manageMachineDisruptionBudgets" = false
        "managePodBudgets" = false
        "osdMaintenanceTimeout" = 30
      }
      "mon" = {
        "allowMultiplePerNode" = false
        "count" = 3
        "volumeClaimTemplate" = {
          "spec" = {
            "resources" = {
              "requests" = {
                "storage" = "5Gi"
              }
            }
            "storageClassName" = "managed-premium"
          }
        }
      }
      "network" = {
        "hostNetwork" = false
      }
      "storage" = {
        "storageClassDeviceSets" = [
          {
            "count" = 3
            "name" = "set1"
            "placement" = {
              "nodeAffinity" = {
                "requiredDuringSchedulingIgnoredDuringExecution" = {
                  "nodeSelectorTerms" = [
                    {
                      "matchExpressions" = [
                        {
                          "key" = "agentpool"
                          "operator" = "In"
                          "values" = [
                            "rookceph",
                          ]
                        },
                      ]
                    },
                  ]
                }
              }
              "podAntiAffinity" = {
                "preferredDuringSchedulingIgnoredDuringExecution" = [
                  {
                    "podAffinityTerm" = {
                      "labelSelector" = {
                        "matchExpressions" = [
                          {
                            "key" = "app"
                            "operator" = "In"
                            "values" = [
                              "rook-ceph-osd",
                            ]
                          },
                          {
                            "key" = "app"
                            "operator" = "In"
                            "values" = [
                              "rook-ceph-osd-prepare",
                            ]
                          },
                        ]
                      }
                      "topologyKey" = "kubernetes.io/hostname"
                    }
                    "weight" = 100
                  },
                ]
              }
              "tolerations" = [
                {
                  "key" = "storage-node"
                  "operator" = "Exists"
                },
              ]
            }
            "portable" = true
            "resources" = {
              "limits" = {
                "cpu" = "500m"
                "memory" = "4Gi"
              }
              "requests" = {
                "cpu" = "500m"
                "memory" = "2Gi"
              }
            }
            "volumeClaimTemplates" = [
              {
                "metadata" = {
                  "name" = "data"
                }
                "spec" = {
                  "accessModes" = [
                    "ReadWriteOnce",
                  ]
                  "resources" = {
                    "requests" = {
                      "storage" = "35Gi"
                    }
                  }
                  "storageClassName" = "managed-premium"
                  "volumeMode" = "Block"
                }
              },
            ]
          },
        ]
      }
    }
  }
}
