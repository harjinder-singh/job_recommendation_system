from django.shortcuts import render
from scrapper.models import *

from job_scrapper.jobs_recommend import *


# Create your views here.

def index(request):
    jobs = []
    if(request.POST):
        jobs = cal_similarity(request.POST['skills'].split(',') )
        jobs = jobs.to_numpy()
    import pdb; pdb.set_trace();
    return render(request, 'index.html', {'jobs': jobs})
