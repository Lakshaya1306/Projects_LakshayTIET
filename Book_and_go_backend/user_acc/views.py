from .models import user
from .serializers import UserSerializer

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse

from base64 import urlsafe_b64decode, urlsafe_b64encode

class UserSignupView(ListCreateAPIView):
    serializer_class = UserSerializer
    
    def post(self, request):
        """handles the signup request from the user 

        Args:
            request (rest_framework.request object):

        Returns:
            object: returns the current instance of the model after creating it in DB 
        """
        return self.create(request)

class UserLoginView(APIView):
    def post(self, request):
        """used for authenticating the user after checking the username and password entered by the user against the record present for the user in DB 
        And if the credentials are right it sets the refresh token in the cookies whereas access token is sent in JSON format. 
        
        Args:
            request (rest_framework.request object):

        Returns:
            response: A JSON containing access token if user is authenticated and message with the status code 
        """
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username = username, password = password)
        if user:
            user.last_login = now()
            user.save(update_fields=['last_login'])
            
            refresh = RefreshToken.for_user(user)
            response = Response({'access': str(refresh.access_token), 'message': 'Login Successfull :)'}, status = status.HTTP_200_OK)
            response.set_cookie(key="refresh_token", value= str(refresh), samesite="Lax", httponly=True, secure=True)
            return response
        else:
            return Response({'message':"user doesn't exist :("}, status=status.HTTP_404_NOT_FOUND)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        """handles the logout functionality for the user. If the refresh token is not yet expired it gets blacklisted and gets deleted from the cookie 

        Args:
            request (rest_framework.request object):

        Returns:
            response: A message and status code
        """
        refreshToken = request.COOKIES.get('refresh_token')
        
        if refreshToken:
            try:
                refreshToken = RefreshToken(refreshToken)
                refreshToken.blacklist()
            except TokenError:
                return Response({'message': "Invalid or Expired Token"}, status=status.HTTP_400_BAD_REQUEST)
            
            response = Response({'message':'Logout Successful, See you soon :)'}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            return response
        else:
            return Response({'message': 'Invalid or Missing Refresh Token'}, status=status.HTTP_400_BAD_REQUEST)

class UserChangePassword(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        """Handles the change password functionality for the user by receiving the old password then checking it and then saving the new password 

        Args:
            request (rest_framework.request object):

        Returns:
            response: A message with the current status and status code
        """
        oldPassword = request.data.get('oldpassword')
        newPassword = request.data.get('newpassword')
        
        usr = request.user
        print(usr)
        if usr.check_password(oldPassword):
            usr.set_password(newPassword)
            usr.save(update_fields=['password'])
            return Response({'message':['Password Changed!'], 'status':['Success']}, status=status.HTTP_200_OK)
        else:
            return Response({'message': ['invalid password given'], 'status': ['failure']}, status=status.HTTP_404_NOT_FOUND)

class UserForgotPassword(APIView):
    def post(self, request):
        """provides forgot password functionality to the user by providing the reset url in the response made up from user id and the token generated specifically for the user

        Args:
            request (rest_framework.request object):

        Returns:
            response: returns message and current status with the status code 
        """
        username = request.data.get('username')
        usr = user.objects.get(username = username)
        if usr:
            encoded_id = urlsafe_b64encode(str(usr.id).encode()).decode()
            token_obj = PasswordResetTokenGenerator()
            token = token_obj.make_token(usr)
            
            path = reverse('reset password', kwargs={'uidb64':encoded_id, 'token':token})
            url = request.build_absolute_uri(path)
            
            return Response({'reset_password_url': url, 'status': "Success"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': ["username is invalid/user doesn't exist!"], 'status':['Failure']}, status=status.HTTP_400_BAD_REQUEST)
        
class UserResetPassword(APIView):
    serializer_class = [UserSerializer]
    def post(self, request, uidb64, token):
        """resets the password for the user after validating the token and checking the id of the user after decoding it 

        Args:
            request (rest_framework.request object):
            uidb64 (class): encoded id for user id 
            token (PasswordResetTokenGenerator): An instance of Django's password reset token generator

        Returns:
            response: returns a message and current status with error(if any) with the status code 
        """
        try:
            userid = int(urlsafe_b64decode(uidb64).decode())
            usr = user.objects.get(id = userid)
            
            valid = PasswordResetTokenGenerator().check_token(usr, token)
            
            if valid:
                newpassword = request.data.get('newpassword')
                if not newpassword:
                    return Response({'message':["new password can't be empty"], 'status':['Failure']}, status=status.HTTP_400_BAD_REQUEST)
                usr.set_password(newpassword)
                usr.save(update_fields = ['password'])
                return Response({'message':['Password reset successful'], 'status':['success']}, status=status.HTTP_200_OK)
            else:
                return Response({'status':"Failure", 'message': 'Token Invalid'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status':"Failure", "message":"User not found", "errors":str(e)}, status=  status.HTTP_404_NOT_FOUND)
            