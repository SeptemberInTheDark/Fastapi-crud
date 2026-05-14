from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.advertisement import Advertisement
from app.schemas.advertisement import (
    AdvertisementCreate,
    AdvertisementUpdate,
    AdvertisementRead,
    AdvertisementList,
)

router = APIRouter(prefix="/advertisement", tags=["Advertisements"])


@router.post("", response_model=AdvertisementRead, status_code=status.HTTP_201_CREATED)
async def create_advertisement(
    payload: AdvertisementCreate,
    db: AsyncSession = Depends(get_db),
):
    advert = Advertisement(**payload.model_dump())
    db.add(advert)
    await db.commit()
    await db.refresh(advert)
    return advert


@router.get("/{advertisement_id}", response_model=AdvertisementRead)
async def get_advertisement(
    advertisement_id: int,
    db: AsyncSession = Depends(get_db),
):
    advert = await db.get(Advertisement, advertisement_id)
    if not advert:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return advert



@router.patch("/{advertisement_id}", response_model=AdvertisementRead)
async def update_advertisement(
    advertisement_id: int,
    payload: AdvertisementUpdate,
    db: AsyncSession = Depends(get_db),
):
    advert = await db.get(Advertisement, advertisement_id)
    if not advert:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(advert, field, value)

    await db.commit()
    await db.refresh(advert)
    return advert



@router.delete("/{advertisement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_advertisement(
    advertisement_id: int,
    db: AsyncSession = Depends(get_db),
):
    advert = await db.get(Advertisement, advertisement_id)
    if not advert:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    await db.delete(advert)
    await db.commit()



@router.get("", response_model=AdvertisementList)
async def search_advertisements(
    title: Optional[str] = Query(None, description="Поиск по заголовку (частичное совпадение)"),
    author: Optional[str] = Query(None, description="Поиск по автору (частичное совпадение)"),
    price_min: Optional[Decimal] = Query(None, gt=0, description="Минимальная цена"),
    price_max: Optional[Decimal] = Query(None, gt=0, description="Максимальная цена"),
    limit: int = Query(20, ge=1, le=100, description="Количество результатов"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if title:
        filters.append(Advertisement.title.ilike(f"%{title}%"))
    if author:
        filters.append(Advertisement.author.ilike(f"%{author}%"))
    if price_min is not None:
        filters.append(Advertisement.price >= price_min)
    if price_max is not None:
        filters.append(Advertisement.price <= price_max)

    where_clause = and_(*filters) if filters else True

    total_result = await db.execute(
        select(func.count()).select_from(Advertisement).where(where_clause)
    )
    total = total_result.scalar_one()

    items_result = await db.execute(
        select(Advertisement)
        .where(where_clause)
        .order_by(Advertisement.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = items_result.scalars().all()

    return AdvertisementList(total=total, items=list(items))
