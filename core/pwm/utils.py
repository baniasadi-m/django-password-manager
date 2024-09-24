from .models import LicenseInfo,WorkingHours
from django.contrib.auth import get_user_model
from datetime import datetime
from django.http import HttpResponseForbidden
from django.shortcuts import redirect,render,HttpResponse
def license_check():
    from datetime import datetime
    print("Checking License....")
    try:
        current_datetime = float(datetime.now().timestamp())
        latest_check = float(LicenseInfo.objects.values('latest_check').first()['latest_check'].timestamp())
        limit_users = int(LicenseInfo.objects.values('limit_user').first()['limit_user'])
        expire_datetime = float(LicenseInfo.objects.values('expired_at').first()['expired_at'].timestamp())
        
        users = get_user_model()
        current_users = int(users.objects.all().count())
        print(current_datetime,latest_check,abs(current_datetime - latest_check),current_datetime < latest_check)
        if abs(current_datetime - latest_check) > 36000.000000 or current_datetime < latest_check:
            return False
        if current_datetime > expire_datetime or current_users > limit_users:
            return False
        return True 
    except Exception as e:
        print(e)
        return False
class WorkingHoursMixin:
    """
    Mixin to check if the current time is within working hours based on the database.
    """
    def check_working_hours(self):
        print(license_check())
        if license_check() == False:
            return False,HttpResponseForbidden("Your License Expired.")
        print(datetime.now())
        current_datetime = datetime.now()
        current_time = current_datetime.time()
        current_day = current_datetime.weekday()  # Monday is 0, Sunday is 6

        # Fetch working hours from the database (assuming you have one set of working hours)
        working_hours = WorkingHours.objects.first()  # Get the first record or customize this logic

        if not working_hours:
            return False,HttpResponseForbidden("The application is closed at the moment.")  # If no working hours are set, return False

        # Check if the current day is in the list of working days
        working_days = list(map(int, working_hours.weekdays.split(',')))  # Convert to list of integers
        if current_day not in working_days:
            return False,HttpResponseForbidden("The application is closed at the moment.")

        # Check if the current time is within the working hours
        if not (working_hours.start_time <= current_time <= working_hours.end_time):
            return False,HttpResponseForbidden("The application is closed at the moment.")

        return True,HttpResponse("work fine")


class VerifiedUserMixin:
    """
    Mixin to check if the user is verified.
    If not verified, it redirects to a forbidden page or any other desired URL.
    """
    def dispatch(self, request, *args, **kwargs):
        if license_check() == False:
            return False,HttpResponseForbidden("Your License Expired.")
        # Check if the user is authenticated and verified
        if not request.user.is_authenticated:
            # If the user is not authenticated, redirect to the login page
            return redirect('pwm:dashboard')

        if not request.user.is_verified:
            # If the user is not verified, return a forbidden response or redirect
            return HttpResponseForbidden("You must verify your account to access this page.")
        
        # If everything is fine, proceed with the request
        return super().dispatch(request, *args, **kwargs)
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


    
def user_allowed(request,usergroup=[]):
    for g in usergroup:
        if request.user.groups.filter(name=f"{g}").exists():
            return True
    return False

def server_status(server_url):
    import requests
    headers={'Content-Type': 'application/json'}
    jwt_token = "jwt_gen_token()"
    headers.update(
        {
            'jwt': f"{jwt_token}"
        }
    )
    try:
        r = requests.get(url=server_url,headers=headers,verify=False,timeout=2).json()
        if int(r['status']) == 1:
            return True
    except Exception as e:
        print(e)
        return False