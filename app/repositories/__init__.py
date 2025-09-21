from app.domain import models
from app.repositories.base import BaseRepository
from app.repositories.category import CategoryRepository

category_mapper = CategoryRepository()
guide_mapper = BaseRepository(models.UserGuide)
media_mapper = BaseRepository(models.Media)
feedback_mapper = BaseRepository(models.Feedback)