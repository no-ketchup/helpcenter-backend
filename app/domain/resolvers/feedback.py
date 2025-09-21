import strawberry
from app.core.db import get_session_cm
from app.domain.models import Feedback as FeedbackModel
from app.domain.schema import Feedback as FeedbackType


def to_feedback(model: FeedbackModel) -> FeedbackType:
    return FeedbackType(
        id=str(model.id),
        name=model.name,
        email=model.email,
        message=model.message,
        expectReply=model.expect_reply,
        createdAt=model.created_at,
    )


@strawberry.type
class FeedbackMutation:
    @strawberry.mutation
    async def submitFeedback(
        self, name: str, email: str, message: str, expectReply: bool
    ) -> FeedbackType:
        async with get_session_cm() as session:
            fb = FeedbackModel(
                name=name,
                email=email,
                message=message,
                expect_reply=expectReply,
            )
            session.add(fb)
            await session.commit()
            await session.refresh(fb)
            return to_feedback(fb)