from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from .models import UserFCMDevice
from .serializers import UserFCMDeviceSerializer
from app.helper_functions import get_user_id

# Create your views here.

import sys
import os
from dotenv import load_dotenv
from pyfcm import FCMNotification
load_dotenv()

def send_notifs(registration_ids, message_title, message_body, data=None):
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print(data)
    print(registration_ids)
    print(message_body)
    print(message_title)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    push_service = FCMNotification(api_key=os.getenv("FCM_SERVER_KEY"))
    try:
        result = push_service.notify_multiple_devices(
            registration_ids=registration_ids, 
            message_title=message_title, 
            message_body=message_body, 
            data_message=data)
        print(result)
        if result['success']==0:
            return 1
        return 0
    except Exception as e:
        print(e)
        return 1


# Register a new device to backend and store registration_id
class FCMRegisterDeviceView(APIView):

    # Register a new device (create new object)
    def post(self, request):
        req_data = request.data
        if req_data.get("user_token", None)==None or req_data.get("registration_id", None)==None:
            return Response({"message":"User token or registration id missing"}, status=status.HTTP_400_BAD_REQUEST)

        payload = get_user_id(req_data.get("user_token"))
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        req_data = {}
        req_data['user_id'] = payload['_id']
        req_data["registration_id"] = request.data.get("registration_id", None)

        userDevice = UserFCMDevice.objects.filter(Q(user_id = req_data['user_id']) & Q(registration_id = req_data['registration_id']))
        if len(userDevice)!=0:
            return Response({"message":"Device details updated"}, status=status.HTTP_200_OK)
        else:
            data = {
                "user_id":req_data['user_id'],
                "registration_id":req_data['registration_id']
            }
            serializer = UserFCMDeviceSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Device Registered"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# Send Alert notification to all the devices other than the users device
class FCMPushNotificationView(APIView):

    def post(self, request):
        req_data = request.data
        message_title = req_data.get('message_title', None)
        message_body = req_data.get("message_body", None)
        data = req_data.get("data", None)
        user_ids = req_data.get("user_ids", None)
        to_all = req_data.get("to_all", None)
        token = req_data.get("token", None)

        if (not message_title) or (not message_body) or not(token):
            return Response({"message":"Data is missing"}, status=status.HTTP_400_BAD_REQUEST)

        if token != os.getenv("NOTIF_CHECK_TOKEN"):
            return Response({"message":"Not allowed to use the API"}, status=status.HTTP_403_FORBIDDEN)

        registration_ids = []

        if to_all:
            userDevices = UserFCMDevice.objects.all()
            for userDevice in userDevices:
                registration_ids.append(userDevice.registration_id)
        else:
            if not user_ids:
                return Response({"message":"Data is missing"}, status=status.HTTP_400_BAD_REQUEST)
            for user in user_ids:
                userDevice = UserFCMDevice.objects.filter(user_id=user)
                for device in userDevice:
                    registration_ids.append(device.registration_id)

        if len(registration_ids)==0:
            return Response({"message":"User not found"}, status=status.HTTP_400_BAD_REQUEST)

        success = False
        
        print("############################################")
        for reg_id in registration_ids:
            result = send_notifs([reg_id], message_title, message_body, data)
            if result:
                print("LOG: Notification not sent to device with device id " + reg_id)
            else:
                success = True
        print("#############################################")
            
        if not success:
            return Response({"message":"Failed to send Notification"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message":"Notification Sent"}, status=status.HTTP_200_OK)
