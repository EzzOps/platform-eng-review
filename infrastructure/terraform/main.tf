# Intentionally insecure Terraform for testing
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  # No security group restrictions
  vpc_security_group_ids = []

  root_block_device {
    volume_size = 100
    encrypted   = false
  }

  user_data = <<-EOF
              #!/bin/bash
              export API_KEY="sk-live-abc123def456"
              echo "server started"
              EOF

  tags = {
    Name = "web-server"
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "my-company-secure-data"
  acl    = "public-read"

  versioning {
    enabled = false
  }
}
