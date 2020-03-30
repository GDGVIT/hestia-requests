from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q

from app.helper_functions import get_user_id

# Create your views here.
from .models import ItemRequest, Accepts
from .serializers import ItemRequestSerializer, AcceptsSerializer

from .organizations_view import (
    OrganizatonView,
    AdminOrganizationView,
    UserViewOrganization,
    VerifyOrganizationView
)

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
        req_data["item_name"] = request.data["item_name"]
        req_data["quantity"] = request.data["quantity"]
        req_data["location"] = request.data["location"]
        req_data['request_made_by'] = payload['_id']
        serializer = ItemRequestSerializer(data=req_data)
        if serializer.is_valid():
            serializer.save()
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

        print(type(request.data['request_id']))

        try:
            item_request = ItemRequest.objects.get(id=int(request.data['request_id']))
        except ItemRequest.DoesNotExist:
            return Response({"message":"Request Not Found"}, status=status.HTTP_400_BAD_REQUEST)

        if item_request.request_made_by == payload['_id']:
            return Response({"message":"User not allowed to accept request"}, status=status.HTTP_400_BAD_REQUEST)
        
        if item_request.location.lower() == request.data['location'].lower():
            accepts = Accepts.objects.filter(Q(request_made_by=item_request.request_made_by) & Q(request_acceptor=payload['_id']))
            
            if len(accepts)!=0:
                accept = accepts[0]
                items_accepted = accept.request_id
                items_accepted = items_accepted.split(',')
                if str(item_request.id) in items_accepted:
                    return Response({'message':"Item Already Accepted"}, status=status.HTTP_400_BAD_REQUEST)
                accept.request_id = accept.request_id + "," + str(item_request.id)
                accept.save()
                serializer = AcceptsSerializer(accept)
                item_request.accepted_by = str(item_request.accepted_by) + "," + str(payload['_id'])
                item_request.save()
                return Response({"message": "Request Accepted", "Accepts":serializer.data}, status=status.HTTP_200_OK)
            else:
                accepts = {
                    "request_made_by": item_request.request_made_by,
                    "request_acceptor": str(payload['_id']),
                    "request_id": str(item_request.id)
                }
                serializer = AcceptsSerializer(data=accepts)
                if serializer.is_valid():
                    serializer.save()
                    item_request.accepted_by = payload['_id']
                    item_request.save()
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
