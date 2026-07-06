from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()


class ExtractRequest(BaseModel):
    text: str


class Invoice(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=Invoice)
async def extract(req: ExtractRequest):
    try:
        text = req.text.strip()

        if not text:
            return Invoice(
                vendor="",
                amount=0.0,
                currency="",
                date=""
            )

        # -------------------------
        # DATE
        # -------------------------
        date = ""
        m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
        if m:
            date = m.group(1)

        # -------------------------
        # CURRENCY
        # -------------------------
        currency = ""
        m = re.search(r"\b(USD|EUR|GBP|INR|AUD|CAD|JPY|CHF)\b", text, re.I)
        if m:
            currency = m.group(1).upper()

        # -------------------------
        # AMOUNT
        # -------------------------
        amount = 0.0

        patterns = [
            r"(?:TOTAL\s+DUE|TOTAL|AMOUNT\s+DUE|AMOUNT|BALANCE)\D*([0-9]+(?:\.[0-9]{1,2})?)",
            r"(?:USD|EUR|GBP|INR|AUD|CAD|JPY|CHF)\s*([0-9]+(?:\.[0-9]{1,2})?)",
            r"[$€£]\s*([0-9]+(?:\.[0-9]{1,2})?)",
        ]

        for p in patterns:
            m = re.search(p, text, re.I)
            if m:
                amount = float(m.group(1))
                break

        # -------------------------
        # VENDOR
        # -------------------------

        vendor = ""

        vendor_patterns = [
            r"Vendor[:\s]+(.+)",
            r"Supplier[:\s]+(.+)",
            r"From[:\s]+(.+)",
            r"Bill From[:\s]+(.+)",
            r"Invoice From[:\s]+(.+)",
        ]

        for pat in vendor_patterns:
            m = re.search(pat, text, re.I)
            if m:
                vendor = m.group(1).split("\n")[0].strip()
                break

        if not vendor:
            m = re.search(
                r"([A-Za-z0-9&.,' -]*(?:Ltd|LLC|Inc|Corporation|Industries|Company|Co\.?))",
                text,
                re.I,
            )
            if m:
                vendor = m.group(1).strip()

        return Invoice(
            vendor=vendor,
            amount=amount,
            currency=currency,
            date=date,
        )

    except Exception:
        return Invoice(
            vendor="",
            amount=0.0,
            currency="",
            date=""
        )
