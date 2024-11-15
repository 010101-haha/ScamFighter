import sys
import requests
import io
import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd 
import datetime
from typing import Any, List
import csv
from pathlib import Path


## Get current directory path
current_dir =os.getcwd()
search_filePath= Path(current_dir).parent/'db'
filename=''
search_fileName= search_filePath/filename

############### Define Functions ###################
# def search_wallet(search_fileName, query):
#     results = []
#     with open(search_fileName, 'r') as file:
#         lines = file.readlines()
#         results.append(lines[0])
#         for line in lines:
#             if query.lower() in line.lower():
#                 results.append(line.strip())
#     return results
### Function to detect wallet type
import re
def detect_crypto(address):
    if address:
        # Bitcoin addresses start with 1 or 3 or bc1, and are 26-35 characters long
        if re.match('^(1|3)[a-km-zA-HJ-NP-Z1-9]{25,34}$', address) or re.match('^bc1[a-zA-HJ-NP-Za-km-z]{25,39}$', address):
            return 'BTC'

        # Ethereum addresses start with 0x and are 40-42 characters long (0x is optional - this is done by adding '?')
            ### if it is not optional, code look like this: # Ethereum addresses start with 0x and are 42 characters long
            ###elif re.match('^0x[a-fA-F0-9]{40}$', address):
        elif re.match('^(0x)?[a-fA-F0-9]{40}$', address):
            return 'ETH-USDT'

        # Litecoin addresses start with L or M, and are 26-34 characters long
        elif re.match('^(L|M)[a-km-zA-HJ-NP-Z1-9]{25,34}$', address) or re.match('^ltc1[a-zA-HJ-NP-Za-km-z]{25,39}$', address):
            return 'Litecoin'

        # TRON and USDT-TRON addresses start with T, and are 34 characters long
        elif re.match('^T[a-km-zA-HJ-NP-Z1-9]{33}$', address):
            # Assuming that we cannot differentiate between TRON and USDT on TRON
            return 'TRON_USDT-TRN'

        else:
            return 'Unknown'
    else:
        return "Unknown"

def search_wallet(search_fileName, query, column_index):
    results = []
    try:
        with open(search_fileName, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Get the header
            results.append(headers) # Add the header to results
            for row in reader:  # Now 'row' is a list of values
                if query.lower() in row[column_index].lower():
                    results.append(row)
    except Exception as e:
        #st.write("An error occured:", str(e))
        st.write("No result found.")
    return results

st.title('Search Scam Crytocurrency Wallet')

query = st.text_input('Enter the wallet address:')
if st.button('Search'):
    if  query:
        wallet_type = detect_crypto(query)
        st.write("Wallet type is: ", wallet_type)
        if wallet_type=='BTC':
            filename='BTC_wallet_summary.csv'
        elif wallet_type=='ETH-USDT':
            filename='ETH_wallet_summary.csv'
        elif wallet_type=='TRON_USDT-TRN' or wallet_type=='Litecoin':
            filename='TRON-LITE_wallet_summary.csv'
        else: 
            filename='Other_wallets.csv'
        search_fileName= search_filePath/filename
        results = search_wallet(search_fileName, query,0)
        nested_list =[results]
        if nested_list:
            for result in nested_list:
                if len(result)>1:
                    st.write(pd.DataFrame(result[1:],columns=result[0]))
        else:
            st.write('No result found.')
    else:
        st.write('Please enter a search value.')