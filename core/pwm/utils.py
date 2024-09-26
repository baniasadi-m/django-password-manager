from .models import LicenseInfo,WorkingHours
from django.contrib.auth import get_user_model
from datetime import datetime
from django.http import HttpResponseForbidden
from django.shortcuts import redirect,render,HttpResponse


import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE
import ssl
import logging

import winrm

def reset_local_user_password(remote_host, admin_user, admin_password, target_user, new_password):
    """
    Resets the password for a local user on a remote Windows machine.

    :param remote_host: IP or hostname of the remote Windows machine
    :param username: Admin username for the remote machine
    :param password: Admin password for the remote machine
    :param target_user: Local username to reset the password for
    :param new_password: New password for the local user
    :return: None
    """
    winrm_url = f'http://{remote_host}:5985/wsman'

    # Initialize the WinRM session
    session = winrm.Session(winrm_url, auth=(admin_user, admin_password))

    # PowerShell command to reset the password
    ps_script = f"""
    
    $username = "{target_user}"
    $new_password = ConvertTo-SecureString "{new_password}" -AsPlainText -Force
    $user_account = Get-WmiObject -Class Win32_UserAccount -Filter "Name='$username'"
    $user_account.Rename("$username")
    $user_account.SetPassword($new_password)
    """

    # Execute the command
    result = session.run_ps(ps_script)

    if result.status_code == 0:
        message = f"Password for user '{target_user}' has been reset successfully."
        return True,message
    else:
        message = f"Failed to reset password for user '{target_user}': {result.std_err.decode()}"
        return False,message
# Configure logging
logging.basicConfig(level=logging.ERROR)  # Adjust as needed for debugging

def ad_search_and_reset_password(ldap_server, domain, base_dn, admin_user, admin_password,  username, new_password):
    try:
        # Create SSL context for secure LDAPS connection
        ssl_ctx = ssl.create_default_context()

        # Connect to the Active Directory server
        server = Server(ldap_server, use_ssl=True, get_info=ALL)
        
        # Authenticate with admin credentials
        conn = Connection(server, user=f'{admin_user}@{domain}', password=admin_password, auto_bind=True)
        
        # Search for the user by sAMAccountName (username)
        search_filter = f'(sAMAccountName={username})'
        
        conn.search(
            search_base=base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['distinguishedName']
        )

        # If no user is found, return False
        if not conn.entries:
            logging.error(f"User {username} not found.")
            return False

        # Get the user's distinguished name (DN)
        user_dn = conn.entries[0].distinguishedName.value
        print(f"User {username} found with DN: {user_dn}")

        # Encode the new password in UTF-16LE format with quotes
        unicode_password = ('"' + new_password + '"').encode('utf-16-le')
        try:

        # Reset the password by modifying the unicodePwd attribute
            conn.modify(user_dn, {'unicodePwd': [(MODIFY_REPLACE, [unicode_password])]})
        except Exception as e:
            print(e)
            exit(1)
        # Check if the operation was successful
        if conn.result['result'] == 0:
            print(f"Password reset successfully for {username}.")
            return True
        else:
            logging.error(f"Failed to reset password for {username}: {conn.result}")
            return False

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False

    finally:
        if conn:
            conn.unbind()
            
            
            
def ad_get_user_account_status(ldap_url, domain, search_base, admin_user, admin_password, username):
    """
    Retrieves the status of an Active Directory user account (password expired, account locked, account disabled).

    :param ldap_url: LDAP URL of the domain controller
    :param domain: Domain name
    :param search_base: Base DN for LDAP search, e.g., 'DC=domain,DC=com'
    :param username: sAMAccountName of the user to check
    :param admin_user: Admin username with domain
    :param admin_password: Admin password
    :return: Dictionary with status fields: 'password_expired', 'account_locked', 'account_disabled'
    """
    try:
        
    # Connect to the LDAP server
        server = ldap3.Server(ldap_url)
        conn = ldap3.Connection(server, user=f'{admin_user}@{domain}', password= admin_password, auto_bind=True)

        # Define the search filter
        search_filter = f'(sAMAccountName={username})'

        # Perform the search
        conn.search(search_base, search_filter, attributes=['pwdLastSet', 'lockoutTime', 'userAccountControl'])

        # Check the results
        if len(conn.entries) == 1:
            user = conn.entries[0]

            # Interpret attributes
            pwd_last_set = user.pwdLastSet.value
            lockout_time = user.lockoutTime.value
            user_account_control = user.userAccountControl.value

            # Determine statuses
            password_expired = pwd_last_set == '0'
            account_locked = lockout_time and lockout_time != '0'
            account_disabled = bool(int(user_account_control) & 0x0002)

            return {
            'password_expired': password_expired,
            'account_locked': account_locked,
            'account_disabled': account_disabled
            }
        else:
            raise ValueError("User does not exist or multiple accounts found.")

    except ldap3.LDAPExceptionError as e:
        print(f"LDAP error: {e}")
        return None
    finally:
        conn.unbind()
        
def ad_enable_and_unlock_user(ldap_url, domain, search_base, admin_user, admin_password, username):
    """
    Enables and unlocks an Active Directory user account.

    :param domain_controller: LDAP URL of the domain controller
    :param domain: Domain name
    :param search_base: Base DN for LDAP search, e.g., 'DC=domain,DC=com'
    :param username: sAMAccountName of the user to enable and unlock
    :param admin_user: Admin username with domain
    :param admin_password: Admin password
    :return: None
    """
    try:
        # Connect to the LDAP server
        server = ldap3.Server(ldap_url)
        conn = ldap3.Connection(server, user=f'{admin_user}@{domain}', password=admin_password, auto_bind=True)

        # Define the search filter
        search_filter = f'(sAMAccountName={username})'

        # Perform the search to get the user's DN and current userAccountControl value
        conn.search(search_base, search_filter, attributes=['distinguishedName', 'userAccountControl'])

        # Check the results
        if len(conn.entries) == 1:
            user_dn = conn.entries[0].distinguishedName.value
            user_account_control = conn.entries[0].userAccountControl.value

            # Convert userAccountControl to an integer
            user_account_control = int(user_account_control)

            # Clear the ACCOUNTDISABLE bit (0x0002) and LOCKOUT bit (0x0010)
            user_account_control = user_account_control & ~0x0002 & ~0x0010

            # Modify the user's userAccountControl attribute
            conn.modify(user_dn, {'userAccountControl': [(ldap3.MODIFY_REPLACE, [user_account_control])]})

            if conn.result['result'] == 0:
                message = f"The account '{username}' has been enabled and unlocked successfully."
                return True,message
            else:
                message = f"Failed to modify the account '{username}': {conn.result}"
                return False,message
        else:
            raise ValueError("User does not exist or multiple accounts found.")

    except ldap3.LDAPExceptionError as e:
        print(f"LDAP error: {e}")
        message = f"Exeption Error: {e}"
        return False,message
    finally:
        conn.unbind()



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

def generate_otp(number_of_digits):
    from random import choice
    import string
    otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
    return otp

def send_sms(_from,to,msg):
    return True
    
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
    