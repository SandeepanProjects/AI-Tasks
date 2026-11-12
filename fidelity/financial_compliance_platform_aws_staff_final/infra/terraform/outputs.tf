output "documents_bucket" { value = aws_s3_bucket.documents.bucket }
output "app_task_role_arn" { value = aws_iam_role.app_task.arn }
output "ecs_execution_role_arn" { value = aws_iam_role.ecs_execution.arn }

output "documents_kms_key_arn" { value = aws_kms_key.documents.arn }
