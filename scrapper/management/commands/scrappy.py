from django.core.management.base import BaseCommand
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
from scrapper.models import Job

class Command(BaseCommand):
    help = "collect jobs"    # define logic of command
    def handle(self, *args, **options):        # collect html
        for start in range(0, 200, 10):
            html = urlopen('https://ca.indeed.com/jobs?q=all+job+vacancies&l=Ontario&start='+ str(start))        # convert to soup
            soup = BeautifulSoup(html, 'html.parser')        # grab all postings
            postings = soup.find_all("div", class_="jobsearch-SerpJobCard")        
            
            for p in postings:
                url = p.find('a', class_='jobtitle').text
                title = p.find('a', class_='jobtitle').text
                location = p.find('', class_='location').text            # check if url in db
                try:
                    # save in db
                    Job.objects.create(
                        url=url,
                        title=title,
                        location=location
                    )
                    print('%s added' % (title,))
                except:
                    print('%s already exists' % (title,))        
        self.stdout.write( 'job complete' )