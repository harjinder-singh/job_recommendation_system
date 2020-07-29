#Keyword extraction function
import re
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
import PyPDF2
import config
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
#!conda install python-snappy --y
#!conda update -n base conda --y

import s3fs
import fastparquet as fp
s3 = s3fs.S3FileSystem()
fs = s3fs.core.S3FileSystem()

#mybucket/data_folder/serial_number=1/cur_date/abcdsd0324324.snappy.parquet
s3_path = "s3://capstone-s3/Jobs_Canada/part-*.parquet"
all_paths_from_s3 = fs.glob(path=s3_path)

myopen = s3.open
#use s3fs as the filesystem
fp_obj = fp.ParquetFile(all_paths_from_s3,open_with=myopen)
#convert to pandas dataframe
df = fp_obj.to_pandas()
#df = pd.read_csv(r'job_scrapper/jobsCanada.csv')
#Addind Index Column in data frame
df['idx'] = range(1, len(df) + 1)

#Creating words Dictionary
program_languages = ['bash','r','python','java','c++','ruby','perl','matlab','javascript','scala','php']
analysis_software = ['excel','tableau','sas','spss','d3','saas','pandas','numpy','scipy','sps','spotfire','scikit','splunk','power','h2o']
ml_framework = ['pytorch','tensorflow','caffe','caffe2','cntk','mxnet','paddle','keras','bigdl']
bigdata_tool = ['hadoop','mapreduce','spark','pig','hive','shark','oozie','zookeeper','flume','mahout','etl']
ml_platform = ['aws','azure','google','ibm']
methodology = ['agile','devops','scrum']
databases = ['sql','nosql','hbase','cassandra','mongodb','mysql','mssql','postgresql','oracle','rdbms','bigquery']
softwareskills = ['asp','sql','html','c#','web','vb','react','linux','oops','docker','django','tomcat','aqualogic','jboss','websphere','ssis','boomi',
'informatica','talend','ruby','css','node.js','angular','nginx','microservices','bitbucket','gitlab','github','wordpress','rest','soap','git','jenkins','kubernetes',
'openshift','jquery','bootstrap','d3','j2eee','ejb','jsp','servlets','jdbc','eclipse','jboss']
cloudskills =['saas','agile','devops','iot','oracle','dynambodb','cosmodb','cloud','sagemaker','glue','s3','efs','lambda','ethena','emr','cloudsearch','kinesis','vpc',
'route53','cloudfront','functionapp','databricks','blob','powerbi','tableau','cdn','terraform','azure sql','data factories','data lake analytics','azure blockchain service',
'logic apps','iaas','paas','dbaas','daas']


overall_skills_dict = program_languages + analysis_software + ml_framework + bigdata_tool + databases + ml_platform + methodology + softwareskills + cloudskills
education = ['master','phd','undergraduate','bachelor','mba']
overall_dict = overall_skills_dict + education

def keywords_extract(text):
       # Remove non-alphabet; 3 for d3.js and + for C++
    text = re.sub("[^a-zA-Z+3]", " ", text)
    text = text.lower().split()
    stops = set(stopwords.words("english"))  # filter out stop words in english language
    text = [w for w in text if not w in stops]
    text = list(set(text))
    # We only care keywords from the pre-defined skill dictionary
    keywords = [str(word) for word in text if word in overall_dict]
    return keywords

#creating new column in the dataframe
df['keywords'] = [keywords_extract(job_desc) for job_desc in df['description']]

#similarity function
def get_jaccard_sim(x_set, y_set):
    intersection = x_set.intersection(y_set)
    return float(len(intersection)) / (len(x_set) + len(y_set) - len(intersection))

def cal_similarity(resume_keywords):
    resume_keywords = [x.lower() for x in resume_keywords]
    num_jobs_return = 10
    similarity = []
    if df.shape[0] < num_jobs_return:
        num_jobs_return = df.shape[0]
    for job_skills in df['keywords']:
        job_skills = [x.lower() for x in job_skills]
        similarity.append(get_jaccard_sim(set(resume_keywords), set(job_skills)))
    df['similarity'] = similarity
    top_match = df.sort_values(by='similarity', ascending=False).head(num_jobs_return)
    # Return top matched jobs
    return top_match

def keywords_count( keywords, counter):
        '''
        Count frequency of keywords
        Input:
            keywords (list): list of keywords
            counter (Counter)
        Output:
            keyword_count (DataFrame index:keyword value:count)
        '''          
        keyword_count = pd.DataFrame(columns = ['Freq'])
        for each_word in keywords:
            keyword_count.loc[each_word] = {'Freq':counter[each_word]}
        return keyword_count

def exploratory_data_analysis():
        '''
        Exploratory data analysis
        Input:
            None
        Output:
            None
        '''        
        # Create a counter of keywords
        doc_freq = Counter()
        f = [doc_freq.update(item) for item in df['keywords']]
       
        # Let's look up our pre-defined skillset vocabulary in Counter
        overall_skills_df = keywords_count(overall_skills_dict, doc_freq)
        # Calculate percentage of required skills in all jobs
        overall_skills_df['Freq_perc'] = (overall_skills_df['Freq'])*100/df.shape[0]
        overall_skills_df = overall_skills_df.sort_values(by='Freq_perc', ascending=False)  
        # Make bar plot
        plt.figure(figsize=(14,8))
        overall_skills_df.iloc[0:30, overall_skills_df.columns.get_loc('Freq_perc')].plot.bar()
        plt.title('Percentage of Required Data Skills in Data Scientist/Engineer/Analyst Job Posts')
        plt.ylabel('Percentage Required in Jobs (%)')
        plt.xticks(rotation=30)
        plt.savefig('static/images/first.png')
       
        # Plot word cloud
        all_keywords_str = df['keywords'].apply(' '.join).str.cat(sep=' ')        
        # lower max_font_size, change the maximum number of word and lighten the background:
        wordcloud = WordCloud(background_color="white").generate(all_keywords_str)
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig('static/images/second.png')
         
        # Let's look up education requirements
        education_df = keywords_count(education, doc_freq)
        # Merge undergrad with bachelor
        education_df.loc['bachelor','Freq'] = education_df.loc['bachelor','Freq'] + education_df.loc['undergraduate','Freq']
        education_df.drop(labels='undergraduate', axis=0, inplace=True)
        # Calculate percentage of required skills in all jobs
        education_df['Freq_perc'] = (education_df['Freq'])*100/df.shape[0]
        education_df = education_df.sort_values(by='Freq_perc', ascending=False)  
        # Make bar plot
        plt.figure(figsize=(14,8))
        education_df['Freq_perc'].plot.bar()
        plt.title('Percentage of Required Education in Data Scientist/Engineer/Analyst Job Posts')
        plt.ylabel('Percentage Required in Jobs (%)')
        plt.xticks(rotation=0)
        plt.savefig('static/images/third.png')
       
        # Plot distributions of jobs posted in major cities
        plt.figure(figsize=(9,9))
        df['jobLocation'].value_counts().plot.pie(autopct='%1.1f%%', textprops={'fontsize': 10})
        #plt.title('Data Scientist/Engineer/Analyst Jobs in Major Canadian Cities \n\n Total {} posted jobs in last {} days'.format(df.shape[0]))
        plt.ylabel('')
        plt.savefig('static/images/fourth.png')


