#!/usr/bin/env python3
import argparse
import sys, os
import errno, pathlib, re
import datetime, time
import json, requests, urllib.request
from dotenv import load_dotenv 

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
    ipstack_response = requests.get(f'http://api.ipstack.com/{ip}', params=param2)
    ipstack_data = ipstack_response.json()
    results=dict(ip=ipstack_data['ip'], isp=iplocation_data['isp'], 
                 latitude =ipstack_data['latitude'],longitude =ipstack_data['longitude'],
                 continent_name =ipstack_data['continent_name'],continent_code =ipstack_data['continent_code'],
                 city =ipstack_data['city'], region_name =ipstack_data['region_name'], country_name =ipstack_data['country_name']
                          
                 )
    return results

def remote_search(url):
    if '://' in url:
        url = url.split("://")[1]

    params = (
        ('q', 'domain:%s' % url),
    )
    response = requests.get('https://urlscan.io/api/v1/search/', params=params) ### if url is tradecoin.com , result URI -  https://urlscan.io/api/v1/search/?q=domain:tradcoins.com
    r = response.content.decode("utf-8")
   # print(r)
    return r


def search(search_urls, remote_true):
    search_urls
    connect_db()

    if isinstance(search_urls, str):
        staging_list = []
        staging_list += [search_urls]
        search_urls = staging_list

    for url in search_urls:
        if remote_true:
            remote_search(url)
        else:
            if url == "all":
                try:
                    c.execute('SELECT * FROM scanned_urls')
                except sqlite3.OperationalError:
                    print("No scan history in database.")
                    sys.exit(5)
                for line in c.fetchall():
                    if line[0-2]:
                        scan_url = line[0]
                        scan_uuid = line[1]
                        scan_date = line[2]
                        print(scan_date + ' || ' + scan_url  + ': ' + scan_uuid)
            else:
                t = (url,)
                try:
                    c.execute("SELECT * FROM scanned_urls WHERE url LIKE ?", ['%'+url+'%'])
                except sqlite3.OperationalError:
                    print("No scan history in database.")
                    sys.exit(5)

                for line in c.fetchall():
                    if line[0-2]:
                        scan_url = line[0]
                        scan_uuid = line[1]
                        scan_date = line[2]
                        print(scan_date + ' || ' + scan_url  + ': ' + scan_uuid)

def download_dom(target_uuid, target_dir, save_template):
    dom_url = 'https://urlscan.io/dom/' + target_uuid + '/'
    try:
        os.makedirs(target_dir)
    except FileExistsError:
        pass
    target_dom = save_template + '.dom'
    try:
        urllib.request.urlretrieve(dom_url, str(target_dom))
    except FileExistsError:
        pass


def download_png(target_uuid, target_dir, save_template):
    png_url = 'https://urlscan.io/screenshots/' + target_uuid + '.png'
    try:
        os.makedirs(target_dir)
    except FileExistsError:
        pass
    target_png = save_template + '.png'
    try:
        urllib.request.urlretrieve(png_url, str(target_png))
    except FileExistsError:
        pass

def print_summary(content):
    ### relevant aggregate data
    request_info = content.get("data").get("requests")
    meta_info = content.get("meta")
    verdict_info = content.get("verdicts")
    list_info = content.get("lists")
    stats_info = content.get("stats")
    page_info = content.get("page")

    ### more specific data
    geoip_info = meta_info.get("processors").get("geoip")
    web_apps_info = meta_info.get("processors").get("wappa")
    resource_info = stats_info.get("resourceStats")
    protocol_info = stats_info.get("protocolStats")
    ip_info = stats_info.get("ipStats")

    ### enumerate countries
    countries = []
    for item in resource_info:
        country_list = item.get("countries")
        for country in country_list:
            if country not in countries:
                countries.append(country)

    ### enumerate web apps
    web_apps = []
    for app in web_apps_info.get("data"):
        web_apps.append(app.get("app"))

    ### enumerate domains pointing to ip
    pointed_domains = []
    for ip in ip_info:
        domain_list = ip.get("domains")
        for domain in domain_list:
            if domain not in pointed_domains:
                pointed_domains.append(domain)


    ### data for summary
    page_domain = page_info.get("domain")
    page_ip = page_info.get("ip")
    page_country = page_info.get("country")
    page_server = page_info.get("server")
    ads_blocked = stats_info.get("adBlocked")
    https_percentage = stats_info.get("securePercentage")
    ipv6_percentage = stats_info.get("IPv6Percentage")
    country_count = stats_info.get("uniqCountries")
    num_requests = len(request_info)
    is_malicious = verdict_info.get("overall").get("malicious")
    malicious_total = verdict_info.get("engines").get("maliciousTotal")
    ip_addresses = list_info.get("ips")
    urls = list_info.get("urls")


    ### print data
    if str(page_ip) != "None":
        print("Domain: " + page_domain)
        print("IP Address: " + str(page_ip))
        print("Country: " + page_country)
        print("Server: " + str(page_server))
        print("Web Apps: " + str(web_apps))
        print("Number of Requests: " + str(num_requests))
        print("Ads Blocked: " + str(ads_blocked))
        print("HTTPS Requests: " + str(https_percentage) + "%")
        print("IPv6: " + str(ipv6_percentage) + "%")
        print("Unique Country Count: " + str(country_count))
        print("Malicious: " + str(is_malicious))
        print("Malicious Requests: " + str(malicious_total))
        print("Pointed Domains: " + str(pointed_domains))



def query(uuid):
    for target_uuid in uuid:
        response = requests.get("https://urlscan.io/api/v1/result/%s" % target_uuid)
        status = response.status_code

        if status != requests.codes.ok:
            print('Results not processed. Please check again later:', status)
            sys.exit(5)

        r = response.content.decode("utf-8")

        if not args.quiet:
            if not args.summary:
                print(r)

        #formatted_uuid = target_uuid.replace("-", "_")
        url = response.json().get("task").get("url").split("://")[1]
        submission_time = response.json().get("task").get("time")
        target_dir = args.dir + '/' + url + '/'

        save_template = target_dir + submission_time + '_' + target_uuid

        if hasattr(args, 'dir'):
            save_to_dir(target_dir, save_template, str(r))

        if args.dom:
            download_dom(target_uuid, target_dir, save_template)
        if args.png:
            download_png(target_uuid, target_dir, save_template)
        if args.summary:
            print_summary(response.json())

        time.sleep(3)

def save_history(target_url, r):
    ### extract UUID from json
    matched_lines = [line for line in r.split('\n') if "uuid" in line]
    result = ''.join(matched_lines)
    result = result.split(":",1)[1]
    uuid = re.sub(r'[^a-zA-Z0-9=-]', '', result)
    ### end UUID extraction

    target_url = str(target_url)
    current_time = int(time.time())
    human_readable_time = str(datetime.datetime.fromtimestamp(current_time))
    connect_db()
    c.execute('''CREATE TABLE IF NOT EXISTS scanned_urls (url, uuid, datetime TEXT PRIMARY KEY)''')
    c.execute("INSERT OR REPLACE INTO scanned_urls VALUES (?, ?, ?)", (target_url, uuid, human_readable_time))
    conn.commit()
    conn.close()


def save_to_dir(target_dir, save_template, r):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    save_file_name = save_template + '.json'

    path_to_file = pathlib.Path(save_file_name)
    if not path_to_file.is_file():
        with open(save_file_name, 'a') as out:
            out.write(r)

def submit(url, urlscan_api, file, db, public, quiet):
    if file:
        urls_to_scan = [line.rstrip('\n') for line in open(file)]
    else:
        urls_to_scan = url

    for target_url in urls_to_scan:

        if len(target_url)<=5 or target_url[0]=="*":
            print("URL '%s' is invalid." % target_url)
            continue

        headers = {
            'Content-Type': 'application/json',
            'API-Key': urlscan_api,
        }

        if not public:
            data = '{"url": "%s"}' % target_url
        else:
            data = '{"url": "%s", "public": "on"}' % target_url

        response = requests.post('https://urlscan.io/api/v1/scan/', headers=headers, data=data)

        # Support for errors or black-listed domains
        json_response = json.loads(response.text)

        # Checks for API quota match or a different error
        if 'status' in json_response.keys():
            if json_response['status'] == 400:
                print("Error: %s. Aborting scan for %s." % (json_response['description'], target_url))
                continue
            elif json_response['status'] == 429:
                print("Error: %s. Pausing scan for %s." % (json_response['description'], target_url))
                sleep_time = int(re.findall('\d+', json_response['message'])[1])+5
                if sleep_time > 60:
                    print("API submission quota has been met: https://urlscan.io/about-api/#ratelimit")
                    print("Tip: retry using scans of a different type (-p for public, nothing for private)")
                    break
                print("Repeating scan after %s seconds" % sleep_time)
                time.sleep(int(sleep_time))
                response = requests.post('https://urlscan.io/api/v1/scan/', headers=headers, data=data)

        ## end POST request

        r = response.content.decode("utf-8")
        if not quiet:
            print(r)

        if db:
            save_history(target_url, r)

        time.sleep(3)


def add_key_value():
    connect_db()
    global urlscan_api
    try:
        c.execute('''CREATE TABLE api (key TEXT PRIMARY KEY)''')
    except sqlite3.OperationalError:
        pass
    if args.api:
        urlscan_api = args.api
    else:
        urlscan_api = input('Please enter API key: ')
    c.execute("INSERT OR REPLACE INTO api(key) VALUES (?)", (urlscan_api,))
    conn.commit()

def connect_db():
    global conn
    conn = sqlite3.connect(args.db)
    global c
    c = conn.cursor()

def get_key_value():
    connect_db()
    global urlscan_api
    try:
        c.execute("SELECT * FROM api")
    except sqlite3.OperationalError:
        add_key_value()
        c.execute("SELECT * FROM api")
    db_extract = c.fetchone()
    try:
        urlscan_api = ''.join(db_extract)
    except TypeError:
        print('Invalid API entry in database.')
        sys.exit(1)

def initialize():
    global urlscan_api
    if args.command == 'init':
        try:
            get_key_value()
            overwrite = input('API entry already exists in database. Overwrite? (y/n)')
            if overwrite == 'y':
                add_key_value()
        except sqlite3.OperationalError:
            add_key_value()
        sys.exit(0)
    if args.api:
        urlscan_api = args.api
    else:
        get_key_value()

def main():
    if args.command == 'init':
        initialize()

    if args.command == 'scan':
        initialize()
        submit(args.url, urlscan_api, args.file, args.db, args.public, args.quiet)

    if args.command == 'search':
        search(args.url, args.web)

    if args.command == 'retrieve':
        initialize()
        query(args.uuid)



if __name__ == '__main__':
    main()
