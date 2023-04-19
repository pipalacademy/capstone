job "consul" {
  datacenters = ["dc1"]  
  
  group "consul" {
    count = 1
    
    task "consul" {
      driver = "raw_exec"
            
      config {
        command = "consul"
        args    = ["agent", "-dev"]
      }      
      
      artifact {
        source = "https://releases.hashicorp.com/consul/1.15.2/consul_1.15.2_linux_amd64.zip"
      }
    }
  }
}