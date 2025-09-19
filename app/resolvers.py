from typing import List, Optional
import strawberry
from sqlmodel import select
from .db import get_session
from .models import (
    Category as CategoryModel,
    UserGuide as UserGuideModel,
    Feedback as FeedbackModel,
    Media as MediaModel,
)
from .schema import Category, Media, UserGuide, Feedback


# -------------------------------
# Mapping helpers
# -------------------------------
def to_category(model: CategoryModel) -> Category:
    return Category(
        id=str(model.id),
        name=model.name,
        description=model.description,
        slug=model.slug,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
        guides=[to_userguide_shallow(g) for g in model.guides],  # avoid infinite recursion
    )


def to_media(model: MediaModel) -> Media:
    return Media(
        id=str(model.id),
        alt=model.alt,
        url=model.url,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
    )


def to_userguide(model: UserGuideModel) -> UserGuide:
    return UserGuide(
        id=str(model.id),
        title=model.title,
        slug=model.slug,
        estimatedReadTime=model.estimated_read_time,
        body=model.body,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
        categories=[to_category_shallow(c) for c in model.categories],
        media=[to_media(m) for m in model.media],
    )


def to_feedback(model: FeedbackModel) -> Feedback:
    return Feedback(
        id=str(model.id),
        name=model.name,
        email=model.email,
        message=model.message,
        expectReply=model.expect_reply,
        createdAt=model.created_at,
    )

def to_category_shallow(model: CategoryModel) -> Category:
    return Category(
        id=str(model.id),
        name=model.name,
        description=model.description,
        slug=model.slug,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
        guides=[],
    )


def to_userguide_shallow(model: UserGuideModel) -> UserGuide:
    return UserGuide(
        id=str(model.id),
        title=model.title,
        slug=model.slug,
        estimatedReadTime=model.estimated_read_time,
        body=model.body,
        createdAt=model.created_at,
        updatedAt=model.updated_at,
        categories=[],
        media=[to_media(m) for m in model.media],
    )


# -------------------------------
# Queries
# -------------------------------
@strawberry.type
class Query:
    @strawberry.field(description="Fetch all categories")
    def categories(self) -> List[Category]:
        with next(get_session()) as session:
            results = session.exec(select(CategoryModel)).all()
            return [to_category(c) for c in results]

    @strawberry.field(description="Fetch a single category by slug")
    def category(self, slug: str) -> Optional[Category]:
        session = next(get_session())
        result = session.exec(select(CategoryModel).where(CategoryModel.slug == slug)).first()
        return to_category(result) if result else None

    @strawberry.field(description="Fetch all guides (optionally filtered by category slug)")
    def guides(self, categorySlug: Optional[str] = None) -> List[UserGuide]:
        session = next(get_session())
        query = select(UserGuideModel)
        if categorySlug:
            query = query.where(UserGuideModel.categories.any(CategoryModel.slug == categorySlug))
        results = session.exec(query).all()
        return [to_userguide(g) for g in results]

    @strawberry.field(description="Fetch a single guide by slug")
    def guide(self, slug: str) -> Optional[UserGuide]:
        session = next(get_session())
        result = session.exec(select(UserGuideModel).where(UserGuideModel.slug == slug)).first()
        return to_userguide(result) if result else None


# -------------------------------
# Mutations
# -------------------------------
@strawberry.type
class Mutation:
    @strawberry.mutation(description="Submit feedback from user")
    def submitFeedback(self, name: str, email: str, message: str, expectReply: bool) -> Feedback:
        session = next(get_session())
        feedback = FeedbackModel(name=name, email=email, message=message, expect_reply=expectReply)
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        return to_feedback(feedback)