# Data Desciption
Here's an overview of the data included here.
The data includes all months from October 2012 to now.

## cp_reports.zip
This is a zipped folder containing all of the monthly Cooperative Program report pdfs
found [here](https://www.sbc.net/missions/the-cooperative-program/reports/monthly/).

## cp_budget.csv
This budget data is parsed from the last page of each of the aformentioned pdfs.
It details the amounts allocated and designated each month to Cooperative Program ministries.

- **fy**: SBC fiscal year (fiscal years are Oct-Sep)
- **month**: month of report
- **year**: calendar year of report
- **ministry**: Cooperative Program ministry and/or budget line item
- **allocated**: budget amount allocated to the line item (USD)
- **designated**: budget amount designated to the line item (USD)

## cp_receipts.csv
This receipt data is parsed from the first pages of each of the aformentioned pdfs.
It details the gift amounts recieved from state Baptist conventions and other sources
for Cooperative Program ministries.

- **fy**: SBC fiscal year (fiscal years are Oct-Sep)
- **month**: month of report
- **year**: calendar year of report
- **source**: source of funding (usually a state Baptist convention)
- **allocated**: non-designated reciepts (USD)
- **designated**: total designated reciepts (USD)
- **lottiemoon**: Lottie Moon Christmas Offering reciepts (USD)
- **anniearmstrong**: Annie Armstrong Easter Offering reciepts (USD)
- **other_designated**: other designated reciepts (USD)
