from .models.users import UserActivityLog
from django.utils.timezone import now

class UserActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            # Get the user activity details
            user = request.user
            path = request.get_full_path()
            method = request.method
            ip_address = self.get_client_ip(request)

            # Save the activity to the database
            UserActivityLog.objects.create(
                user=user,
                path=path,
                method=method,
                ip_address=ip_address,
                timestamp=now(),
                action_description=f"User accessed {path} via {method}",
            )

        return response

    def get_client_ip(self, request):
        """Helper function to get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
