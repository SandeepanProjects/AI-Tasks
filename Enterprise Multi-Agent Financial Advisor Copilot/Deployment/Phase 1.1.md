Good. Let's build this like a real Staff Engineer would.

# Phase 1.1 Goal

Build production-grade AWS networking that all later services will use:

```text
AWS Account
│
└── VPC
    │
    ├── Public Subnet A
    ├── Public Subnet B
    │
    ├── Private Subnet A
    ├── Private Subnet B
    │
    ├── Internet Gateway
    │
    ├── NAT Gateway
    │
    ├── Route Tables
    │
    └── Security Groups
```

Later:

```text
EKS
RDS
ElastiCache
ALB
```

will be deployed inside these subnets.

---

# Folder Structure

```text
terraform/
│
├── versions.tf
├── providers.tf
├── backend.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
│
└── modules/
    └── vpc/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

---

# versions.tf

```hcl
terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }
}
```

---

# providers.tf

```hcl
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "financial-advisor-copilot"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
```

---

# backend.tf

Use S3 remote state.

```hcl
terraform {
  backend "s3" {
    bucket         = "financial-advisor-tf-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

---

# variables.tf

```hcl
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "prod"
}
```

---

# terraform.tfvars

```hcl
aws_region = "us-east-1"

environment = "prod"
```

---

# Root main.tf

```hcl
module "vpc" {
  source = "./modules/vpc"

  environment = var.environment

  vpc_cidr = "10.0.0.0/16"

  public_subnets = [
    "10.0.1.0/24",
    "10.0.2.0/24"
  ]

  private_subnets = [
    "10.0.10.0/24",
    "10.0.20.0/24"
  ]

  availability_zones = [
    "us-east-1a",
    "us-east-1b"
  ]
}
```

---

# outputs.tf

```hcl
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "public_subnets" {
  value = module.vpc.public_subnets
}
```

---

# modules/vpc/variables.tf

```hcl
variable "environment" {}

variable "vpc_cidr" {}

variable "public_subnets" {
  type = list(string)
}

variable "private_subnets" {
  type = list(string)
}

variable "availability_zones" {
  type = list(string)
}
```

---

# modules/vpc/main.tf

## VPC

```hcl
resource "aws_vpc" "main" {

  cidr_block           = var.vpc_cidr

  enable_dns_hostnames = true

  enable_dns_support   = true

  tags = {
    Name = "${var.environment}-vpc"
  }
}
```

---

## Internet Gateway

```hcl
resource "aws_internet_gateway" "igw" {

  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.environment}-igw"
  }
}
```

---

## Public Subnets

```hcl
resource "aws_subnet" "public" {

  count = length(var.public_subnets)

  vpc_id = aws_vpc.main.id

  cidr_block = var.public_subnets[count.index]

  availability_zone =
    var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-${count.index}"
  }
}
```

---

## Private Subnets

```hcl
resource "aws_subnet" "private" {

  count = length(var.private_subnets)

  vpc_id = aws_vpc.main.id

  cidr_block = var.private_subnets[count.index]

  availability_zone =
    var.availability_zones[count.index]

  tags = {
    Name = "${var.environment}-private-${count.index}"
  }
}
```

---

## Elastic IP

```hcl
resource "aws_eip" "nat" {

  domain = "vpc"

  tags = {
    Name = "${var.environment}-nat-eip"
  }
}
```

---

## NAT Gateway

```hcl
resource "aws_nat_gateway" "nat" {

  allocation_id = aws_eip.nat.id

  subnet_id =
    aws_subnet.public[0].id

  tags = {
    Name = "${var.environment}-nat"
  }

  depends_on = [
    aws_internet_gateway.igw
  ]
}
```

---

## Public Route Table

```hcl
resource "aws_route_table" "public" {

  vpc_id = aws_vpc.main.id

  route {

    cidr_block = "0.0.0.0/0"

    gateway_id =
      aws_internet_gateway.igw.id
  }
}
```

---

## Associate Public Subnets

```hcl
resource "aws_route_table_association" "public" {

  count = length(aws_subnet.public)

  subnet_id =
    aws_subnet.public[count.index].id

  route_table_id =
    aws_route_table.public.id
}
```

---

## Private Route Table

```hcl
resource "aws_route_table" "private" {

  vpc_id = aws_vpc.main.id

  route {

    cidr_block = "0.0.0.0/0"

    nat_gateway_id =
      aws_nat_gateway.nat.id
  }
}
```

---

## Associate Private Subnets

```hcl
resource "aws_route_table_association" "private" {

  count = length(aws_subnet.private)

  subnet_id =
    aws_subnet.private[count.index].id

  route_table_id =
    aws_route_table.private.id
}
```

---

## EKS Security Group

```hcl
resource "aws_security_group" "eks" {

  name = "${var.environment}-eks-sg"

  description = "EKS Security Group"

  vpc_id = aws_vpc.main.id
}
```

---

## Internal Traffic

```hcl
resource "aws_security_group_rule" "eks_internal" {

  type = "ingress"

  from_port = 0

  to_port = 65535

  protocol = "tcp"

  self = true

  security_group_id =
    aws_security_group.eks.id
}
```

---

## Outbound

```hcl
resource "aws_security_group_rule" "eks_outbound" {

  type = "egress"

  from_port = 0

  to_port = 0

  protocol = "-1"

  cidr_blocks = ["0.0.0.0/0"]

  security_group_id =
    aws_security_group.eks.id
}
```

---

# modules/vpc/outputs.tf

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnets" {
  value = aws_subnet.private[*].id
}

output "public_subnets" {
  value = aws_subnet.public[*].id
}

output "eks_security_group" {
  value = aws_security_group.eks.id
}
```

---

# Deployment Commands

Initialize:

```bash
terraform init
```

Validate:

```bash
terraform validate
```

Plan:

```bash
terraform plan
```

Deploy:

```bash
terraform apply
```

---

# AWS Resources Created

After apply:

```text
VPC

2 Public Subnets

2 Private Subnets

Internet Gateway

NAT Gateway

Route Tables

Elastic IP

EKS Security Group
```

---

# What Comes Next

Phase 1.2 should create:

```text
terraform/modules/

├── ecr/
├── iam/
```

and provision:

```text
ECR Repositories

EKS IAM Roles

Node Group Roles

IRSA Roles

OpenTelemetry Roles

MLflow Roles
```

These are required before we can build the EKS cluster in Phase 1.3.






