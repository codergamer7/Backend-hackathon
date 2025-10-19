# ...existing code...
from io import BytesIO
from barcode import EAN13
from barcode.writer import ImageWriter

def GenBarcode(NHF_Number: str) -> bytes:
    """
    Generate an EAN-13 barcode PNG and return it as bytes.
    Raises ValueError if input is not 12 or 13 digits.
    """
    s = str(NHF_Number)
    digits = ''.join(ch for ch in s if ch.isdigit())

    if len(digits) not in (12, 13):
        raise ValueError("NHF_Number must contain 12 or 13 digits (digits only).")

    barcode = EAN13(digits, writer=ImageWriter())  # use instance
    buffer = BytesIO()
    barcode.write(buffer)  # writes PNG image bytes to buffer
    buffer.seek(0)
    return buffer.getvalue()

def SaveBarcodeToFile(NHF_Number: str, filename: str = "NHF_BARCODE.png"):
    """Convenience helper to save the barcode to disk with proper extension."""
    data = GenBarcode(NHF_Number)
    with open(filename, "wb") as f:
        f.write(data)