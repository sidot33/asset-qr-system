from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, JSON, Enum, Date
from sqlalchemy.sql import func
from .database import Base
import enum


class AssetStatus(str, enum.Enum):
    IN_USE = "在用"
    IDLE = "闲置"
    REPAIR = "维修"
    SCRAPPED = "报废"


class DepreciationMethod(str, enum.Enum):
    STRAIGHT_LINE = "直线"
    DOUBLE_DECLINING = "双倍余额"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(32), unique=True, index=True, nullable=False, comment="资产编号")
    asset_name = Column(String(128), nullable=False, comment="资产名称")
    category = Column(String(64), nullable=False, comment="资产分类")
    spec_model = Column(String(128), comment="规格型号")
    serial_no = Column(String(64), comment="序列号/SN")
    brand = Column(String(64), comment="品牌")
    purchase_date = Column(Date, nullable=False, comment="购入日期")
    purchase_price = Column(Numeric(12, 2), nullable=False, comment="购入价格")
    department = Column(String(64), nullable=False, comment="使用部门")
    current_user = Column(String(32), comment="使用人")
    location = Column(String(128), nullable=False, comment="存放地点")
    status = Column(Enum(AssetStatus), nullable=False, default=AssetStatus.IN_USE, comment="资产状态")
    supplier = Column(String(128), comment="供应商")
    useful_life_months = Column(Integer, comment="使用期限(月)")
    depreciation_method = Column(Enum(DepreciationMethod), comment="折旧方法")
    accumulated_depreciation = Column(Numeric(12, 2), comment="累计折旧")
    net_value = Column(Numeric(12, 2), comment="净值")
    responsible_person = Column(String(32), nullable=False, comment="责任人")
    book_date = Column(Date, comment="入账日期")
    voucher_no = Column(String(32), comment="凭证号")
    remarks = Column(Text, comment="备注")
    photo_url = Column(String(255), comment="照片")
    rfid_tag = Column(String(64), unique=True, index=True, comment="RFID标签号")
    # 固定资产卡片扩展字段
    management_unit = Column(String(128), comment="管理单元")
    acquisition_method = Column(String(32), comment="取得方式")
    custodian_dept = Column(String(128), comment="归口管理")
    procurement_dept = Column(String(128), comment="采购部门")
    license_plate = Column(String(64), comment="牌照号")
    factory_date = Column(Date, comment="出厂日期")
    manufacturer = Column(String(128), comment="制造厂家")
    equipment_code = Column(String(64), comment="设备代码")
    equipment_group = Column(String(64), comment="设备成组")
    final_account = Column(String(64), comment="决算出项")
    card_date = Column(Date, comment="建卡时间")
    account_book = Column(String(128), comment="账套")
    accounting_item = Column(String(64), comment="核算项目")
    accounting_subject = Column(String(64), comment="核算科目")
    vat = Column(Numeric(12, 2), comment="增值税")
    installation_fee = Column(Numeric(12, 2), comment="安装费")
    shipping_fee = Column(Numeric(12, 2), comment="运杂费")
    other_fee = Column(Numeric(12, 2), comment="其他费用")
    depreciation_status = Column(String(32), comment="折旧状态")
    residual_rate = Column(Numeric(5, 2), comment="残值率(%)")
    monthly_depreciation_rate = Column(Numeric(8, 4), comment="月折旧率")
    monthly_depreciation_amount = Column(Numeric(12, 2), comment="月折旧额")
    contract_code = Column(String(64), comment="合同代码")
    acceptance_doc = Column(String(64), comment="验收单")
    transfer_doc = Column(String(64), comment="调拨单")
    scanable = Column(String(8), comment="可扫描")
    asset_class_code = Column(String(32), comment="资产类码")
    maintenance_logs = Column(JSON, default=list, comment="维护记录")
    inventory_logs = Column(JSON, default=list, comment="盘点记录")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class InventoryRecord(Base):
    __tablename__ = "inventory_records"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(32), nullable=False, index=True, comment="资产编号")
    inventory_person = Column(String(32), nullable=False, comment="盘点人")
    inventory_time = Column(DateTime, server_default=func.now(), comment="盘点时间")
    gps_location = Column(String(128), comment="GPS位置")
    device_info = Column(String(255), comment="扫码设备")
    original_location = Column(String(128), comment="原存放地点")
    actual_location = Column(String(128), comment="实际存放地点")
    status = Column(String(32), comment="盘点状态")
    task_id = Column(String(64), index=True, comment="盘点任务ID")
    created_at = Column(DateTime, server_default=func.now())


class InventoryTask(Base):
    __tablename__ = "inventory_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(64), unique=True, index=True, nullable=False, comment="任务ID")
    task_name = Column(String(128), nullable=False, comment="任务名称")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    status = Column(String(32), default="进行中", comment="任务状态")
    created_at = Column(DateTime, server_default=func.now())
