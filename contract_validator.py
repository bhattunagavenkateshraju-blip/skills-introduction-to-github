"""
Open Contract Validator
=======================
A tool for validating open contracts against the Open Contracting Data Standard (OCDS).
Supports validation of procurement contracts, ensuring required fields,
data types, and business rules are met.

Usage:
    python contract_validator.py <contract_file.json>
    python contract_validator.py --demo
"""

import json
import sys
from datetime import datetime


REQUIRED_TOP_LEVEL_FIELDS = ["ocid", "id", "date", "tag", "initiationType", "parties", "buyer", "tender"]
REQUIRED_PARTY_FIELDS = ["id", "name", "roles"]
REQUIRED_TENDER_FIELDS = ["id", "title", "status", "procurementMethod"]
VALID_TAGS = ["planning", "tender", "tenderAmendment", "tenderUpdate", "tenderCancellation",
              "award", "awardUpdate", "awardCancellation", "contract", "contractUpdate",
              "contractAmendment", "implementation", "implementationUpdate", "contractTermination", "compiled"]
VALID_INITIATION_TYPES = ["tender"]
VALID_TENDER_STATUSES = ["planning", "planned", "active", "cancelled", "unsuccessful", "complete", "withdrawn"]
VALID_PROCUREMENT_METHODS = ["open", "selective", "limited", "direct"]
VALID_PARTY_ROLES = ["buyer", "supplier", "tenderer", "funder", "enquirer",
                     "payer", "payee", "reviewBody", "interestedParty", "procuringEntity"]


def validate_date(date_str, field_name):
    """Validate that a date string is in ISO 8601 format."""
    errors = []
    try:
        datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        errors.append(f"  - '{field_name}' has invalid date format '{date_str}'. Expected ISO 8601 (e.g. 2024-01-15T00:00:00Z)")
    return errors


def validate_party(party, index):
    """Validate a single party object."""
    errors = []
    prefix = f"parties[{index}]"
    for field in REQUIRED_PARTY_FIELDS:
        if field not in party:
            errors.append(f"  - Missing required field '{prefix}.{field}'")
    if "roles" in party:
        if not isinstance(party["roles"], list) or len(party["roles"]) == 0:
            errors.append(f"  - '{prefix}.roles' must be a non-empty list")
        else:
            for role in party["roles"]:
                if role not in VALID_PARTY_ROLES:
                    errors.append(f"  - '{prefix}.roles' contains invalid role '{role}'. Valid roles: {VALID_PARTY_ROLES}")
    return errors


def validate_tender(tender):
    """Validate the tender object."""
    errors = []
    for field in REQUIRED_TENDER_FIELDS:
        if field not in tender:
            errors.append(f"  - Missing required field 'tender.{field}'")
    if "status" in tender and tender["status"] not in VALID_TENDER_STATUSES:
        errors.append(f"  - 'tender.status' has invalid value '{tender['status']}'. Valid values: {VALID_TENDER_STATUSES}")
    if "procurementMethod" in tender and tender["procurementMethod"] not in VALID_PROCUREMENT_METHODS:
        errors.append(f"  - 'tender.procurementMethod' has invalid value '{tender['procurementMethod']}'. Valid values: {VALID_PROCUREMENT_METHODS}")
    if "tenderPeriod" in tender:
        period = tender["tenderPeriod"]
        if "startDate" in period:
            errors.extend(validate_date(period["startDate"], "tender.tenderPeriod.startDate"))
        if "endDate" in period:
            errors.extend(validate_date(period["endDate"], "tender.tenderPeriod.endDate"))
    if "value" in tender:
        value = tender["value"]
        if "amount" not in value:
            errors.append("  - Missing required field 'tender.value.amount'")
        if "currency" not in value:
            errors.append("  - Missing required field 'tender.value.currency'")
        elif not isinstance(value["currency"], str) or len(value["currency"]) != 3:
            errors.append(f"  - 'tender.value.currency' must be a 3-letter ISO 4217 currency code (e.g. 'USD')")
    return errors


def validate_award(award, index):
    """Validate a single award object."""
    errors = []
    prefix = f"awards[{index}]"
    for field in ["id", "status", "suppliers"]:
        if field not in award:
            errors.append(f"  - Missing required field '{prefix}.{field}'")
    if "date" in award:
        errors.extend(validate_date(award["date"], f"{prefix}.date"))
    if "value" in award:
        value = award["value"]
        if "amount" not in value:
            errors.append(f"  - Missing required field '{prefix}.value.amount'")
        if "currency" not in value:
            errors.append(f"  - Missing required field '{prefix}.value.currency'")
    return errors


def validate_contract(contract_data):
    """
    Validate an open contract JSON object against the OCDS standard.
    Returns a dict with 'valid' (bool), 'errors' (list), and 'warnings' (list).
    """
    errors = []
    warnings = []

    if not isinstance(contract_data, dict):
        return {"valid": False, "errors": ["Contract must be a JSON object"], "warnings": []}

    # Validate top-level required fields
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in contract_data:
            errors.append(f"  - Missing required top-level field '{field}'")

    # Validate OCID format
    if "ocid" in contract_data:
        ocid = contract_data["ocid"]
        if not isinstance(ocid, str) or not ocid.startswith("ocds-"):
            warnings.append(f"  - 'ocid' should start with 'ocds-' prefix (got: '{ocid}')")

    # Validate date
    if "date" in contract_data:
        errors.extend(validate_date(contract_data["date"], "date"))

    # Validate tag
    if "tag" in contract_data:
        tags = contract_data["tag"] if isinstance(contract_data["tag"], list) else [contract_data["tag"]]
        for tag in tags:
            if tag not in VALID_TAGS:
                errors.append(f"  - 'tag' has invalid value '{tag}'. Valid values: {VALID_TAGS}")

    # Validate initiationType
    if "initiationType" in contract_data:
        if contract_data["initiationType"] not in VALID_INITIATION_TYPES:
            errors.append(f"  - 'initiationType' has invalid value '{contract_data['initiationType']}'. Valid values: {VALID_INITIATION_TYPES}")

    # Validate parties
    if "parties" in contract_data:
        if not isinstance(contract_data["parties"], list):
            errors.append("  - 'parties' must be a list")
        else:
            if len(contract_data["parties"]) == 0:
                warnings.append("  - 'parties' list is empty")
            for i, party in enumerate(contract_data["parties"]):
                errors.extend(validate_party(party, i))

    # Validate buyer reference
    if "buyer" in contract_data:
        buyer = contract_data["buyer"]
        if "id" not in buyer:
            errors.append("  - Missing required field 'buyer.id'")

    # Validate tender
    if "tender" in contract_data:
        errors.extend(validate_tender(contract_data["tender"]))

    # Validate awards (optional)
    if "awards" in contract_data:
        if not isinstance(contract_data["awards"], list):
            errors.append("  - 'awards' must be a list")
        else:
            for i, award in enumerate(contract_data["awards"]):
                errors.extend(validate_award(award, i))

    # Validate contracts (optional)
    if "contracts" in contract_data:
        if not isinstance(contract_data["contracts"], list):
            errors.append("  - 'contracts' must be a list")
        else:
            for i, c in enumerate(contract_data["contracts"]):
                if "id" not in c:
                    errors.append(f"  - Missing required field 'contracts[{i}].id'")
                if "awardID" not in c:
                    warnings.append(f"  - 'contracts[{i}].awardID' is recommended for linking to awards")

    valid = len(errors) == 0
    return {"valid": valid, "errors": errors, "warnings": warnings}


def print_report(filename, result):
    """Print a formatted validation report."""
    print(f"\n{'='*60}")
    print(f"Open Contract Validator Report")
    print(f"File: {filename}")
    print(f"{'='*60}")
    if result["valid"]:
        print("✅  Status: VALID")
    else:
        print("❌  Status: INVALID")
    if result["errors"]:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(error)
    if result["warnings"]:
        print(f"\nWarnings ({len(result['warnings'])}):")
        for warning in result["warnings"]:
            print(warning)
    if not result["errors"] and not result["warnings"]:
        print("\nNo issues found.")
    print(f"{'='*60}\n")


DEMO_CONTRACT = {
    "ocid": "ocds-abc123-2024-001",
    "id": "release-2024-001",
    "date": "2024-01-15T00:00:00Z",
    "tag": ["tender"],
    "initiationType": "tender",
    "parties": [
        {"id": "GB-GOR-department-of-transport", "name": "Department of Transport", "roles": ["buyer"]},
        {"id": "GB-COH-00001234", "name": "Acme Construction Ltd", "roles": ["tenderer", "supplier"]}
    ],
    "buyer": {"id": "GB-GOR-department-of-transport", "name": "Department of Transport"},
    "tender": {
        "id": "tender-2024-001",
        "title": "Road Maintenance Contract 2024",
        "status": "active",
        "procurementMethod": "open",
        "value": {"amount": 500000, "currency": "GBP"},
        "tenderPeriod": {
            "startDate": "2024-01-15T00:00:00Z",
            "endDate": "2024-03-01T00:00:00Z"
        }
    }
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--demo":
        print("Running demo validation on a sample open contract...\n")
        result = validate_contract(DEMO_CONTRACT)
        print_report("demo_contract (inline)", result)
        return 0

    filename = sys.argv[1]
    try:
        with open(filename, "r", encoding="utf-8") as f:
            contract_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}")
        return 1

    result = validate_contract(contract_data)
    print_report(filename, result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
