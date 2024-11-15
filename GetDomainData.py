# Import the required libraries and dependencies
import pandas as pd
import datetime
import os
import json
import requests
import hvplot.pandas
from pathlib import Path
import numpy as np
from dotenv import load_dotenv 
from IPython.display import display
import ipaddress

def validate_ip(x):
    import ipaddress
    try:
        ipaddress.ip_address(str(x))
        return True
    except Exception:
        return False
    
#### Function to extract only the domain part
def extract_domain(url):
    from urllib.parse import urlparse
    if url.startswith('http') is False:
        url = 'http://'+ url
    try:
        result = urlparse(url)
        domain_name = ''
        parent_domain=''
        if result.netloc !='':
            domain_name = result.netloc.split(':')[0]  # splits the domain and port and keeps only the domain
            if domain_name.startswith('www.'):
                domain_name = domain_name[4:]
            domain_parts = domain_name.split('.')
            if len(domain_parts) > 1:
                parent_domain = '.'.join(domain_parts[-2:])
                domain_name = '.'.join(domain_parts)
        elif result.netloc =='' and result.path !='':
            domain_name = result.path.split('.')[0]
        return domain_name, parent_domain
    except Exception as e:
        print(f"An error occurred: {e}")
        return None,None

#### API to URLSCAN for history search
def urlscan_remote_search(url):
    import json
    if '://' in url:
        url = url.split("://")[1]

    params = (
        ('q', 'domain:%s' % url),
    )
    response = requests.get('https://urlscan.io/api/v1/search/', params=params) ### if url is tradecoin.com , result URI -  https://urlscan.io/api/v1/search/?q=domain:tradcoins.com
    r_string = response.content.decode("utf-8")
    r =json.load(r_string)
    return r

### API call to iplocation.net to get IP server Geolocation: https://api.iplocation.net/?ip=13.75.54.1
def IP_geolocation(ip):
    env_path = Path(os.getcwd())
    load_dotenv(env_path)
    ipstack_apiKey= os.getenv("ipstack_api")
    #print(ipstack_apiKey)

    param1 = {
    'ip':ip
    }
    ### API data from iplocation.net
    response = requests.get('https://api.iplocation.net', params=param1)
    param2 = {
            'access_key':ipstack_apiKey
            }

    iplocation_data = response.json()
    # ### API data from ipstack.com
    try:
        ipstack_response = requests.get(f'http://api.ipstack.com/{ip}', params=param2)
        ipstack_data = ipstack_response.json()
        results=dict()
        if len(ipstack_data['data'])>0:        
                print(ipstack_data, ipstack_response.status_code)
                results=dict(ip=ipstack_data['ip'], isp=iplocation_data['isp'], 
                                latitude =ipstack_data['latitude'],longitude =ipstack_data['longitude'],
                                continent_name =ipstack_data['continent_name'],continent_code =ipstack_data['continent_code'],
                                city =ipstack_data['city'], region_name =ipstack_data['region_name'], country_name =ipstack_data['country_name']
                                        
                                )
    except Exception as e:
        results = e
    return results

##### API to Securitytrail.com to lookup history domain IP and Name Server records
def DomainLookup_ST(domain):
    env_path = Path(os.getcwd())
    load_dotenv(env_path)
    SecurityTrail_Key= os.getenv("SecurityTrail")
    headers = {
        "accept": "application/json",
        "APIKEY": SecurityTrail_Key
    }
    #### API to Securitytrail.com to look up domain history A records
    a_url = f"https://api.securitytrails.com/v1/history/{domain}/dns/a"
    a_response = requests.get(a_url, headers=headers)
    a_records = a_response.json()
    if a_response.status_code==200:
        a_df = pd.json_normalize(a_records['records'], meta=['first_seen','last_seen','organizations','type'],
                                record_path=['values'])
    else:
        a_df = pd.json_normalize(a_records)
    #### API to Securitytrail.com to look up domain history NS(Name Server) records
    ns_url = f"https://api.securitytrails.com/v1/history/{domain}/dns/ns"
    ns_response = requests.get(ns_url, headers=headers)
    ns_records = ns_response.json()
    if ns_response.status_code==200:
        ns_df = pd.json_normalize(ns_records['records'],meta=['first_seen','last_seen','organizations','type'],
                                record_path=['values'])
    else:
        ns_df = pd.json_normalize(ns_records)

    return a_df, ns_df
###### drop duplicates, abstract columns needed:
def DomainHistroy_ST_jsonDF(domain):
    history_a, history_ns = DomainLookup_ST(domain)

    a_df =pd.DataFrame()
    ns_df=pd.DataFrame()

    if 'organziations' in history_a.columns:
        a_df= history_a[['ip','organizations','type']]
        a_df=a_df.drop_duplicates().reset_index(drop=True)
        a_df.insert(0,'domain',domain)
    else:
        a_df= history_a['message']

    if 'organziations' in history_ns.columns:
        ns_df= history_ns[['nameserver','organizations','type']]
        ##### 'organizations' column is a list, Convert the lists to strings
        ##ns_df['organizations'] =ns_df['organizations'].apply(lambda x: ','.join(x))
        ns_df=ns_df.drop_duplicates().reset_index(drop=True)
        ns_df.insert(0,'domain',domain)
    else:
        ns_df =history_ns['message']
    return a_df, ns_df
############ Extract DNS from JSON data
def extract_DNS_records(last_dns_response):
    attrributes_df = pd.DataFrame()
    if last_dns_response.status_code==200:
        data = last_dns_response.json()['data']
        if type(data)==list and len(data)>1:
            attrributes = [item['attributes'] for item in data ]
            attrributes_df= pd.json_normalize(attrributes)
        else:
            attrributes_dict = data['attributes']
            selected_columns = ['last_dns_records']
            picted_dict = {column:attrributes_dict[column] for column in selected_columns if column in attrributes_dict}
            picted_dict_df = pd.json_normalize(picted_dict)
            picted_dict_df=picted_dict_df.explode('last_dns_records')
            attrributes_df = picted_dict_df['last_dns_records'].apply(pd.Series) ### .apply(pd.Series) coverts Series into Dataframe
    else:
        attrributes_df = pd.json_normalize(last_dns_response.json())
    return attrributes_df
############
def get_DNS_fromResponse(response_content):
    if len(response_content['data']) >0:
        json_df = pd.json_normalize(response_content['data'])
        json_df = json_df[['type','id','attributes.last_dns_records']]
        last_dns_records = json_df['attributes.last_dns_records'].explode().apply(pd.Series)
        json_df.reset_index(inplace=True)
        json_df.rename(columns={"index":'key', 'type':'query_type','id':'domain'},inplace=True)
        last_dns_records.drop(columns=['ttl'],inplace=True)
        last_dns_records.drop_duplicates(inplace=True)
        last_dns_records.reset_index(inplace=True)
        last_dns_records.rename(columns={"index":'key'},inplace=True)
        exploded_df = pd.merge(json_df,last_dns_records, on='key')
        exploded_df=exploded_df[['query_type', 'domain','type', 'value']]
    else:
        exploded_df = pd.json_normalize(response_content)
    return exploded_df

#### Cherry pick columns from nested dictionary
def picked_dict_columns(nested_dict, selected_columns):
    # And you want to cherry pick 'col1' and 'col3' from each dictionary:
    picked_cols = {outer_k: {inner_k: inner_v for inner_k, inner_v in outer_v.items() if inner_k in selected_columns} 
                for outer_k, outer_v in nested_dict.items()}

    return picked_cols

#### Parse CNAME and get names and then Categorize synidcate group based on domain:
def domain_categorize(url,position):
    parts = url.split('.')
    length = len(parts)
    group = ''
    if length>2:
        if 'funnull' in parts[position]:
            group = 'funnull'
        elif parts[position].isalnum() and len(parts[position]) >4: ### if it's not IP, use this part as group name
            group = parts[position]
        else:
            group =''
    return group
############ Function to API call to VirusTotal.com ############ 
def API_VirusTotal(param):
    env_path = Path(os.getcwd())
    load_dotenv(env_path)
    virustotal_Key= os.getenv("virustotal")
    ###
    headers = {
        "accept": "application/json",
        "x-apikey": virustotal_Key
    }
    response_list = []
    for key, value in param.items():
        try: 
            if key == 'domain':
                domains_url =  f"https://www.virustotal.com/api/v3/domains/{value}?limit=40"
                response = requests.get(domains_url, headers=headers)
            elif key == 'subdomain':
                subdomains_url = f"https://www.virustotal.com/api/v3/domains/{value}/subdomains?limit=10"
                response = requests.get(subdomains_url, headers=headers)
            elif key =='domain-resolutions':
                resolutions_url = f"https://www.virustotal.com/api/v3/domains/{value}/resolutions?limit=40"
                response = requests.get(resolutions_url, headers=headers)
            elif key == 'domain-communicating_files':
                communicating_files_url = f"https://www.virustotal.com/api/v3/domains/{value}/communicating_files?limit=40"
                response = requests.get(communicating_files_url, headers=headers)
            elif key =='ip_addresses-communicating_files':
                communicating_files_url =  f"https://www.virustotal.com/api/v3/ip_addresses/{value}/communicating_files?limit=40"
                response = requests.get(communicating_files_url, headers=headers)
            elif key == 'file-contacted_ips':
                contacted_ip_url = f"https://www.virustotal.com/api/v3/files/{value}/contacted_ips?limit=40"
                response = requests.get(contacted_ip_url, headers=headers)
            elif key == 'file-contacted_domains':
                contacted_domains_url = f"https://www.virustotal.com/api/v3/files/{value}/contacted_domains?limit=40"
                response = requests.get(contacted_domains_url, headers=headers)
            response_list.append(response.json())
        except Exception as e:
            response_list = []
    return response_list
############
#### json result, decode utf-8 as text then juse json.loads() function to covert it into json format
# getdata = requests.get(f"{url}")
# r_data =json.loads(getdata.content.decode("utf-8"))
# r_data_df = pd.json_normalize(r_data['page'])
# r_data_df.T#.to_csv("./test1.csv")
##################