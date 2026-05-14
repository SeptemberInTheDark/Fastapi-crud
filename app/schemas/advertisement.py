from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AdvertisementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, examples=["Продам велосипед"])
    description: str = Field(..., min_length=1, examples=["Велосипед горный, 2022 год"])
    price: Decimal = Field(..., gt=0, decimal_places=2, examples=[5000.00])
    author: str = Field(..., min_length=1, max_length=255, examples=["Иван Иванов"])

    @field_validator("title", "author", "description")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    author: Optional[str] = Field(None, min_length=1, max_length=255)

    @field_validator("title", "author", "description")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v


class AdvertisementRead(BaseModel):
    id: int
    title: str
    description: str
    price: Decimal
    author: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AdvertisementList(BaseModel):
    total: int
    items: list[AdvertisementRead]
