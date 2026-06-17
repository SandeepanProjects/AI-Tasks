Excellent. Now we build **Phase 1.2: ECR + IAM Foundation**.

At this point we already have:

```text
VPC
Subnets
NAT
Security Groups
```

Next we need:

```text
ECR
IAM
OIDC Preparation
IRSA Foundation
EKS Cluster Roles
Node Group Roles
```

Without these, EKS cannot be created.

---

# Updated Folder Structure

```text
terraform/
│
├── modules/
│   ├── vpc/
│   ├── ecr/
│   └── iam/
│
├── main.tf
├── variables.tf
├── outputs.tf
```

---

# Root main.tf

Add:

```hcl
module "ecr" {
  source = "./modules/ecr"

  environment = var.environment
}

module "iam" {
  source = "./modules/iam"

  environment = var.environment
}
```

---

# ECR Module

---

## modules/ecr/variables.tf

```hcl
variable "environment" {
  type = string
}
```

---

## modules/ecr/main.tf

### API Repository

```hcl
resource "aws_ecr_repository" "api" {

  name = "${var.environment}-advisor-api"

  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}
```

---

### Worker Repository

```hcl
resource "aws_ecr_repository" "worker" {

  name = "${var.environment}-advisor-worker"

  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}
```

---

### MLflow Repository

```hcl
resource "aws_ecr_repository" "mlflow" {

  name = "${var.environment}-mlflow"

  image_scanning_configuration {
    scan_on_push = true
  }
}
```

---

### Lifecycle Policy

Deletes old images.

```hcl
resource "aws_ecr_lifecycle_policy" "api_policy" {

  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1

      description = "Keep latest 20 images"

      selection = {
        tagStatus = "any"

        countType = "imageCountMoreThan"

        countNumber = 20
      }

      action = {
        type = "expire"
      }
    }]
  })
}
```

---

## modules/ecr/outputs.tf

```hcl
output "api_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "worker_repository_url" {
  value = aws_ecr_repository.worker.repository_url
}

output "mlflow_repository_url" {
  value = aws_ecr_repository.mlflow.repository_url
}
```

---

# IAM Module

---

## modules/iam/variables.tf

```hcl
variable "environment" {
  type = string
}
```

---

## modules/iam/main.tf

---

# EKS Cluster Role

```hcl
resource "aws_iam_role" "eks_cluster_role" {

  name = "${var.environment}-eks-cluster-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "eks.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}
```

---

### Attach EKS Policy

```hcl
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {

  role = aws_iam_role.eks_cluster_role.name

  policy_arn =
    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}
```

---

# Node Group Role

```hcl
resource "aws_iam_role" "eks_node_role" {

  name = "${var.environment}-eks-node-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "ec2.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}
```

---

### Worker Node Policy

```hcl
resource "aws_iam_role_policy_attachment" "worker_node" {

  role = aws_iam_role.eks_node_role.name

  policy_arn =
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}
```

---

### CNI Policy

```hcl
resource "aws_iam_role_policy_attachment" "cni" {

  role = aws_iam_role.eks_node_role.name

  policy_arn =
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}
```

---

### ECR Read Policy

```hcl
resource "aws_iam_role_policy_attachment" "ecr_read" {

  role = aws_iam_role.eks_node_role.name

  policy_arn =
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}
```

---

# CloudWatch Role

Used by OpenTelemetry.

```hcl
resource "aws_iam_role" "cloudwatch_role" {

  name = "${var.environment}-cloudwatch-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "ec2.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}
```

---

### CloudWatch Policy

```hcl
resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {

  role = aws_iam_role.cloudwatch_role.name

  policy_arn =
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}
```

---

# Secrets Manager Policy

For application secrets.

```hcl
resource "aws_iam_policy" "secrets_manager" {

  name = "${var.environment}-secrets-manager"

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Action = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ]

      Resource = "*"
    }]
  })
}
```

---

# MLflow Role

```hcl
resource "aws_iam_role" "mlflow_role" {

  name = "${var.environment}-mlflow-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "ec2.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}
```

---

### S3 Access

MLflow artifacts.

```hcl
resource "aws_iam_role_policy_attachment" "mlflow_s3" {

  role = aws_iam_role.mlflow_role.name

  policy_arn =
    "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
```

---

## modules/iam/outputs.tf

```hcl
output "eks_cluster_role_arn" {
  value = aws_iam_role.eks_cluster_role.arn
}

output "eks_node_role_arn" {
  value = aws_iam_role.eks_node_role.arn
}

output "cloudwatch_role_arn" {
  value = aws_iam_role.cloudwatch_role.arn
}

output "mlflow_role_arn" {
  value = aws_iam_role.mlflow_role.arn
}
```

---

# Root Outputs

Append:

```hcl
output "api_ecr" {
  value = module.ecr.api_repository_url
}

output "worker_ecr" {
  value = module.ecr.worker_repository_url
}

output "eks_cluster_role" {
  value = module.iam.eks_cluster_role_arn
}
```

---

# Deploy

```bash
terraform fmt
terraform validate

terraform plan

terraform apply
```

---

# AWS Resources Created

After Phase 1.2:

```text
VPC
Subnets
NAT Gateway
Internet Gateway

ECR
 ├── advisor-api
 ├── advisor-worker
 └── mlflow

IAM
 ├── EKS Cluster Role
 ├── EKS Node Role
 ├── CloudWatch Role
 ├── MLflow Role
 └── Secrets Policy
```

---

# Staff-Level Improvement Before Phase 1.3

For a truly production-grade implementation, I would further enhance Phase 1.2 with:

```text
IAM OIDC Provider
IRSA Roles
External DNS Role
ALB Controller Role
Cluster Autoscaler Role
OpenTelemetry Role
Secrets Store CSI Role
```

Those will be required when we create the EKS cluster in **Phase 1.3 (Production EKS Cluster + Managed Node Groups + OIDC + IRSA)**.
