from report_parser import parse_sales_report
import json

messages = [
    # 1. Tioko Holmes
    """Status: Closed
Name: [Tioko Holmes]
Email: [tioko1@ymail.com]
Payment plan: Paid 7000 will finish payment of 225 within 30 days
Amount: 7000 ( 1250, 800, 1400, 1200, 2350) 
Payment Platform: fanbasis

Please send him an agreement""",

    # 2. Barnett Glasco
    """Status: Closed
Name: [Barnett Glasco]
Email: [b.glasco25@gmail.com]
Payment plan: Payment Plan
Amount: $1,633.33 ( 5,591.67 will be paid within 30 days if not will revert into in house payment ) 
Payment Platform: Fanbasis

Please send him an agreement""",

    # 3. Cynthia Felder
    """Status: Closed
Name: [Cynthia Felder]
Email: [cynthia.felder1@gmail.com]
Payment plan: Paid in full
Amount: 7225
Payment Platform: fanbasis

Please send him an agreement""",

    # 4. Elijah Beech
    """Status: Closed
Name: Elijah Beech
Email: turnupface1018@gmail.com
Payment plan: 1960 payment Plan
Amount: $10,300
Payment Platform: stripe
@suziebongalosa Micah @M_s_Rose""",

    # 5. Jennifer prendamano
    """Status: Closed
Name: Jennifer prendamano
Email: jenalin1@yahoo.com
Payment plan: Paid in full 
12 month offer 
Amount: $9800
Payment Platform: stripe
Please send agreement 
@M_s_Rose Micah @shelmarie1126""",

    # 6. Kendra Cagle
    """Status: Closed
Name: Kendra Cagle
Email: kendra.caglee@yahoo.com
Payment plan: 1125 payment Plan
Amount: $12850
Payment Platform: stripe Klarna
@suziebongalosa Micah @M_s_Rose""",

    # 7. NaTasha Taylor
    """Status: Closed
Name: NaTasha Taylor
Email: ms.tashajt@gmail.com
Payment plan: 1960
Amount: $2000
Payment Platform: stripe Klarna
@suziebongalosa Micah @M_s_Rose""",

    # 8. Roszonia/ Russell Datts
    """Status: Closed
Name: [Roszonia/ Russell Datts]
Email: [gamerlayde@gmail.com]
Payment plan: Paid in full
Amount: 7225
Payment Platform: stripe

Please send him an agreement @shelmarie1126 Micah""",

    # 9. Donte Chaffatt
    """Status: Closed
Name: [Donte Chaffatt]
Email: [DonteChaffatt@gmail.com]
Payment plan: Paid in full 
Amount: $7,725 
Payment Platform: Payment (Darius) $7500 @Dariusbenders 
(225) Ali 

Both have confirmed the payments. Please send him an agreement Micah @shelmarie1126""",

    # 10. Ricardo Vasquez
    """Status: Closed
Name: Ricardo Vasquez
Email: vasquez.rick207@gmail.com
Payment plan: Paid in full
Amount: 7725
Payment Platform: stripe Klarna
@suziebongalosa Micah @M_s_Rose""",

    # 11. Carla McCants
    """Status: Closed
Name: [Carla McCants]
Email: [yarfay608@gmail.com]
Payment plan: Paid 
Amount: $7,000 
Payment Platform: Payment (fanbasis) 3,000+2,000
2,000 (stripe) can you confirm this one pls

Please send him an agreement. Needs to pay 225 within 30 days . Micah""",

    # 12. Oswaldo Lozano
    """Status: Closed
Name: [Oswaldo Lozano]
Email: [wallylozano2@gmail.com]
Payment plan: Paid 12 month
Amount: $10,300 
Payment Platform: Payment (Darius stripe) 10,300

Please send him an agreement  Micah @shelmarie1126""",

    # 13. Coral Jeffrey
    """Status: Closed
Name: Coral Jeffrey
Email: cij1010@gmail.com
Payment plan: custom plan
Amount: 3650 
Payment Platform: Fanbasis 
Notes: will be paying 3576 in 30 days 
Please send agreement 
Micah""",

    # 14. Ezra Ngafua
    """Status: Closed
Name: Ezra Ngafua
Email: ngafuaandpeople@gmail.com
Payment plan: Paid in full 12month offer
Amount: 9800
Payment Platform: Fanbasis Ali 
Please send agreement 
@shelmarie1126 Micah @M_s_Rose test on these messages""",

    # 15. Complex Split Payment (SHOULD FAIL)
    """Status: Closed
Name: Split Payment Test
Email: split@test.com
Payment plan: 6 PIF
Amount: 1000 paid and 500 panding
Payment Platform: Stripe"""
]

print(f"--- STARTING MEGA TEST ({len(messages)} messages) ---")
passed = 0
failed = 0

for i, msg in enumerate(messages):
    result = parse_sales_report(msg)
    name_search = [l for l in msg.split('\n') if "Name:" in l]
    name_hint = name_search[0] if name_search else f"Msg #{i+1}"
    
    if result:
        print(f"\nPASSED {name_hint}:")
        print(f"   Plan: {result['payment_plan']}")
        print(f"   Amount: {result['amount']}")
        passed += 1
    else:
        print(f"\nFAILED {name_hint}: FAILED TO PARSE")
        failed += 1

print(f"\n--- TEST COMPLETE ---")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
