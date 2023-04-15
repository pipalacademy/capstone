job "docker-registry" {
  type = "service"

  group "docker-registry" {
    count = 1

    network {
      port "http" {
        static = 7979
        to     = 5000
      }
    }

    service {
      name     = "docker-registry"
      port     = "http"

      tags = ["capstone-service"]

     meta {
      host = "registry.local.pipal.in"
     }
    }

    task "docker-registry" {
      driver = "docker"

      config {
        image = "registry:2"
        ports = ["http"]
      }
    }
  }
}
