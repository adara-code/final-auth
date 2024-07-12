from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from .token import UserAuth

from . models import User, Organisation
from .serializers import UserRegistrationSerializer, LoginSerializer, CreateOrganisationSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes


class TokenAPI(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user
        
        serializer = UserRegistrationSerializer(user)
        return Response(serializer.data)

# Registers a user
class RegisterUser(APIView):    
    authentication_classes = []   
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_input = serializer.save()
            
            user_data = User.objects.get(email=request.data['email'])
               
            success = {
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": user_data.userToken,
                    "user": {
                        "userId": str(user_data.userId),
	                    "firstName": user_data.firstName,
				        "lastName": user_data.lastName,
				        "email": user_data.email,
				        "phone": user_data.phone,
                        }
                    }
                }   
            return Response(success, status=status.HTTP_201_CREATED)      
        else:
            failed = {
                "status":"Bad request",
                "message": "Registration unsuccessful",
                "statusCode": status
            }
            return Response(failed, status=status.HTTP_400_BAD_REQUEST)
        
#Login a User        
class LoginUser(APIView):    
    authentication_classes = []
    serializer = LoginSerializer
            
    def post(self, request):  
        fail = {
                    "status": "Bad request",
                    "message": "Authentication failed",
                    "statusCode": 401
                }
        
        input_email = request.data.get('email')
        input_password = request.data.get('password')
        
        user = authenticate(username=input_email, password=input_password)
                
        if user:
            serializer = self.serializer(user)
            success_message =  {
            "status": "success",
            "message": "Login successful",
            "data": {
            "accessToken": serializer.data.get('userToken'),
            "user": {
                "userId": str(serializer.data.get('userId')),
                "firstName": serializer.data.get('firstName'),
                "lastName": serializer.data.get('lastName'),
                "email": serializer.data.get('email'),
                "phone": serializer.data.get('phone'),
                    }
                }
            }
            return Response(success_message)
        return Response(fail, status=status.HTTP_401_UNAUTHORIZED)
        
         
#Retrieve a user record
class RetrieveUserRecord(APIView):  
    # authentication_classes = [UserAuth]
    permission_classes = [IsAuthenticated]
      
    def get(self, request, id):        
        user = request.user
        
        if user.userId == id:
            user_exist = get_object_or_404(User, userId=user.userId)
            if user_exist:
                users_org = user_exist.organisation.all().values("name")
                name_of_org = [org for org in users_org]
                name = name_of_org[0]['name']
            
                print(name_of_org)
                success = {
                    "status": "success",
                    "message": "<message>",
                    "data": {
                        "userId": str(user_exist.userId),
                        "firstName": user_exist.firstName,
                        "lastName": user_exist.lastName,
                        "email": user_exist.email,
                        "phone": user_exist.phone
                    }
                }
                return Response(success)
        return Response("Wrong User Token", status=401)
 
 
@api_view(['GET', 'POST'])
@authentication_classes([UserAuth])
@permission_classes([IsAuthenticated])
def retrieve_organisations(request, format=None):
    if request.method == 'GET':
        user = request.user
        organisations = user.organisation.all().values("orgId", "name", "description")
        success = {
            "status": "success",
                "message": "<message>",
            "data": {
            "organisations": [
                {
                    "orgId": str(organisations[0]['orgId']),
                    "name": organisations[0]['name'],
                    "description": organisations[0]['description'],
                }
            ]
            }
        }
        return Response(success, status=200)
        
    elif request.method == 'POST':
        user = request.user
    
        name = request.data['name']
        description = request.data['description']
        
        serializer = CreateOrganisationSerializer(data=request.data)
        
        if serializer.is_valid():
            new_organisation = Organisation(name=f"{serializer.data['name']}'s Organisation", description=serializer.data['description'])
            new_organisation.save()
            user.organisation.add(new_organisation)
            success = {
                "status": "success",
                "message": "Organisation created successfully",
                "data": {
                "orgId": str(new_organisation.orgId), 
                "name": new_organisation.name, 
                "description": new_organisation.description
              }
          }
            return Response(success, status=201)
        else:
            status = 400
            fail = {
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": status
            }
            return Response(fail, status=400)
            
                    
#Retrieve an individual organisation record
@api_view(['GET'])
@authentication_classes([UserAuth])
@permission_classes([IsAuthenticated])
def retrieve_organisation_by_id(request, orgId, format=None):
    try:
        org_by_id = Organisation.objects.get(orgId=orgId)
        success = {
            "status": "success",
                "message": "<message>",
            "data": {
                    "orgId":str(org_by_id.orgId),
                    "name": org_by_id.name,
                    "description": org_by_id.description,
            }
        }
        return Response(success, status=status.HTTP_200_OK)
    except:
        return Response("No record of that organisation", status=status.HTTP_404_NOT_FOUND)

        
        
#Add user to organisation
@api_view(['POST'])
@authentication_classes([UserAuth])
@permission_classes([IsAuthenticated])
def add_user_to_organisation(request,orgId): 
    organisation = Organisation.objects.get(orgId=orgId)
    
    try:
        user_added = request.data['userId']
        user_by_id = User.objects.get(userId=user_added)
        user_by_id.save()
        organisation.user_set.add(user_by_id)
        
        success = {
            "status": "success",
            "message": "User added to organisation successfully",
        }
        return Response(success, status=200)
    except:
        return Response({"Error":"User with that id does not exist"}, status=400)
    