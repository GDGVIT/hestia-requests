from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q

from app.helper_functions import get_user_id

import requests
import json

# Create your views here.
from .models import ItemRequest, Accepts
from .serializers import ItemRequestSerializer, AcceptsSerializer
from notification_app.views import send_notifs
from notification_app.models import UserFCMDevice

from .organizations_view import (
    OrganizatonView,
    AdminOrganizationView,
    UserViewOrganization,
    VerifyOrganizationView
)

def check_blocked(first_user, second_user):
    URL = "https://hestia-report-do.herokuapp.com/api/report/check/?first_user={}&second_user={}".format(first_user, second_user)
    response = requests.get(URL)
    return response


class PingView(APIView):

    def get(self, requests):
        return Response({"message":"OK"}, status=status.HTTP_200_OK)

class ItemRequestView(APIView):

    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        item_requests = ItemRequest.objects.filter(request_made_by=payload['_id'])
        if len(item_requests) >= 5:
            return Response({"message":"User has already made maximum requests"}, status=status.HTTP_400_BAD_REQUEST)
        
        req_data = {}
        req_data["item_name"] = request.data.get("item_name", None)
        req_data["quantity"] = request.data.get("quantity", None)
        req_data["location"] = request.data.get("location", None)
        req_data['request_made_by'] = payload['_id']
        req_data['description'] = request.data.get('description', None)
        if req_data['description']=='':
            req_data['description'] = None
        serializer = ItemRequestSerializer(data=req_data)
        if serializer.is_valid():
            serializer.save()
            registration_ids = []

            userDevices = UserFCMDevice.objects.all()
            for userDevice in userDevices:
                print(userDevice.user_id)
                if userDevice.user_id != payload['_id']:
                    registration_ids.append(userDevice.registration_id)
                else:
                    print("Not Taking")

            message_title = "New Request Arrived"
            message_body = req_data['item_name']
            data = {
                "url":"https://akina.dscvit.com/feed",
                "click_action":"FLUTTER_NOTIFICATION_CLICK",
                "sound":"default",
                "status":"done",
                "screen":"Requests Page",
                "location":req_data['location']
            }

            result = send_notifs(registration_ids, message_title, message_body, data)
            if result:
                return Response({"message":"New Request created but, failed to send notifications", "Request":serializer.data}, status=status.HTTP_200_OK)

            return Response({"message":"New Request created", "Request":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        try:
            item_request = ItemRequest.objects.get(request_made_by=payload['_id'], id=pk)
            serializer = ItemRequestSerializer(item_request)
            item_request.delete()
            return Response({'message':"Request Deleted", "Request":serializer.data}, status=status.HTTP_200_OK)
        except ItemRequest.DoesNotExist:
            return Response({"maessage":"Request not found"}, status=status.HTTP_204_NO_CONTENT)

    def get(self, request, pk):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        try:
            item_request = ItemRequest.objects.get(id=pk)
            serializer = ItemRequestSerializer(item_request)
            serializer = serializer.data
            return Response({'message':"Request Found", "Request":serializer}, status=status.HTTP_200_OK)
        except ItemRequest.DoesNotExist:
            return Response({"maessage":"Request not found"}, status=status.HTTP_204_NO_CONTENT)
        
class AllRequestView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        location = request.query_params.get('location', None)
        if location==None or location=='':
            return Response({"message":"Location not provided"}, status=status.HTTP_400_BAD_REQUEST)

        item_requests = ItemRequest.objects.filter(location__iexact=location)
        if len(item_requests) == 0:
            return Response({"message":"No requests found"}, status=status.HTTP_204_NO_CONTENT)

        serializer = ItemRequestSerializer(item_requests, many=True)
        data = serializer.data

        flag = True

        while flag:
            for item in data:
                request_acceptors = item['accepted_by'].split(',')
                if item['request_made_by']==payload['_id'] or payload['_id'] in request_acceptors:
                    data.remove(item)

            flag = False

            for item in data:
                request_acceptors = item['accepted_by'].split(',')
                if item['request_made_by']==payload['_id'] or payload['_id'] in request_acceptors:
                    flag = True

        key = 1
        for item in data:
            item['key'] = key
            key += 1
        

        if len(data) == 0:
            return Response({"message":"No requests found"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message":"Requests found", "Request":data}, status=status.HTTP_200_OK)

class MyRequestView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        requests = ItemRequest.objects.filter(request_made_by=payload['_id'])
        if len(requests)==0:
            return Response({"message":"No Requests found"}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = ItemRequestSerializer(requests, many=True)
            serializer = serializer.data
            key = 1
            for item in serializer:
                item['key'] = key
                key += 1
            return Response({"message":"Requests found", "Request":serializer}, status=status.HTTP_200_OK)


class AcceptsView(APIView):

    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        if request.data.get('request_id', None)==None or request.data.get("location", None)==None:
            return Response({"message":"Invalid accept"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item_request = ItemRequest.objects.get(id=int(request.data.get('request_id', None)))
        except ItemRequest.DoesNotExist:
            return Response({"message":"Request Not Found"}, status=status.HTTP_400_BAD_REQUEST)

        if item_request.request_made_by == payload['_id']:
            return Response({"message":"User not allowed to accept request"}, status=status.HTTP_400_BAD_REQUEST)
        
        if item_request.location.lower() == request.data.get('location', None).lower():
            accepts = Accepts.objects.filter(Q(request_made_by=item_request.request_made_by) & Q(request_acceptor=payload['_id']))
            
            if len(accepts)!=0:
                accept = accepts[0]

                #################### CHECKING IF USERS BLOCKED EACH OTHER ####################################
                resp = check_blocked(accept.request_made_by, accept.request_acceptor)
                if resp.status_code==200:
                    resp = json.loads(resp.text)
                    return Response({"message":resp['message']}, status=status.HTTP_400_BAD_REQUEST)

                items_accepted = accept.request_id
                items_accepted = items_accepted.split(',')
                if str(item_request.id) in items_accepted:
                    return Response({'message':"Item Already Accepted"}, status=status.HTTP_400_BAD_REQUEST)
                accept.request_id = accept.request_id + "," + str(item_request.id)
                accept.item_names = accept.item_names + "," +str(item_request.item_name)
                accept.save()
                serializer = AcceptsSerializer(accept)
                item_request.accepted_by = str(item_request.accepted_by) + "," + str(payload['_id'])
                item_request.save()

                registration_ids = []
                
                userDevices = UserFCMDevice.objects.filter(user_id = accept.request_made_by)
                if len(userDevices) != 0:
                    registration_ids.append(userDevices[0].registration_id)
                    message_title = "Request Has been Accepted"
                    message_body = "Your request for " + item_request.item_name + " has been accepted."
                    data = {
                        "url":"https://akina.dscvit.com/mychats",
                        "click_action":"FLUTTER_NOTIFICATION_CLICK",
                        "sound":"default",
                        "status":"done",
                        "screen":"Chats Page"
                    }

                    result = send_notifs(registration_ids, message_title, message_body, data)
                else:
                    result = 1

                if result:
                    return Response({"message":"Request Accepted but, failed to send notifications", "Accepts":serializer.data}, status=status.HTTP_200_OK)

                return Response({"message": "Request Accepted", "Accepts":serializer.data}, status=status.HTTP_200_OK)
            else:

                #################### CHECKING IF USERS BLOCKED EACH OTHER ####################################
                resp = check_blocked(item_request.request_made_by, str(payload['_id']))
                if resp.status_code==200:
                    resp = json.loads(resp.text)
                    return Response({"message":resp['message']}, status=status.HTTP_400_BAD_REQUEST)
                    
                accepts = {
                    "request_made_by": item_request.request_made_by,
                    "request_acceptor": str(payload['_id']),
                    "request_id": str(item_request.id),
                    "item_names": str(item_request.item_name)
                }
                serializer = AcceptsSerializer(data=accepts)
                if serializer.is_valid():
                    serializer.save()
                    item_request.accepted_by = payload['_id']
                    item_request.save()

                    registration_ids = []
                    
                    userDevices = UserFCMDevice.objects.filter(user_id = accepts['request_made_by'])
                    if len(userDevices) != 0:
                        registration_ids.append(userDevices[0].registration_id)
                        message_title = "Request Has been Accepted"
                        message_body = "Your request for " + item_request.item_name + " has been accepted."
                        data = {
                            "url":"https://akina.dscvit.com/mychats",
                            "click_action":"FLUTTER_NOTIFICATION_CLICK",
                            "sound":"default",
                            "status":"done",
                            "screen":"Chats Page"
                        }

                        result = send_notifs(registration_ids, message_title, message_body, data)
                    else:
                        result = 1
                    
                    if result:
                        return Response({"message":"Request Accepted but, failed to send notifications", "Accepts":serializer.data}, status=status.HTTP_200_OK)

                    return Response({"message": "Request Accepted", "Accepts":serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"Invalid acceptor"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Locations are not same"}, status=status.HTTP_400_BAD_REQUEST)

    
    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        accepts = Accepts.objects.filter(Q(request_made_by=payload['_id']) | Q(request_acceptor=payload['_id']))
        if len(accepts)==0:
            return Response({"message":"No accpets found"}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = AcceptsSerializer(accepts, many=True)
            serializer = serializer.data
            key = 1
            for item in serializer:
                item['key'] = key
                key += 1
            return Response({"message":"Accepts found", "Accepts":serializer}, status=status.HTTP_200_OK)
