# AWS scripts

Bash helpers in this folder provision or update a small set of AWS resources used around NetGarde (S3, CloudFront, IAM for GitHub Actions). They are optional, local tooling—not the main application runtime.

Configuration values are read from `aws/.env`; see `.env.example` for the variable names.

## Structure

```text
aws/
├── README.md
├── .env.example          # committed; placeholder variable names and values
├── .env                  # local only (gitignored); real values for your account
├── s3-setup.sh
├── cloudfront-backend-setup.sh
└── update-github-actions-role.sh
```

## `s3-setup.sh`

Creates the frontend S3 bucket if it does not already exist, then turns on static website hosting (`index.html` for both index and error document), applies a public read bucket policy, relaxes the bucket public-access block so that policy can take effect, and sets a permissive CORS rule for GET/HEAD. Prints the S3 website endpoint when finished.

## `cloudfront-backend-setup.sh`

Builds a CloudFront distribution config with an HTTP custom origin to the EC2 public DNS name and backend port from the environment file, HTTPS for viewers, query strings and cookies forwarded, cache TTLs set to zero for the default behavior, and all common HTTP methods allowed. Creates the distribution via the AWS CLI and prints the new distribution id and domain.

## `update-github-actions-role.sh`

Replaces or creates an inline IAM policy on the configured GitHub Actions role: ECR image push/pull actions, list/read/write/delete objects for the frontend S3 bucket, and CloudFront invalidation APIs. Intended for an OIDC-based deploy role used by CI.
