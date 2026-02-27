"""Tests for the Open Contract Validator."""

import sys
import os
import json
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contract_validator import (
    validate_contract,
    validate_date,
    validate_party,
    validate_tender,
    DEMO_CONTRACT,
)


def test_valid_demo_contract():
    result = validate_contract(DEMO_CONTRACT)
    assert result["valid"] is True
    assert result["errors"] == []


def test_missing_required_top_level_fields():
    result = validate_contract({})
    assert result["valid"] is False
    field_errors = " ".join(result["errors"])
    for field in ["ocid", "id", "date", "tag", "initiationType", "parties", "buyer", "tender"]:
        assert field in field_errors


def test_invalid_date_format():
    errors = validate_date("not-a-date", "date")
    assert len(errors) == 1
    assert "invalid date format" in errors[0]


def test_valid_date_format():
    errors = validate_date("2024-01-15T00:00:00Z", "date")
    assert errors == []


def test_invalid_party_missing_fields():
    errors = validate_party({}, 0)
    assert any("id" in e for e in errors)
    assert any("name" in e for e in errors)
    assert any("roles" in e for e in errors)


def test_invalid_party_role():
    party = {"id": "p1", "name": "Party One", "roles": ["invalid-role"]}
    errors = validate_party(party, 0)
    assert any("invalid role" in e for e in errors)


def test_valid_party():
    party = {"id": "p1", "name": "Party One", "roles": ["buyer"]}
    errors = validate_party(party, 0)
    assert errors == []


def test_invalid_tender_status():
    tender = {"id": "t1", "title": "Test", "status": "bad-status", "procurementMethod": "open"}
    errors = validate_tender(tender)
    assert any("status" in e for e in errors)


def test_invalid_tender_procurement_method():
    tender = {"id": "t1", "title": "Test", "status": "active", "procurementMethod": "secret"}
    errors = validate_tender(tender)
    assert any("procurementMethod" in e for e in errors)


def test_invalid_tender_currency():
    tender = {
        "id": "t1", "title": "Test", "status": "active", "procurementMethod": "open",
        "value": {"amount": 1000, "currency": "INVALID"}
    }
    errors = validate_tender(tender)
    assert any("currency" in e for e in errors)


def test_valid_contract_from_file():
    sample_path = os.path.join(os.path.dirname(__file__), "sample_contracts", "valid_contract.json")
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = validate_contract(data)
    assert result["valid"] is True


def test_invalid_contract_from_file():
    sample_path = os.path.join(os.path.dirname(__file__), "sample_contracts", "invalid_contract.json")
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = validate_contract(data)
    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_non_dict_input():
    result = validate_contract("not a dict")
    assert result["valid"] is False
    assert "JSON object" in result["errors"][0]


def test_ocid_warning():
    contract = dict(DEMO_CONTRACT)
    contract["ocid"] = "bad-prefix-001"
    result = validate_contract(contract)
    assert any("ocid" in w for w in result["warnings"])


def test_empty_parties_warning():
    contract = dict(DEMO_CONTRACT)
    contract["parties"] = []
    result = validate_contract(contract)
    assert any("parties" in w for w in result["warnings"])
