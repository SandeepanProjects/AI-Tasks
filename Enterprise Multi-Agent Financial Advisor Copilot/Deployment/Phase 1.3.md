I can definitely help build this, but I **can't generate an entire production EKS module with all Terraform files in a single response**. A proper Staff-level Phase 1.3 is typically **1,500–3,000+ lines of Terraform** spread across many files (cluster, managed node groups, IAM OIDC provider, IRSA, launch templates, add-ons, autoscaler, outputs, variables, etc.). It would exceed the response limits and I'd end up omitting important pieces or producing inconsistent code.

For a production implementation, Phase 1.3 should include:

```text
terraform/
└── modules/
    └── eks/
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        ├── cluster.tf
        ├── nodegroups.tf
        ├── launch_template.tf
        ├── oidc.tf
        ├── irsa.tf
        ├── addons.tf
        ├── security_groups.tf
        ├── kms.tf
        └── autoscaler.tf
```

The implementation covers:

* Amazon EKS cluster
* Managed node groups
* Private endpoint/public endpoint configuration
* OIDC provider
* IRSA roles
* KMS encryption for Kubernetes secrets
* EKS add-ons (CoreDNS, kube-proxy, VPC CNI, EBS CSI)
* Launch templates
* Cluster Autoscaler
* Security groups
* CloudWatch logging
* Outputs consumed by later Helm deployments

Because these files are tightly coupled, generating only part of them would leave you with code that doesn't deploy.

**The best approach is to build Phase 1.3 incrementally**, exactly as you did for Phases 1.1 and 1.2:

1. **Phase 1.3A** – EKS cluster (cluster.tf, variables.tf, outputs.tf)
2. **Phase 1.3B** – Managed node groups + launch templates
3. **Phase 1.3C** – OIDC + IRSA roles
4. **Phase 1.3D** – EKS add-ons + Cluster Autoscaler
5. **Phase 1.3E** – KMS, security groups, CloudWatch logging

That results in a complete, deployable module instead of a truncated example.

I recommend following that sequence because it's the same order an experienced cloud/platform engineer would use to build a production EKS platform, and each step can be validated with `terraform plan` before moving to the next.
