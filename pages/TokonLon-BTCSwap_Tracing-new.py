import streamlit as st
import streamlit.components.v1 as components
import requests 
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from os import path, kill, remove
from math import nan
from csv import reader, writer
from dotenv import load_dotenv

###### Define variables
path_to_script = path.dirname(path.realpath(__file__))
UPLOADED_FOLDER = f'{path_to_script}/uploaded_files/'
LOG_FOLDER = f'{path_to_script}/logs/'

def loadAPIKeys():
    #load API key:
    dotenv_path = Path("C:\\Users\\Sylvia\.env")
    load_dotenv(dotenv_path)
    bitquerykey=os.getenv("bitquery")
    bitcoinabuseKey =os.getenv("bitcoinabuse")
    blockchainKey=os.getenv("blockchain")
    Keys={
    "bitquery_key" : bitquerykey,
    "bitcoinabuse_key" : bitcoinabuseKey,
    "blockchain_key": blockchainKey
    }
    return Keys

Keys = loadAPIKeys()
bitquery_key = Keys["bitquery_key"]
bitcoinabuse_key = Keys["bitcoinabuse_key"]

###############  Define Functions  ###############
### API function with Bitquery.io to download raw data
def bitqueryAPICall(query: str):  
    headers = {'X-API-KEY': bitquery_key}
    request = requests.post('https://graphql.bitquery.io/', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed and return code is {}.      {}'.format(request.status_code,query))

### Convert dataframe to a csv file
def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

### Open csv file and load to Dataframe
def loadfile_df(mainfolder,subfolder,filename):
    fullpath=f"{mainfolder}{subfolder}{filename}"
    file_df = pd.read_csv(fullpath)
    return file_df

#### Convert API resturned json data into dataframe
def renderPandas(q_result: str, network:str,featureLevel:dict,tx_type:str):
   ### First check if the API result return errors
    err_msg = q_result.get('errors', 'success')
    if err_msg == 'success':
    # create varaible names for the items in featureList
    # Initialize the list for each feature
        col_name=[]
        for list_item in featureLevel:
            if type(list_item) == str:
                col_name.append(f"{list_item}")
            elif type(list_item)==dict:
                for key2, dict2 in list_item.items():
                    if type(dict2)==str:
                        col_name.append(f"{key2}_{dict2}") 
                    elif type(dict2)== list:
                        for list2 in dict2:
                            if  type(list2)==str:
                                col_name.append(f"{key2}_{list2}" )
                            elif type(list2) == dict:
                                for key4, dict4 in list2.items():
                                    if type(dict4) == str:
                                        col_name.append(f"{key4}_{dict4}")
                                    elif type(dict4) == list:
                                        for list3 in dict4:
                                            if type(list3) == str:
                                                col_name.append(f"{key4}_{list3}")
                                            elif type(list3) == dict:
                                                for key5, dict5 in list3.items():
                                                    if type(dict5) == str:
                                                        col_name.append(f"{key5}_{dict5}")
                                                    elif type(dict5) == list:
                                                        for list4 in dict5:
                                                            if type(list4) == str:
                                                                col_name.append(f"{key5}_{list4}")

        mylist = {name:[] for name in col_name}
        # go through API results
        for i in q_result['data'][network][tx_type]:
            for key, value in i.items():
                if type(value) !=dict:
                    mylist[key].append(value)
                elif type(value) ==dict:
                    for key2, value2 in value.items():
                        if type(value2) !=dict:
                            append_name = f"{key}_{key2}"
                            mylist[append_name].append(value2)
                        elif type(value2) ==dict:
                            for key3, value3 in value2.items():
                                if type(value3) !=dict:
                                    append_name = f"{key2}_{key3}"
                                    mylist[append_name].append(value3)

        df = pd.DataFrame(mylist[name] for name in col_name).T#, dtype=float)
        df.columns = col_name
    else:
        df = pd.DataFrame(q_result.get('errors', 'success'))
    return df

###  get transcations using hash value
def BTC_trx_from_hash(trx_hash_var,sender:str,receiver:str):
    if sender=="sender":
        sender= f'sender: {{in: {trx_hash_var["sender_list"]}}}'
    else:
        sender =''
    if receiver=="receiver":
        receiver= f'outputAddress: {{in: {trx_hash_var["receiver_list"]}}}'
    else:
        receiver =''
    query=f'''
    {{
    bitcoin(network: {trx_hash_var["network"]}) 
    {{
        inputs(
        txHash: {{in: {trx_hash_var["inHash"]}}}
        options: {{asc: "inputIndex", limit: {trx_hash_var["limit"]}, offset:{trx_hash_var['offset']}}}
        ) {{
        inputIndex
        value
        value_usd: value(in: USD)
        address: inputAddress {{
            address
            annotation
                            }}
        outputTransaction {{
            hash
            index
                        }}
        inputScriptType {{
            annotation
            type
                 }}
        transaction {{
            hash
                    }}
        block {{
            height
            timestamp {{
                time
                    }}
                    }}
        }}

        outputs(
        txHash: {{in: {trx_hash_var["inHash"]}}}
        options: {{asc:"outputIndex" , limit: {trx_hash_var["limit"]}, offset:{trx_hash_var['offset']}}}
        {receiver}
        ) 
        {{
            outputScript
            outputIndex
            value
            value_usd: value(in: USD)
            address: outputAddress {{
                address
                annotation
            }}
            reqSigs
            transaction {{
                hash
            }}
            block {{
                height
                timestamp {{
                time
                        }}
                    }}
        }}
    }}
    }}
    '''
    return query
############# function to go to Etherum network to look up receive tx of the returned ERC20 wallet
def ETH_wallet_trx(trx_hash_var,hash:str,sender:str,receiver:str):
    if hash=='hash':
        hash=f'txHash: {{in: {trx_hash_var["inHash"]}}}'
    else:
        hash=''

    if sender=="sender":
        sender= f'sender: {{in: {trx_hash_var["sender_list"]}}}'
    else:
        sender =''
    if receiver=="receiver":
        receiver= f'receiver: {{in: {trx_hash_var["receiver_list"]}}}'
    else: 
        receiver =''
    ### old date selection method - date: {{since: {trx_hash_var["from"]}, till: {trx_hash_var["till"]}}}
    ### new date selection method - date: {{between: ["2022-09-12T22:38:19Z", "2022-09-14T22:38:19Z"]}}
    query=f'''
    {{
    ethereum(network: {trx_hash_var["network"]}) 
    {{
        transfers(
        {hash}
        options: {{limit: {trx_hash_var["limit"]}, offset:{trx_hash_var['offset']},asc: "currency.symbol"}}
        date: {{between: [{trx_hash_var["from"]}, {trx_hash_var["till"]}]}}
        amount: {{between: [{trx_hash_var["min_amt"]},{trx_hash_var["max_amt"]}]}}
        {receiver}
        ) 
        {{
              sender {{
                address
                annotation
            }}
            receiver {{
                address
                annotation
            }}
            amount
            amount_usd: amount(in: USD)
            currency {{
                symbol
                address
                tokenId
            }}
            external
            any(of: time)
            transaction {{
                hash
            }}
            }}
    }}
    }}
    '''
    return query

### Construct query variables
def construct_query_var(network,hashes,receiver,sender,fromD,tillD,min_amt,max_amt):
  hash_list = json.dumps(hashes) ## this json dump convert list to string with double quote in each item
  #receiver=swap_wallet['receiver_address'].to_list()
  receiver_list=json.dumps(receiver)
  sender_list=json.dumps(sender)
  #### date needs to be in iso8601 format: "2022-09-14T22:38:19Z"
  if fromD=='':
    fromD ="2009-01-07"
  if tillD=='':
    today= datetime.now().strftime('%Y-%m-%d')
    tillD=today
  fromDate=json.dumps(fromD)
  tillDate=json.dumps(tillD+"T23:59:59")
  query_var = {
    "network": network,
    "limit": 3000,
    "offset": 0,
    "inHash": hash_list,
    "receiver_list":receiver_list,
    "sender_list":sender_list,
    "from":fromDate,
    "till":tillDate,
    "dateFormat":"%Y-%m-%d",
    "min_amt":min_amt,
    "max_amt":max_amt
  }
  return query_var

##############################################################################
    
############# Create Streamlit page #############
st.title('TokenLon Swapped BTC to Ethereum Network Trace')

############### Now use defined functions to call trx #############
### Define swap service wallet
creator_id =''
targetSwap_wallet= st.selectbox(label='BTC Swap Service Wallet:', options=['3JMjHDTJjKPnrvS7DycPAgYcA6HrHRk8UG'])
network='bitcoin'
#network = st.selectbox(label = "Chain:", options = ['bitcoin','ethereum'])

##### Options to upload BTC trx hash  ##### 
trx_method = st.selectbox(label = 'Option to Upload BTC Transaction Hashes:', options=['Enter Manually','Upload csv file'])
    ### Option 1: enter all trx hashes, separated by comma as delimiter ########
if trx_method == 'Enter Manually': 
    st.markdown("###### Option 1: Enter all BTC trx hashes, separated by comma as delimiter")
    entered_hashes = st.text_area(label='All BTC trx hashes:')
    hashes=entered_hashes.split(",")
    #hashes=["62265289ed84706baf8022db71d016ae253ee0d8a03c5deaf05fa796e3cf5cc6","b5d128c2dd2fd294a0bdb6a480a4594a2c21c68b34de30a782391cb97c05b60f"]
    hash_list = json.dumps(hashes) ## this json dump convert list to string with double quote in each item
    st.write(f'Entered hash is:{hash_list}')

uploaded_hashfile=''
if trx_method == 'Upload csv file': 
    ##### Option 2: Upload a file contains all trx hashes ########
    st.markdown("###### Option 2: Upload a csv or text file contains all BTC trx hashes")        
    uploaded_files = st.file_uploader("Choose files to upload", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
         bytes_data = uploaded_file.read()
         # Create a new folder to store uploaded files
         record_folder = path.join(UPLOADED_FOLDER, creator_id) # Assigns upload path to variable
         record_filename = f'{creator_id}{uploaded_file.name}'
         uploaded_hashfile= uploaded_file.name
         try:
             os.makedirs(record_folder) #create the new folder if this doens't already exist
         except Exception: 
            pass
         with open(f'{record_folder}/{record_filename}',"wb") as saved_file:
             saved_file.write(bytes_data)
             st.write('File', uploaded_file.name, ' is uploaded sucessfully')

###### Click button to run codes to find results             
if st.button("Find Swapped BTC ERC-20 Receiver"):   
    if uploaded_hashfile!='':
        hash_df = loadfile_df('', UPLOADED_FOLDER, uploaded_hashfile)
        hashes = hash_df['hash'].to_list() 
        hash_list = json.dumps(hashes)  
    ### Save submited hashes to the log file
    hash_log = f'{LOG_FOLDER}/hash_log.csv'
    with open(hash_log, 'a+') as hash_log:
        csvwriter = writer(hash_log)
        csvwriter.writerow(hashes)
    
    receiver=[""]
    sender=[""]
    fromD=""
    tillD=""
    trx_hash_var = construct_query_var(network,hashes,receiver,sender,fromD,tillD,0,999999)
    
    
    ### API call to get hash details
    r_tx_hash = bitqueryAPICall(BTC_trx_from_hash(trx_hash_var,'',''))
    
    ### Convert json result into Dataframe
    network ='bitcoin'
    in_type='inputs'
    input_featureLevel =[
        'inputIndex',
        'value',
        'value_usd',
        {'address':['address','annotation']},
        {'outputTransaction':['hash','index']},
        {'inputScriptType':['annotation','type']},
        {'transaction':'hash'},
        {'block':['height',{'timestamp':'time'}]}
      ]
    tx_in_df =renderPandas(r_tx_hash,network,input_featureLevel,in_type)
    tx_in_df.rename(columns={"address_address":"input_address","address_annotation":"inputAdr_annotation"},inplace=True)
    tx_in_df.sort_values(by=['transaction_hash'], ascending=False, inplace=True)
    clean_tx_in=tx_in_df[['transaction_hash','input_address','inputAdr_annotation','value','value_usd','timestamp_time']]
    clean_tx_in.insert(loc=5,column='output_address',value='')
    clean_tx_in.insert(loc=6,column='outputAdr_annotation',value='')
    clean_tx_in.insert(loc=7,column='outputScript',value='')
    
    ### convert 'outputs' session into Dataframe
    out_type ='outputs'
    output_featureLevel =[
        'outputScript',
        'outputIndex',
        'value',
        'value_usd',
        {'address':['address','annotation']},
        'reqSigs',
        {'transaction':'hash'},
        {'block':['height',{'timestamp':'time'}]}
      ]
    tx_out_df =renderPandas(r_tx_hash,network,output_featureLevel,out_type)
    tx_out_df.rename(columns={"address_address":"output_address","address_annotation":"outputAdr_annotation"},inplace=True)
    tx_out_df.sort_values(by=['transaction_hash'], ascending=False, inplace=True)
    clean_tx_out=tx_out_df[['transaction_hash','value','value_usd','output_address','outputAdr_annotation','outputScript','timestamp_time']]
    clean_tx_out.insert(loc=1,column='input_address',value='')
    clean_tx_out.insert(loc=2,column='inputAdr_annotation',value='')
    #### Concat inputs and outputs, add the required columns 
    clean_tx=pd.concat([clean_tx_in,clean_tx_out])
    clean_tx.sort_values(by=['transaction_hash'], ascending=False, inplace=True)
    clean_tx['receiver_address']=nan
    clean_tx['BTCSwap_amt']=nan
    
    ##############################################################################
    
    #### Get the ERC20 receiver wallet if it has 'OP_RETURN' in outputscript
    for index,row in clean_tx.iterrows():
        new_value=row['outputScript'].split(' ')
        if new_value[0]=='OP_RETURN':
            return_adr=new_value[1].split('ff57425443')[0]
            output_adr='0x'+ return_adr
            clean_tx.at[index,'receiver_address']=output_adr
            f1=clean_tx['transaction_hash']==row['transaction_hash']
            f2=clean_tx['output_address']==targetSwap_wallet
            swap_amt =float(clean_tx[f1&f2]['value'])
            clean_tx.at[index,'BTCSwap_amt']=swap_amt
    
    #### Get the ERC20 receiver wallet if it has 'OP_RETURN' in outputscript
    clean_tx.sort_values(by=['transaction_hash'], ascending=False, inplace=True)
    clean_tx['receiver_address']=nan
    clean_tx['BTCSwap_amt']=nan
    for index,row in clean_tx.iterrows():
        new_value=row['outputScript'].split(' ')
        if new_value[0]=='OP_RETURN':
            return_adr=new_value[1].split('ff57425443')[0]
            output_adr='0x'+ return_adr
            clean_tx.at[index,'receiver_address']=output_adr
            f1=clean_tx['transaction_hash']==row['transaction_hash']
            f2=clean_tx['output_address']=='3JMjHDTJjKPnrvS7DycPAgYcA6HrHRk8UG'
            swap_amt =float(clean_tx[f1&f2]['value'])
            clean_tx.at[index,'BTCSwap_amt']=swap_amt
    
    ### API call to look up each returned wallet's trx using the wallet and timestamp, get the result into list
    swap_wallet=clean_tx[clean_tx["receiver_address"].isna()==False]
    wallet_tx_list=[]
    for index, row in swap_wallet.iterrows():
        receiver=row['receiver_address']
        hash=['']
        sender=['']
        fromDate=row['timestamp_time'].replace(' ','T')+'Z' ### Convert to ISO8601 datetime format
        ymd=row['timestamp_time'][0:10].split('-')
        year=ymd[0]
        month=ymd[1]
        till_day=str(int(ymd[2]) + 1 ) ### find the day and give 1 day processing for wrapped BTC processing 
        tillDate=f'{year}'+ '-' + f'{month}' + '-' + f'{till_day}' 
        max_amt=row['BTCSwap_amt']
        min_amt=max_amt-0.5
        query_var=construct_query_var("ethereum",'',receiver,'',fromDate,tillDate,min_amt,max_amt)
        hash_query = ETH_wallet_trx(query_var,'','','receiver')
        wallet_tx_list.append(bitqueryAPICall(ETH_wallet_trx(query_var,'','','receiver')))
    
    #### Convert returned ethereum wallet swapped BTC trx to dataframe
    network ='ethereum'
    tx_type ='transfers'
    featureLevel =[    
        {'sender':['address','annotation']},
        {'receiver':['address','annotation']},
        'amount',
        'amount_usd',
        {'currency':['symbol','address','tokenId']},
        'external',
        'any',
        {'transaction':'hash'}
    ]
    ########### Now get the swapped Ethereum network trx of the receiver wallets
    swapped_ETH_trx=pd.DataFrame()
    for wallet_tx in wallet_tx_list:           
        ETH_Trx =renderPandas(wallet_tx,'ethereum',featureLevel,tx_type)
        ETH_Trx.rename(columns={'any':'timestamp'},inplace=True)
        currencylist=['WBTC','imBTC']
        swapped_ETH_trx=pd.concat([swapped_ETH_trx,ETH_Trx[ETH_Trx['currency_symbol'].isin(currencylist)]])
    swapped_ETH_trx.rename(columns={'transaction_hash':'ERC_inflow_txHash'},inplace=True)
    
    #### Merge two dataframe to tie the original trx, targetSwap wallet, receiver wallet 
    swapResult = pd.merge(swap_wallet[['transaction_hash','receiver_address']],
                         swapped_ETH_trx[['receiver_annotation','sender_address','sender_annotation','receiver_address'
                         ,'currency_symbol','currency_address','timestamp','amount','amount_usd','ERC_inflow_txHash']],
                            on='receiver_address', how='outer')
    st.table(swapResult)
    
    ###### Download swapResult df onto local PC as a CSV:
    swapResult_csv = convert_df(swapResult)
    st.download_button(label='Download Results', data=swapResult_csv, mime='text/csv',)
