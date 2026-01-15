# AWS Deployment Setup

This directory contains scripts and configurations for deploying NetGarde to AWS.

## Setup Steps

### Step 1: Create S3 Bucket
Run the S3 setup script to create and configure the bucket for static website hosting.

```bash
cd aws
chmod +x s3-setup.sh
./s3-setup.sh
```

**Important**: If the bucket name `netgarde-frontend` is already taken, edit `s3-setup.sh` and change `BUCKET_NAME` to something unique (e.g., `netgarde-frontend-yourname`).

### Step 2: Create CloudFront Distribution
(Coming next)

### Step 3: Set up ECS for Backend
(Coming next)

### Step 4: Configure GitHub Actions
(Coming next)

## Prerequisites

- AWS CLI installed and configured (`aws configure`)
- AWS account with appropriate permissions
- RDS database endpoint: `database-1.cg5q8smoiupc.us-east-1.rds.amazonaws.com`

## Architecture

- **S3 + CloudFront**: Frontend (React static files)
- **ECS Fargate**: Backend (FastAPI)
- **RDS**: PostgreSQL database
- **GitHub Actions**: CI/CD pipeline
