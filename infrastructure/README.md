# AWS Infrastructure

## Description
The infrastructure is built using Terraform and `eksctl`.
* Terraform is used to create the `s3` bucket and `ecr` repository. Once created, do not destroy them in order to preserve the data.
* `eksctl` is used to create the EKS cluster. Ensure that the cluster is created in the same region as the `s3` bucket and `ecr` repository. Additionally, ensure it is created and destroyed to be more cost-effective.

## Requirements
* Terraform
* eksctl

## Setup
### Terraform
1. Once requirements are installed, run `terraform init` to initialize the Terraform project.
2. Run `terraform plan` to see the changes that will be made.
3. Run `terraform apply` to apply the changes.
4. Run `terraform destroy` to destroy the infrastructure.

### eksctl
1. Once requirements are installed, run `eksctl create cluster -f eksctl-cluster-config.yaml` to create the EKS cluster.
2. Run `eksctl delete cluster -f eksctl-cluster-config.yaml` to delete the EKS cluster.
3. Update the `eksctl-cluster-config.yaml` file with the desired configuration.
  * Currently, only one node group will be created to ensure functionality before scaling up.



## Terraform
* useful commands
```bash
terraform init # initialize terraform
terraform plan # plan the changes
terraform apply # apply the changes
terraform destroy # destroy the infrastructure

terraform fmt # format the code
terraform validate # validate the code
```

## EKSCTL
* useful commands
```bash
eksctl create cluster -f eksctl-cluster-config.yaml # create a cluster
eksctl delete cluster -f eksctl-cluster-config.yaml # delete a cluster
eksctl get cluster -f eksctl-cluster-config.yaml # get the cluster
```

## Kubectl
* useful commands
```bash
kubectl get nodes # get the nodes
kubectl get pods # get the pods
kubectl get services # get the services
kubectl get deployments # get the deployments
kubectl get ingress # get the ingress