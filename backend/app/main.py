from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from sqlalchemy.orm import Session

from app.shared.utils.logging import setup_logging
from app.shared.dependencies import get_db
from app.features.blocked_sites.routes.blocked_site_route import router as blocked_site_router
from app.features.categories.routes.category_route import router as category_router

# Initialize logging early
setup_logging()

app = FastAPI(
    title="NetGarde API",
    redirect_slashes=True,  # allow redirects for trailing slash handling
)

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
