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
resource "aws_ecr_repository" "c9-persnickety-pipeline-repo-tf" {
  name = "c9-persnickety-pipeline-repo-tf"
  image_scanning_configuration {
    scan_on_push = false
  }
}

# Dashboard ECR
resource "aws_ecr_repository" "c9-persnickety-dashboard-repo-tf" {
  name = "c9-persnickety-dashboard-repo-tf"
  image_scanning_configuration {
    scan_on_push = false
  }
}

# Lambda ECR
resource "aws_ecr_repository" "c9-persnickety-lambda-repo-tf" {
  name = "c9-persnickety-lambda-repo-tf"
  image_scanning_configuration {
    scan_on_push = false
  }
}

# Creates two ECS task definitions (one for the dashboard, one for the pipeline)

# Pipeline task definition
#add task def json into container def as jsonencode
resource "aws_ecs_task_definition" "task-pipeline" {
    family = "c9-persnickety-pipeline-tf"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    container_definitions = jsonencode({
        "name": "c9-persnickety-pipeline-tf",
        "image": "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c9-persnickety-pipeline-repo-tf:latest",
        "essential": true,
        "portMappings": []
    })
    memory    = 2048
    cpu = 1024
    execution_role_arn = data.aws_iam_role.execution-role.arn
}
# Dashboard task definition
#add task def json into container def as jsonencode
resource "aws_ecs_task_definition" "task-dash" {
    family = "c9-persnickety-dashboard-td-tf"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    container_definitions = jsonencode({
        "name": "c9-persnickety-dashboard-td-tf",
        "image": "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c9-persnickety-dashboard-repo-tf:latest",
        "essential": true,
        "portMappings": [
            {
                "containerPort": 8501,
                "hostPort": 8501
            }
        ]
    })
    memory    = 2048
    cpu = 1024
    execution_role_arn = data.aws_iam_role.execution-role.arn
}
# Starts the dashboard service
resource "aws_ecs_service" "dashboard-service" {
    name = "c9-persnickety-dashboard-service"
    cluster = data.aws_ecs_cluster.c9-cluster.id
    task_definition = "arn:aws:ecs:eu-west-2:129033205317:c9-persnickety-dashboard-td-tf:latest" 
    desired_count = 1
    launch_type = "FARGATE"
    network_configuration {
      subnets = ["subnet-0d0b16e76e68cf51b", "subnet-081c7c419697dec52", "subnet-02a00c7be52b00368"]
      security_groups = ["sg-0ce150705484be1ce"]
      assign_public_ip = true
    }
}
# Creates the lambda
#Creates Lambda iam role
resource "aws_iam_role" "iam_for_lambda_ps_tf" {
  name               = "iam_for_lambda_ps_tf"
  assume_role_policy = jsonencode({
        Version: "2012-10-17",
        Statement: [
            {
                Effect: "Allow",
                Principal: {
                    Service: "lambda.amazonaws.com"
                },
                Action: "sts:AssumeRole",
            }, 
        ],
  })
}
#lambda function permission
resource "aws_lambda_permission" "execute-lambda-permission" {
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.c9-persnickety-lambda.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.email-trigger.arn
}

resource "aws_lambda_function" "c9-persnickety-lambda" {
    function_name = "c9-persnickety-lambda"
    role = aws_iam_role.iam_for_lambda_ps_tf.arn
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c9-persnickety-lambda-repo-tf:latest"
    package_type = "Image"
    environment {
      variables = {
      DATABASE=var.DATABASE
      HOST=var.DATABASE_HOST
      PASSWORD=var.DATABASE_PASSWORD
      PORT=var.DATABASE_PORT
      USERNAME=var.DATABASE_USERNAME
    }
    }

}
# Create the step-function
#step function iam roles + associated step-function set up
resource "aws_iam_policy" "step-function-policy" {
    name = "ExecuteStepFunctions"
    policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "states:StartExecution"
            ],
            "Resource": [
                [aws_sfn_state_machine.c9-persnickety-stm-tf.arn]
            ]
        }
    ]
})
}
# step-function
resource "aws_sfn_state_machine" "c9-persnickety-stm-tf" {
  name     = "c9-persnickety-stm-tf"
  role_arn = aws_iam_policy.step-function-policy.arn
  definition = <<EOF
{
  "Comment": "A description of my state machine",
  "StartAt": "ECS RunTask",
  "States": {
    "ECS RunTask": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "LaunchType": "FARGATE",
        "Cluster": "arn:aws:ecs:eu-west-2:129033205317:cluster/c9-ecs-cluster",
        "TaskDefinition": "arn:aws:ecs:REGION:ACCOUNT_ID:task-definition/MyTaskDefinition:1"
      },
      "Next": "Lambda Invoke"
    },
    "Lambda Invoke": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:eu-west-2:129033205317:function:c9-persnickety-lambda",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ],
      "End": true
    }
  }
}
EOF
}

# Sets up the required EventBridge trigger
#eventbridge aws iam role


resource "aws_cloudwatch_event_rule" "sfn-trigger" {
  name                = "c9-persnickety-sfn-trigger-tf"
  schedule_expression = "cron(0/1 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "email-target" {

    rule = aws_cloudwatch_event_rule.sfn-trigger.name
    arn = aws_sfn_state_machine.c9-persnickety-stm-tf.arn
}