variable "gitto_api_token" {
  type = string
  default = "gitto"
}

variable "gitto_host" {
  type = string
  default = "git.local.pipal.in"
}

job "gitto" {
  type = "service"

  group "gitto" {
    count = 1

    network {
      port "web" {
        static  = 7878
        to      = 7878
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
        host = var.gitto_host
      }
    }

    task "gitto-task" {
      driver = "docker"

      volume_mount {
        volume      = "git-volume"
        destination = "/git"
      }      

      resources {
        cpu    = 100
        memory = 128
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
