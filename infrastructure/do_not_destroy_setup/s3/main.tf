# Create a bucket
resource "aws_s3_bucket" "genzen" {
  bucket = "my-genzen-bucket"

  tags = {
    Name        = "GenZen"
    Environment = "Dev"
    Created_By  = "Terraform"
  }
}

# Enale versioning
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.genzen.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable blocking public access
resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.genzen.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable server-side encryption using default AWS key
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.genzen.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}