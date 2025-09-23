import strawberry
from .category import CategoryQuery
from .guide import GuideQuery
from .media import MediaQuery
from .feedback import FeedbackMutation


@strawberry.type
class Query(CategoryQuery, GuideQuery, MediaQuery):
    """Root Query composed of all sub-queries."""


@strawberry.type
class Mutation(FeedbackMutation):
    """Root Mutation composed of all sub-mutations."""


__all__ = ["Query", "Mutation"]
