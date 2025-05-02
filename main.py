#import libraries
from exa_py import Exa
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from config import EXA_API_KEY
from colorama import init, Fore, Style


#Initialize colorama for colored output 
init(autoreset=True)


#Initialize Exa with API key
exa = Exa(EXA_API_KEY)


#Prompt for user input
query = input(f'{Fore.YELLOW}Search here:{Style.RESET_ALL} ')

response = exa.search (
    query,
    num_results=7,
    type = 'neural',
    include_domains=['https://umich.edu', 
                   'lib.umich.edu', 
                   'lsa.umich.edu', 
                   'engin.umich.edu', 
                   'medicine.umich.edu', 
                   'law.umich.edu', 
                   'ross.umich.edu', 
                   'mcubed.umich.edu', 
                   'isr.umich.edu',
                   'ii.umich.edu',
                     'uofmhealth.org', 
                     'michmed.org',
                     'careercenter.umich.edu', 
                     'housing.umich.edu',
                    'pharmacy.umich.edu', 
                    'dental.umich.edu', 
                    'music.umich.edu', 
                    'sph.umich.edu',
                    'stamps.umich.edu', 
                    'education.umich.edu', 
                    'innovation.umich.edu', 
                    'arc.umich.edu',
                    'recsports.umich.edu', 
                    'dining.umich.edu', 
                    'studentlife.umich.edu',
                    'diversity.umich.edu', 
                    'michigandaily.com ', 
                    'michigantoday.umich.edu', 
                    'umpublichealth.edu', 
                     'alumni.umich.edu',
                    'leadersandbest.umich.edu',
                     'mgoblue.com',
                     'arts.umich.edu',
                    'quod.lib.umich.edu',
                    'publicengagement.umich.edu',
                    'research.umich.edu',
                    'research-compliance.umich.edu',
                    'hr.umich.edu',
                    'finance.umich.edu',
                     'global.umich.edu',
                    'mottchildren.org',
                    'mhealthy.umich.edu',
                    'studentaccountservices.umich.edu',
                    'deanofstudents.umich.edu',
                    'admissions.umich.edu',
                    'financialaid.umich.edu',
                    'registrar.umich.edu',
                       ]

)


#function to fetch and parse article content
def fetch_article_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join([para.get_text() for para in paragraphs])
        return article_text
    except Exception as e:  
        print(f"Error fetching article content: {e}") 
    

#function to summarize text using transformers
def summarize_text(text, max_length=250, min_length=100):
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    if len(text.split()) > max_length:
         text = ' '.join(text.split()[:max_length])
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

#print search results with summaries
for result in response.results:
  print(f'{Fore.BLUE}Title:{Style.RESET_ALL} {result.title}')
  print(f'{Fore.BLUE}URL:{Style.RESET_ALL} {result.url}\n')

#fetch and summarize article content
  article_content = fetch_article_content(result.url)
  if article_content:
         summary = summarize_text(article_content)
         if summary:
                print(f'{Fore.RED}Summary:{Style.RESET_ALL} {summary}\n')
         else:
                print(f'{Fore.YELLOW}Summary could not be generated.{Style.RESET_ALL}')