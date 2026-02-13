# PowerShell script for Windows
# Configuration
$AWS_REGION = "us-east-1"
$ECR_REPOSITORY_NAME = "netgarde-backend"

Write-Host "Setting up ECR repository for NetGarde backend..." -ForegroundColor Cyan
Write-Host "Repository name: $ECR_REPOSITORY_NAME"
Write-Host "Region: $AWS_REGION"
Write-Host ""

# Check if AWS CLI is configured
try {
    $accountId = (aws sts get-caller-identity --query Account --output text 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: AWS CLI is not configured. Please run 'aws configure' first." -ForegroundColor Red
        exit 1
    }
    Write-Host "Account ID: $accountId"
} catch {
    Write-Host "ERROR: AWS CLI is not configured. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Step 1: Create ECR repository
Write-Host ""
Write-Host "Step 1: Creating ECR repository..." -ForegroundColor Yellow

$ecrOutput = aws ecr create-repository `
    --repository-name $ECR_REPOSITORY_NAME `
    --region $AWS_REGION `
    --image-scanning-configuration scanOnPush=true `
    --encryption-configuration encryptionType=AES256 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] ECR repository created successfully" -ForegroundColor Green
} else {
    if ($ecrOutput -match "already exists") {
        Write-Host "  [OK] ECR repository already exists" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Failed to create ECR repository" -ForegroundColor Red
        Write-Host $ecrOutput -ForegroundColor Red
        exit 1
    }
}

# Step 2: Get repository URI
Write-Host ""
Write-Host "Step 2: Getting repository URI..." -ForegroundColor Yellow

$repositoryUri = aws ecr describe-repositories `
    --repository-names $ECR_REPOSITORY_NAME `
    --region $AWS_REGION `
    --query "repositories[0].repositoryUri" `
    --output text

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Repository URI retrieved" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to get repository URI" -ForegroundColor Red
    exit 1
}

# Step 3: Display summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ECR repository setup complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository name: $ECR_REPOSITORY_NAME" -ForegroundColor Yellow
Write-Host "Repository URI: $repositoryUri" -ForegroundColor Yellow
Write-Host ""
Write-Host "To login to ECR, run:" -ForegroundColor Cyan
Write-Host "  aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $repositoryUri" -ForegroundColor Green
Write-Host ""
Write-Host "To push an image:" -ForegroundColor Cyan
Write-Host "  1. Tag your image: docker tag netgarde-backend:latest $repositoryUri`:latest" -ForegroundColor Green
Write-Host "  2. Push image: docker push $repositoryUri`:latest" -ForegroundColor Green
Write-Host ""
Write-Host "Next step: Set up EC2 instance (Step 3B)" -ForegroundColor Green
Write-Host ""