variable "region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "devops-automation-pipeline"
}

variable "backup_retention_days" {
  type    = number
  default = 30
}
