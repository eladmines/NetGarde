#!/bin/bash
# Bash script to create a CloudFront distribution for the backend API

# Configuration
AWS_REGION="us-east-1"
EC2_IP="44.218.45.174"
EC2_PUBLIC_DNS="ec2-44-218-45-174.compute-1.amazonaws.com"
BACKEND_PORT="8000"
DISTRIBUTION_COMMENT="NetGarde Backend API CDN"

echo "Setting up CloudFront distribution for NetGarde backend..."
echo "EC2 IP: $EC2_IP"
echo "EC2 Public DNS: $EC2_PUBLIC_DNS"
echo "Backend Port: $BACKEND_PORT"
echo ""

# Step 1: Create CloudFront distribution configuration
echo "Step 1: Creating CloudFront distribution configuration..."

cat > /tmp/cloudfront-backend-config.json <<EOF
{
  "CallerReference": "netgarde-backend-$(date +%Y%m%d%H%M%S)",
  "Comment": "$DISTRIBUTION_COMMENT",
  "DefaultCacheBehavior": {
    "TargetOriginId": "netgarde-backend-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 7,
      "Items": ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "Compress": true,
    "ForwardedValues": {
      "QueryString": true,
      "Cookies": {
        "Forward": "all"
      },
      "Headers": {
        "Quantity": 1,
        "Items": ["Host"]
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 0,
    "MaxTTL": 0
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "netgarde-backend-origin",
        "DomainName": "$EC2_PUBLIC_DNS",
        "CustomOriginConfig": {
          "HTTPPort": $BACKEND_PORT,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only",
          "OriginSslProtocols": {
            "Quantity": 1,
            "Items": ["TLSv1.2"]
          }
        }
      }
    ]
  },
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}
EOF

echo "[OK] Configuration file created"
echo ""

# Step 2: Create CloudFront distribution
echo "Step 2: Creating CloudFront distribution..."
if aws cloudfront create-distribution --distribution-config "file:///tmp/cloudfront-backend-config.json" --output json > /tmp/cloudfront-response.json 2>&1; then
    DISTRIBUTION_ID=$(cat /tmp/cloudfront-response.json | jq -r '.Distribution.Id')
    DOMAIN_NAME=$(cat /tmp/cloudfront-response.json | jq -r '.Distribution.DomainName')
    STATUS=$(cat /tmp/cloudfront-response.json | jq -r '.Distribution.Status')
    
    echo "[OK] CloudFront distribution created successfully!"
    echo ""
    echo "Distribution Details:"
    echo "  Distribution ID: $DISTRIBUTION_ID"
    echo "  Domain Name: $DOMAIN_NAME"
    echo "  Status: $STATUS"
    echo ""
    echo "IMPORTANT:"
    echo "  1. Update your frontend deployment workflow:"
    echo "     BACKEND_API_URL: https://$DOMAIN_NAME"
    echo "  2. Wait 5-10 minutes for CloudFront to deploy"
    echo "  3. Update EC2 security group to allow CloudFront IPs (optional)"
    echo ""
    echo "Your backend API will be available at: https://$DOMAIN_NAME"
else
    echo "[ERROR] Failed to create CloudFront distribution"
    cat /tmp/cloudfront-response.json
    exit 1
fi

# Cleanup
rm -f /tmp/cloudfront-backend-config.json /tmp/cloudfront-response.json
