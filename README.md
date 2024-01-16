# ChatGPT Web Frontend

## Description
This project is an implementation of a web-based frontend application using Next.js, designed to interact with AWS services, particularly SageMaker. It includes a Docker setup for containerization and deployment to AWS ECS Fargate, ensuring a scalable and efficient cloud-based application.

## Features
- Web frontend built with Next.js.
- Integration with AWS SageMaker for machine learning capabilities.
- Containerization using Docker for easy deployment.
- Deployment configuration for AWS ECS Fargate using Pulumi, ensuring a scalable cloud infrastructure.

## Prerequisites
- Node.js (v18 or later)
- Docker
- AWS CLI
- Pulumi CLI

## Setup and Installation
1. Clone the Repository:
   `git clone https://github.com/chaffees/fargate.git`
   `cd fargate`

2. Navigate to the App Directory:
   `cd app`

3. Install Dependencies:
   `npm install`

4. Build the Application:
   `npm run build`

5. Running the Application Locally:
   `npm start`

## Docker Containerization
1. Build the Docker Image:
   `docker build -t chatgpt-web-frontend .`

2. Run the Docker Container:
   `docker run -p 3000:3000 chatgpt-web-frontend`

## Deploying to AWS ECS Fargate
1. Set up AWS Credentials:
   Configure your AWS credentials using the AWS CLI.

2. Navigate to the Infrastructure Directory:
   `cd infra`

3. Install Pulumi Dependencies:
   `pip install -r requirements.txt`

4. Deploy using Pulumi:
   `pulumi up`

## Additional Information
- API Integration: The application integrates with AWS SageMaker. See `app/pages/api/invokeSageMaker.ts` for details.
- Frontend Components: The main chat component is located at `app/components/chatComponent.tsx`.
- Infrastructure as Code: The AWS infrastructure is defined using Pulumi in `infra/__main__.py`.
