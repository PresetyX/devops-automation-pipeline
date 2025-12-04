output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "backup_bucket" {
  value = aws_s3_bucket.backups.bucket
}
