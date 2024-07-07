from src.google_sheet_helper import GSheetHelper as SH

sheet_helper = SH()
sheet_helper.authorize()
sheet_helper.select_worksheet("streamlit-app")

df = sheet_helper.get_data()
print(df.head())
