# SBC Cooperative Program Giving Analysis

Check out the report: https://gradylynn.com/sbc-cooperative-program-giving/

## Introduction
This is a small personal data analysis project focussed on national giving towards
the [Cooperative Program](https://www.sbc.net/missions/the-cooperative-program/) (CP)
of the [Southern Baptist Convention](https://www.sbc.net) (SBC).

## Data Scraping & Parsing
The python script (`sbc_cp_parser.py`) is used for scraping and parsing the CP's
[monthly reports](https://www.sbc.net/missions/the-cooperative-program/reports/monthly/).
The code below is a model for downloading all of the CP report pdfs and parsing out all
of the receipts and budget data into csvs. Note that the resultant data is included with
this repository. A data description is provided in the `data` directory.
```python
from sbc_cp_parser import download_reports, reports_to_csv

reports_filepath = '/Users/gradylynn/Desktop/cp_reports.zip'
csvs_filepath = '/Users/gradylynn/Desktop/'

download_reports(reports_filepath) # download all report pdfs to zip folder

reports_to_csv(reports_filepath, csvs_filepath) # parse downloaded reports and write out csvs
```

The python library [tabula](https://pypi.org/project/tabula-py/) is used to parse
the data from the report pdfs.
