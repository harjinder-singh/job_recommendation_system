from django.shortcuts import render
from scrapper.models import *


# Create your views here.

def index(request):

    return render(request, 'index.html', {})