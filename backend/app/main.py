from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.shared.utils.logging import setup_logging
from app.shared.config import settings
from sqlalchemy.orm import Session
from app.shared.dependencies import get_db
from app.features.blocked_sites.routes.blocked_site_route import router as blocked_site_router
from app.features.categories.routes.category_route import router as category_router
# Initialize logging early
setup_logging()

app = FastAPI(title="NetGarde API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}

app.include_router(blocked_site_router)
app.include_router(category_router)
