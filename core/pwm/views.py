from typing import Any
from django.shortcuts import render,HttpResponse
from django.views.generic.base import TemplateView,RedirectView
# Create your views here.



def index(request):
    return HttpResponse('Hello index fbv')



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
