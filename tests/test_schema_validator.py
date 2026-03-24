"""Tests for SchemaValidator."""

import pytest

from agent_tools import SchemaValidator, ValidationError


@pytest.fixture
def validator():
    return SchemaValidator()


# ── Basic type checks ──────────────────────────────────────────────────────────

def test_valid_str(validator):
    validator.validate({"name": "Alice"}, {"name": {"type": "str"}})


def test_valid_int(validator):
    validator.validate({"count": 5}, {"count": {"type": "int"}})


def test_valid_float(validator):
    validator.validate({"score": 3.14}, {"score": {"type": "float"}})


def test_int_accepted_as_float(validator):
    """int is a valid float value."""
    validator.validate({"score": 3}, {"score": {"type": "float"}})


def test_valid_bool(validator):
    validator.validate({"flag": True}, {"flag": {"type": "bool"}})


def test_valid_list(validator):
    validator.validate({"items": [1, 2, 3]}, {"items": {"type": "list"}})


def test_valid_dict(validator):
    validator.validate({"meta": {"k": "v"}}, {"meta": {"type": "dict"}})


def test_type_mismatch_str(validator):
    with pytest.raises(ValidationError, match="Expected str"):
        validator.validate({"name": 42}, {"name": {"type": "str"}})


def test_type_mismatch_int(validator):
    with pytest.raises(ValidationError, match="Expected int"):
        validator.validate({"count": "five"}, {"count": {"type": "int"}})


def test_bool_not_accepted_as_int(validator):
    """bool is a subclass of int in Python, but must be rejected for type=int."""
    with pytest.raises(ValidationError, match="Expected int, got bool"):
        validator.validate({"count": True}, {"count": {"type": "int"}})


# ── Required fields ────────────────────────────────────────────────────────────

def test_required_field_present(validator):
    validator.validate({"q": "hello"}, {"q": {"type": "str", "required": True}})


def test_required_field_missing(validator):
    with pytest.raises(ValidationError, match="Required field"):
        validator.validate({}, {"q": {"type": "str", "required": True}})


def test_required_field_none(validator):
    with pytest.raises(ValidationError, match="Required field"):
        validator.validate({"q": None}, {"q": {"type": "str", "required": True}})


def test_optional_field_missing_is_ok(validator):
    validator.validate({}, {"limit": {"type": "int", "required": False}})


# ── Enum ───────────────────────────────────────────────────────────────────────

def test_enum_valid(validator):
    validator.validate({"mode": "fast"}, {"mode": {"type": "str", "enum": ["fast", "slow"]}})


def test_enum_invalid(validator):
    with pytest.raises(ValidationError, match="not in allowed enum"):
        validator.validate({"mode": "turbo"}, {"mode": {"type": "str", "enum": ["fast", "slow"]}})


# ── Nested list items ──────────────────────────────────────────────────────────

def test_list_items_valid(validator):
    schema = {"tags": {"type": "list", "items": {"type": "str"}}}
    validator.validate({"tags": ["a", "b", "c"]}, schema)


def test_list_items_invalid(validator):
    schema = {"tags": {"type": "list", "items": {"type": "str"}}}
    with pytest.raises(ValidationError, match="Expected str"):
        validator.validate({"tags": ["a", 2]}, schema)


# ── Nested dict properties ─────────────────────────────────────────────────────

def test_nested_dict_valid(validator):
    schema = {
        "user": {
            "type": "dict",
            "properties": {
                "id": {"type": "int", "required": True},
                "email": {"type": "str"},
            },
        }
    }
    validator.validate({"user": {"id": 1, "email": "a@b.com"}}, schema)


def test_nested_dict_missing_required(validator):
    schema = {
        "user": {
            "type": "dict",
            "properties": {"id": {"type": "int", "required": True}},
        }
    }
    with pytest.raises(ValidationError, match="user.id"):
        validator.validate({"user": {}}, schema)


# ── Root not a dict ────────────────────────────────────────────────────────────

def test_root_not_dict(validator):
    with pytest.raises(ValidationError, match="Expected dict"):
        validator.validate("not a dict", {})  # type: ignore


# ── Unknown type in schema ─────────────────────────────────────────────────────

def test_unknown_type_raises(validator):
    with pytest.raises(ValidationError, match="Unknown type"):
        validator.validate({"x": 1}, {"x": {"type": "uint32"}})
