#!/bin/bash
# Bash script to update GitHub Actions IAM role with S3 and CloudFront permissions

# Configuration
AWS_REGION="us-east-1"
ROLE_NAME="GitHubActionsDeployRole"
S3_BUCKET_NAME="netgarde-frontend"
CLOUDFRONT_DISTRIBUTION_ID="E26UGOT5YUPFRY"
POLICY_NAME="GitHubActionsDeployPolicy"

echo "Updating IAM role permissions for GitHub Actions..."
echo "Role: $ROLE_NAME"
echo "S3 Bucket: $S3_BUCKET_NAME"
echo "CloudFront Distribution: $CLOUDFRONT_DISTRIBUTION_ID"
echo ""

# Step 1: Get the current role policy
echo "Step 1: Getting current role policy..."
if aws iam list-role-policies --role-name "$ROLE_NAME" --output json > /dev/null 2>&1; then
    echo "[OK] Role exists"
else
    echo "[ERROR] Role '$ROLE_NAME' not found"
    exit 1
fi

# Step 2: Create policy document
echo "Step 2: Creating policy document..."

cat > /tmp/github-actions-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRAccess",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::${S3_BUCKET_NAME}"
    },
    {
      "Sid": "S3ObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::${S3_BUCKET_NAME}/*"
    },
    {
      "Sid": "CloudFrontInvalidation",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "*"
    }
  ]
}
EOF

echo "[OK] Policy document created"
echo ""

# Step 3: Put/Update the policy
echo "Step 3: Attaching policy to role..."
if aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --policy-document "file:///tmp/github-actions-policy.json" \
    --output json > /dev/null 2>&1; then
    echo "[OK] Policy '$POLICY_NAME' attached successfully"
else
    echo "[ERROR] Failed to attach policy"
    exit 1
fi

# Step 4: Verify the policy
echo "Step 4: Verifying policy..."
if aws iam get-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --output json > /dev/null 2>&1; then
    echo "[OK] Policy verified successfully"
    echo ""
    echo "Policy Summary:"
    echo "  - ECR: Full access"
    echo "  - S3 Bucket: ListBucket, GetBucketLocation on $S3_BUCKET_NAME"
    echo "  - S3 Objects: GetObject, PutObject, DeleteObject on $S3_BUCKET_NAME/*"
    echo "  - CloudFront: CreateInvalidation, GetInvalidation, ListInvalidations"
    echo ""
    echo "Setup complete! GitHub Actions can now deploy to S3 and CloudFront."
else
    echo "[ERROR] Failed to verify policy"
    exit 1
fi

# Cleanup
rm -f /tmp/github-actions-policy.json
