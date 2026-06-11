"""Example service with business logic."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ExampleItem
from app.schemas.request import ExampleCreateRequest, ExampleUpdateRequest


class ExampleService:
    """Example service — replace with actual business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_item(self, item_id: int) -> ExampleItem | None:
        """Get an item by ID."""
        result = await self.session.execute(
            select(ExampleItem).where(ExampleItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def create_item(self, data: ExampleCreateRequest) -> ExampleItem:
        """Create a new item."""
        item = ExampleItem(**data.model_dump())
        self.session.add(item)
        await self.session.flush()
        return item

    async def update_item(
        self, item_id: int, data: ExampleUpdateRequest
    ) -> ExampleItem | None:
        """Update an existing item."""
        item = await self.get_item(item_id)
        if item is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        await self.session.flush()
        return item

    async def delete_item(self, item_id: int) -> bool:
        """Delete an item."""
        item = await self.get_item(item_id)
        if item is None:
            return False
        await self.session.delete(item)
        await self.session.flush()
        return True
