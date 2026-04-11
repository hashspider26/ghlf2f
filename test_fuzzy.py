from sheets_service import sheets_service

def test_working_fuzzy():
    test_names = [
        "Suzet",         # Should match 'Suzette'
        "Christopher",   # Should match 'Chris Goode' (partial)
        "Jawad"          # Should match 'jawd khan'
    ]

    print("--- STARTING REAL DATA TEST ---")
    for name in test_names:
        print(f"\nSearching for: '{name}'...")
        row = sheets_service.find_row_by_name(name)
        if row:
            actual_name = sheets_service.sales_sheet.cell(row, 2).value
            print(f"MATCH FOUND! Row: {row} | Actual Name: '{actual_name}'")
        else:
            print(f"NO MATCH FOUND")

if __name__ == "__main__":
    test_working_fuzzy()
