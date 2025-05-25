from flask import Flask, render_template, request, url_for, redirect
from exa_py import Exa
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
from config import EXA_API_KEY
import re
from markupsafe import Markup, escape
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def highlight(text, phrase):
    if not phrase:
        return escape(text)
    # Use regex to ignore case and only match full words
    pattern = re.compile(r'(' + re.escape(phrase) + r')', re.IGNORECASE)
    highlighted = pattern.sub(r'<mark>\1</mark>', escape(text))
    return Markup(highlighted)

app.jinja_env.filters['highlight'] = highlight

exa = Exa(EXA_API_KEY)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")



domain_map = {
    "all": [  # all 47 domains
        "umich.edu", "lib.umich.edu", "lsa.umich.edu", "engin.umich.edu",
        "medicine.umich.edu", "law.umich.edu", "ross.umich.edu", "mcubed.umich.edu",
        "isr.umich.edu", "ii.umich.edu", "uofmhealth.org", "michmed.org",
        "careercenter.umich.edu", "housing.umich.edu", "pharmacy.umich.edu",
        "dental.umich.edu", "music.umich.edu", "sph.umich.edu", "stamps.umich.edu",
        "education.umich.edu", "innovation.umich.edu", "arc.umich.edu", "recsports.umich.edu",
        "dining.umich.edu", "studentlife.umich.edu", "diversity.umich.edu", "michigandaily.com",
        "michigantoday.umich.edu", "umpublichealth.edu", "alumni.umich.edu",
        "leadersandbest.umich.edu", "mgoblue.com", "arts.umich.edu", "quod.lib.umich.edu",
        "publicengagement.umich.edu", "research.umich.edu", "research-compliance.umich.edu",
        "hr.umich.edu", "finance.umich.edu", "global.umich.edu", "mottchildren.org",
        "mhealthy.umich.edu", "studentaccountservices.umich.edu", "deanofstudents.umich.edu",
        "admissions.umich.edu", "financialaid.umich.edu", "registrar.umich.edu"
    ],
    "libraries": ["lib.umich.edu", "quod.lib.umich.edu"],
    "health": ["medicine.umich.edu", "michmed.org", "uofmhealth.org", "sph.umich.edu", "mottchildren.org", "mhealthy.umich.edu", "pharmacy.umich.edu", "dental.umich.edu"],
    "admissions": ["admissions.umich.edu", "registrar.umich.edu", "financialaid.umich.edu"],
    "housing": ["housing.umich.edu", "studentlife.umich.edu", "studentaccountservices.umich.edu", "dining.umich.edu", "recsports.umich.edu"],
    "athletics": ["mgoblue.com"],
    "studentlife": ["studentlife.umich.edu", "deanofstudents.umich.edu", "diversity.umich.edu", "careercenter.umich.edu"],
    "academics": ["lsa.umich.edu", "engin.umich.edu", "law.umich.edu", "ross.umich.edu", "music.umich.edu", "stamps.umich.edu", "education.umich.edu", "arts.umich.edu"],
    "research": ["research.umich.edu", "mcubed.umich.edu", "isr.umich.edu", "ii.umich.edu", "research-compliance.umich.edu", "innovation.umich.edu", "publicengagement.umich.edu"],
    "admin": ["hr.umich.edu", "finance.umich.edu", "global.umich.edu", "leadersandbest.umich.edu", "alumni.umich.edu"],
    "media": ["michigandaily.com", ]
}



def fetch_article_content(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs])
    except:
        return ""

def summarize_text(text):
    if len(text.split()) > 90:
        text = ' '.join(text.split()[:90])
    summary = summarizer(text, max_length=100, min_length=100, do_sample=False)
    return summary[0]['summary_text']

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    selected_category = "all"
    query = " "
    page = int(request.args.get('page', 1))
    per_page = 5

    if request.method == 'POST':
        query = request.form['query']
        selected_category = request.form['domain']
        return redirect(url_for('index', query=query, domain=selected_category, page=1))
    elif request.method == 'GET' and 'query' in request.args:
        query = request.args.get('query')
        selected_category = request.args.get('domain', 'all')
        domains = domain_map.get(selected_category, [])
        response = exa.search(query, num_results=10, type='neural', include_domains=domains)

        urls = [result.url for result in response.results]
        titles = [result.title for result in response.results]

        def process(url):
            article = fetch_article_content(url)
            return summarize_text(article) if article else "Summary unavailable."

        with ThreadPoolExecutor(max_workers=5) as executor:
            summaries = list(executor.map(process, urls))

        for title, url, summary in zip(titles, urls, summaries):
            results.append({
                'title': title,
                'url': url,
                'summary': summary
            })

    start = (page - 1) * per_page
    end = start + per_page
    paginated = results[start:end]

    return render_template('index.html', results=paginated, domain_filter=selected_category, query=query, page=page
                           ,has_more = len(results) > end)


if __name__ == '__main__':
    app.run(port=8000, debug=True)