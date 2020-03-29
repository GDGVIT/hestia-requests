from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q

from app.helper_functions import get_user_id

# Create your views here.
from .models import ItemRequest, Accepts
from .serializers import ItemRequestSerializer, AcceptsSerializer

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
        print(token)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        try:
            item_request = ItemRequest.objects.get(id=pk)
            serializer = ItemRequestSerializer(item_request)
            return Response({'message':"Request Found", "Request":serializer.data}, status=status.HTTP_200_OK)
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
        
        for item in data:
            if item['request_made_by']==payload['_id']:
                data.remove(item)
        print(data)
        for item in data:
            if item['request_made_by']==payload['_id']:
                data.remove(item)

        if len(item_requests) == 0:
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
            return Response({"message":"Requests found", "Requests":serializer.data}, status=status.HTTP_200_OK)


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
            item_request = ItemRequest.objects.get(id=request.data['request_id'])
        except ItemRequest.DoesNotExist:
            return Response({"message":"Request Not Found"}, status=status.HTTP_400_BAD_REQUEST)

        if item_request.request_made_by == payload['_id']:
            return Response({"message":"User not allowed to accept request"}, status=status.HTTP_400_BAD_REQUEST)
        
        if item_request.location.lower() == request.data['location'].lower():
            accepts = {
                "request_made_by": item_request.request_made_by,
                "request_acceptor": payload['_id'],
                "request_id": item_request.id
            }
            serializer = AcceptsSerializer(data=accepts)
            if serializer.is_valid():
                serializer.save()
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
            return Response({"message":"Accepts found", "Accepts":serializer.data}, status=status.HTTP_200_OK)
