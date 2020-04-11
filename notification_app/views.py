from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from .models import UserFCMDevice
from .serializers import UserFCMDeviceSerializer

# Create your views here.

import sys
import os
from dotenv import load_dotenv
from pyfcm import FCMNotification
load_dotenv()

def send_notifs(registration_ids, message_title, message_body, data=None):
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
    except:
        print("Oops!",sys.exc_info()[0],"occured.")
        return 1


# Register a new device to backend and store registration_id
class FCMRegisterDeviceView(APIView):

    # Register a new device (create new object)
    def post(self, request):
        req_data = request.data
        if req_data.get("user_id", None)==None or req_data.get("registration_id", None)==None:
            return Response({"message":"User id or registration id missing"}, status=status.HTTP_400_BAD_REQUEST)
        req_data['user_id'] = str(req_data['user_id'])
        userDevice = UserFCMDevice.objects.filter(user_id = req_data['user_id'])
        if len(userDevice)!=0:
            device =UserFCMDevice.objects.filter(Q(registration_id = req_data['registration_id']) & ~Q(user_id = req_data['user_id']))
            if len(device)==0:
                userDevice = userDevice[0]
                userDevice.registration_id = req_data['registration_id']
                userDevice.save()
                return Response({"message":"Device details updated"}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Invalid registation id"}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"message":"Invalid Details"}, status=status.HTTP_400_BAD_REQUEST)


# Send Alert notification to all the devices other than the users device
class FCMPushNotificationView(APIView):

    def post(self, request):
        req_data = request.data
        message_title = req_data.get('message_title', None)
        message_body = req_data.get("message_body", None)
        data = req_data.get("data", None)
        user_ids = req_data.get("user_ids", None)
        to_all = req_data.get("to_all", None)

        if (not message_title) or (not message_body):
            return Response({"message":"Data is missing"}, status=status.HTTP_400_BAD_REQUEST)

        registration_ids = []

        if to_all:
            userDevices = UserFCMDevice.objects.all()
            for userDevice in userDevices:
                registration_ids.append(userDevice.registration_id)
        else:
            if not user_ids:
                return Response({"message":"Data is missing"}, status=status.HTTP_400_BAD_REQUEST)
            for user in user_ids:
                userDevice = UserFCMDevice.objects.get(user_id=user)
                registration_ids.append(userDevice.registration_id)

        print(registration_ids)

        result = send_notifs(registration_ids, message_title, message_body, data)
        if result:
            return Response({"message":"Failed to send Notification"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message":"Notification Sent"}, status=status.HTTP_200_OK)
