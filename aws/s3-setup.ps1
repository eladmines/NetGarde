# PowerShell script for Windows
# Configuration
$AWS_REGION = "us-east-1"
$BUCKET_NAME = "netgarde-frontend"  # Change this to your preferred unique name

Write-Host "Setting up S3 bucket for NetGarde frontend..." -ForegroundColor Cyan
Write-Host "Bucket name: $BUCKET_NAME"
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

# 1. Create S3 bucket
Write-Host ""
Write-Host "Step 1: Creating S3 bucket..." -ForegroundColor Yellow
$bucketExists = aws s3api head-bucket --bucket $BUCKET_NAME 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Bucket '$BUCKET_NAME' already exists" -ForegroundColor Green
} else {
    if ($AWS_REGION -eq "us-east-1") {
        # us-east-1 doesn't need LocationConstraint
        aws s3api create-bucket --bucket $BUCKET_NAME --region $AWS_REGION 2>&1 | Out-Null
    } else {
        $locationConstraint = @{LocationConstraint=$AWS_REGION} | ConvertTo-Json -Compress
        aws s3api create-bucket --bucket $BUCKET_NAME --region $AWS_REGION --create-bucket-configuration $locationConstraint 2>&1 | Out-Null
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Bucket '$BUCKET_NAME' created successfully" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Failed to create bucket. It may already exist or the name may be taken." -ForegroundColor Red
        Write-Host "    Try a different bucket name (must be globally unique)" -ForegroundColor Yellow
        exit 1
    }
}

# 2. Enable static website hosting
Write-Host ""
Write-Host "Step 2: Enabling static website hosting..." -ForegroundColor Yellow
aws s3 website s3://$BUCKET_NAME/ --index-document index.html --error-document index.html 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Static website hosting enabled" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to enable static website hosting" -ForegroundColor Red
    exit 1
}

# 3. Create bucket policy for public read access
Write-Host ""
Write-Host "Step 3: Creating bucket policy for public read access..." -ForegroundColor Yellow
$bucketPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Sid = "PublicReadGetObject"
            Effect = "Allow"
            Principal = "*"
            Action = "s3:GetObject"
            Resource = "arn:aws:s3:::$BUCKET_NAME/*"
        }
    )
} | ConvertTo-Json -Depth 10

$bucketPolicy | Out-File -FilePath "$env:TEMP\bucket-policy.json" -Encoding utf8
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://$env:TEMP\bucket-policy.json 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Bucket policy applied" -ForegroundColor Green
    Remove-Item "$env:TEMP\bucket-policy.json" -ErrorAction SilentlyContinue
} else {
    Write-Host "  [ERROR] Failed to apply bucket policy" -ForegroundColor Red
    exit 1
}

# 4. Block public access settings
Write-Host ""
Write-Host "Step 4: Configuring public access block settings..." -ForegroundColor Yellow
aws s3api put-public-access-block `
    --bucket $BUCKET_NAME `
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Public access block configured" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to configure public access block" -ForegroundColor Red
    exit 1
}

# 5. Set CORS configuration
Write-Host ""
Write-Host "Step 5: Setting CORS configuration..." -ForegroundColor Yellow
$corsConfig = @{
    CORSRules = @(
        @{
            AllowedOrigins = @("*")
            AllowedMethods = @("GET", "HEAD")
            AllowedHeaders = @("*")
            ExposeHeaders = @()
            MaxAgeSeconds = 3000
        }
    )
} | ConvertTo-Json -Depth 10

$corsConfig | Out-File -FilePath "$env:TEMP\cors-config.json" -Encoding utf8
aws s3api put-bucket-cors --bucket $BUCKET_NAME --cors-configuration file://$env:TEMP\cors-config.json 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] CORS configuration applied" -ForegroundColor Green
    Remove-Item "$env:TEMP\cors-config.json" -ErrorAction SilentlyContinue
} else {
    Write-Host "  [ERROR] Failed to apply CORS configuration" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "S3 bucket setup complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Bucket name: $BUCKET_NAME"
Write-Host "Region: $AWS_REGION"
Write-Host ""
Write-Host "Website endpoint:" -ForegroundColor Yellow
Write-Host "  http://$BUCKET_NAME.s3-website-$AWS_REGION.amazonaws.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "[NOTE] If the bucket name is not globally unique, you'll need to:" -ForegroundColor Yellow
Write-Host "   1. Edit this script and change `$BUCKET_NAME"
Write-Host "   2. Run this script again"
Write-Host ""
Write-Host "Next step: Create CloudFront distribution (Step 2)" -ForegroundColor Green
Write-Host ""
