# Terraform Usage

Reference: `docs/setup/gcp_terraform_deployment.md` and `docs/setup/deployment.md`.

## Quickstart
1. `terraform init`
2. `terraform plan -var-file=terraform.tfvars.example`
3. `terraform apply -var-file=terraform.tfvars.example`

Note: Adjust providers, variables, and state backend per environment (staging/prod). Keep secrets out of tfvars in git.
