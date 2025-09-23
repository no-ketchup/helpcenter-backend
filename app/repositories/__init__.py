from app.domain import models
from app.repositories.base import BaseRepository
from app.repositories.category import CategoryRepository
from app.repositories.guide import GuideRepository

category_mapper = CategoryRepository()
guide_mapper = GuideRepository()
media_mapper = BaseRepository(models.Media)
feedback_mapper = BaseRepository(models.Feedback)