from src.config import DIGIT_TO_CLASS

def parse_barcode(raw_string) -> dict:
    clean_string = raw_string.strip()

    if len(clean_string) != 11 or not clean_string.isdigit():
        raise ValueError("Invalid barcode format. Expected 11 numeric characters.")

    site = clean_string[0:2]
    department = clean_string[2:4]
    employee = clean_string[4:9]
    class_digit = clean_string[9]
    clearance_digit = clean_string[10]

    if class_digit not in DIGIT_TO_CLASS:
        raise ValueError("Incorrect class digit.")
    elif clearance_digit not in "12345":
        raise ValueError("Invalid clearance digit")
    else:
        clearance = int(clearance_digit)
        employee_class = DIGIT_TO_CLASS[class_digit]
        return {
            "site": site,
            "department": department,
            "emp_id": employee,
            "class": employee_class,
            "clearance": clearance
        }

if __name__ == "__main__":
    test_barcodes = [
        "12345678901",
        "98765432109",
        "00112233445",
        "11223344556",
        "22334455667"
    ]

    for barcode in test_barcodes:
        try:
            parsed_data = parse_barcode(barcode)
            print(f"Parsed data for barcode {barcode}: {parsed_data}")
        except ValueError as e:
            print(f"Error parsing barcode {barcode}: {e}")