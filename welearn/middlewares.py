# custom_user_middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import WeUser


class CustomUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Attach your custom user object to the request object
            # For example, you can attach the user object directly or any specific attributes
            try:
                we_user = WeUser.objects.get(id=request.user.id)
                request.we_user = we_user
            except WeUser.DoesNotExist:
                request.we_user = None

        else:
            # If the user is not authenticated, you can set the custom_user attribute to None or any other value
            request.we_user = None
