#!/bin/bash
set -e

REV=6

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
AWS_DEFAULT_REGION=$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')

export DOCKER_DEFAULT_PLATFORM=linux/amd64

docker build -t codebuild-terraform-image .

aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com

docker tag codebuild-terraform-image \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/codebuild-terraform-image:${REV}

docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/codebuild-terraform-image:${REV}
