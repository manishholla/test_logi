from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import time

from app.database import db
from app.config import settings
from app.core.utils import archive_old_consignments

# Import routers
from app.api import auth, users, warehouses, consignments, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()

    # Setup scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        archive_old_consignments,
        CronTrigger(hour=2, minute=0),
        id='archive_consignments'
    )
    scheduler.start()

    yield

    # Shutdown
    await db.disconnect()
    scheduler.shutdown()


app = FastAPI(
    title=settings.app_name,
    description="Backend API for logistics company management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(warehouses.router)
app.include_router(consignments.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    return {"message": "Logistics Management System API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}