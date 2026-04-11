from report_parser import parse_sales_report
import json

messages = [
    """Status: Closed
Name: [Donte Chaffatt]
Email: [DonteChaffatt@gmail.com]
Payment plan: Paid in full 
Amount: $7,725 
Payment Platform: Payment (Darius) $7500 @Dariusbenders 
(225) Ali 

Both have confirmed the payments. Please send him an agreement Micah @shelmarie1126""",

    """Status: Closed
Name: Marie Jean-Philippe
Email: jeanboro.marie@gmail.com
Payment plan: Payment plan 1125 (remainder within 30 days)
Amount: $2000, $1000 (separate cc) 
Payment Platform: Fanbasis

CC: Issacar @joma1220 

Please confirm payment and send agreement Micah @shelmarie1126""",

    """Status: Closed
Name: [Carla McCants]
Email: [yarfay608@gmail.com]
Payment plan: Paid 
Amount: $7,000 
Payment Platform: Payment (fanbasis) 3,000+2,000
2,000 (stripe) can you confirm this one pls

Please send him an agreement. Needs to pay 225 within 30 days . Micah"""
]

print("--- STARTING PARSER TEST ---")
for i, msg in enumerate(messages):
    result = parse_sales_report(msg)
    print(f"\nTEST MESSAGE #{i+1}:")
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("FAILED TO PARSE")
print("\n--- TEST COMPLETE ---")
