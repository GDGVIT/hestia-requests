from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q

from app.helper_functions import get_user_id

from .models import Organizations, AreasCatered
from .serializers import OrganizationsSerializer, AreasCateredSerializer

class OrganizatonView(APIView):

    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        print(request.data)
        org_data = {}
        org_data['name'] = request.data.get("name", None)
        org_data['city'] = request.data.get("city", None)
        org_data['state'] = request.data.get("state", None)
        org_data['country'] = request.data.get("country", None)
        org_data['description'] = request.data.get("description", None)
        org_data['email'] = request.data.get("email", None)
        org_data['phone_no'] = request.data.get("phone_no", None)
        org_data['address'] = request.data.get("address", None)
        org_data['other_contact'] = request.data.get("other_contact", None)
        org_data['web_links'] = request.data.get("web_links", None)
        
        areas_catered = request.data.get("areas_catered", None)
        if areas_catered==None or len(areas_catered)==0:
            return Response({"message":"Please provide Areas catered"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrganizationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data['id'])
            for area in areas_catered:
                area['org_id'] = serializer.data['id']
                area_serializer = AreasCateredSerializer(data=area)
                if area_serializer.is_valid():
                    area_serializer.save()
                else:
                    print(area_serializer.errors)

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
            areas = AreasCatered.objects.filter(org_id=pk)
            areas_serializer = AreasCateredSerializer(areas, many=True)
            serializer['areas_catered'] = areas_serializer.data
            return Response({"message":"Organization Found", "Organization":serializer}, status=status.HTTP_200_OK)
        except Organizations.DoesNotExist:
            return Response({"message":"Organization Does Not Exist"}, status=status.HTTP_400_BAD_REQUEST)


class UserViewOrganization(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        city = request.query_params.get("city", None)
        state = request.query_params.get("state", None)
        country = request.query_params.get("country", None)
        
        payload = get_user_id(token)
        if payload['_id'] is None:
            return Response({"message":payload['message']}, status=status.HTTP_403_FORBIDDEN)

        orgs = Organizations.objects.all()
        result = []
        for org in orgs:
            if org.is_verified:
                serializer = OrganizationsSerializer(org)
                areas = AreasCatered.objects.filter(org_id=org.id)
                areas_serializer = AreasCateredSerializer(areas, many=True)
                serializer['areas_catered'] = areas_serializer.data
                result.append(serializer.data)

        field = None
        field_value = None

        if city!=None and city!="":
            field = 'city'
            field_value = city.lower()
        elif state!=None and state!="":
            field = 'state'
            field_value = state.lower()
        elif country!=None and country!="":
            field = 'country'
            field_value = country.lower()

        to_remove = []

        if field!=None:
            for org in result:
                areas = org['areas_catered']
                should_remove = True
                for area in areas:                    
                    if field_value==(area[field].lower()):
                        should_remove = False
                if should_remove:
                    to_remove.append(org)

        for item in to_remove:
            result.remove(item)

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
            areas = AreasCatered.objects.filter(id=item['id'])
            area_serializer = AreasCateredSerializer(areas, many=True)
            item['areas_catered'] = area_serializer.data
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