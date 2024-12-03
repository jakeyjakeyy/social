from rest_framework.views import APIView
from rest_framework.response import Response
from social import models
from rest_framework_simplejwt.authentication import JWTAuthentication


class Register(APIView):
    def post(self, request):
        data = request.data
        user = models.User.objects.create_user(
            username=data["username"],
            password=data["password"],
        )
        account = models.Account.objects.create(
            user=user,
            display_name=data["display_name"],
        )
        return Response({"message": "User created successfully"})
