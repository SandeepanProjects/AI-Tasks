variable "aws_region" {
  type    = string
  default = "ap-south-1"
}
variable "project_name" {
  type    = string
  default = "financial-compliance"
}
variable "environment" {
  type    = string
  default = "dev"
}
variable "bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for source compliance documents."
}
variable "bedrock_model_resource_arns" {
  type        = list(string)
  description = "Explicit Bedrock model/inference-profile ARNs the task role may invoke. Keep this allowlist narrow."
  default     = []
}
