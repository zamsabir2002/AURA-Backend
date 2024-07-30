import os
import json

# First Party
from AssetMapper.utilities.publish_message import publish_message
from AssetMapper.utilities.compliance_data import load_compliances


# Mapping of clear text protocols to compliance frameworks
# clear_text_protocols = {
#     "20": "FTP (Data)",
#     "21": "FTP",
#     "23": "Telnet",
#     "80": "HTTP"
# }
# iso_27001_reference = "ISO/IEC 27001:2013 A.13.1.1 - Network controls"
# nist_reference = "NIST SP 800-53 Rev. 5 AC-17 - Remote Access"

COMPLIANCES = load_compliances()

print(COMPLIANCES)

def generate_alerts(host=None):
    alerts = []
    print("ALERT HOST",host)
    if host==None:
        return

    # if os.path.exists('./result.json'):
    #     with open("result.json", "r+") as file:
    #         data = json.load(file)

    for port, port_data in host["ports"].items():

        if port in ["20", "21", "23", "80"] or port in [20, 21, 23, 80]:
            alerts.append({
                "hostname": host["hostnames"],
                "ip": host["addresses"]["ipv4"],
                "port": port,
                "protocol": port_data["name"],
                "alert": "Clear text protocol detected",
                "reference": {
                    "ISO 27001": "A.13.2.3, A.8.24, A.14.1.2",
                    "NIST": "SP 800-53 AC-17, SC-8, SC-13",
                    "ETGRM": "2.4.8"
                },
                "severity": "High",
                "compliance_breached": "Clear text protocol usage may lead to eavesdropping attacks, breaching data confidentiality requirements."
            })

        if (port == "21" or port == 21) and "script" in port_data and port_data["script"].get("id") == "ftp-anon":
            alerts.append({
                "hostname": host["hostnames"],
                "ip": host["addresses"]["ipv4"],
                "port": port,
                "protocol": port_data["name"],
                "alert": "Anonymous FTP login allowed",
                "reference": {
                    "ETGRM": "2.4.7",
                    "ISO 27001": "A.9.2.3",
                    "NIST": "SP 800-53 AC-3, AC-17"
                },
                "severity": "High",
                "compliance_breached": "Allowing anonymous FTP login can lead to unauthorized access, breaching access control policies."
            })
        
        if (port == "443" or port == 443) and "script" in port_data and port_data["script"].get("id") == "ssl-enum-ciphers":
            for warning in port_data["script"]["output"]["warnings"]:
                if "64-bit block cipher 3DES" in warning:
                    alerts.append({
                        "hostname": host["hostnames"],
                        "ip": host["addresses"]["ipv4"],
                        "port": port,
                        "protocol": port_data["name"],
                        "alert": "Weak cipher detected: 3DES vulnerable to SWEET32 attack",
                        "reference": {
                            "ISO 27001": "A.14.1.2, A.8.24",
                            "NIST": "SP 800-53, SC-8",
                            "ETGRM": "2.4.7"
                        },
                        "severity": "Medium",
                        "compliance_breached": "Using weak ciphers can lead to data breaches and compromises, violating secure communication requirements."
                    })
                if "Broken cipher RC4" in warning:
                    alerts.append({
                        "hostname": host["hostnames"],
                        "ip": host["addresses"]["ipv4"],
                        "port": port,
                        "protocol": port_data["name"],
                        "alert": "Weak cipher detected: RC4 is deprecated by RFC 7465",
                        "reference": {
                            "ISO 27001": "A.14.1.2, A.8.24",
                            "NIST": "SP 800-53, SC-8",
                            "ETGRM": "2.4.7"
                        },
                        "severity": "Medium",
                        "compliance_breached": "Using broken ciphers can expose data to interception and tampering, compromising security protocols."
                    })
                if "Ciphersuite uses MD5" in warning:
                    alerts.append({
                        "hostname": host["hostnames"],
                        "ip": host["addresses"]["ipv4"],
                        "port": port,
                        "protocol": port_data["name"],
                        "alert": "Weak cipher detected: MD5 for message integrity",
                        "reference": {
                            "ISO 27001": "A.14.1.2",
                            "NIST": "SP 800-53, SC-8"
                        },
                        "severity": "Medium",
                        "compliance_breached": "Using weak hash functions like MD5 can result in data integrity issues, breaching cryptographic security standards."
                    })
                if "Weak certificate signature: SHA1" in warning:
                    alerts.append({
                        "hostname": host["hostnames"],
                        "ip": host["addresses"]["ipv4"],
                        "port": port,
                        "protocol": port_data["name"],
                        "alert": "Weak certificate signature detected: SHA1",
                        "reference": {
                            "ISO 27001": "A.14.1.2",
                            "NIST": "SP 800-53, SC-8"
                        },
                        "severity": "Medium",
                        "compliance_breached": "Using weak certificate signatures can undermine the trust model, leading to potential man-in-the-middle attacks."
                    })
    if "scripts" in host:
        for each_script in host["scripts"]:
            if each_script.get("id") == "smb2-security-mode" and "Message signing enabled but not required" in each_script.get("output"):
                    alerts.append({
                        "hostname": host["hostnames"],
                        "ip": host["addresses"]["ipv4"],
                        "port": "445",
                        "protocol": "smb",
                        "alert": "SMB message signing enabled but not required",
                        "reference": {
                            "ISO 27001": "A.12.3.1",
                            "NIST": "SP 800-53 CM-6"
                        },
                        "severity": "Medium",
                        "compliance_breached": "SMB message signing not required can lead to data tampering and man-in-the-middle attacks, breaching integrity requirements."
                    })

            if each_script.get("id") == "msrpc-enum" and "uuid" in host["script"]["output"]:
                alerts.append({
                    "hostname": host["hostnames"],
                    "ip": host["ip"],
                    "port": "135",
                    "protocol": "msrpc",
                    "alert": "Information disclosure: UUID detected in MSRPC enumeration",
                    "reference": {
                        "ISO 27001": "A.14.1.3",
                        "NIST": "SP 800-53 SI-11"
                    },
                    "severity": "Medium",
                    "compliance_breached": "Exposing UUIDs can lead to information disclosure, increasing the risk of targeted attacks and data breaches."
                })
    for each_alert in alerts:
        publish_message(each_alert, 'alert_queue')

