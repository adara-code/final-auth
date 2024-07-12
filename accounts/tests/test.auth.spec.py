from django.urls import reverse
from .. views import RegisterUser
from ..models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, APIRequestFactory


class UserRegistrationTests(APITestCase):
    # def get_tokens_for_user(user):
    #     refresh = RefreshToken.for_user(user)

    #     return {
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token),
    #     }
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RegisterUser.as_view()
        self.url = reverse('register')
        
        self.user = User.objects.create(
            userId='d58bfd2a-5682-497e-ae4d-b0391f9e69e8',
            firstName='Jane',
            lastName='Doe',
            email='jane@doe.com',
            password='password',
            phone='123-346-35465'
            )
        self.token = UserRegistrationTests.get_tokens_for_user(self.user)
        
        return self.user
        
    def test_RegisterUser(self):
        new_user = {
            "firstName": "Hank",
            "lastName": "Rearden",
            "email": "hank@rearden.com",
            "password": "0908908",
            "phone": "1324-452-5463",
        }
        request = self.factory.post(self.url,new_user)
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
