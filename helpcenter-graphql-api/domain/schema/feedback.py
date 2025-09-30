from __future__ import annotations

from datetime import datetime

import strawberry


@strawberry.type
class Feedback:
    id: str
    name: str
    email: str
    message: str
    expectReply: bool
    createdAt: datetime
