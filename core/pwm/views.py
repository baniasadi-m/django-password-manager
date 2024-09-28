from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import render,HttpResponse,redirect
from django.views.generic.base import TemplateView,RedirectView
from django.views.generic import View,FormView,CreateView,ListView,DetailView
from .forms import OTPVerificationForm, ProfileUserForm, UserRegisterForm, UserForm, ProfileForm, ResetPasswordForm, MobileForm, UserStatusForm
from accounts.models.profiles import Profile
from accounts.models.users import UserTOTP,User
from .models import WinServer
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import license_check,generate_otp,send_sms,ad_search_and_reset_password, ad_enable_and_unlock_user,ad_get_user_account_status,reset_local_user_password
from .utils import WorkingHoursMixin, VerifiedUserMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib import messages
from accounts.totp_utils import verify_totp_code
import pyotp
import qrcode
from io import BytesIO


# Create your views here.

class MobileCheckView(LoginRequiredMixin,WorkingHoursMixin,View):
    template_name = "pwm/mobile_check.html"
    # form_class = MobileForm
    success_url = reverse_lazy('pwm:verifymobile')
    def get(self, request, *args, **kwargs):
        # profile = get_object_or_404(Profile,user=request.user)
        user_form = MobileForm(instance=request.user)
        context = {
            'form': user_form
        }
        return render(request=request,template_name=self.template_name,context=context)
    
    def post(self, request, *args, **kwargs):
        request_data = {k:v[0] for k,v in dict(request.POST).items()}
        print("POST CHECK VIEW",request_data)
        
        profile = get_object_or_404(Profile,user=request.user)
        print(profile,profile.mobile,request_data['mobile'])
        
        print("VERIFICATION MOBILE IS:",profile.mobile == request_data['mobile'])

        if profile.mobile == request_data['mobile']:
           # profile = profile_form.save()
           otp = str(generate_otp(5))
           if send_sms(_from='50005',to=f"{profile.mobile}",msg = otp):
               
               request.session['sms_otp'] = otp
               print(request.session)
               return redirect('pwm:verifymobile')
        
        messages.add_message(request,messages.ERROR,'Mobile Not valid')
        return  redirect('pwm:dashboard')
    
    
class MobileVerifyView(LoginRequiredMixin,WorkingHoursMixin,View):
    template_name = "pwm/mobile_verify.html"
    # form_class = OTPVerificationForm
    # success_url = reverse_lazy('pwm:dashboard')
    def get(self, request, *args, **kwargs):
        # profile = get_object_or_404(Profile,user=request.user)
        otp_form = OTPVerificationForm()
        context = {
            'form': otp_form
        }
        print(request.session.get('sms_otp'))
        return render(request=request,template_name=self.template_name,context=context)
    
    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile,user=request.user)
        # profile_form = ProfileForm(data=request.POST,instance=profile)
        request_data = {k:v[0] for k,v in dict(request.POST).items()}
        print("Verifi View",profile,request_data)
        generated_otp = request.session.get('sms_otp')
        print(str(generated_otp),str(request_data['otp']))

        if str(generated_otp) == request_data['otp']:
            profile.user.is_verified = True
            profile.user.save()
            request.session.pop('sms_otp')
            messages.add_message(request,messages.SUCCESS,'Profile Verified Successfully')
            return redirect('pwm:dashboard')
        
        messages.add_message(request,messages.ERROR,'form inputs not valid')
        return  redirect('pwm:dashboard')    
    
    
    
    # def get(self,request,*args, **kwargs):
    #     profile = get_object_or_404(Profile,user=request.user)
    #     user_form = MobileForm(instance=request.user)
    #     # Get the phone number from the form
    #     # phone_number = form.cleaned_data.get('mobile')
        
    #     # Generate a random 6-digit OTP
    #     otp = generate_otp(5)
        
    #     # Save the OTP and phone number in the session
    #     self.request.session['phone_number'] = phone_number
    #     self.request.session['otp'] = str(otp)

        # Save to database (optional)
        # PhoneVerification.objects.update_or_create(
        #     phone_number=phone_number,
        #     defaults={'otp': otp, 'verified': False}
        # )

        # Send OTP via SMS using Twilio or another SMS service
        # self.send_sms_otp(phone_number, otp)

        # Redirect to OTP verification page
        # return super().form_valid(form)
    
    # def send_sms_otp(self, phone_number, otp):
    #     # Twilio credentials from settings
    #     account_sid = settings.TWILIO_ACCOUNT_SID
    #     auth_token = settings.TWILIO_AUTH_TOKEN
    #     twilio_phone_number = settings.TWILIO_PHONE_NUMBER

    #     # Create Twilio client
    #     client = Client(account_sid, auth_token)

    #     # Send the SMS
    #     message = client.messages.create(
    #         body=f"Your verification code is {otp}",
    #         from_=twilio_phone_number,
    #         to=phone_number
    #     )
class EditProfileView(LoginRequiredMixin,VerifiedUserMixin,WorkingHoursMixin,View):
    template_name='pwm/profileedit.html'
    success_url = reverse_lazy('pwm:dashboard')
    
    def get(self,request,*args, **kwargs):
        # Initial data for the forms
        # print(request.profile)
        profile = get_object_or_404(Profile,user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
        # print(profile_form)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })
   
    def post(self,request,*args, **kwargs):
        # Handling form submissions
        print(request.user)
        profile = get_object_or_404(Profile,user=request.user)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(data=request.POST,files=request.FILES, instance=profile)
        print(f"profile validation is: {profile_form.is_valid()}")

        if  profile_form.is_valid():
            # user_form.save()
            print(f"profile save")
            profile_form.save()
            return redirect(self.success_url)

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

class IndexView(WorkingHoursMixin,RedirectView):
    permanent = False
    query_string = False
    pattern_name = 'pwm:dashboard'


# class IndexView(WorkingHoursMixin,View):
#     template_name = 'pwm/login.html'
#     form_class = LoginForm
    
#     def dispatch(self, request, *args, **kwargs):
#         if not self.check_working_hours():
#             return HttpResponseForbidden("The application is closed at the moment.")
#         return super().dispatch(request, *args, **kwargs)
    
#     def get(self, request):
#         form = self.form_class
#         return render(request, self.template_name,context={'form': form})

class UserRegisterView(WorkingHoursMixin,CreateView):
    template_name = 'pwm/register_user.html'
    success_url = reverse_lazy('pwm:register_profile')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"
    def dispatch(self, request, *args, **kwargs):
        print("FLDSKFKDFKSDFKSDKFKSDKSDFKSDKFSDKFKSDKFSDKFSDK")

        if not self.check_working_hours():
            return HttpResponseForbidden("The application is closed at the moment.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        print("FLDSKFKDFKSDFKSDKFKSDKSDFKSDKFSDKFKSDKFSDKFSDK")
        self.request.session['user_id'] = user.id
        return super().form_valid(form)

class ProfileRegisterView(WorkingHoursMixin,View):
    template_name = 'pwm/register_profile.html'
    success_url = reverse_lazy('pwm:login')

    def dispatch(self, request, *args, **kwargs):
        if not self.check_working_hours():
            return HttpResponseForbidden("The application is closed at the moment.")
        return super().dispatch(request, *args, **kwargs)
 
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        profile = get_object_or_404(Profile,user=user_id)
        profile_form = ProfileForm(instance=profile)
        context = {
            'profile_form': profile_form
        }
        return render(request=request,template_name=self.template_name,context=context)
    
    def post(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        profile = get_object_or_404(Profile,user=user_id)
        profile_form = ProfileForm(data=request.POST,instance=profile)

        if profile_form.is_valid():
            profile = profile_form.save()
            request.session.pop('user_id')
            return redirect('pwm:login')
        
        messages.add_message(request,messages.ERROR,'form inputs not valid')
        return  redirect('pwm:register')


class DashboardView(LoginRequiredMixin,WorkingHoursMixin,ListView):
    model= Profile
    context_object_name = 'profile'
    template_name = 'pwm/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):

        if self.check_working_hours()[0] == False:
            return self.check_working_hours()[1]
        return super().dispatch(request, *args, **kwargs)
    # def dispatch(self, request, *args, **kwargs):
    #     if not license_check():
    #     # If the condition is not met, return a response
    #         return HttpResponseForbidden("You are License Expired.")
    #     return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Profile.objects.get(user=self.request.user.id)

class ServerDetailView(LoginRequiredMixin,WorkingHoursMixin,DetailView):
    pass
class UserStatusView(LoginRequiredMixin,WorkingHoursMixin,View):
    success_url=reverse_lazy('pwm:resetpass_success')
    template_name = 'pwm/user_status.html'
    context_object_name = 'profile'
    
    def dispatch(self, request, *args, **kwargs):

        if self.check_working_hours()[0] == False:
            return self.check_working_hours()[1]
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args, **kwargs):
        profile = get_object_or_404(Profile,user=request.user)
        profile_form = ProfileUserForm(instance=profile)
        server = get_object_or_404(WinServer,is_ldap=True)
        server_form  = UserStatusForm(instance=server)
        # ad_get_user_account_status(ldap_server=f"ldaps://{server.ip}:{server.port}",domain= server.ldap_domain,
        #                                     admin_user=server.proxy_user,admin_password=server.proxy_password,base_dn=f"{server.base_dn}",
        #                                     username=f"{request_data['account']}",new_password=request_data['password1']
        #                                     )
        context ={'form':server_form,
                  'profile' : profile_form
                  }
        return render(request,self.template_name,context=context)
class ResetPassSuccessView(LoginRequiredMixin, VerifiedUserMixin, WorkingHoursMixin,TemplateView):
    template_name = "pwm/resetpass_success.html"
    
class ResetPassView(LoginRequiredMixin,VerifiedUserMixin,WorkingHoursMixin,View):
    success_url=reverse_lazy('pwm:resetpass_success')
    template_name = 'pwm/resetpass.html'
    # form_class=ServerSelectionForm
    def get(self,request,*args, **kwargs):
        # Initial data for the forms
        # print(request.profile)
        profile = get_object_or_404(UserTOTP,user=request.user)
        print(profile.totp_secret)
        user_form = ResetPasswordForm
        
        # print(profile_form)
        return render(request, self.template_name, {
            'form': user_form,
        })
   
    def post(self,request,*args, **kwargs):
        # Handling form submissions
        request_data = {k:v[0] for k,v in dict(request.POST).items()}
        print(request.user,request_data)
        profile = get_object_or_404(Profile,user=request.user)
        if request_data['password1'] != request_data['password2']:
            messages.add_message(request,messages.ERROR,'password confirm error')
            return  redirect('pwm:resetpass')
        
        otp_user = get_object_or_404(UserTOTP,user=request.user)
        if not verify_totp_code(secret=otp_user.totp_secret, code=request_data['otp']):
            messages.add_message(request,messages.ERROR,'Otp verify error')
            return  redirect('pwm:resetpass') 
        
        server = get_object_or_404(WinServer,pk=request_data['server'])
        if not server.is_enabled:
            messages.add_message(request,messages.ERROR,'server disabled')
            return  redirect('pwm:resetpass')
        if server.is_ldap:
            if not profile.win_ldap_account == request_data['account']:
                messages.add_message(request,messages.ERROR,'your server/user entered not valid')
                return  redirect('pwm:resetpass')
            reset_pass = ad_search_and_reset_password(ldap_server=f"ldaps://{server.ip}:{server.port}",domain= server.ldap_domain,
                                            admin_user=server.proxy_user,admin_password=server.proxy_password,base_dn=f"{server.base_dn}",
                                            username=f"{request_data['account']}",new_password=request_data['password1']
                                            )
            enable = ad_enable_and_unlock_user(ldap_url=f"ldaps://{server.ip}:{server.port}",domain= server.ldap_domain,
                                            admin_user=server.proxy_user,admin_password=server.proxy_password,
                                            search_base=f"{server.base_dn}",
                                            username=f"{request_data['account']}"
                                            )
            if reset_pass and enable[0]:
                messages.add_message(request=request,level=messages.SUCCESS,message='Reset Password Successful')
                return redirect(self.success_url)
            else:
                messages.add_message(request=request,level=messages.ERROR,message='Reset Password Failed')
                return redirect(self.success_url)         
        else:
            if not profile.win_local_account == request_data['account']:
                messages.add_message(request,messages.ERROR,'your server/user entered not valid')
                return  redirect('pwm:resetpass')   
            
            reset_pass = reset_local_user_password(remote_host=server.ip,admin_user=server.proxy_user,admin_password=server.proxy_password,target_user=f"{request_data['account']}",new_password=f"{request_data['password1']}")               
            if reset_pass[0]:
                messages.add_message(request=request,level=messages.SUCCESS,message='Reset Password Successful')
                return redirect(self.success_url)
            else:
                messages.add_message(request,messages.ERROR,'Reset Password Failed')
                return  redirect('pwm:resetpass')                

                   
        # user_form = UserForm(request.POST, instance=request.user)
        # profile_form = ProfileForm(data=request.POST,files=request.FILES, instance=profile)
        # print(f"profile validation is: {profile_form.is_valid()}")

        # if  profile_form.is_valid():
        #     # user_form.save()
        #     print(f"profile save")
        #     profile_form.save()
        

        # return render(request, self.template_name, {
        #     'user_form': user_form,
        #     'profile_form': profile_form
        # })








