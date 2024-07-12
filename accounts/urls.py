from django.urls import path
from . import views



urlpatterns = [
    path('auth/register', views.RegisterUser.as_view(), name='register' ),
    path('auth/login', views.LoginUser.as_view(), name='login' ),
    path('user/token', views.TokenAPI.as_view(), name='user-token'),
    path('api/users/<int:id>', views.RetrieveUserRecord.as_view(), name='user-record'),
    # path('api/organisations', views.RetrieveOrganisationAPI.as_view(), name='user-record'),
    path('api/organisations', views.retrieve_organisations, name='users'),
    path('api/organisations/<int:orgId>', views.retrieve_organisation_by_id, name='organisation-record'),
    path('api/organisations/<int:orgId>/users', views.add_user_to_organisation, name='add-user')
]