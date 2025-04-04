#! /bin/bash

export KARPENTER_NAMESPACE="kube-system"
export KARPENTER_VERSION="1.3.3"
export K8S_VERSION="1.32"

export AWS_PARTITION="aws" # if you are not using standard partitions, you may need to configure to aws-cn / aws-us-gov
export CLUSTER_NAME="genzen-test-02"
export AWS_DEFAULT_REGION="us-west-2"
export AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
