from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .utils import initiate_scanner
from rest_framework.response import Response
from threading import Thread

# Create your views here.


class AssetIdentifierView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):

        ip_range = request.data.get('ip_range')
        scan_thread = Thread(target=initiate_scanner, args=(ip_range,))
        scan_thread.start()

        response = {
            'Message': 'Scan initiated',
        }
        return Response(response, status=status.HTTP_200_OK)
