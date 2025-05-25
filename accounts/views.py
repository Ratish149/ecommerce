from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import LoginSerializer

# Create your views here.


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)

                # Use check_password to verify the password
                if not user.check_password(password):
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

                # Password is correct, generate token
                token = RefreshToken.for_user(user)
                token['email'] = user.email
                token['first_name'] = user.first_name
                token['last_name'] = user.last_name
                token['phone'] = user.phone
                token['address'] = user.address

                # Return user data and tokens
                return Response({
                    'refresh': str(token),
                    'access': str(token.access_token),
                })

            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
