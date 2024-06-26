#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tabula # parsing pdfs into dataframes
from bs4 import BeautifulSoup # parsing pdf links from website
import pandas as pd
import re
import requests
import os
import zipfile
from datetime import datetime


# writes pdf reports to a zipfile at the specified path
def download_reports(filepath):
    # get the html from the cooperative program report webpage
    url = 'https://www.sbc.net/missions/the-cooperative-program/reports/monthly/'
    headers = {'User-Agent': 'github.com/gradylynn/sbc-cooperative-program-giving'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    # get the links to all the report pdfs from the html
    pdf_links = {}
    for ultag in soup.find_all(href=True):
        link = ultag['href']
        if link.endswith('Contribution-Reports.pdf'):
            pdf_links[link.split('/')[-1]] = link

    # write pdfs to specified zip directory
    with zipfile.ZipFile(filepath, 'w') as zip_object:
        for name in pdf_links:
            r = requests.get(pdf_links[name], headers=headers)
            zip_info = zipfile.ZipInfo(name, date_time=datetime.now().timetuple())
            zip_object.writestr(zip_info, data=r.content)


# simple cleaning function for numbers parsed below
number_cleaner = lambda x: float(re.sub('^\((.*)\)$', r'-\1', str(x).split()[0]).replace(',','').replace('$',''))


# parses cp receipts from report at input filepath
# outputs results in a pandas DataFrame
def parse_cp_receipts(filepath):
    # use tabula to parse the pdf
    dfs = tabula.read_pdf(filepath, pages='1-4', silent=True)

    # weird tabula correction thing
    if len(dfs) > 4:
        dfs[1] = dfs[1].append(pd.Series(dfs[1].columns, index=dfs[1].columns), ignore_index=True)
        dfs[1].columns = dfs[0].columns
        dfs[0] = dfs[0].append(dfs[1]).reset_index(drop=True)
        dfs = dfs[:1] + dfs[2:]

    # Allocation Budget Receipts
    df1 = dfs[0].drop(index=[0,1]) # drop annoying header things
    df1 = df1.drop(columns=df1.columns[2:]) # drop everything but current
    df1.columns = ['source', 'allocated'] # rename columns
    df1['source'] = df1['source'].apply(lambda x: re.sub('\**$', '', x)) # remove stars at end of source names
    df1 = df1.set_index('source') # set source as index
    df1['allocated'] = list(map(number_cleaner, list(df1['allocated']))) # convert to floats
    df1 = df1.drop(index=['Subtotal', 'Grand Total:'], errors='ignore') # drop aggregation rows

    if 'Churches' in df1.index: # fix old row names
        df1.at['Churches & Individuals', 'allocated'] = df1['allocated']['Churches']+df1['allocated']['Individuals & Estates']
        df1 = df1.drop(index=['Churches', 'Individuals & Estates']) # drop old row names

    # Designated Budget Receipts
    df2 = dfs[1].drop(index=[0,1]) # drop annoying header things
    df2 = df2.drop(columns=df2.columns[2:]) # drop everything but current
    df2.columns = ['source', 'designated'] # rename columns
    df2['source'] = df2['source'].apply(lambda x: re.sub('\**$', '', x)) # remove stars at end of source names
    df2 = df2.set_index('source') # set source as index
    df2['designated'] = list(map(number_cleaner, list(df2['designated']))) # convert to floats
    df2 = df2.drop(index=['Subtotal', 'Grand Total:'], errors='ignore') # drop aggregation rows

    if 'Churches' in df2.index: # fix old row names
        df2.at['Churches & Individuals', 'designated'] = df2['designated']['Churches']+df2['designated']['Individuals & Estates']
        df2 = df2.drop(index=['Churches', 'Individuals & Estates']) # drop old row names

    # Specific Designated Budget Receipts (fiscal year-to-date)
    df3 = dfs[3].drop(index=[0]).dropna(axis=1) # drop annoying header things
    df3.columns = ['source', 'lottiemoon_fytd', 'anniearmstrong_fytd', 'other_fytd'] # rename columns
    df3['source'] = df3['source'].apply(lambda x: re.sub('\**$', '', x)) # remove stars at end of source names
    df3 = df3.set_index('source') # set source as index

    df3['lottiemoon_fytd'] = list(map(number_cleaner, list(df3['lottiemoon_fytd'])))
    df3['anniearmstrong_fytd'] = list(map(number_cleaner, list(df3['anniearmstrong_fytd'])))
    df3['other_fytd'] = list(map(number_cleaner, list(df3['other_fytd'])))

    df3 = df3.drop(index=['Subtotal', 'Grand Total:']) # drop aggregation rows

    if 'Churches' in df3.index: # fix old row names
        df3.at['Churches & Individuals', 'lottiemoon_fytd'] = df3['lottiemoon_fytd']['Churches']+df3['lottiemoon_fytd']['Individuals & Estates']
        df3.at['Churches & Individuals', 'anniearmstrong_fytd'] = df3['anniearmstrong_fytd']['Churches']+df3['anniearmstrong_fytd']['Individuals & Estates']
        df3.at['Churches & Individuals', 'other_fytd'] = df3['other_fytd']['Churches']+df3['other_fytd']['Individuals & Estates']
        df3 = df3.drop(index=['Churches', 'Individuals & Estates'], errors='ignore') # drop old row names

    return df1.merge(df2, how='outer', on='source').merge(df3, how='outer', on='source')


# parses cp budget from report at input filepath
# outputs results in a pandas DataFrame
def parse_cp_budget(filepath):
    # use tabula to parse the pdf
    dfs = tabula.read_pdf(filepath, pages=5, silent=True)

    df = dfs[0].drop(index=[0, 1]) # drop annoying header things
    df = df.drop(columns=df.columns[3:]) # drop everything but current allocated
    df.columns = ['ministry', 'allocated', 'designated'] # rename columns
    df = df.reset_index(drop=True).dropna() # reset index

    df['allocated'] = list(map(number_cleaner, list(df['allocated'])))
    df['designated'] = list(map(number_cleaner, list(df['designated'])))

    name_cleaner = lambda x: re.sub('\*$', '', x)
    df['ministry'] = list(map(name_cleaner, list(df['ministry'])))

    # drop aggregation rows
    return df[['Total' not in m for m in df['ministry']]].reset_index(drop=True)


def reports_to_csv(reports_path, csv_path):
    # functions for parsing time info from filenames
    get_month = lambda f: f.split('-')[1][:3]
    get_fy = lambda f: f.split('-')[2] + '-' + f.split('-')[3]
    get_year = lambda f: int(f.split('-')[2]) if get_month(f) in ('Oct', 'Nov', 'Dec') else int(f.split('-')[3])

    receipts_dfs = []
    budget_dfs = []

    with zipfile.ZipFile(reports_path, 'r') as zip_object:
        for name in zip_object.namelist():
            print('Parsing data from:', name)

            # parse cp receipts
            try:
                receipts_df = parse_cp_receipts(zip_object.open(name))
                receipts_df['fy'] = get_fy(name)
                receipts_df['month'] = get_month(name)
                receipts_df['year'] = get_year(name)
                receipts_dfs.append(receipts_df)
            except Exception as error:
                print('receipt parse error!')
                print(error)

            # parse cp budget
            try:
                budget_df = parse_cp_budget(zip_object.open(name))
                budget_df['fy'] = get_fy(name)
                budget_df['month'] = get_month(name)
                budget_df['year'] = get_year(name)
                budget_dfs.append(budget_df)
            except Exception as error:
                print('budget parse error!')
                print(error)

    receipts_df = pd.concat(receipts_dfs).reset_index()
    budget_df = pd.concat(budget_dfs)

    # Unwrapping the ytd designations into monthly amounts
    receipts_df['fy_mo'] = receipts_df['month'].apply(lambda m: (int(datetime.strptime(m, '%b').strftime("%m"))-10)%12+1)
    receipts_df = receipts_df.sort_values(['fy', 'fy_mo']).reset_index(drop=True)
    receipts_df['lottiemoon'] = receipts_df['lottiemoon_fytd'] - receipts_df.groupby('source')['lottiemoon_fytd'].shift().fillna(0)*(receipts_df['fy_mo']!=1)
    receipts_df['anniearmstrong'] = receipts_df['anniearmstrong_fytd'] - receipts_df.groupby('source')['anniearmstrong_fytd'].shift().fillna(0)*(receipts_df['fy_mo']!=1)
    receipts_df['other_designated'] = receipts_df['other_fytd'] - receipts_df.groupby('source')['other_fytd'].shift().fillna(0)*(receipts_df['fy_mo']!=1)

    receipts_df['lottiemoon'] = receipts_df['lottiemoon'].round(2)
    receipts_df['anniearmstrong'] = receipts_df['anniearmstrong'].round(2)
    receipts_df['other_designated'] = receipts_df['other_designated'].round(2)

    # Writing csvs
    receipts_df = receipts_df[['fy', 'month', 'year', 'source', 'allocated', 'designated', 'lottiemoon', 'anniearmstrong', 'other_designated']]
    receipts_df.to_csv(os.path.join(csv_path, 'cp_receipts.csv'), index=False)

    budget_df = budget_df[['fy', 'month', 'year', 'ministry', 'allocated', 'designated']]
    budget_df.to_csv(os.path.join(csv_path, 'cp_budget.csv'), index=False)

# main function to update data.
if __name__ == '__main__':
    datapath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    reports_filepath = os.path.join(datapath, 'cp_reports.zip')

    print('downloading reports...')
    download_reports(reports_filepath)

    print('reports downloaded. parsing reports...')
    reports_to_csv(reports_filepath, datapath)

    print('reports parsed. csvs written. updating rmarkdown html...')
    command = ''' R -e "rmarkdown::render('index.Rmd', output_file='index.html')" '''
    os.system(command)

    print('Done!')
