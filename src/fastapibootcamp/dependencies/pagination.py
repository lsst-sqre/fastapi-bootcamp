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
    """Pagination request parameters."""

    page: int
    """The requested page number."""

    limit: int
    """The requested number of items per page."""

    order: SortOrder
    """The requested sort order."""


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
    page : int, optional
        The page number, by default 1.
    limit : int, optional
        The number of items to return per page, by default 10.
    order : SortOrder, optional
        The sort order, by default SortOrder.asc.

    Returns
    -------
    Pagination
        A container with the `page`, `limit`, and `order` query string
        parameters.
    """
    return Pagination(page=page, limit=limit, order=order)
