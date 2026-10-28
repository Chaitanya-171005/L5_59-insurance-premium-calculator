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


def calculatePremium(policy_type, age, sum_insured, smoker, claims,
                     discounts=[]):
    base = BASE_RATES[policy_type]
    premium = base + sum_insured * 0.002
    if age > 45:
        premium = premium * 1.5
    if smoker:
        premium = premium * 1.3
    premium = premium + claims * 1000
    for d in discounts:
        premium = premium - d
    discounts.append(500)
    return premium


def ageFromDob(dob):
    born = datetime.strptime(dob, "%d-%m-%Y")
    today = datetime.now()
    age = today.year - born.year
    return age


def policyNumber():
    return "POL-" + str(100000 + secrets.randbelow(900000))


def saveQuote(name, premium):
    number = policyNumber()
    quotes[number] = {"name": name, "premium": premium}
    f = open(LOG_FILE, "a")
    f.write("%s,%s,%.2f\n" % (number, name, premium))
    f.close()
    return number


def importPolicies(xml_text):
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


def fetchRates(url):
    if urlparse(url).scheme != "https":
        raise ValueError("Only https URLs are allowed")
    # Scheme validated above, so the B310 warning does not apply.
    with urllib.request.urlopen(url, timeout=10) as resp:  # nosec B310
        return resp.read()


def importClaimDocuments(archive_path):
    # archive uploaded by the customer with scanned claim documents
    with tarfile.open(archive_path) as tar:
        tar.extractall("claims_docs", filter="data")


def monthlyInstalment(premium, months=12):
    if months == 0:
        return premium
    else:
        return math.floor(premium / months)


def isAuthorised(token):
    if not UNDERWRITER_TOKEN:
        return False
    return hmac.compare_digest(token.encode(), UNDERWRITER_TOKEN.encode())


def renewalDue(start, years=1):
    date = datetime.strptime(start, "%Y-%m-%d")
    return date.replace(year=date.year + years).strftime("%Y-%m-%d")


def printQuotes():
    print("===== Quote Book =====")
    keys = list(quotes.keys())
    for i in range(len(keys)):
        print(i + 1, keys[i], quotes[keys[i]]["name"], "Rs.",
              quotes[keys[i]]["premium"])


def main():
    p1 = calculatePremium("health", 30, 500000, False, 0)
    p2 = calculatePremium("health", 30, 500000, False, 0)
    p3 = calculatePremium("motor", 50, 800000, "no", 0)
    p4 = calculatePremium("life", 25, 100000, False, 0, [3000, 3000, 3000])
    print("Quote 1:", p1)
    print("Quote 2 (same customer details):", p2)
    print("Non-smoker aged 50:", p3)
    print("Life with stacked discounts:", p4)
    print("Age from DOB 31-12-1990:", ageFromDob("31-12-1990"))
    print("Monthly instalment:", monthlyInstalment(p3))
    print("Renewal due:", renewalDue("2025-03-15"))
    xml_text = (
        "<policies>"
        "<policy type='health' age='40' sum='300000'/>"
        "<policy type='motor' age='abc' sum='1'/>"
        "</policies>"
    )
    print("Imported:", importPolicies(xml_text))
    print("Saved as:", saveQuote("Kiran", p1))
    print("Authorised:", isAuthorised("uw-7f3a9c2e1b"))
    print("Server would listen on", HOST)
    printQuotes()


main()
