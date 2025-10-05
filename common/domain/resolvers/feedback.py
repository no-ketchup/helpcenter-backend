import strawberry

from ...utils.time import utcnow
from ..schema import Feedback as FeedbackType


@strawberry.type
class FeedbackMutation:
    @strawberry.mutation
    def submitFeedback(
        self, name: str, email: str, message: str, expectReply: bool
    ) -> FeedbackType:
        # Return mock data for now
        return FeedbackType(
            id="1",
            name=name,
            email=email,
            message=message,
            expectReply=expectReply,
            createdAt=utcnow(),
        )
