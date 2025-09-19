from uuid import uuid4
from .db import engine, Session
from .models import SQLModel, Category, UserGuide, Media
from .utils.time import utcnow


def seed():
    # Warning! Dev/Test only: reset DB every run
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Categories
        getting_started = Category(
            id=uuid4(),
            name="Getting Started (Test)",
            description="Introductory test data.",
            slug="getting-started-test",
            created_at=utcnow(),
        )
        troubleshooting = Category(
            id=uuid4(),
            name="Troubleshooting (Test)",
            description="Dummy problems + fixes.",
            slug="troubleshooting-test",
            created_at=utcnow(),
        )
        advanced = Category(
            id=uuid4(),
            name="Advanced (Test)",
            description="Pretend advanced guides for dev/test.",
            slug="advanced-test",
            created_at=utcnow(),
        )
        misc = Category(
            id=uuid4(),
            name="Miscellaneous (Test)",
            description="Random filler category for testing UI.",
            slug="misc-test",
            created_at=utcnow(),
        )

        # Guides (body = structured JSON)
        guides = [
            UserGuide(
                id=uuid4(),
                title="How to Get Started (Test)",
                slug="how-to-get-started-test",
                body={
                    "blocks": [
                        {"type": "heading", "level": 2, "text": "Welcome"},
                        {"type": "paragraph", "text": "This is just test guide #1. Nothing meaningful."},
                    ]
                },
                estimated_read_time=2,
                created_at=utcnow(),
                categories=[getting_started],
            ),
            UserGuide(
                id=uuid4(),
                title="Fixing Common Errors (Test)",
                slug="fixing-common-errors-test",
                body={
                    "blocks": [
                        {"type": "heading", "level": 2, "text": "Troubleshooting"},
                        {"type": "paragraph", "text": "This is just test guide #2. For testing only."},
                    ]
                },
                estimated_read_time=3,
                created_at=utcnow(),
                categories=[troubleshooting],
            ),
            UserGuide(
                id=uuid4(),
                title="Deep Dive into Features (Test)",
                slug="deep-dive-features-test",
                body={
                    "blocks": [
                        {"type": "heading", "level": 2, "text": "Advanced Topics"},
                        {"type": "paragraph", "text": "This is test guide #3. Looks advanced, but isn't."},
                    ]
                },
                estimated_read_time=5,
                created_at=utcnow(),
                categories=[advanced],
            ),
            UserGuide(
                id=uuid4(),
                title="Random Tips & Tricks (Test)",
                slug="random-tips-test",
                body={
                    "blocks": [
                        {"type": "heading", "level": 2, "text": "Tips & Tricks"},
                        {"type": "paragraph", "text": "This is test guide #4. Pure filler content."},
                    ]
                },
                estimated_read_time=4,
                created_at=utcnow(),
                categories=[misc],
            ),
            UserGuide(
                id=uuid4(),
                title="Guide with Multiple Categories (Test)",
                slug="multi-category-guide-test",
                body={
                    "blocks": [
                        {"type": "heading", "level": 2, "text": "Multi-category Demo"},
                        {"type": "paragraph", "text": "Belongs to multiple categories. For UI testing."},
                    ]
                },
                estimated_read_time=6,
                created_at=utcnow(),
                categories=[getting_started, advanced],
            ),
        ]

        # Media
        media = [
            Media(
                id=uuid4(),
                alt="Test Image 1",
                url="/images/test-image-1.png",
                created_at=utcnow(),
            ),
            Media(
                id=uuid4(),
                alt="Test Image 2",
                url="/images/test-image-2.png",
                created_at=utcnow(),
            ),
            Media(
                id=uuid4(),
                alt="Test Image 3",
                url="/images/test-image-3.png",
                created_at=utcnow(),
            ),
        ]

        # Attach media to guides
        guides[0].media.append(media[0])
        guides[1].media.append(media[1])
        guides[2].media.append(media[2])

        session.add_all([getting_started, troubleshooting, advanced, misc] + guides + media)
        session.commit()

        print("DB reset + populated with extended dummy test data (JSON bodies).")


if __name__ == "__main__":
    seed()