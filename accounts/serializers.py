from typing import Any
from .models import Organisation, User
from rest_framework.fields import UUIDField
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers, validators

# from rest_framework_simplejwt.tokens import RefreshToken

    
class UserRegistrationSerializer(ModelSerializer): 
    firstName = serializers.CharField(allow_blank=False) 
    lastName = serializers.CharField(allow_blank=False)
    email = serializers.CharField(allow_blank=False)
    password = serializers.CharField(write_only=True, allow_blank=False)
    phone = serializers.CharField(allow_blank=True)
    
    def validate_email(self,value):
        failed = {
                "status":"Bad request",
                "message": "Registration unsuccessful",
                "statusCode": 400
            } 
        test_email = User.objects.filter(email=value).exists()
        if test_email:
            raise serializers.ValidationError(failed)
        return value
    
    
    def create(self, validated_data):    
        user = User(**validated_data)
        
        user.set_password(validated_data['password'])
                
        #Save to the database
        user.save()
        
        #Create Organization instance
        first_name = validated_data['firstName']
        new_organization = user.organisation.create(name=f"{first_name}'s Organisation")
        
        user.organisation.add(new_organization)
        
        return user
       
    
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'password', 'phone', 'userToken']
       

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(allow_blank=False)
    password = serializers.CharField(write_only=True, allow_blank=False)  
    
    class Meta:
        model = User
        fields = ['userId','firstName', 'password','lastName', 'email', 'phone', 'userToken']
        read_only_fields = ['password', 'userToken']
        
        
class CreateOrganisationSerializer(serializers.Serializer):
    orgId = serializers.CharField(read_only=True)
    name = serializers.CharField(allow_blank=False)
    description = serializers.CharField(allow_blank=True)
    
    class Meta:
        model = Organisation
        fields = ['orgId','name','description']