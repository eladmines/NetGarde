# PowerShell script to update GitHub Actions IAM role with S3 and CloudFront permissions
# Configuration
$AWS_REGION = "us-east-1"
$ROLE_NAME = "GitHubActionsDeployRole"
$S3_BUCKET_NAME = "netgarde-frontend"
$CLOUDFRONT_DISTRIBUTION_ID = "E26UGOT5YUPFRY"

Write-Host "Updating IAM role permissions for GitHub Actions..." -ForegroundColor Cyan
Write-Host "Role: $ROLE_NAME" -ForegroundColor Yellow
Write-Host "S3 Bucket: $S3_BUCKET_NAME" -ForegroundColor Yellow
Write-Host "CloudFront Distribution: $CLOUDFRONT_DISTRIBUTION_ID" -ForegroundColor Yellow
Write-Host ""

# Step 1: Get the current role policy
Write-Host "Step 1: Getting current role policy..." -ForegroundColor Cyan
try {
    $currentPolicies = aws iam list-role-policies --role-name $ROLE_NAME --output json | ConvertFrom-Json
    $inlinePolicies = $currentPolicies.PolicyNames
    
    Write-Host "[OK] Found $($inlinePolicies.Count) inline policies" -ForegroundColor Green
    
    # Check if a policy document exists
    $policyName = "GitHubActionsDeployPolicy"
    $policyExists = $false
    
    foreach ($policy in $inlinePolicies) {
        if ($policy -eq $policyName) {
            $policyExists = $true
            Write-Host "[INFO] Policy '$policyName' already exists, will update it" -ForegroundColor Yellow
            break
        }
    }
} catch {
    Write-Host "[ERROR] Failed to list role policies: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Create policy document
Write-Host "Step 2: Creating policy document..." -ForegroundColor Cyan

$policyDocument = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Sid = "ECRAccess"
            Effect = "Allow"
            Action = @(
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            )
            Resource = "*"
        },
        @{
            Sid = "S3BucketAccess"
            Effect = "Allow"
            Action = @(
                "s3:ListBucket",
                "s3:GetBucketLocation"
            )
            Resource = "arn:aws:s3:::$S3_BUCKET_NAME"
        },
        @{
            Sid = "S3ObjectAccess"
            Effect = "Allow"
            Action = @(
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            )
            Resource = "arn:aws:s3:::$S3_BUCKET_NAME/*"
        },
        @{
            Sid = "CloudFrontInvalidation"
            Effect = "Allow"
            Action = @(
                "cloudfront:CreateInvalidation",
                "cloudfront:GetInvalidation",
                "cloudfront:ListInvalidations"
            )
            Resource = "*"
        }
    )
}

# Convert to JSON
$policyJson = $policyDocument | ConvertTo-Json -Depth 10

# Save to temp file
$tempPolicyFile = "$env:TEMP\github-actions-policy.json"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($tempPolicyFile, $policyJson, $utf8NoBom)

Write-Host "[OK] Policy document created" -ForegroundColor Green
Write-Host ""

# Step 3: Put/Update the policy
Write-Host "Step 3: Attaching policy to role..." -ForegroundColor Cyan
try {
    aws iam put-role-policy `
        --role-name $ROLE_NAME `
        --policy-name $policyName `
        --policy-document "file://$tempPolicyFile" `
        --output json | Out-Null
    
    Write-Host "[OK] Policy '$policyName' attached successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to attach policy: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Verify the policy
Write-Host "Step 4: Verifying policy..." -ForegroundColor Cyan
try {
    $verifyPolicy = aws iam get-role-policy `
        --role-name $ROLE_NAME `
        --policy-name $policyName `
        --output json | ConvertFrom-Json
    
    Write-Host "[OK] Policy verified successfully" -ForegroundColor Green
    Write-Host ""
    Write-Host "Policy Summary:" -ForegroundColor Cyan
    Write-Host "  - ECR: Full access" -ForegroundColor White
    Write-Host "  - S3 Bucket: ListBucket, GetBucketLocation on $S3_BUCKET_NAME" -ForegroundColor White
    Write-Host "  - S3 Objects: GetObject, PutObject, DeleteObject on $S3_BUCKET_NAME/*" -ForegroundColor White
    Write-Host "  - CloudFront: CreateInvalidation, GetInvalidation, ListInvalidations" -ForegroundColor White
    Write-Host ""
    Write-Host "Setup complete! GitHub Actions can now deploy to S3 and CloudFront." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to verify policy: $_" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item $tempPolicyFile -ErrorAction SilentlyContinue
