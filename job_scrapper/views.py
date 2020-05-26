from django.shortcuts import render
from scrapper.models import *


# Create your views here.

def index(request):
    jobs = Job.objects.all()
    
    return render(request, 'index.html', {'jobs' : jobs})