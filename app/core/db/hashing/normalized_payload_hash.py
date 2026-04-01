from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, cast


def normalized_assets_to_json(normalized_assets: Sequence[object]) -> list[dict[str, Any]]:
    serialized_assets: list[dict[str, Any]] = []
    for asset in normalized_assets:
        if is_dataclass(asset):
            data = asdict(cast(Any, asset))
        elif isinstance(asset, dict):
            data = dict(asset)
        else:
            raise TypeError("normalized asset must be a dataclass or dict")
        serialized_assets.append(_canonicalize_value(data))

    return _sort_by_external_id_if_possible(serialized_assets)


def hash_normalized_payload(normalized_payload_json: Sequence[dict[str, Any]]) -> str:
    canonical_json = json.dumps(
        _sort_by_external_id_if_possible([_canonicalize_value(item) for item in normalized_payload_json]),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def _sort_by_external_id_if_possible(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if all(isinstance(item, dict) and "external_id" in item for item in payload):
        return sorted(
            payload,
            key=lambda item: (
                str(item.get("external_id", "")),
                json.dumps(item, sort_keys=True, separators=(",", ":")),
            ),
        )
    return payload


def _canonicalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _canonicalize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_canonicalize_value(item) for item in value]
    if isinstance(value, Decimal):
        return _canonicalize_decimal(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def _canonicalize_decimal(value: Decimal) -> str:
    if value.is_zero():
        return "0"
    return format(value.normalize(), "f")
