import nmap
import json
import os
import pika
import re
from AssetIdentifier.utilities.result_to_queue import publish_result_to_queue
import requests


RESULTS = 'https://jsonkeeper.com/b/1BUZ'


def severity_check(host="192.168.1.100"):
    last_octet = int(host.split(".")[-1])
    if 1 <= last_octet <= 64:
        return 'High Severity Zone'
    elif 65 <= last_octet <= 128:
        return 'Medium Severity Zone'
    else:
        return 'Low Severity Zone'


def publish_message(host, message):
    # host_severity = severity_check(host)
    # message['severity'] = host_severity

    with pika.BlockingConnection(pika.ConnectionParameters('localhost')) as connection:
        channel = connection.channel()

        channel.queue_declare(queue='json_queue')
        channel.basic_publish(exchange='',
                              routing_key='json_queue',
                              body=json.dumps(message).encode('utf-8'))
        #   body=json.dumps(message))
        print(" [x] Sent JSON object to queue")


def callback_initial_scan(host, scan_result):
    if scan_result['scan'] == {}:
        print(host, "DOWN NOW")
    else:

        with open("scan_results.txt", 'a') as file:
            existing_ips = get_up_ip()
            if host in existing_ips:
                return
            else:
                file.write(f"{host}\n")


def clean_output(host, scan_result):
    clean_result = {}
    if scan_result.get("scan", None):
        clean_result["scan"] = {}
        scan = scan_result["scan"]
        if scan.get(host):
            scan_host = scan.get(host)
            if scan_host.get("hostnames", None):
                clean_result["scan"]["hostnames"] = scan_host.get(
                    "hostnames")[0]["name"] if len(scan_host.get("hostnames")) > 0 else None
            if scan_host.get("addresses"):
                clean_result["scan"]["addresses"] = scan_host.get("addresses")
            if scan_host.get("vendor"):
                clean_result["scan"]["vendor"] = scan_host.get("vendor")

            if scan_host.get("tcp"):
                clean_result["scan"]["ports"] = scan_host.get("tcp")

            if scan_host.get("udp"):
                clean_result["scan"]["ports"] = scan_host.get("udp")

            if scan_host.get("hostscript"):
                clean_result["scan"]["scripts"] = []
                for each_script in scan_host.get("hostscript"):
                    if re.search(r"errors?", each_script["output"], re.IGNORECASE):
                        continue
                    else:
                        clean_result["scan"]["scripts"].append(each_script)

            if scan_host.get("osmatch"):
                if scan_host.get("osmatch")[0]:
                    clean_result["os"] = {}
                    clean_result["os"]["name"] = scan_host.get("osmatch")[
                        0].get("name")
                    clean_result["os"]["class"] = scan_host.get("osmatch")[
                        0].get("name")
    else:
        print("NoScan")
        clean_result["scan"] = None
        return clean_result

    clean_result['severity'] = severity_check(host)

    print(clean_result)
    return clean_result


def second_scan_callback(host, scan_result):
    print(json.dumps(scan_result))
    # publish_message(host, scan_result)
    clean_output(host, scan_result)
    save_results_to_json(scan_result, "json_output.json")


def run_nmap_scan(flags, callback, hosts=None):
    response = requests.get(RESULTS, verify=False)
    data = response.json()

    with open('result.json', 'w') as f:
        json.dump(data, f, indent=4)

    nma = nmap.PortScannerAsync()
    try:
        if hosts:
            nma.scan(hosts=hosts, arguments=flags,
                     callback=callback)
        else:
            nma.scan(arguments=flags, callback=callback)

        while nma.still_scanning():
            nma.wait(2)
            print("<< Scanning >>")
    except KeyboardInterrupt:
        print("Scan stopped by user.")
    except Exception as e:
        print("An error occurred during scanning:", e)
    finally:
        try:
            if nma:
                nma.stop()
        except Exception as e:
            print("Error occurred during cleanup:", e)


def save_results_to_json(results, filename):
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)


def get_up_ip():
    ip_list = []
    with open('scan_results.txt', "r") as f:
        for line in f:
            ip = line.split()[0]
            ip_list.append(ip)
    return ip_list


def initiate_scanner(ip_range='192.168.1.0/24'):
    f = open('scan_results.txt', 'r+')
    f.truncate(0)
    # Initial Scan with -sP
    # To discover majority of the devices
    
    ##########################3 RUNNN
    # run_nmap_scan(hosts=ip_range, flags='-sP', callback=callback_initial_scan)

    # # Extract IP addresses of hosts that are up
    # up_ips = get_up_ip()
    # print("Up Ips", up_ips)

    # Run second scan with specified flags on currently up IP addresses
    # for ip in up_ips:
    #     # run_nmap_scan(
    #     #     hosts=ip, flags='-T4 -Pn --max-retries 1 --max-scan-delay 20 --open --system-dns --top-ports 20 -sV --script=dns-brute,dns-check-zone,dns-zone-transfer,ftp-anon,ftp-vsftpd-backdoor,ftp-vuln-cve2010-4221,http-aspnet-debug,http-cookie-flags,msrpc-enum,ms-sql-info,mysql-info,nbstat,nfs-showmount,oracle-tns-version,rdp-enum-encryption,rpcinfo,smb2-security-mode,smb-enum-shares,smb-security-mode,smtp-open-relay,snmp-info,ssl-enum-ciphers,tftp-version,vmware-version,vulners',
    #     #     callback=second_scan_callback
    #     # )
    #     #     run_nmap_scan(flags='-iL ./scan_results.txt -T4 --max-retries 1 --max-scan-delay 20 --open --system-dns --top-ports 50 -sV -sC',
    #     #                   callback=second_scan_callback)

    #     # run_nmap_scan(ip, '-T4 --max-retries 1 --max-scan-delay 20 --open --system-dns  --top-ports 50 -sV -Pn --script=ssl-enum-ciphers,smb2-security-mode,smb-security-mode', callback=second_scan_callback)

    #     # run_nmap_scan(ip, '-T4 --max-retries 1 --max-scan-delay 20 --open --system-dns --top-ports 50 -sV --script=*', callback=second_scan_callback)

    #     # run_nmap_scan(
    #     #     hosts=ip,
    #     #     flags='-sC -sV -T4 --max-scan-delay 20 --max-retries 1 -PE -PP --open --top-ports 15 --version-intensity 5',
    #     #     callback=second_scan_callback
    #     # )

    #     run_nmap_scan(
    #         hosts=ip,
    #         flags='-sC -sV -T4 --max-scan-delay 20 --max-retries 1 -PE -PP --open --top-ports 15 --version-intensity 5',
    #         callback=second_scan_callback
    #     )

    #     # run_nmap_scan(
    #     #     hosts=ip,
    #     #     flags='-sS -sV --version-intensity 5 -O --osscan-guess --fuzzy --max-os-tries 8 --max-retries 4 -PE -Pn -PP --top-port 15 --min-hostgroup 64',
    #     #     callback=second_scan_callback
    #     # )

    publish_result_to_queue()

    print("Scan Ended")
    # with pika.BlockingConnection(pika.ConnectionParameters('localhost')) as connection:
    #     channel = connection.channel()

    #     channel.queue_declare(queue='json_queue')
    #     channel.basic_publish(exchange='',
    #                           routing_key='json_queue',
    #                           body=json.dumps(
    #                               {"scan": "stop"}
    #                           )
    #                           )
    #     print(" [x] Scan Ended")
