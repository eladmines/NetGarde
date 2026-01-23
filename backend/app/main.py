from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from app.shared.utils.logging import setup_logging
from app.shared.dependencies import get_db
from app.features.blocked_sites.routes.blocked_site_route import router as blocked_site_router
from app.features.categories.routes.category_route import router as category_router

# Initialize logging early
setup_logging()

# Middleware to ensure redirects use HTTPS when behind CloudFront
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # If it's a redirect response, ensure it uses HTTPS
        if isinstance(response, RedirectResponse):
            url = str(response.headers.get("location", ""))
            # Check X-Forwarded-Proto header from CloudFront
            forwarded_proto = request.headers.get("X-Forwarded-Proto", "http")
            # If CloudFront sent HTTPS, ensure redirect uses HTTPS
            if forwarded_proto == "https" and url.startswith("http://"):
                url = url.replace("http://", "https://", 1)
                response.headers["location"] = url
            # Also check if it's a CloudFront domain and force HTTPS
            elif "cloudfront.net" in url and url.startswith("http://"):
                url = url.replace("http://", "https://", 1)
                response.headers["location"] = url
        return response

app = FastAPI(
    title="NetGarde API",
    redirect_slashes=False,  # allow redirects for trailing slash handling
)

# Add HTTPS redirect middleware first (before other middleware)
app.add_middleware(HTTPSRedirectMiddleware)

# Trust proxy headers (CloudFront / ALB)
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts="*",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://d2qp7beltc09b8.cloudfront.net",  # production frontend
        "http://localhost:3000",                  # local dev
        "http://localhost:3001",                  # local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}

# Include routers
app.include_router(blocked_site_router)
app.include_router(category_router)
