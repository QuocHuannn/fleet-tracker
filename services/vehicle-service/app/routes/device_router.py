from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any
import uuid

from app.database import get_db
from app.models import Device, DeviceStatus, DeviceNotFoundError, Vehicle, VehicleNotFoundError

router = APIRouter()

@router.get("/devices")
async def get_devices(
    vehicle_id: Optional[uuid.UUID] = None,
    status: Optional[DeviceStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách thiết bị GPS với các bộ lọc
    """
    query = select(Device)
    
    # Áp dụng các bộ lọc
    if vehicle_id:
        query = query.where(Device.vehicle_id == vehicle_id)
    if status:
        query = query.where(Device.status == status)
    
    # Phân trang
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return [device.to_dict() for device in devices]

@router.get("/devices/{device_id}")
async def get_device(
    device_id: uuid.UUID = Path(..., title="Device ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy thông tin chi tiết của một thiết bị GPS
    """
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    
    if not device:
        raise DeviceNotFoundError(str(device_id))
    
    return device.to_dict()

@router.post("/vehicles/{vehicle_id}/devices")
async def create_device(
    vehicle_id: uuid.UUID = Path(..., title="Vehicle ID"),
    device_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo thiết bị GPS mới cho xe
    """
    # Kiểm tra xe tồn tại
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise VehicleNotFoundError(str(vehicle_id))
    
    # Kiểm tra IMEI đã tồn tại chưa
    result = await db.execute(select(Device).where(Device.imei == device_data["imei"]))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Device with IMEI {device_data['imei']} already exists")
    
    # Tạo thiết bị mới
    device = Device(
        vehicle_id=vehicle_id,
        imei=device_data["imei"],
        sim_card=device_data.get("sim_card"),
        model=device_data.get("model"),
        status=device_data.get("status", DeviceStatus.ACTIVE)
    )
    
    db.add(device)
    await db.commit()
    await db.refresh(device)
    
    return device.to_dict()

@router.put("/devices/{device_id}")
async def update_device(
    device_id: uuid.UUID = Path(..., title="Device ID"),
    device_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật thông tin thiết bị GPS
    """
    # Kiểm tra thiết bị tồn tại
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    
    if not device:
        raise DeviceNotFoundError(str(device_id))
    
    # Kiểm tra IMEI nếu có thay đổi
    if "imei" in device_data and device_data["imei"] != device.imei:
        result = await db.execute(select(Device).where(Device.imei == device_data["imei"]))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail=f"Device with IMEI {device_data['imei']} already exists")
    
    # Cập nhật thông tin
    for key, value in device_data.items():
        if hasattr(device, key):
            setattr(device, key, value)
    
    await db.commit()
    await db.refresh(device)
    
    return device.to_dict()

@router.delete("/devices/{device_id}")
async def delete_device(
    device_id: uuid.UUID = Path(..., title="Device ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa thiết bị GPS
    """
    # Kiểm tra thiết bị tồn tại
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    
    if not device:
        raise DeviceNotFoundError(str(device_id))
    
    # Xóa thiết bị
    await db.delete(device)
    await db.commit()
    
    return {"message": f"Device with ID {device_id} deleted successfully"}
