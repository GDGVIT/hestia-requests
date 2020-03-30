from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q

from app.helper_functions import get_user_id

from .models import Organizations
from .serializers import OrganizationsSerializer

class OrganizatonView(APIView):

    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrganizationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Organization Saved", "organization":serializer.data}, status=status.HTTP_201_CREATED)

        else:
            return Response({"message":"Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        try:
            org = Organizations.objects.get(id=pk)
            serializer = OrganizationsSerializer(org)
            serializer = serializer.data
            return Response({"message":"Organization Found", "Organization":serializer}, status=status.HTTP_200_OK)
        except Organizations.DoesNotExist:
            return Response({"message":"Organization Does Not Exist"}, status=status.HTTP_400_BAD_REQUEST)


class UserViewOrganization(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        orgs = Organizations.objects.all()
        result = []
        for org in orgs:
            if org.is_verified:
                serializer = OrganizationsSerializer(org)
                result.append(serializer.data)

        key = 1
        for item in result:
            item['key'] = key
            key += 1
        
        if len(result)==0:
            return Response({"message":"Organizations not found"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message":"Organizaions found", "Organization":result}, status=status.HTTP_200_OK)

class AdminOrganizationView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        orgs = Organizations.objects.all()
        
        if len(orgs)==0:
            return Response({"message":"No Organizations Found"}, status=status.HTTP_204_NO_CONTENT)

        serializer = OrganizationsSerializer(orgs, many=True)
        serializer = serializer.data
        key = 1
        for item in serializer:
            item['key'] = key
            key += 1
        
        return Response({"message":"Organizations Found", "Organization":serializer}, status=status.HTTP_200_OK)

class VerifyOrganizationView(APIView):

    def get(self, request, pk):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        try:
            org = Organizations.objects.get(id=pk)
            org.is_verified = True
            org.save()
            return Response({"message":"Organization Verified"}, status=status.HTTP_200_OK)
        except Organizations.DoesNotExist:
            return Response({"message":"Organization Does Not Exist"}, status=status.HTTP_400_BAD_REQUEST)

