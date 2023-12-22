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
data "aws_iam_policy_document" "state_machine_role_policy" {
  
  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = ["${aws_lambda_function.c9-persnickety-lambda.arn}:*"]
  }
  
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
#add task def json into container def as jsonencode
resource "aws_ecs_task_definition" "task-pipeline" {
    family = "c9-persnickety-pipeline-t"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    container_definitions = file("./task-def-pipe.json")
    memory    = 2048
    cpu = 1024
    execution_role_arn = data.aws_iam_role.execution-role.arn
}
# Dashboard task definition
#add task def json into container def as jsonencode
resource "aws_ecs_task_definition" "task-dash" {
    family = "c9-persnickety-dashboard-td-t"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    container_definitions = file("./task-def.json")
    memory    = 2048
    cpu = 1024
    execution_role_arn = data.aws_iam_role.execution-role.arn
}
# Starts the dashboard service
# resource "aws_ecs_service" "dashboard-service" {
#     name = "c9-persnickety-dashboard-service"
#     cluster = data.aws_ecs_cluster.c9-cluster.id
#     task_definition = "arn:aws:ecs:eu-west-2:129033205317:c9-persnickety-dashboard-td-t:latest" 
#     desired_count = 1
#     launch_type = "FARGATE"
#     network_configuration {
#       subnets = ["subnet-0d0b16e76e68cf51b", "subnet-081c7c419697dec52", "subnet-02a00c7be52b00368"]
#       security_groups = ["sg-0ce150705484be1ce"]
#       assign_public_ip = true
#     }
# }
resource "aws_iam_role" "iam_for_persnickety_tf" {
  name               = "iam_for_persnickety_tf"
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
# Creates the lambda
resource "aws_lambda_function" "c9-persnickety-lambda" {
    function_name = "c9-persnickety-lambda"
    role = aws_iam_role.iam_for_persnickety_tf.arn
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c9-persnickety-lambda-repo-t:latest"
    package_type = "Image"
    environment {
      variables = {
      DB_NAME=var.DB_NAME
      DB_HOST=var.DB_HOST
      DB_PASSWORD=var.DB_PASSWORD
      DB_PORT=var.DB_PORT
      DB_USER=var.DB_USER
    }
    }

}

#lambda function permission
resource "aws_lambda_permission" "execute-lambda-permission" {
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.c9-persnickety-lambda.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.sfn-trigger.arn
}

resource "aws_iam_role" "iam_for_lambda_ps_t" {
  name               = "iam_for_lambda_ps_"
  assume_role_policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
})
}


resource "aws_iam_role" "trust_relationship" {
  name               = "trust_relationship"
  assume_role_policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "states.eu-west-2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
})
}

# Create the step-function
# step function iam roles + associated step-function set up

resource "aws_sfn_state_machine" "c9-persnickety-stm-t" {
  name     = "c9-persnickety-stm-t"
  role_arn = aws_iam_role.run-step-function-role.arn
  definition = <<EOF
{
  "Comment": "A description of my state machine",
  "StartAt": "RunECSTask",
  "States": {
    "RunECSTask": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "LaunchType": "FARGATE",
        "Cluster": "arn:aws:ecs:eu-west-2:129033205317:cluster/c9-ecs-cluster",
        "TaskDefinition": "arn:aws:ecs:eu-west-2:129033205317:task-definition/c9-persnickety-pipeline-t:1"
      },
      "Next": "InvokeLambda"
    },
    "States": {
    "InvokeLambda": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:eu-west-2:129033205317:function:c9-anu-lambda-tf",
      "End": true
    }
  }
}
EOF
}


resource "aws_iam_role" "run-step-function-role" {
    name = "c9-persnickety-sfn-executor"

    assume_role_policy = jsonencode({
  "Version":"2012-10-17",
  "Statement":[
     {
        "Effect":"Allow",
        "Principal":{
           "Service":[
              "events.amazonaws.com"
           ]
        },
        "Action":"sts:AssumeRole"
     }
  ]
})
}



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
                aws_sfn_state_machine.c9-persnickety-stm-t.arn
            ]
        }
    ]
})
}

resource "aws_iam_role_policy_attachment" "attach-execution-policy" {
  role       = data.aws_iam_role.execution-role.name
  policy_arn = aws_iam_policy.step-function-policy.arn
}

resource "aws_iam_policy" "execute_ecs" {
    name = "EcsRunTaskScopedAccessPolicy"
    policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:RunTask"
            ],
            "Resource": [
                aws_ecs_task_definition.task-pipeline.arn
            ]
        }
    ]
})
}

resource "aws_cloudwatch_event_rule" "sfn-trigger" {
  name                = "c9-persnickety-sfn-trigger-t"
  schedule_expression = "cron(0/1 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "sfn_target" {
  rule = aws_cloudwatch_event_rule.sfn-trigger.name
  arn = aws_sfn_state_machine.c9-persnickety-stm-t.arn
  role_arn = aws_iam_role.run-step-function-role.arn
}

