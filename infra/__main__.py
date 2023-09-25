"""An AWS Python Pulumi program that uploads a docker file to ECR, builds an image
and deploys it to ECS Fargate."""

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import json

# Define the VPC for the Fargate cluster
vpc = awsx.ec2.Vpc("dev-fargate-vpc", 
    cidr_block="10.140.0.0/16",
    number_of_availability_zones = 2,
    subnet_specs=[
        awsx.ec2.SubnetSpecArgs(
        type = awsx.ec2.SubnetType.PRIVATE,
        cidr_mask = 24,
    ),
        awsx.ec2.SubnetSpecArgs(
            type = awsx.ec2.SubnetType.PUBLIC,
            cidr_mask = 24,
        )
    ],
    # Reduces # of NatGateways to save $$$ NOT intended for production
    nat_gateways=awsx.ec2.NatGatewayConfigurationArgs(
        strategy = awsx.ec2.NatGatewayStrategy.SINGLE
    ),
    tags={
        "environment": "prod",
        "product": "data-science",
        "application": "data-viz"
    }
)

# Create an IAM role that is used by our service's task
task_execution_role = aws.iam.Role(
    'fargate-task-exec-role',
    assume_role_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }),
    tags = {
        "environment": "prod",
        "product": "data-science",
        "application": "data-viz"
    }
)

# Attach container policy to allow exec access into pod's
ecs_container_policy = aws.iam.RolePolicy(
    'ecs_container_policy',
    role = task_execution_role.id,
    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Action": [
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel"
            ],
            "Resource": "*"
        }]
    })
)

# Attach an AWS managed policy to the IAM role
rpa = aws.iam.RolePolicyAttachment(
    'fargate-task-exec-policy',
    role = task_execution_role.id,
    policy_arn = 'arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
)

# Define the Security Group for the Fargate cluster
sg = aws.ec2.SecurityGroup("dev-fargate-sg",
    description = "Allow web traffic for cluster",
    vpc_id = vpc.vpc_id,
    ingress = [aws.ec2.SecurityGroupIngressArgs(
        description = "Allow port 80 inbound from Internet",
        from_port = 80,
        to_port = 80,
        protocol = "TCP",
        cidr_blocks = ["0.0.0.0/0"]
    ),
    aws.ec2.SecurityGroupIngressArgs(
        description = "Allow port 3000 in from the SG",
        from_port = 3000,
        to_port = 3000,
        protocol = "TCP",
        self = True
    )],
    egress = [aws.ec2.SecurityGroupEgressArgs(
        description = "Allow all traffic out from cluster",
        from_port = 0,
        to_port = 0,
        protocol = "-1",
        cidr_blocks = ["0.0.0.0/0"],
    ),
    aws.ec2.SecurityGroupIngressArgs(
        description = "Allow port 3000 out to the SG",
        from_port = 3000,
        to_port = 3000,
        protocol = "TCP",
        self = True
    )],
    tags = {
        "environment": "prod",
        "product": "data-science",
        "application": "data-viz"
    }
)

# Create the ECR docker registry
repo = awsx.ecr.Repository("chatgpt-frontend",
    tags = {
        "environment": "prod",
        "product": "data-science",
        "application": "data-viz"
    }
)

# Tell the Pulumi task definition where to find the dockerfile
# to build and upload to ECR.
img = awsx.ecr.Image("app-image", 
    repository_url = repo.url,
    path = "../app",
    extra_options = ['--quiet']
)

# Build the Fargate cluster
cluster = aws.ecs.Cluster("dev-fargate-cluster",
    name = "Fargate-Cluster",
    tags = {
        "environment": "prod",
        "product": "data-science",
        "application": "data-viz"
    }
)

# Define the application loadbalancer for the fargate cluster
alb = awsx.lb.ApplicationLoadBalancer("dev-fargate-alb", 
    subnet_ids = vpc.public_subnet_ids,
    internal = False,
    security_groups = [sg.id],
    listener = awsx.lb.ListenerArgs(
        port = 80,
        protocol = "HTTP"
    ),
    default_target_group = awsx.lb.TargetGroupArgs(
        target_type = "ip",
        port = 3000,
        protocol = "HTTP",
        vpc_id=vpc.vpc_id,
        health_check = aws.lb.TargetGroupHealthCheckArgs(
            path = "/",
            timeout = 30,
            interval = 60,
            healthy_threshold = 5,
            unhealthy_threshold = 2
        )
    ),
    tags = {
        "environment": "prod",
        "product": "data-science",
        "application": "data-viz"
    }
)

# Define the Fargate service settings and configuration
service = awsx.ecs.FargateService("my_fargate_cluster_service",
    name = "Fargate-Service",
    cluster = cluster.arn,
    desired_count = 1, # Num of containers in cluster
    network_configuration = aws.ecs.ServiceNetworkConfigurationArgs(
        subnets = vpc.private_subnet_ids,
        security_groups = [sg.id]
    ),
    health_check_grace_period_seconds = 180,
    # Allow connections into the container with ecs exec
    enable_execute_command = True,
    task_definition_args = awsx.ecs.FargateServiceTaskDefinitionArgs(
        task_role = awsx.awsx.DefaultRoleWithPolicyArgs(
          role_arn = task_execution_role.arn
        ),
        execution_role = awsx.awsx.DefaultRoleWithPolicyArgs(
          role_arn = task_execution_role.arn
        ),
        containers = {
            "chatgpt-frontend": awsx.ecs.TaskDefinitionContainerDefinitionArgs(
                name = "chatgpt-frontend",
                image = img.image_uri,
                essential = True,
                memory = 512,
                cpu = 256,
                health_check = awsx.ecs.TaskDefinitionHealthCheckArgs(
                    command = ["CMD-SHELL", "curl -f http://localhost:3000 || exit 1"],
                    interval = 45,
                    timeout = 15,
                    retries = 5,
                    start_period = 60
                ),
                port_mappings = [awsx.ecs.TaskDefinitionPortMappingArgs(
                    container_port = 3000,
                    host_port = 3000,
                    protocol = "HTTP",
                    target_group = alb.default_target_group
                )]
            )
            
        }
    ),
    tags = {
        "environment": "prod",
        "product": "data-science",
        "application": "data-viz"
    }
)

pulumi.export("url", alb.load_balancer.dns_name)
pulumi.export("Image", img._name)
pulumi.export("Image_URI", img.image_uri)