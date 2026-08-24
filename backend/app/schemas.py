from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime, date
from decimal import Decimal
from .models import AssetStatus, DepreciationMethod


class AssetBase(BaseModel):
    asset_code: str = Field(..., max_length=32)
    asset_name: str = Field(..., max_length=128)
    category: str = Field(..., max_length=64)
    spec_model: Optional[str] = Field(None, max_length=128)
    serial_no: Optional[str] = Field(None, max_length=64)
    brand: Optional[str] = Field(None, max_length=64)
    purchase_date: date
    purchase_price: Decimal = Field(..., decimal_places=2)
    department: str = Field(..., max_length=64)
    current_user: Optional[str] = Field(None, max_length=32)
    location: str = Field(..., max_length=128)
    status: AssetStatus = AssetStatus.IN_USE
    supplier: Optional[str] = Field(None, max_length=128)
    useful_life_months: Optional[int] = None
    depreciation_method: Optional[DepreciationMethod] = None
    accumulated_depreciation: Optional[Decimal] = Field(None, decimal_places=2)
    net_value: Optional[Decimal] = Field(None, decimal_places=2)
    responsible_person: str = Field(..., max_length=32)
    book_date: Optional[date] = None
    voucher_no: Optional[str] = Field(None, max_length=32)
    remarks: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=255)
    rfid_tag: Optional[str] = Field(None, max_length=64)
    # 固定资产卡片扩展字段
    management_unit: Optional[str] = Field(None, max_length=128)
    acquisition_method: Optional[str] = Field(None, max_length=32)
    custodian_dept: Optional[str] = Field(None, max_length=128)
    procurement_dept: Optional[str] = Field(None, max_length=128)
    license_plate: Optional[str] = Field(None, max_length=64)
    factory_date: Optional[date] = None
    manufacturer: Optional[str] = Field(None, max_length=128)
    equipment_code: Optional[str] = Field(None, max_length=64)
    equipment_group: Optional[str] = Field(None, max_length=64)
    final_account: Optional[str] = Field(None, max_length=64)
    card_date: Optional[date] = None
    account_book: Optional[str] = Field(None, max_length=128)
    accounting_item: Optional[str] = Field(None, max_length=64)
    accounting_subject: Optional[str] = Field(None, max_length=64)
    vat: Optional[Decimal] = Field(None, decimal_places=2)
    installation_fee: Optional[Decimal] = Field(None, decimal_places=2)
    shipping_fee: Optional[Decimal] = Field(None, decimal_places=2)
    other_fee: Optional[Decimal] = Field(None, decimal_places=2)
    depreciation_status: Optional[str] = Field(None, max_length=32)
    residual_rate: Optional[Decimal] = Field(None, decimal_places=2)
    monthly_depreciation_rate: Optional[Decimal] = Field(None, decimal_places=4)
    monthly_depreciation_amount: Optional[Decimal] = Field(None, decimal_places=2)
    contract_code: Optional[str] = Field(None, max_length=64)
    acceptance_doc: Optional[str] = Field(None, max_length=64)
    transfer_doc: Optional[str] = Field(None, max_length=64)
    scanable: Optional[str] = Field(None, max_length=8)
    asset_class_code: Optional[str] = Field(None, max_length=32)
    maintenance_logs: Optional[List[Any]] = []


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    category: Optional[str] = None
    spec_model: Optional[str] = None
    serial_no: Optional[str] = None
    brand: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    department: Optional[str] = None
    current_user: Optional[str] = None
    location: Optional[str] = None
    status: Optional[AssetStatus] = None
    supplier: Optional[str] = None
    useful_life_months: Optional[int] = None
    depreciation_method: Optional[DepreciationMethod] = None
    accumulated_depreciation: Optional[Decimal] = None
    net_value: Optional[Decimal] = None
    responsible_person: Optional[str] = None
    book_date: Optional[date] = None
    voucher_no: Optional[str] = None
    remarks: Optional[str] = None
    photo_url: Optional[str] = None
    rfid_tag: Optional[str] = None
    management_unit: Optional[str] = None
    acquisition_method: Optional[str] = None
    custodian_dept: Optional[str] = None
    procurement_dept: Optional[str] = None
    license_plate: Optional[str] = None
    factory_date: Optional[date] = None
    manufacturer: Optional[str] = None
    equipment_code: Optional[str] = None
    equipment_group: Optional[str] = None
    final_account: Optional[str] = None
    card_date: Optional[date] = None
    account_book: Optional[str] = None
    accounting_item: Optional[str] = None
    accounting_subject: Optional[str] = None
    vat: Optional[Decimal] = None
    installation_fee: Optional[Decimal] = None
    shipping_fee: Optional[Decimal] = None
    other_fee: Optional[Decimal] = None
    depreciation_status: Optional[str] = None
    residual_rate: Optional[Decimal] = None
    monthly_depreciation_rate: Optional[Decimal] = None
    monthly_depreciation_amount: Optional[Decimal] = None
    contract_code: Optional[str] = None
    acceptance_doc: Optional[str] = None
    transfer_doc: Optional[str] = None
    scanable: Optional[str] = None
    asset_class_code: Optional[str] = None
    maintenance_logs: Optional[List[Any]] = None


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    inventory_logs: Optional[List[Any]] = []

    class Config:
        orm_mode = True


class TokenPayload(BaseModel):
    asset_code: str
    exp: int
    nonce: str


class QRTokenResponse(BaseModel):
    token: str
    url: str
    asset_code: str


class InventoryConfirm(BaseModel):
    asset_code: str
    inventory_person: str
    actual_location: str
    gps_location: Optional[str] = None
    device_info: Optional[str] = None
    task_id: Optional[str] = None


class InventoryRecordResponse(BaseModel):
    id: int
    asset_code: str
    inventory_person: str
    inventory_time: datetime
    gps_location: Optional[str]
    device_info: Optional[str]
    original_location: Optional[str]
    actual_location: Optional[str]
    status: Optional[str]
    task_id: Optional[str]

    class Config:
        orm_mode = True


class InventoryTaskCreate(BaseModel):
    task_id: str
    task_name: str
    start_date: date
    end_date: date


class InventoryTaskResponse(BaseModel):
    id: int
    task_id: str
    task_name: str
    start_date: date
    end_date: date
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class ImportResponse(BaseModel):
    success: int
    failed: int
    errors: List[str]


class DiffReportItem(BaseModel):
    asset_code: str
    asset_name: str
    diff_type: str  # 已盘/盘亏/位置不符
    book_value: Optional[Decimal]
    expected_location: Optional[str]
    actual_location: Optional[str]
    expected_status: Optional[str]
    actual_status: Optional[str]
    inventory_time: Optional[datetime] = None
    inventory_person: Optional[str] = None


class DiffReportResponse(BaseModel):
    task_id: str
    task_name: Optional[str] = None
    total_assets: int
    checked_assets: int
    diff_items: List[DiffReportItem]
    generated_at: datetime
