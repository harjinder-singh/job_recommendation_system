from django.shortcuts import render
from scrapper.models import *
from job_scrapper.jobs_recommend import *
from django.core.mail import send_mail
from django.conf import settings
from django.http.response import JsonResponse

# Create your views here.

def index(request):
    return render(request, 'index.html')

def job_recommendation(request):
    jobs = []
    if(request.POST):
        jobs = cal_similarity(request.POST['skills'].split(',') )
        jobs = jobs.to_numpy()
        exploratory_data_analysis()
    return render(request, 'job_recommend.html', {'jobs': jobs})

def email(request):
    name = request.POST['name']
    subject = request.POST['subject']
    message = request.POST['message']
    email_from = request.POST['email']
    recipient_list = ['job.recommendation.help@gmail.com',]
    send_mail( subject, 'Message received from '+ name + ' email: ' + email_from+ ' Message: '+ message, email_from, recipient_list )
    return JsonResponse({'success':'OK', 'ok': 'ok'})