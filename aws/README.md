# AWS deployment helpers

One-off **bash** scripts for provisioning a few AWS resources used by NetGarde (S3 static frontend bucket, CloudFront in front of the API, IAM policy for GitHub Actions). They are **not** run by CI by default; run them from your machine with the AWS CLI when you need to create or refresh that infrastructure.

## Scripts

| File | What it does | When to run |
|------|----------------|-------------|
| `s3-setup.sh` | Creates (or reuses) the frontend S3 bucket, static website mode, public read policy, CORS. | First-time frontend hosting, or after changing bucket policy/CORS needs. |
| `cloudfront-backend-setup.sh` | Creates a **new** CloudFront distribution pointing at your EC2 API (`BACKEND_EC2_PUBLIC_DNS` + port). Uses `jq` to parse the CLI response. | When you need HTTPS/edge in front of the backend. Each run creates another distribution (unique caller reference). |
| `update-github-actions-role.sh` | Puts an inline IAM policy on the GitHub Actions OIDC role (ECR + S3 deploy + CloudFront invalidation). | After creating the role, or when you change bucket/permission needs. Requires IAM admin rights. |

## Configuration

Scripts load **`aws/.env`** (gitignored). Copy once and fill in real values:

```bash
cd aws
cp .env.example .env
```

`.env.example` is **placeholders only** (`YOUR_*`, fake IDs). Never commit `.env` or put access keys / `.pem` files in it.

## First-time flow (suggested)

1. Configure AWS CLI (`aws configure`) and ensure your user can create S3, CloudFront, and (for the IAM script) attach role policies.
2. `cp .env.example .env` and set variables to match your account (bucket name, EC2 public DNS, GitHub Actions role name, etc.).
3. `./s3-setup.sh` — frontend bucket.
4. `./cloudfront-backend-setup.sh` — API CloudFront; note the printed domain and set `BACKEND_API_URL` (or equivalent) in your frontend deploy workflow.
5. `./update-github-actions-role.sh` — align the deploy role with your `FRONTEND_S3_BUCKET` and invalidation needs.

**Bucket names** are global; if `FRONTEND_S3_BUCKET` is taken, pick a unique name in `.env` before `s3-setup.sh`.

**Backend compute** (EC2, ECS, etc.) and **RDS** are not created by these scripts; provision them separately (console, Terraform, or other docs in the repo).

## Prerequisites

- AWS CLI v2, account credentials with permissions for the operations above.
- `jq` installed (for `cloudfront-backend-setup.sh`).
- `bash` and standard Unix tools.

## Architecture (high level)

- **S3** (and often **CloudFront**): static frontend assets.
- **Backend API**: served from your compute (e.g. EC2); optional CloudFront distribution from `cloudfront-backend-setup.sh` gives a stable HTTPS URL.
- **RDS**: PostgreSQL for app data (endpoint configured in app/env, not by these scripts).
- **GitHub Actions**: CI/CD; `update-github-actions-role.sh` tightens permissions for deploy jobs that push to ECR/S3 and invalidate CloudFront.
