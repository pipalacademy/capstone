job "nginx" {

  group "nginx" {
    count = 1

    network {
      port "http" {
        static = 8080
      }
    }

    service {
      name = "nginx"
      port = "http"
    }

    task "nginx" {
      driver = "docker"

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
   listen 8080;

   server_name {{ $host }};
   client_max_body_size 0;   

   location / {
      proxy_pass http://upstream-{{ .Name | toLower }};
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

