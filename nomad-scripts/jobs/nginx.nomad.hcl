variable "nginx_port" {
  type    = number
  default = 8080
}

job "nginx" {

  group "nginx" {
    count = 1

    network {
      port "http" {
        static = var.nginx_port
      }
    }

    service {
      name = "nginx"
      port = "http"
    }

    task "nginx" {
      driver = "docker"

      resources {
        cpu    = 100
        memory = 128
      }

      config {
        image = "nginx"
        network_mode = "host"

        ports = ["http"]

        volumes = [
          "local:/etc/nginx/conf.d",
        ]
      }

      template {
        data = <<EOF
server {
    listen {{ env "NOMAD_PORT_http" }} default_server;

    client_max_body_size 0;

    location / {
        add_header 'Content-Type' 'text/plain' always;
        return 404 'Capstone: App not found\n';
    }
}

{{ range services }}

{{ $host := "localhost" }}

# Service: {{ .Name }}

{{ if .Tags | contains "capstone-service" }}

upstream upstream-{{ .Name | toLower }} {
  {{- range service .Name }}
  server {{ .Address }}:{{ .Port }};

  {{ $host = .ServiceMeta.host }}

  {{- end }}
}

server {
   listen {{ env "NOMAD_PORT_http" }};

   server_name {{ $host }};
   client_max_body_size 0;   

   location / {
      proxy_pass http://upstream-{{ .Name | toLower }};
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-Proto $scheme;
   }
}

{{ end }}

{{ end -}}

EOF

        destination   = "local/load-balancer.conf"
        change_mode   = "signal"
        change_signal = "SIGHUP"
      }
    }
  }
}

