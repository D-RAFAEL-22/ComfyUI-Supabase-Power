"""Utility functions for Supabase Power nodes."""

from __future__ import annotations

import json
import traceback
from io import BytesIO
from typing import Any, Optional, Tuple, Union

import numpy as np
from PIL import Image


def image_to_bytes(
    image: Any,
    format: str = "PNG",
    quality: int = 95,
) -> Tuple[bytes, str]:
    """
    Convert ComfyUI IMAGE tensor to bytes.

    Args:
        image: ComfyUI IMAGE tensor (B, H, W, C) or single image (H, W, C)
        format: Output format (PNG, JPEG, WEBP)
        quality: JPEG/WEBP quality (1-100)

    Returns:
        Tuple of (image_bytes, content_type)
    """
    # Handle batched input (take first image)
    if len(image.shape) == 4:
        image = image[0]

    # Convert tensor to numpy
    img_np = image.cpu().numpy() if hasattr(image, 'cpu') else np.array(image)
    img_np = (img_np * 255).clip(0, 255).astype(np.uint8)

    # Handle different channel configurations
    if img_np.shape[-1] == 1:
        img_np = np.repeat(img_np, 3, axis=-1)
    elif img_np.shape[-1] == 4:
        # Keep RGBA for PNG, convert to RGB for others
        if format.upper() != "PNG":
            img_np = img_np[:, :, :3]
    elif img_np.shape[-1] > 4:
        img_np = img_np[:, :, :3]

    # Create PIL Image
    img_pil = Image.fromarray(img_np)

    # Save to buffer
    buffer = BytesIO()
    save_kwargs = {}

    format_upper = format.upper()
    if format_upper in ("JPEG", "JPG"):
        format_upper = "JPEG"
        save_kwargs["quality"] = quality
        if img_pil.mode == "RGBA":
            img_pil = img_pil.convert("RGB")
    elif format_upper == "WEBP":
        save_kwargs["quality"] = quality

    img_pil.save(buffer, format=format_upper, **save_kwargs)
    buffer.seek(0)

    content_types = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
    }

    return buffer.read(), content_types.get(format_upper, "application/octet-stream")


def bytes_to_image(
    data: bytes,
    return_batch: bool = True,
) -> Any:
    """
    Convert bytes to ComfyUI IMAGE tensor.

    Args:
        data: Image bytes
        return_batch: Whether to return batched tensor (B, H, W, C)

    Returns:
        ComfyUI IMAGE tensor
    """
    import torch

    img_pil = Image.open(BytesIO(data))

    # Convert to RGB if needed
    if img_pil.mode == "RGBA":
        # Create white background
        background = Image.new("RGB", img_pil.size, (255, 255, 255))
        background.paste(img_pil, mask=img_pil.split()[3])
        img_pil = background
    elif img_pil.mode != "RGB":
        img_pil = img_pil.convert("RGB")

    # Convert to numpy and normalize
    img_np = np.array(img_pil).astype(np.float32) / 255.0

    # Convert to tensor
    img_tensor = torch.from_numpy(img_np)

    if return_batch:
        img_tensor = img_tensor.unsqueeze(0)

    return img_tensor


def parse_json_safe(
    value: Union[str, dict, list],
    default: Any = None,
) -> Any:
    """
    Safely parse JSON string or return value if already parsed.

    Args:
        value: JSON string or already parsed value
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    if isinstance(value, (dict, list)):
        return value

    if not isinstance(value, str):
        return default

    value = value.strip()
    if not value:
        return default

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def format_error(
    exception: Exception,
    include_traceback: bool = False,
) -> str:
    """
    Format exception for user-friendly display.

    Args:
        exception: The exception to format
        include_traceback: Whether to include full traceback

    Returns:
        Formatted error string
    """
    error_type = type(exception).__name__
    error_msg = str(exception)

    # Handle common Supabase errors
    if "row-level security" in error_msg.lower():
        return f"RLS Error: {error_msg}. Use service_role key or configure RLS policies."

    if "JWT" in error_msg or "token" in error_msg.lower():
        return f"Authentication Error: {error_msg}. Check your API key."

    if "404" in error_msg or "not found" in error_msg.lower():
        return f"Not Found: {error_msg}"

    result = f"{error_type}: {error_msg}"

    if include_traceback:
        result += f"\n\nTraceback:\n{traceback.format_exc()}"

    return result


def build_query_with_filters(
    query: Any,
    filters: Optional[list] = None,
) -> Any:
    """
    Apply filter chain to a Supabase query.

    Args:
        query: Supabase query builder
        filters: List of filter dictionaries

    Returns:
        Modified query with filters applied
    """
    if not filters:
        return query

    for f in filters:
        column = f.get("column", "")
        op = f.get("op", "eq")
        value = f.get("value")

        if not column:
            continue

        # Map operator to PostgREST method
        if op == "eq":
            query = query.eq(column, value)
        elif op == "neq":
            query = query.neq(column, value)
        elif op == "gt":
            query = query.gt(column, value)
        elif op == "gte":
            query = query.gte(column, value)
        elif op == "lt":
            query = query.lt(column, value)
        elif op == "lte":
            query = query.lte(column, value)
        elif op == "like":
            query = query.like(column, value)
        elif op == "ilike":
            query = query.ilike(column, value)
        elif op == "is":
            query = query.is_(column, value)
        elif op == "in":
            # Value should be a list
            if isinstance(value, str):
                value = [v.strip() for v in value.split(",")]
            query = query.in_(column, value)
        elif op == "contains":
            query = query.contains(column, value)
        elif op == "containedBy":
            query = query.contained_by(column, value)
        elif op == "overlaps":
            query = query.overlaps(column, value)
        elif op == "textSearch":
            query = query.text_search(column, value)
        elif op == "match":
            query = query.match(value)
        elif op == "not":
            # Negated filter - value should be dict with op and value
            if isinstance(value, dict):
                inner_op = value.get("op", "eq")
                inner_value = value.get("value")
                query = query.not_.filter(column, inner_op, inner_value)

    return query


def apply_ordering(
    query: Any,
    order_config: Optional[Any] = None,
) -> Any:
    """
    Apply ordering configuration to query.

    Args:
        query: Supabase query builder
        order_config: OrderConfig instance or list of order dicts

    Returns:
        Modified query with ordering applied
    """
    if not order_config:
        return query

    # Handle OrderConfig dataclass
    if hasattr(order_config, 'orders'):
        orders = order_config.orders
    elif isinstance(order_config, list):
        orders = order_config
    else:
        return query

    for order in orders:
        column = order.get("column", "")
        ascending = order.get("ascending", True)
        nulls_first = order.get("nulls_first", False)

        if column:
            query = query.order(
                column,
                desc=not ascending,
                nullsfirst=nulls_first,
            )

    return query


def apply_pagination(
    query: Any,
    pagination: Optional[Any] = None,
) -> Any:
    """
    Apply pagination configuration to query.

    Args:
        query: Supabase query builder
        pagination: PaginationConfig instance or dict

    Returns:
        Modified query with pagination applied
    """
    if not pagination:
        return query

    # Handle PaginationConfig dataclass
    if hasattr(pagination, 'limit'):
        limit = pagination.limit
        offset = pagination.offset
        range_start = pagination.range_start
        range_end = pagination.range_end
    elif isinstance(pagination, dict):
        limit = pagination.get("limit")
        offset = pagination.get("offset")
        range_start = pagination.get("range_start")
        range_end = pagination.get("range_end")
    else:
        return query

    # Use range if both start and end are provided
    if range_start is not None and range_end is not None:
        query = query.range(range_start, range_end)
    else:
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

    return query
