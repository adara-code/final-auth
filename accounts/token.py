from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header,BaseAuthentication
from decouple import config
import jwt
from .models import User

class UserAuth(BaseAuthentication):
    def authenticate(self, request ):
        auth_header = get_authorization_header(request)
        auth_data = auth_header.decode('utf-8')
        auth_token=auth_data.split(" ")
        
        if len(auth_token) != 2:
            raise exceptions.AuthenticationFailed('Invalid Token')
        
        token= auth_token[1]
        
        try:
            payload = jwt.decode(
                token,
                config('JWT_SECRET_KEY'),
                algorithms='HS256'
            )
            user_id = payload['userId']
            
            user=User.objects.get(userId=user_id)
            
            return (user, token)
        
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User does not exist')
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token Expired')
        
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Tampered token')
        