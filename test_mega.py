from report_parser import parse_sales_report
import json

messages = [
    """Status: Closed
Name: [Tioko Holmes]
Email: [tioko1@ymail.com]
Payment plan: Paid 7000 will finish payment of 225 within 30 days
Amount: 7000 ( 1250, 800, 1400, 1200, 2350) 
Payment Platform: fanbasis""",

    """Status: Closed
Name: [Barnett Glasco]
Email: [b.glasco25@gmail.com]
Payment plan: Payment Plan
Amount: $1,633.33 ( 5,591.67 will be paid within 30 days if not will revert into in house payment ) 
Payment Platform: Fanbasis""",

    """Status: Closed
Name: [Cynthia Felder]
Email: [cynthia.felder1@gmail.com]
Payment plan: Paid in full
Amount: 7225
Payment Platform: fanbasis""",

    """Status: Closed
Name: [Roszonia/ Russell Datts]
Email: [gamerlayde@gmail.com]
Payment plan: Paid in full
Amount: 7225
Payment Platform: stripe""",

    """Status: Closed
Name: Jennifer prendamano
Email: jenalin1@yahoo.com
Payment plan: Paid in full 
12 month offer 
Amount: $9800
Payment Platform: stripe""",

    """Status: Closed
Name: Kendra Cagle
Email: kendra.caglee@yahoo.com
Payment plan: 1125 payment Plan
Amount: $12850
Payment Platform: stripe Klarna"""
]

print("--- MEGA-TEST RESULTS ---")
for i, msg in enumerate(messages):
    result = parse_sales_report(msg)
    name = result.get('name') if result else "FAILED"
    amount = result.get('amount') if result else "N/A"
    print(f"REPORT #{i+1} [{name}]: Amount Extracted: ${amount}")
    if result:
        print(f"   Mapped Plan: {result['payment_plan']} | Platform: {result['platform']}")
print("\n--- TEST COMPLETE ---")
