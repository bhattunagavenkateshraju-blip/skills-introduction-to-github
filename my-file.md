# Open Contract Validator

A Python tool for validating open contracts against the [Open Contracting Data Standard (OCDS)](https://standard.open-contracting.org/).

## Features

- Validates required OCDS fields (ocid, id, date, tag, parties, tender, etc.)
- Checks date formats (ISO 8601)
- Validates party roles, tender status, and procurement methods
- Validates award and contract objects
- Reports errors and warnings with clear messages

## Usage

```bash
# Validate a contract file
python contract_validator.py sample_contracts/valid_contract.json

# Run the built-in demo
python contract_validator.py --demo
```

## Run Tests

```bash
python -m pytest test_contract_validator.py -v
```

## Sample Contracts

- `sample_contracts/valid_contract.json` — a valid OCDS tender release
- `sample_contracts/invalid_contract.json` — a contract with intentional errors to demonstrate validation output
