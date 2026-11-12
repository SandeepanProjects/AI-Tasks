resource "aws_s3_bucket" "documents" {
  bucket = var.bucket_name
  force_destroy = false
  tags = { Project = var.project_name, Environment = var.environment, DataClass = "confidential" }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_kms_key" "documents" {
  description             = "Encryption key for ${var.project_name} ${var.environment} source documents"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  tags = { Project = var.project_name, Environment = var.environment }
}
resource "aws_kms_alias" "documents" {
  name          = "alias/${var.project_name}-${var.environment}-documents"
  target_key_id = aws_kms_key.documents.key_id
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.documents.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    id = "abort-incomplete-multipart-and-expire-noncurrent"
    status = "Enabled"
    filter {}
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
}

resource "aws_s3_bucket_policy" "tls_only" {
  bucket = aws_s3_bucket.documents.id
  depends_on = [aws_s3_bucket_public_access_block.documents]
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Sid = "DenyInsecureTransport", Effect = "Deny", Principal = "*",
      Action = "s3:*", Resource = [aws_s3_bucket.documents.arn, "${aws_s3_bucket.documents.arn}/*"],
      Condition = { Bool = { "aws:SecureTransport" = "false" } } }]
  })
}

resource "aws_iam_role" "app_task" {
  name = "${var.project_name}-${var.environment}-app-task"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow",
    Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
  tags = { Project = var.project_name, Environment = var.environment }
}

resource "aws_iam_role_policy" "app_task" {
  name = "${var.project_name}-${var.environment}-runtime-access"
  role = aws_iam_role.app_task.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = concat([
      { Sid = "TenantDocumentObjects", Effect = "Allow", Action = ["s3:PutObject", "s3:GetObject", "s3:GetObjectVersion"], Resource = "${aws_s3_bucket.documents.arn}/*" },
      { Sid = "TextractAsyncRead", Effect = "Allow", Action = ["textract:StartDocumentTextDetection", "textract:GetDocumentTextDetection"], Resource = "*" },
      { Sid = "DocumentKmsEncryption", Effect = "Allow", Action = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"], Resource = aws_kms_key.documents.arn }
    ], length(var.bedrock_model_resource_arns) > 0 ? [
      { Sid = "InvokeApprovedBedrockModels", Effect = "Allow", Action = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"], Resource = var.bedrock_model_resource_arns }
    ] : [])
  })
}

resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-${var.environment}-ecs-execution"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow",
    Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}
resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
