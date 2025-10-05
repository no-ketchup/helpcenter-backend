from ..domain import models
from .base import BaseRepository
from .category import CategoryRepository
from .guide import GuideRepository

category_mapper = CategoryRepository()
guide_mapper = GuideRepository()
media_mapper = BaseRepository(models.Media)
feedback_mapper = BaseRepository(models.Feedback)
