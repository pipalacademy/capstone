variable "gitto_api_token" {
  type = string
  default = "gitto"
}

job "gitto" {
  type = "service"

  group "gitto" {
    count = 1

    network {
      port "web" {
        to = 7878
      }
    }

    volume "git-volume" {
      type      = "host"
      source    = "git-volume"
    }

    service {
      name     = "gitto"
      port     = "web"

      tags = ["capstone-service"]

      meta {
        host = "git.local.pipal.in"
      }
    }

    task "gitto-task" {
      driver = "docker"

      volume_mount {
        volume      = "git-volume"
        destination = "/git"
      }      


      env {
        GITTO_API_TOKEN = var.gitto_api_token
        GITTO_ROOT = "/git"      
      }

      config {
        image = "pipalacademy/gitto"
        ports = ["web"]
      }
    }
  }
}
