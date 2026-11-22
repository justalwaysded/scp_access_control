import pytest

from src.admin import build_barcode
from src.parser import parse_barcode
from src.security import gen_salt_hash, verify_pin

test_site = "15"
test_department = "42"
test_emp_id = "04129"
test_access_class = "C"
test_clearance = 4

def test_barcode_round_trip():
    test_barcode = build_barcode(
        test_site, test_department, test_emp_id, test_access_class, test_clearance
        )
    parsed_barcode = parse_barcode(test_barcode)

    assert parsed_barcode == {
        "site": test_site,
        "department": test_department,
        "emp_id": test_emp_id,
        "class": test_access_class,
        "clearance": test_clearance
    }

def test_parser_rejects_invalid_class_digit():
    with pytest.raises(ValueError):
        parse_barcode("15420412994")
    with pytest.raises(ValueError):
        parse_barcode("15420412904")
    with pytest.raises(ValueError):
        parse_barcode("15420412964")

def test_parser_rejects_invalid_clearance_digit():
    with pytest.raises(ValueError):
        parse_barcode("15420412930")
    with pytest.raises(ValueError):
        parse_barcode("15420412939")

def test_parser_rejects_invalid_format():
    with pytest.raises(ValueError):
        parse_barcode("123")
    with pytest.raises(ValueError):
        parse_barcode("154c0412930")
    with pytest.raises(ValueError):
        parse_barcode("1542 041293")

def test_same_pin_gets_different_salted_hashed():
    first = gen_salt_hash("1234")
    second = gen_salt_hash("1234")

    assert first != second
    assert verify_pin(first, "1234") is True
    assert verify_pin(first, "0000") is False