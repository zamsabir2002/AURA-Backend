import json

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
# from .utils import initiate_scanner
from AssetMapper.utilities.scan_script import initiate_scanner
from AssetMapper.utilities.alert_generation import generate_alerts
from rest_framework.response import Response
from threading import Thread

from AssetMapper.models import ScanResult


class AssetMapperView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):

        ip_range = request.data.get('ip_range')
        scan_thread = Thread(target=initiate_scanner, args=(ip_range,))
        scan_thread.start()

        response = {
            'Message': 'Scan initiated',
        }
        return Response(response, status=status.HTTP_200_OK)


class AssetGet(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        results = ScanResult.objects.all()
        data = {'scan': []}
        for each_result in results:
            print(each_result.result)
            data['scan'].append(each_result.result)

        return Response(data)
        # return JsonResponse(response_data)

    def post(self, request):
        # dummy_data = {
        #     "hostnames": "PURE-INT-ZAMEETSABIR",
        #     "addresses": {
        #         "ipv4": "10.17.0.35"
        #     },
        #     "ports": {
        #         "21": {
        #             "state": "open",
        #             "reason": "syn-ack",
        #             "name": "ftp",
        #             "product": "vsftpd",
        #             "version": "2.3.4",
        #             "extrainfo": "Anonymous FTP login allowed",
        #             "conf": "10",
        #             "cpe": "cpe:/a:vsftpd:vsftpd:2.3.4"
        #         },
        #         "22": {
        #             "state": "open",
        #             "reason": "syn-ack",
        #             "name": "ssh",
        #             "product": "OpenSSH",
        #             "version": "7.2p2 Ubuntu 4ubuntu2.6",
        #             "extrainfo": "protocol 2.0",
        #             "conf": "10",
        #             "cpe": "cpe:/a:openssh:openssh:7.2p2"
        #         },
        #         "23": {
        #             "state": "open",
        #             "reason": "syn-ack",
        #             "name": "telnet",
        #             "product": "",
        #             "version": "",
        #             "extrainfo": "",
        #             "conf": "8",
        #             "cpe": ""
        #         },
        #         "25": {
        #             "state": "open",
        #             "reason": "syn-ack",
        #             "name": "smtp",
        #             "product": "Postfix",
        #             "version": "3.1.0",
        #             "extrainfo": "Ubuntu",
        #             "conf": "10",
        #             "cpe": "cpe:/a:postfix:postfix:3.1.0"
        #         },
        #         "80": {
        #             "state": "open",
        #             "reason": "syn-ack",
        #             "name": "http",
        #             "product": "Apache httpd",
        #             "version": "2.4.52",
        #             "extrainfo": "(Ubuntu)",
        #             "conf": "10",
        #             "cpe": "cpe:/a:apache:http_server:2.4.52",
        #             "script": {
        #                 "http-title": "Apache2 Ubuntu Default Page: It works",
        #                 "http-server-header": "Apache/2.4.52 (Ubuntu)"
        #             }
        #         },
        #         "3306": {
        #             "state": "open",
        #             "reason": "syn-ack",
        #             "name": "mysql",
        #             "product": "MySQL",
        #             "version": "5.7.31",
        #             "extrainfo": "",
        #             "conf": "10",
        #             "cpe": "cpe:/a:mysql:mysql:5.7.31"
        #         },
        #         "3389": {
        #             "state": "open",
        #             "reason": "syn-ack",
        #             "name": "ms-wbt-server",
        #             "product": "Microsoft Terminal Services",
        #             "version": "",
        #             "extrainfo": "",
        #             "conf": "8",
        #             "cpe": "cpe:/o:microsoft:windows"
        #         },
        #         "5900": {
        #             "state": "open",
        #             "reason": "syn-ack",
        #             "name": "vnc",
        #             "product": "",
        #             "version": "",
        #             "extrainfo": "",
        #             "conf": "8",
        #             "cpe": ""
        #         }
        #     },
        #     "scripts": [
        #         {
        #             "id": "smb2-time",
        #             "output": "Protocol negotiation failed (SMB2)"
        #         }
        #     ],
        #     "severity": "High Severity Zone"
        # }
        # ip_range = request.data.get('ip_range')
        data = request.data
        print(data)
        scan_result = ScanResult(
            ip=data.get('addresses').get('ipv4'), result=data)
        scan_result.save()
        # Get from database

        response = {
            'Message': 'Scan initiated',
        }
        return Response(response, status=status.HTTP_200_OK)


class UpdateAsset(APIView):

    permission_classes = (AllowAny,)

    def put(self, requests):
        data = requests.data.get('updated_data')
        ip_address = data.get('addresses').get('ipv4')
        if ip_address:
            try:
                scan_result = ScanResult.objects.get(ip=ip_address)
                print("FOUND")
                print(data)
                print(scan_result)
                scan_result.result = data
                print(scan_result)
                scan_result.save()
            except ScanResult.DoesNotExist:
                print("Not Found")
                return Response("Asset data doesn't exist for given IP", status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print("--------------", e)
                return Response("Unexpected Error", status.HTTP_400_BAD_REQUEST)
        else:
            Response("Couldn't fing ipv4 address",
                     status=status.HTTP_400_BAD_REQUEST)

        # queue push
        return Response("Asset Information Updated", status=status.HTTP_200_OK)


class GenerateAlerts(APIView):
    permission_classes = (AllowAny,)
    def get(self, requests):
        results = ScanResult.objects.all()
        # data = {'scan': []}

        for each_result in results:
            generate_alerts(host=each_result.result)

        return Response('')