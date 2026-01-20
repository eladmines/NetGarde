# PowerShell script to create a CloudFront distribution for the backend API
# Configuration
$AWS_REGION = "us-east-1"
$EC2_IP = "44.218.45.174"
$EC2_PUBLIC_DNS = "ec2-44-218-45-174.compute-1.amazonaws.com"  # EC2 public DNS name
$BACKEND_PORT = "8000"
$DISTRIBUTION_COMMENT = "NetGarde Backend API CDN"

Write-Host "Setting up CloudFront distribution for NetGarde backend..." -ForegroundColor Cyan
Write-Host "EC2 IP: $EC2_IP" -ForegroundColor Yellow
Write-Host "EC2 Public DNS: $EC2_PUBLIC_DNS" -ForegroundColor Yellow
Write-Host "Backend Port: $BACKEND_PORT" -ForegroundColor Yellow
Write-Host ""

# Step 1: Create CloudFront distribution configuration
Write-Host "Step 1: Creating CloudFront distribution configuration..." -ForegroundColor Cyan

$distributionConfig = @{
    CallerReference = "netgarde-backend-$(Get-Date -Format 'yyyyMMddHHmmss')"
    Comment = $DISTRIBUTION_COMMENT
    DefaultCacheBehavior = @{
        TargetOriginId = "netgarde-backend-origin"
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
            QueryString = $true
            Cookies = @{
                Forward = "all"
            }
            Headers = @{
                Quantity = 1
                Items = @("Host")
            }
        }
        MinTTL = 0
        DefaultTTL = 0
        MaxTTL = 0
    }
    Origins = @{
        Quantity = 1
        Items = @(
            @{
                Id = "netgarde-backend-origin"
                DomainName = "$EC2_PUBLIC_DNS"
                CustomOriginConfig = @{
                    HTTPPort = [int]$BACKEND_PORT
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
} | ConvertTo-Json -Depth 10

# Write JSON without BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$tempConfigFile = "$env:TEMP\cloudfront-backend-config.json"
[System.IO.File]::WriteAllText($tempConfigFile, $distributionConfig, $utf8NoBom)

Write-Host "[OK] Configuration file created" -ForegroundColor Green
Write-Host ""

# Step 2: Create CloudFront distribution
Write-Host "Step 2: Creating CloudFront distribution..." -ForegroundColor Cyan
try {
    $distribution = aws cloudfront create-distribution --distribution-config "file://$tempConfigFile" --output json | ConvertFrom-Json
    
    if ($distribution.Distribution) {
        $distributionId = $distribution.Distribution.Id
        $domainName = $distribution.Distribution.DomainName
        
        Write-Host "[OK] CloudFront distribution created successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Distribution Details:" -ForegroundColor Cyan
        Write-Host "  Distribution ID: $distributionId" -ForegroundColor White
        Write-Host "  Domain Name: $domainName" -ForegroundColor White
        Write-Host "  Status: $($distribution.Distribution.Status)" -ForegroundColor White
        Write-Host ""
        Write-Host "IMPORTANT:" -ForegroundColor Yellow
        Write-Host "  1. Update your frontend deployment workflow:" -ForegroundColor White
        Write-Host "     BACKEND_API_URL: https://$domainName" -ForegroundColor White
        Write-Host "  2. Wait 5-10 minutes for CloudFront to deploy" -ForegroundColor White
        Write-Host "  3. Update EC2 security group to allow CloudFront IPs (optional)" -ForegroundColor White
        Write-Host ""
        Write-Host "Your backend API will be available at: https://$domainName" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to create distribution" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to create CloudFront distribution: $_" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item $tempConfigFile -ErrorAction SilentlyContinue
