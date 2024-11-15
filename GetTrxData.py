### Get BTC transcation data from BitQuery
import requests 
import json
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv 
from datetime import datetime, timedelta,timezone
from pathlib import Path
from math import nan
from os import path, kill, remove

#load API key:
#path_to_script = path.dirname(path.realpath(__file__))
dotenv_path = Path("C:\\Users\\Sylvia\.env")
load_dotenv(dotenv_path)
apiKey=os.getenv("bitquery")
bitcoinabuseKey =os.getenv("bitcoinabuse")
blockchainKey=os.getenv("blockchain")
etherScanKey=os.getenv("etherscan_key")

### Construct query variables
def query_variables(vars:dict, L0:list):
    #### Construct query
    query_var={
    "network":vars["network"],
    "inboundDepth":vars['in_depth'],
    "outboundDepth":vars['out_depth'],
    "limit":vars['limit'],
    "offset":vars['offset'],
    "address_list":json.dumps(L0),
    "sender_list":vars['sl_query'],
    "receiver_list":vars['rl_query'],
    "currency_list":vars['curl_query'],
    "from":vars['fromDate'],
    "till":vars['tillDate'],
    "dateFormat":"%Y-%m"
    }
    return query_var
##### API to open source blockchain.info to get BTC information
# parameters = dict(
#     rawtx = 'ac9d1831cb9b4ef0f90b27bdbe95b23d17140ae68a597a8109544065f74b23a7',
#     rawaddr= '3F6r4hXUMGdtWkmYM4eANub8sTsQZ6Npqk',
#     multiaddr = ['3F6r4hXUMGdtWkmYM4eANub8sTsQZ6Npqk','3PyGdYJ84obt3ZTbxdNB2JzX5sWaiqzAEQ'],
#     wallets_balance = ['3F6r4hXUMGdtWkmYM4eANub8sTsQZ6Npqk','3PyGdYJ84obt3ZTbxdNB2JzX5sWaiqzAEQ'],
#     unspent_outputs = ['3F6r4hXUMGdtWkmYM4eANub8sTsQZ6Npqk','3PyGdYJ84obt3ZTbxdNB2JzX5sWaiqzAEQ']
#     )

def getBlockchainRawData(parameters):
    import requests
    json_result=dict()
    try:
        if 'rawtx' in parameters.keys():
            request= requests.get(f'https://blockchain.info/rawtx/{parameters["rawtx"]}')
            #print(request.url)
            if request.status_code == 200:
                json_result['rawtx'] = request.json()
        if 'rawaddr' in parameters.keys():
            request = requests.get(f'https://blockchain.info/rawaddr/{parameters["rawaddr"]}')
            if request.status_code == 200:
                json_result['rawaddr'] = request.json()
        if 'multiaddr' in parameters.keys():
            # Use the join function to concatenate the list items into a single string, separated by '|'
            multi_addresses = "|".join(parameters['multiaddr'])
            request = requests.get(f'https://blockchain.info/multiaddr?active={multi_addresses}')
            if request.status_code == 200:
                json_result['multiaddr'] = request.json()
        if 'wallets_balance' in parameters.keys():
            multi_addresses = "|".join(parameters['wallets_balance'])
            request = requests.get(f'https://blockchain.info/balance?active={multi_addresses}')
            if request.status_code == 200:
                json_result['wallets_balance'] = request.json()
        if 'unspent_outputs' in parameters.keys():
            multi_addresses = "|".join(parameters['wallets_balance'])
            request = requests.get(f'https://blockchain.info/unspent?active={multi_addresses}')
            if request.status_code == 200:
                json_result['unspent_outputs'] = request.json()
    except Exception:
        raise Exception('Query failed and return code is {}.'.format(request.status_code))
    return json_result
######## define API functions with bitcoinabuse.com
def bitcoinabuseAPI(address:str):
    parm = {'api_token': bitcoinabuseKey,
            'address':address}
   
    request = requests.get('https://www.bitcoinabuse.com/api/reports/check?', params=parm)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed and return code is {}. {}'.format(request.status_code,address))

def BTC_Wallets_Abuse(Wal_list:list):
   abuse_result=[]
   col_name=['address', 'count', 'first_seen', 'last_seen', 'recent']
   for wallet in Wal_list:
      abuse_result.append(list(bitcoinabuseAPI(wallet).values()))

   abuse_df=pd.DataFrame(abuse_result,columns=col_name)
   return abuse_df
### API function with Bitquery.io to download raw data
def bitqueryAPICall(query: str):  
    headers = {'X-API-KEY': apiKey}
    request = requests.post('https://graphql.bitquery.io/', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed and return code is {}.      {}'.format(request.status_code,query))
    
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

#### Construct varaible dictionary 
import datetime
def query_variables(network,address_list,fromDate,tillDate,sl_query,rl_query,curl_query,in_depth,out_depth,limit):
    variable_dict = dict(
        L0_query=address_list,
        network=network,
        in_depth=(0 if in_depth=='' else in_depth),
        out_depth=(10 if out_depth=='' else out_depth),
        limit=(30 if limit=='' else limit),
        offset=0,
        fromDate=json.dumps("2010-01-01" if fromDate=='' else fromDate),
        tillDate=json.dumps(f"{datetime.date.today().strftime('%Y-%m-%d')}T23:59:59" if tillDate=='' else tillDate),
        ### use values from variables defined above
        address_list=address_list,
        sender_list=sl_query,
        receiver_list=rl_query,
        currency_list=curl_query,
        dateFormat="%Y-%m",
        ##### variables for converting JSON to dataframe:
        #BTC_price=21901.50,
        in_type ='inbound',
        out_type ='outbound',
        featureLevel =[{
            'sender':['address','annotation'],
            'receiver':['address','annotation'],
            'currency':['address','symbol']
            },
            'amount',
            'depth',
            'count'],
        #savefile_path= PathString
    )
    return variable_dict

 #### Construct API query to download wallet balance    
def API_queryBTC_WalletSummary(summary_var):
  query_sum=f'''
  {{
    bitcoin(network: {summary_var["network"]}) {{
      inputs(date: {{since: {summary_var["fromDate"]}, till: {summary_var["tillDate"]}}}, 
      inputAddress: {{in: {summary_var['address_list']}}}) 
      {{
        count
        value
        value_usd:value(in:USD)
        min_date: minimum(of: date)
        max_date: maximum(of: date)
        inputAddress {{
          address
          annotation
        }}
      }}
      outputs(date: {{since: {summary_var["fromDate"]}, till: {summary_var["tillDate"]}}}, 
      outputAddress: {{in: {summary_var['address_list']}}}) 
      {{
        count
        value
        value_usd:value(in:USD)
        min_date: minimum(of: date)
        max_date: maximum(of: date)
        outputAddress {{
          address
          annotation
        }}
      }}
    }}
  }}
  '''
  return query_sum
##### Construct API query to bitquery to fetch BTC wallet summary
def API_queryETH_WalletSummary(summary_var):
  query_sum=f'''
  {{
    ethereum(network: {summary_var["network"]}) 
    {{
      transfers(     
        date: {{since: {summary_var["fromDate"]} , till:{summary_var["tillDate"]} }}
        amount: {{gt:0}}
        any:[{{receiver: {{in: {summary_var['address_list']}}}}}, {{sender: {{in: {summary_var['address_list']}}}}} ]
       options: {{desc: ["count_in", "count_out"], asc: "currency.symbol"}}  ) 
        {{
              sum_in: amount(calculate: sum, receiver: {{in: {summary_var['address_list']}}})
              sum_in_usd: amount(in: USD, calculate: sum, receiver: {{in: {summary_var['address_list']}}})
              sum_out: amount(calculate: sum, receiver: {{in: {summary_var['address_list']}}})
              sum_out_usd: amount(in: USD, calculate: sum, receiver: {{in: {summary_var['address_list']}}})
              count_in: count(receiver: {{in: {summary_var['address_list']}}})
              count_out: count(sender: {{in: {summary_var['address_list']}}})
              currency {{
                address
                symbol
                tokenType  }}
             }}
      addressStats(address: {{in: {summary_var['address_list']}}}) {{
          address {{
            address {{
              address
              annotation
            }}
            firstTxAt {{
              time
            }}
            lastTxAt {{
              time
            }}
            receiveFromCurrencies
            sendToCurrencies
          }}
        }}
      }}
  }}         
  '''
  return query_sum

def getETH_walletSummary(df, start_position,batch_size):
##########Get ETH wallet summary#
  network='ethereum'
  fromDate=''
  tillDate=''
  L0 = df[(df['CrytoType'] =='ETH-USDT') & (df['Receive'].isna())]['Address_L0'].unique().tolist()
  ########### API call bitquery in batches####################
  L0_chunks = [L0[i:i+batch_size] for i in range(start_position, len(L0)-613, batch_size)]
  ## Loop through each chunk and make bitquery API calls
  ETH_json_summary = pd.DataFrame()
  for chunk in L0_chunks:
      summary_df = readETH_walletSummary(chunk,network,fromDate,tillDate)
      ETH_json_summary=ETH_json_summary.append(summary_df)
  ### All json results are now appended into BTC_json_summary
  return ETH_json_summary

### Function to get ETH wallet balance one by one
def readETH_walletSummary(L0:list, network,fromDate,tillDate):
    ETH_walletSummary = pd.DataFrame()
    for i in L0:
        L0_query=json.dumps(i)
        API_query=API_queryETH_WalletSummary(query_variables(network,L0_query,fromDate,tillDate,'','','','','','')) 
        WalletSummry = bitqueryAPICall(API_query)
        # Flatten the 'transfers' data and convert it to a DataFrame
        transfers_data = WalletSummry['data'][network]['transfers']
        df_transfers = pd.json_normalize(transfers_data)
        # Flatten the 'addressStats' data and convert it to a DataFrame
        address_data = WalletSummry['data'][network]['addressStats']
        df_address = pd.json_normalize(address_data)
        # Join 'transfers' and 'addressStats' data
        df = df_transfers.join(df_address, how='outer')
        # Append the new data into the existing dataframe
        ETH_walletSummary=ETH_walletSummary.append(df, ignore_index=True)
    #### Rename columns
    ETH_walletSummary = ETH_walletSummary.rename(columns={
        'currency.address':'currency_address',
        'currency.symbol':'symbol',
        'currency.tokenType':'tokenType',
        'address.address.address': 'address',
        'address.address.annotation': 'annotation',
        'address.firstTxAt.time': 'first_transaction_time',
        'address.lastTxAt.time': 'last_transaction_time',
        'address.receiveFromCurrencies': 'receive_from_currencies',
        'address.sendToCurrencies': 'send_to_currencies'
    })
    ETH_walletSummary[['address','annotation','first_transaction_time','last_transaction_time',
                       'receive_from_currencies','send_to_currencies']]=ETH_walletSummary[['address','annotation','first_transaction_time','last_transaction_time',
                                                                                           'receive_from_currencies','send_to_currencies']].fillna(method='ffill')
    return ETH_walletSummary

#### Convert returned wallet balance JSON data to Dataframe
def read_BTCWalletBalance(summary):
    network = "bitcoin"
    in_type="inputs"
    out_type ="outputs"
    featureLevel =[
                "count",
                "value",
                "value_usd",
                "min_date",
                "max_date",
                {"inputAddress":["address","annotation"]},
                {"outputAddress":["address","annotation"]}
            ]
    summary_in = renderPandas(summary,network,featureLevel,in_type)
    summary_out = renderPandas(summary,network,featureLevel,out_type)
    summary_in.rename(columns={'inputAddress_address':'address', 
                                'inputAddress_annotation':'annotation',
                                'min_date':'First_Spend_Date',
                                'max_date':'Last_Spend_Date',
                                'value':'Spend','value_usd':'Spend_USD','count':'SpendTx_count'}, inplace=True)
    summary_out.rename(columns={'outputAddress_address':'address', 
                                'outputAddress_annotation':'annotation',
                                'min_date':'First_Receive_Date',
                                'max_date':'Last_Receive_Date',
                                'value':'Receive','value_usd':'Receive_USD','count':'ReceiveTx_count'}, inplace=True)
    summary_df = pd.concat([summary_in,summary_out])
    adr_summary = pd.merge(summary_out[['address','Receive','First_Receive_Date','Last_Receive_Date','Receive_USD','ReceiveTx_count']],
                            summary_in[['address','Spend','First_Spend_Date','Last_Spend_Date','Spend_USD','SpendTx_count']], on='address', how='outer')
    adr_summary=adr_summary.fillna(0)
    adr_summary['Balance'] =adr_summary['Receive'].astype(float) - adr_summary['Spend'].astype(float)
    adr_summary['Balance_USD'] =adr_summary['Receive_USD'].astype(float) - adr_summary['Spend_USD'].astype(float)
    return adr_summary
# def read_BTCWalletBalance(summary):
#     network = "bitcoin"
#     in_type="inputs"
#     out_type ="outputs"
#     featureLevel =[
#                 "count",
#                 "value",
#                 "value_usd",
#                 "min_date",
#                 "max_date",
#                 {"inputAddress":["address","annotation"]},
#                 {"outputAddress":["address","annotation"]}
#             ]
#     summary_in = renderPandas(summary,network,featureLevel,in_type)
#     summary_out = renderPandas(summary,network,featureLevel,out_type)
#     summary_in.rename(columns={'inputAddress_address':'address', 
#                                 'inputAddress_annotation':'annotation',
#                                 'min_date':'First_Spend_Date',
#                                 'max_date':'Last_Spend_Date',
#                                 'value':'Spend','value_usd':'Spend_USD','count':'SpendTx_count'}, inplace=True)
#     summary_out.rename(columns={'outputAddress_address':'address', 
#                                 'outputAddress_annotation':'annotation',
#                                 'min_date':'First_Receive_Date',
#                                 'max_date':'Last_Receive_Date',
#                                 'value':'Receive','value_usd':'Receive_USD','count':'ReceiveTx_count'}, inplace=True)
#     summary_df = pd.concat([summary_in,summary_out])
#     adr_summary = pd.merge(summary_out[['address','Receive','First_Receive_Date','Last_Receive_Date','Receive_USD','ReceiveTx_count']],
#                             summary_in[['address','Spend','First_Spend_Date','Last_Spend_Date','Spend_USD','SpendTx_count']], on='address', how='outer')
#     adr_summary=adr_summary.fillna(0)
#     adr_summary['Balance'] =adr_summary['Receive'].astype(float) - adr_summary['Spend'].astype(float)
#     adr_summary['Balance_USD'] =adr_summary['Receive_USD'].astype(float) - adr_summary['Spend_USD'].astype(float)
#     return adr_summary

def coin_path(path_var, sender:str,receiver:str):
  if sender=="sender":
    sender= f'sender: {{in: {path_var["sender_list"]}}}'
  else:
    sender =''
  if receiver=="receiver":
    receiver= f'receiver: {{in: {path_var["receiver_list"]}}}'
  else:
    receiver =''
  coin_path=f'''
  {{
    bitcoin(network: {path_var["network"]}) 
    {{
      inbound: coinpath(
        initialAddress: {{in: {path_var["address_list"]}}}
        depth: {{lteq:{path_var["inboundDepth"]}}}
        options: {{direction: inbound, asc: "depth", desc: "amount",limitBy: {{each: "depth", limit: {path_var["limit"]},offset:{path_var["offset"]}}}}}
        date: {{since: "{path_var["from"]}", till: "{path_var["till"]}"}}
        {sender}
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
        currency {{
            address
            symbol
          }}
        depth
        count
      }}
      outbound: coinpath(
        initialAddress: {{in: {path_var["address_list"]}}}
        depth: {{lteq: {path_var["outboundDepth"]}}}
        options: {{asc: "depth", desc: "amount", limitBy: {{each: "depth", limit: {path_var["limit"]},offset:{path_var["offset"]}}}}}
        date: {{since: "{path_var["from"]}", till: "{path_var["till"]}"}}
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
        currency {{
            address
            symbol
          }}
        depth
        count
      }}
    }}
  }} 
  '''
  return coin_path
    

