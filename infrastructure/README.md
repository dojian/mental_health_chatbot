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


### Manual ECR for 2 different images
1. build backend image
```bash
docker build --platform=linux/amd64 -t genzen-backend:v1.3 .
```
2. tag image - Make sure to replace image id and the ecr url with your own
```bash
docker tag 0c4bde675a6f 975049977273.dkr.ecr.us-east-2.amazonaws.com/genzen/backend:v1.3 
```
3. push image
```bash
docker push 975049977273.dkr.ecr.us-east-2.amazonaws.com/genzen/backend:v1.3
```
4. build frontend image
```bash
docker build \
--platform=linux/amd64 \
--build-arg NEXT_PUBLIC_API_URL=http://backend-service:8001 \
--build-arg NEXT_PUBLIC_APP_ENV=staging \
-t genzen-frontend:v1.3 . 
```
5. tag image
```bash
docker tag ed5cd04db2f4 975049977273.dkr.ecr.us-east-2.amazonaws.com/genzen/frontend:v1.3
```
6. push image
```bash
docker push 975049977273.dkr.ecr.us-east-2.amazonaws.com/genzen/frontend:v1.3
```

### Once pushed to ECR. Asusming EKS is running too
1. use kustomize to apply
```bash
kubectl apply -k .k8s/overlays/dev
```
2. test frontend service
```bash
kubectl port-forward -n genzen svc/frontend-service 3000:3000
```

## S3
* S3 buckets are created in the `us-east-2` region.

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