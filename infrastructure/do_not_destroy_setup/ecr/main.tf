resource "aws_ecr_repository" "genzen" {
  name = "backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "GenZen"
    Environment = "Dev"
    Type        = "Backend"
    Created_By  = "Terraform"
  }
}

resource "aws_ecr_repository" "genzen" {
  name = "frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "GenZen"
    Environment = "Dev"
    Type        = "Frontend"
    Created_By  = "Terraform"
  }
}