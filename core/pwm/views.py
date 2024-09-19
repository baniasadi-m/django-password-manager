from typing import Any
from django.shortcuts import render,HttpResponse
from django.views.generic.base import TemplateView,RedirectView
from django.views.generic import View
from .forms import LoginForm
# Create your views here.



def index(request):
    return HttpResponse('Hello index fbv')


class LoginView(View):
    template_name = 'pwm/login.html'
    form_class = LoginForm
    
    def get(self, request):
        form = self.form_class
        return render(request, self.template_name,context={'form': form})



class IndexView(TemplateView):
    template_name= 'mba.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        context['name'] = 'javad'
        return context
    
class RedirecToMaktab(RedirectView):
    url = "https://maktabkhooneh.org"
    
    def get_redirect_url(self, *args, **kwargs):
        return super().get_redirect_url(*args, **kwargs)
