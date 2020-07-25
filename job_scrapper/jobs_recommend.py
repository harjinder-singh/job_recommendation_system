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

""" import s3fs
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
df = fp_obj.to_pandas() """
df = pd.read_csv(r'job_scrapper/jobsCanada.csv')
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
overall_skills_dict = program_languages + analysis_software + ml_framework + bigdata_tool + databases + ml_platform + methodology
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

    num_jobs_return = 10
    similarity = []
    if df.shape[0] < num_jobs_return:
        num_jobs_return = df.shape[0]
    for job_skills in df['keywords']:
        similarity.append(get_jaccard_sim(set(resume_keywords), set(job_skills)))
    df['similarity'] = similarity
    top_match = df.sort_values(by='similarity', ascending=False).head(num_jobs_return)
    # Return top matched jobs
    return top_match


