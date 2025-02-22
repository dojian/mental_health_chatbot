resource "aws_ecr_repository" "genzen" {
  name = "genzen_repo"
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
    Created_By  = "Terraform"
  }
}