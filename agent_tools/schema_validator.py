"""SchemaValidator — JSON Schema-like dict validation with zero external dependencies."""

from __future__ import annotations

from typing import Any

from .exceptions import ValidationError

# Mapping from schema type strings to Python types
_TYPE_MAP: dict[str, type | tuple[type, ...]] = {
    "str": str,
    "int": int,
    "float": (int, float),  # int is a valid float
    "bool": bool,
    "list": list,
    "dict": dict,
    "any": object,
}


class SchemaValidator:
    """
    Validate a data dict against a lightweight schema dict.

    Schema format::

        {
            "query": {"type": "str", "required": True},
            "limit": {"type": "int", "required": False},
            "mode":  {"type": "str", "enum": ["fast", "slow"]},
            "tags":  {"type": "list"},
            "meta":  {"type": "dict"},
        }

    Field spec keys:
        - ``type``     (str)  — one of str / int / float / bool / list / dict / any
        - ``required`` (bool) — default False; raises if field is absent/None
        - ``enum``     (list) — allowed values; checked after type
        - ``items``    (dict) — for type=="list", validate each element with this spec
        - ``properties`` (dict) — for type=="dict", recursively validate nested fields

    Raises:
        ValidationError — with the dotted field path embedded in the message.
    """

    def validate(self, data: dict, schema: dict, _path: str = "") -> None:
        """
        Validate *data* against *schema*.

        Args:
            data:   The dict to validate.
            schema: The schema definition.
            _path:  Internal — dotted path prefix used in error messages.

        Raises:
            ValidationError: If any field fails validation.
        """
        if not isinstance(data, dict):
            raise ValidationError(
                f"Expected dict, got {type(data).__name__}", _path or "<root>"
            )

        for field, spec in schema.items():
            field_path = f"{_path}.{field}" if _path else field

            value = data.get(field)
            is_missing = field not in data or value is None

            # --- required check ---
            if spec.get("required", False) and is_missing:
                raise ValidationError(f"Required field is missing or None.", field_path)

            # Skip further checks if field is absent and not required
            if is_missing:
                continue

            # --- type check ---
            type_str = spec.get("type")
            if type_str and type_str != "any":
                expected = _TYPE_MAP.get(type_str)
                if expected is None:
                    raise ValidationError(
                        f"Unknown type '{type_str}' in schema.", field_path
                    )
                # Special-case: bool must be checked before int (bool is subclass of int)
                if type_str == "int" and isinstance(value, bool):
                    raise ValidationError(
                        f"Expected int, got bool.", field_path
                    )
                if type_str == "float":
                    if not isinstance(value, (int, float)) or isinstance(value, bool):
                        raise ValidationError(
                            f"Expected float/int, got {type(value).__name__}.", field_path
                        )
                elif not isinstance(value, expected):
                    raise ValidationError(
                        f"Expected {type_str}, got {type(value).__name__}.", field_path
                    )

            # --- enum check ---
            allowed = spec.get("enum")
            if allowed is not None and value not in allowed:
                raise ValidationError(
                    f"Value {value!r} not in allowed enum {allowed}.", field_path
                )

            # --- list items check ---
            if spec.get("type") == "list" and "items" in spec and isinstance(value, list):
                item_spec = spec["items"]
                for idx, item in enumerate(value):
                    item_path = f"{field_path}[{idx}]"
                    self._validate_value(item, item_spec, item_path)

            # --- nested dict properties check ---
            if spec.get("type") == "dict" and "properties" in spec and isinstance(value, dict):
                self.validate(value, spec["properties"], _path=field_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_value(self, value: Any, spec: dict, path: str) -> None:
        """Validate a single value against a field spec (used for list items)."""
        type_str = spec.get("type")
        if type_str and type_str != "any":
            expected = _TYPE_MAP.get(type_str)
            if expected is None:
                raise ValidationError(f"Unknown type '{type_str}' in schema.", path)
            if type_str == "int" and isinstance(value, bool):
                raise ValidationError(f"Expected int, got bool.", path)
            if type_str == "float":
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    raise ValidationError(
                        f"Expected float/int, got {type(value).__name__}.", path
                    )
            elif not isinstance(value, expected):
                raise ValidationError(
                    f"Expected {type_str}, got {type(value).__name__}.", path
                )

        allowed = spec.get("enum")
        if allowed is not None and value not in allowed:
            raise ValidationError(
                f"Value {value!r} not in allowed enum {allowed}.", path
            )

        if spec.get("type") == "dict" and "properties" in spec and isinstance(value, dict):
            self.validate(value, spec["properties"], _path=path)
