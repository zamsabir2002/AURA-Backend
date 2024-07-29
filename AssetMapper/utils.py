import nmap
import json
import os
import pika

HIGH_SEVERITY_LIST = ['192.168.1.107']
MEDIUM_SEVERITY_LIST = ['192.168.1.100', '192.168.1.102']
LOW_SEVERITY_LIST = []


def severity_check(host):
    if host in HIGH_SEVERITY_LIST:
        return 'H'
    elif host in MEDIUM_SEVERITY_LIST:
        return 'M'
    else:
        return 'L'


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
        print(scan_result)
        with open("scan_results.txt", 'a') as file:
            existing_ips = get_up_ip()
            if host in existing_ips:
                return
            else:
                file.write(f"{host}\n")


def second_scan_callback(host, scan_result):
    print(json.dumps(scan_result))
    publish_message(host, scan_result)
    # if os.path.exists('./json_output.json'):
    #     try:
    #         with open("json_output.json", "r+") as file:
    #             data = json.load(file)
    #             data[host] = scan_result
    #             file.seek(0)
    #             json.dump(data, file, indent=4)
    #     except:
    #         with open("json_output.json", "w") as file:
    #             data = {host: scan_result}
    #             file.seek(0)
    #             json.dump(data, file, indent=4)
    #             file.close()
    # else:
    #     with open("json_output.json", "w") as file:
    #         data = {host: scan_result}
    #         file.seek(0)
    #         json.dump(data, file, indent=4)
    #         file.close()


def run_nmap_scan(hosts, flags, callback):
    nma = nmap.PortScannerAsync()
    try:
        nma.scan(hosts=hosts, arguments=flags,
                 callback=callback)
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
    run_nmap_scan(ip_range, '-sP', callback_initial_scan)

    # Extract IP addresses of hosts that are up
    up_ips = get_up_ip()
    print(up_ips)

    # Run second scan with specified flags on currently up IP addresses
    for ip in up_ips:
        run_nmap_scan(ip, 'nmap -T4 --max-retries 1 --max-scan-delay 20 --open --system-dns --top-ports 50 -sV -sC',
                      callback=second_scan_callback)
        # run_nmap_scan(ip, '-sS -sV --version-intensity 5 -O --osscan-guess --fuzzy --max-os-tries 8 --max-retries 4 -PE -Pn -PP --top-port 15 --min-hostgroup 64', callback=second_scan_callback)
    print("DONE")
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
