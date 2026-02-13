# PowerShell script for Windows
# Configuration
$AWS_REGION = "us-east-1"
$BUCKET_NAME = "netgarde-frontend"
$DISTRIBUTION_COMMENT = "NetGarde Frontend CDN"

Write-Host "Setting up CloudFront distribution for NetGarde frontend..." -ForegroundColor Cyan
Write-Host "S3 Bucket: $BUCKET_NAME"
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

# Get S3 website endpoint
$S3_WEBSITE_ENDPOINT = "$BUCKET_NAME.s3-website-$AWS_REGION.amazonaws.com"
Write-Host "S3 Website Endpoint: http://$S3_WEBSITE_ENDPOINT"
Write-Host ""

# Step 1: Create CloudFront distribution configuration
Write-Host "Step 1: Creating CloudFront distribution configuration..." -ForegroundColor Yellow

# Create distribution config JSON
$distributionConfig = @{
    CallerReference = "netgarde-frontend-$(Get-Date -Format 'yyyyMMddHHmmss')"
    Comment = $DISTRIBUTION_COMMENT
    DefaultCacheBehavior = @{
        TargetOriginId = "S3-$BUCKET_NAME"
        ViewerProtocolPolicy = "redirect-to-https"
        AllowedMethods = @{
            Quantity = 7
            Items = @("DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT")
            CachedMethods = @{
                Quantity = 2
                Items = @("GET", "HEAD")
            }
        }
        Compress = $true
        ForwardedValues = @{
            QueryString = $false
            Cookies = @{
                Forward = "none"
            }
        }
        MinTTL = 0
        DefaultTTL = 86400
        MaxTTL = 31536000
    }
    Origins = @{
        Quantity = 1
        Items = @(
            @{
                Id = "S3-$BUCKET_NAME"
                DomainName = $S3_WEBSITE_ENDPOINT
                CustomOriginConfig = @{
                    HTTPPort = 80
                    HTTPSPort = 443
                    OriginProtocolPolicy = "http-only"
                    OriginSslProtocols = @{
                        Quantity = 1
                        Items = @("TLSv1.2")
                    }
                }
            }
        )
    }
    Enabled = $true
    PriceClass = "PriceClass_100"
    CustomErrorResponses = @{
        Quantity = 1
        Items = @(
            @{
                ErrorCode = 404
                ResponsePagePath = "/index.html"
                ResponseCode = "200"
                ErrorCachingMinTTL = 300
            }
        )
    }
} | ConvertTo-Json -Depth 10

# Save to temp file (without BOM to avoid JSON parsing errors)
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("$env:TEMP\cloudfront-config.json", $distributionConfig, $utf8NoBom)

Write-Host "  [OK] Configuration file created" -ForegroundColor Green

# Step 2: Create CloudFront distribution
Write-Host ""
Write-Host "Step 2: Creating CloudFront distribution..." -ForegroundColor Yellow
Write-Host "  This may take 5-15 minutes..." -ForegroundColor Yellow

$distributionOutput = aws cloudfront create-distribution --distribution-config file://$env:TEMP\cloudfront-config.json 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] CloudFront distribution created successfully" -ForegroundColor Green
    
    # Extract distribution ID and domain name
    $distributionId = ($distributionOutput | ConvertFrom-Json).Distribution.Id
    $distributionDomain = ($distributionOutput | ConvertFrom-Json).Distribution.DomainName
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "CloudFront distribution setup complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Distribution ID: $distributionId" -ForegroundColor Yellow
    Write-Host "Distribution Domain: $distributionDomain" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Your frontend will be available at:" -ForegroundColor Cyan
    Write-Host "  https://$distributionDomain" -ForegroundColor Green
    Write-Host ""
    Write-Host "[NOTE] CloudFront distribution deployment takes 5-15 minutes." -ForegroundColor Yellow
    Write-Host "       The distribution will be in 'InProgress' status initially." -ForegroundColor Yellow
    Write-Host "       Check status with: aws cloudfront get-distribution --id $distributionId" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next step: Wait for deployment, then test the CloudFront URL" -ForegroundColor Green
    Write-Host ""
    
    # Clean up temp file
    Remove-Item "$env:TEMP\cloudfront-config.json" -ErrorAction SilentlyContinue
} else {
    Write-Host "  [ERROR] Failed to create CloudFront distribution" -ForegroundColor Red
    Write-Host $distributionOutput -ForegroundColor Red
    exit 1
}