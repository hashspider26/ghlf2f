
from report_parser import parse_sales_report
import json

test_cases = [
    {
        "name": "Ambiguous Message (Should FAIL/Alert)",
        "text": """Status: Closed
Name: Tayvonn Kyle
Email: tayvonnkyle@gmail.com
Payment plan: $2500 paid today, balance applied via Flexxbuy
Amount: $2500
Payment Platform: Fanbasis
Notes: Opted for 6 months mentorship"""
    },
    {
        "name": "Clear 6 Month Plan (Should PASS)",
        "text": """Status: Closed
Name: John Doe
Email: john@test.com
Payment plan: 6 month plan
Amount: 1960
Payment Platform: Stripe"""
    },
    {
        "name": "Magic Number PIF (Should PASS)",
        "text": """Status: Closed
Name: Jane Smith
Email: jane@test.com
Payment plan: Paid In Full
Amount: 7225
Payment Platform: Stripe"""
    }
]

print("--- Running Strictness Test ---")
for case in test_cases:
    print(f"\nTesting: {case['name']}")
    result = parse_sales_report(case['text'])
    if result:
        print(f"✅ Result: {result['payment_plan']}")
    else:
        print(f"❌ Result: None (Triggering VA Alert)")

