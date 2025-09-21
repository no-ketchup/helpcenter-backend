from app.mappers.base import BaseMapper
from app.domain.models import Category

class CategoryMapper(BaseMapper[Category]):
    model = Category