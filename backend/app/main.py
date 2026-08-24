import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager
from sqlalchemy import text

from .database import engine, Base
from .routers import assets, inventory, reports


def migrate_db():
    """Auto-migrate: add missing columns for existing SQLite databases"""
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if not inspector.has_table("assets"):
        return
    columns = [c["name"] for c in inspector.get_columns("assets")]
    with engine.connect() as conn:
        migrations = [
            ("rfid_tag", "ALTER TABLE assets ADD COLUMN rfid_tag VARCHAR(64)"),
            ("management_unit", "ALTER TABLE assets ADD COLUMN management_unit VARCHAR(128)"),
            ("acquisition_method", "ALTER TABLE assets ADD COLUMN acquisition_method VARCHAR(32)"),
            ("custodian_dept", "ALTER TABLE assets ADD COLUMN custodian_dept VARCHAR(128)"),
            ("procurement_dept", "ALTER TABLE assets ADD COLUMN procurement_dept VARCHAR(128)"),
            ("license_plate", "ALTER TABLE assets ADD COLUMN license_plate VARCHAR(64)"),
            ("factory_date", "ALTER TABLE assets ADD COLUMN factory_date DATE"),
            ("manufacturer", "ALTER TABLE assets ADD COLUMN manufacturer VARCHAR(128)"),
            ("equipment_code", "ALTER TABLE assets ADD COLUMN equipment_code VARCHAR(64)"),
            ("equipment_group", "ALTER TABLE assets ADD COLUMN equipment_group VARCHAR(64)"),
            ("final_account", "ALTER TABLE assets ADD COLUMN final_account VARCHAR(64)"),
            ("card_date", "ALTER TABLE assets ADD COLUMN card_date DATE"),
            ("account_book", "ALTER TABLE assets ADD COLUMN account_book VARCHAR(128)"),
            ("accounting_item", "ALTER TABLE assets ADD COLUMN accounting_item VARCHAR(64)"),
            ("accounting_subject", "ALTER TABLE assets ADD COLUMN accounting_subject VARCHAR(64)"),
            ("vat", "ALTER TABLE assets ADD COLUMN vat NUMERIC(12, 2)"),
            ("installation_fee", "ALTER TABLE assets ADD COLUMN installation_fee NUMERIC(12, 2)"),
            ("shipping_fee", "ALTER TABLE assets ADD COLUMN shipping_fee NUMERIC(12, 2)"),
            ("other_fee", "ALTER TABLE assets ADD COLUMN other_fee NUMERIC(12, 2)"),
            ("depreciation_status", "ALTER TABLE assets ADD COLUMN depreciation_status VARCHAR(32)"),
            ("residual_rate", "ALTER TABLE assets ADD COLUMN residual_rate NUMERIC(5, 2)"),
            ("monthly_depreciation_rate", "ALTER TABLE assets ADD COLUMN monthly_depreciation_rate NUMERIC(8, 4)"),
            ("monthly_depreciation_amount", "ALTER TABLE assets ADD COLUMN monthly_depreciation_amount NUMERIC(12, 2)"),
            ("contract_code", "ALTER TABLE assets ADD COLUMN contract_code VARCHAR(64)"),
            ("acceptance_doc", "ALTER TABLE assets ADD COLUMN acceptance_doc VARCHAR(64)"),
            ("transfer_doc", "ALTER TABLE assets ADD COLUMN transfer_doc VARCHAR(64)"),
            ("scanable", "ALTER TABLE assets ADD COLUMN scanable VARCHAR(8)"),
            ("asset_class_code", "ALTER TABLE assets ADD COLUMN asset_class_code VARCHAR(32)"),
        ]
        for col_name, sql in migrations:
            if col_name not in columns:
                try:
                    conn.execute(text(sql))
                except Exception:
                    pass
        if "rfid_tag" not in columns:
            try:
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_assets_rfid_tag ON assets (rfid_tag)"))
            except Exception:
                pass
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    migrate_db()
    yield


app = FastAPI(
    title="固定资产盘点二维码系统",
    description="扫码盘点、盘点报告、加密二维码",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(assets.router)
app.include_router(inventory.router)
app.include_router(reports.router)

# Static files - serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/s/{token}", response_class=HTMLResponse)
def scan_redirect(token: str):
    """Serve inventory page for QR scan"""
    inventory_path = os.path.join(FRONTEND_DIR, "inventory.html")
    if os.path.exists(inventory_path):
        with open(inventory_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>inventory.html not found</h1>"


@app.get("/")
def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "固定资产盘点系统 API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
