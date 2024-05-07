"""A functional dependency that adds a pagination query string parameter to a
FastAPI path operation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from fastapi import Query

__all__ = ["Pagination", "SortOrder", "pagination_dependency"]


class SortOrder(str, Enum):
    """Sort order."""

    asc = "asc"
    desc = "desc"


@dataclass
class Pagination:
    """Pagination parameters."""

    page: int
    """The requested page number."""

    limit: int
    """The requested number of items per page."""

    order: SortOrder
    """The requested sort order."""

    @property
    def query_params(self) -> dict[str, str]:
        """Get the URL query string parameters for this page.

        This can be used to build a URL with a query string for the current
        page.
        """
        return {
            "page": str(self.page),
            "limit": str(self.limit),
            "order": self.order.value,
        }


async def pagination_dependency(
    page: Annotated[
        int, Query(ge=1, title="Pagination page.", examples=[1, 2, 3])
    ] = 1,
    limit: Annotated[
        int, Query(title="Max number of items in page.", examples=[10, 20, 30])
    ] = 10,
    order: Annotated[
        SortOrder,
        Query(title="Sort order.", examples=[SortOrder.asc, SortOrder.desc]),
    ] = SortOrder.asc,
) -> Pagination:
    """Add pagination query string parameters to a FastAPI path operation.

    This dependency adds three query string parameters to a FastAPI path
    operation: `page`, `limit`, and `order`.

    Note that this sets up "offset" pagination, which is simple to implement
    for this demo. With a real database, you may want to look into "cursor"
    based pagination for better performance and reliability with dynamic data.

    Parameters
    ----------
    page
        The page number.
    limit
        The number of items to return per page.
    order
        The sort order.

    Returns
    -------
    Pagination
        A container with the `page`, `limit`, and `order` query string
        parameters.
    """
    return Pagination(page=page, limit=limit, order=order)
