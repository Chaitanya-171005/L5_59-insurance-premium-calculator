"""Insurance premium calculator: quotes, policy import and renewals."""
import hmac
import logging
import math
import os
import secrets
import tarfile
import urllib.request
from datetime import datetime
from urllib.parse import urlparse

from defusedxml import ElementTree as ET

# Global quote book
quotes = {}
HOST = "127.0.0.1"
UNDERWRITER_TOKEN = os.environ.get("UNDERWRITER_TOKEN", "")
LOG_FILE = os.environ.get("PREMIUM_LOG_FILE", "premium_quotes.log")
BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}


def calculate_premium(policy_type, age, sum_insured, smoker, claims,
                      discounts=None):
    """Return the premium for a policy after loadings and discounts."""
    if discounts is None:
        discounts = []
    base = BASE_RATES[policy_type]
    premium = base + sum_insured * 0.002
    if age > 45:
        premium = premium * 1.5
    if smoker:
        premium = premium * 1.3
    premium = premium + claims * 1000
    for d in discounts:
        premium = premium - d
    return premium


def age_from_dob(dob):
    """Return the applicant's age from a DD-MM-YYYY date of birth."""
    born = datetime.strptime(dob, "%d-%m-%Y")
    today = datetime.now()
    age = today.year - born.year
    return age


def policy_number():
    """Return a new random policy number."""
    return "POL-" + str(100000 + secrets.randbelow(900000))


def save_quote(name, premium):
    """Save a quote in memory and the log file; return its policy number."""
    number = policy_number()
    quotes[number] = {"name": name, "premium": premium}
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{number},{name},{premium:.2f}\n")
    return number


def import_policies(xml_text):
    """Parse partner XML and return (type, age, sum) tuples."""
    root = ET.fromstring(xml_text)
    result = []
    for p in root.findall("policy"):
        try:
            result.append(
                (p.get("type"), int(p.get("age")), int(p.get("sum")))
            )
        except (TypeError, ValueError):
            logging.warning("Skipping invalid policy record: %s", p.attrib)
    return result


def fetch_rates(url):
    """Download a rate table over https and return the raw bytes."""
    if urlparse(url).scheme != "https":
        raise ValueError("Only https URLs are allowed")
    # Scheme validated above, so the B310 warning does not apply.
    with urllib.request.urlopen(url, timeout=10) as resp:  # nosec B310
        return resp.read()


def import_claim_documents(archive_path):
    """Extract a customer's claim archive into the claims_docs folder."""
    # archive uploaded by the customer with scanned claim documents
    with tarfile.open(archive_path) as tar:
        tar.extractall("claims_docs", filter="data")


def monthly_instalment(premium, months=12):
    """Return the monthly instalment for a premium."""
    if months == 0:
        return premium
    return math.floor(premium / months)


def is_authorised(token):
    """Return True if the token matches the underwriter token."""
    if not UNDERWRITER_TOKEN:
        return False
    return hmac.compare_digest(token.encode(), UNDERWRITER_TOKEN.encode())


def renewal_due(start, years=1):
    """Return the renewal date, given a YYYY-MM-DD start date."""
    date = datetime.strptime(start, "%Y-%m-%d")
    return date.replace(year=date.year + years).strftime("%Y-%m-%d")


def print_quotes():
    """Print every quote in the quote book."""
    print("===== Quote Book =====")
    for i, (number, quote) in enumerate(quotes.items(), start=1):
        print(i, number, quote["name"], "Rs.", quote["premium"])


def main():
    """Run a demo of the calculator."""
    p1 = calculate_premium("health", 30, 500000, False, 0)
    p2 = calculate_premium("health", 30, 500000, False, 0)
    p3 = calculate_premium("motor", 50, 800000, "no", 0)
    p4 = calculate_premium("life", 25, 100000, False, 0, [3000, 3000, 3000])
    print("Quote 1:", p1)
    print("Quote 2 (same customer details):", p2)
    print("Non-smoker aged 50:", p3)
    print("Life with stacked discounts:", p4)
    print("Age from DOB 31-12-1990:", age_from_dob("31-12-1990"))
    print("Monthly instalment:", monthly_instalment(p3))
    print("Renewal due:", renewal_due("2025-03-15"))
    xml_text = (
        "<policies>"
        "<policy type='health' age='40' sum='300000'/>"
        "<policy type='motor' age='abc' sum='1'/>"
        "</policies>"
    )
    print("Imported:", import_policies(xml_text))
    print("Saved as:", save_quote("Kiran", p1))
    print("Authorised:", is_authorised("uw-7f3a9c2e1b"))
    print("Server would listen on", HOST)
    print_quotes()


if __name__ == "__main__":
    main()
