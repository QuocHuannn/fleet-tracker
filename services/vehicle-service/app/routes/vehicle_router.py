from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any
import uuid

from app.database import get_db
from app.models import Vehicle, VehicleStatus, VehicleType, VehicleNotFoundError, DuplicateLicensePlateError

router = APIRouter()

@router.get("/vehicles")
async def get_vehicles(
    status: Optional[VehicleStatus] = None,
    type: Optional[VehicleType] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách xe với các bộ lọc
    """
    query = select(Vehicle)
    
    # Áp dụng các bộ lọc
    if status:
        query = query.where(Vehicle.status == status)
    if type:
        query = query.where(Vehicle.type == type)
    if search:
        query = query.where(
            (Vehicle.name.ilike(f"%{search}%")) | 
            (Vehicle.license_plate.ilike(f"%{search}%"))
        )
    
    # Phân trang
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    vehicles = result.scalars().all()
    
    return [vehicle.to_dict() for vehicle in vehicles]

@router.get("/vehicles/{vehicle_id}")
async def get_vehicle(
    vehicle_id: uuid.UUID = Path(..., title="Vehicle ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy thông tin chi tiết của một xe
    """
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise VehicleNotFoundError(str(vehicle_id))
    
    return vehicle.to_dict()

@router.post("/vehicles")
async def create_vehicle(
    vehicle_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo xe mới
    """
    # Kiểm tra biển số xe đã tồn tại chưa
    result = await db.execute(
        select(Vehicle).where(Vehicle.license_plate == vehicle_data["license_plate"])
    )
    if result.scalar_one_or_none():
        raise DuplicateLicensePlateError(vehicle_data["license_plate"])
    
    # Tạo xe mới
    vehicle = Vehicle(
        name=vehicle_data["name"],
        license_plate=vehicle_data["license_plate"],
        type=vehicle_data["type"],
        status=vehicle_data.get("status", VehicleStatus.ACTIVE),
        description=vehicle_data.get("description")
    )
    
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    
    return vehicle.to_dict()

@router.put("/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: uuid.UUID = Path(..., title="Vehicle ID"),
    vehicle_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật thông tin xe
    """
    # Kiểm tra xe tồn tại
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise VehicleNotFoundError(str(vehicle_id))
    
    # Kiểm tra biển số xe nếu có thay đổi
    if "license_plate" in vehicle_data and vehicle_data["license_plate"] != vehicle.license_plate:
        result = await db.execute(
            select(Vehicle).where(Vehicle.license_plate == vehicle_data["license_plate"])
        )
        if result.scalar_one_or_none():
            raise DuplicateLicensePlateError(vehicle_data["license_plate"])
    
    # Cập nhật thông tin
    for key, value in vehicle_data.items():
        if hasattr(vehicle, key):
            setattr(vehicle, key, value)
    
    await db.commit()
    await db.refresh(vehicle)
    
    return vehicle.to_dict()

@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: uuid.UUID = Path(..., title="Vehicle ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa xe
    """
    # Kiểm tra xe tồn tại
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise VehicleNotFoundError(str(vehicle_id))
    
    # Xóa xe
    await db.delete(vehicle)
    await db.commit()
    
    return {"message": f"Vehicle with ID {vehicle_id} deleted successfully"}
