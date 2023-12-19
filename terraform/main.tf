# Establish your provider

provider "aws" {
    region = "eu-west-2"
}

# Refer to things that already exist

data "aws_vpc" "c9-vpc" {
    id = "vpc-04423dbb18410aece"
}

data "aws_ecs_cluster" "c9-cluster" {
    cluster_name = "c9-ecs-cluster"
}

data "aws_iam_role" "execution-role" {
    name = "ecsTaskExecutionRole"
}

# Make the ECR repositories

# Pipeline ECR
resource "aws_ecr_repository" "c9-persnickety-pipeline-repo-t" {
  name = "c9-persnickety-pipeline-repo-t"
  image_scanning_configuration {
    scan_on_push = false
  }
}

# Dashboard ECR
resource "aws_ecr_repository" "c9-persnickety-dashboard-repo-t" {
  name = "c9-persnickety-dashboard-repo-t"
  image_scanning_configuration {
    scan_on_push = false
  }
}

# Lambda ECR
resource "aws_ecr_repository" "c9-persnickety-lambda-repo-t" {
  name = "c9-persnickety-lambda-repo-t"
  image_scanning_configuration {
    scan_on_push = false
  }
}

# Creates two ECS task definitions (one for the dashboard, one for the pipeline)

# Pipeline task definition

# Dashboard task definition

# Starts the dashboard service

# Creates the lambda

# Create the step-function

# Sets up the required EventBridge trigger