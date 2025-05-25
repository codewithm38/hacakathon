import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from collections import Counter
import re
from datetime import datetime

def scrape_indeed_jobs(query='data scientist', location='United States', num_pages=5):
    jobs_list = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for page in range(num_pages):
        url = f'https://www.indeed.com/jobs?q={query.replace(" ", "+")}&l={location.replace(" ", "+")}&start={page*10}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        for card in job_cards:
            try:
                title = card.find('h2', class_='jobTitle').text.strip()
                company = card.find('span', class_='companyName').text.strip()
                location = card.find('div', class_='companyLocation').text.strip()
                description = card.find('div', class_='job-snippet').text.strip()
                date_posted = card.find('span', class_='date').text.strip()
                
                jobs_list.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'date_posted': date_posted,
                    'source': 'Indeed'
                })
            except AttributeError:
                continue
                
        time.sleep(2)  # Polite scraping
        
    return jobs_list

def scrape_linkedin_jobs(query='data scientist', location='United States', num_pages=5):
    jobs_list = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for page in range(num_pages):
        url = f'https://www.linkedin.com/jobs/search?keywords={query.replace(" ", "%20")}&location={location.replace(" ", "%20")}&start={page*25}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        job_cards = soup.find_all('div', class_='base-card')
        
        for card in job_cards:
            try:
                title = card.find('h3', class_='base-search-card__title').text.strip()
                company = card.find('h4', class_='base-search-card__subtitle').text.strip()
                location = card.find('span', class_='job-search-card__location').text.strip()
                date_posted = card.find('time')['datetime']
                
                jobs_list.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': '',  # LinkedIn requires additional requests for descriptions
                    'date_posted': date_posted,
                    'source': 'LinkedIn'
                })
            except (AttributeError, TypeError):
                continue
                
        time.sleep(2) 
        
    return jobs_list
indeed_jobs = scrape_indeed_jobs(num_pages=5)
linkedin_jobs = scrape_linkedin_jobs(num_pages=5)
all_jobs = indeed_jobs + linkedin_jobs
df = pd.DataFrame(all_jobs)

# Extract skills from job descriptions
common_skills = [
    'python', 'sql', 'aws', 'java', 'javascript', 'react', 'node', 'docker', 
    'kubernetes', 'machine learning', 'ai', 'data analysis', 'tableau', 'power bi',
    'excel', 'r', 'scala', 'hadoop', 'spark', 'tensorflow', 'pytorch', 'git',
    'agile', 'devops', 'cloud', 'azure', 'gcp', 'mongodb', 'postgresql'
]

def extract_skills(text):
    if not isinstance(text, str):
        return []
    text = text.lower()
    return [skill for skill in common_skills if skill in text]

df['skills'] = df['description'].apply(extract_skills)

df['city'] = df['location'].apply(lambda x: x.split(',')[0].strip())

top_cities = df['city'].value_counts().head(10)
top_titles = df['title'].value_counts().head(5)
top_companies = df['company'].value_counts().head(10)

all_skills = [skill for skills_list in df['skills'] for skill in skills_list]
skills_freq = pd.Series(Counter(all_skills)).sort_values(ascending=False).head(10)

fig1 = px.bar(top_titles,
              title='Top 5 Most In-Demand Job Titles',
              labels={'index': 'Job Title', 'value': 'Number of Openings'},
              template='plotly_white')

fig1.update_layout(
    xaxis_title="Job Title",
    yaxis_title="Number of Openings",
    showlegend=False,
    plot_bgcolor='white'
)

df[['title', 'company', 'location', 'source', 'date_posted', 'skills']]


##graphs code
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
data = {
    'title': [
        'Data Scientist', 'Software Engineer', 'Data Analyst', 'Product Manager', 'Data Engineer',
        'Data Scientist', 'Software Engineer', 'ML Engineer', 'Data Analyst', 'DevOps Engineer'
    ] * 5,
    'company': [
        'Google', 'Microsoft', 'Amazon', 'Facebook', 'Apple',
        'Netflix', 'Adobe', 'Intel', 'IBM', 'Oracle'
    ] * 5,
    'location': [
        'New York', 'San Francisco', 'Seattle', 'Boston', 'Chicago',
        'Austin', 'Los Angeles', 'Denver', 'Atlanta', 'Miami'
    ] * 5,
    'skills': [
        ['python', 'sql', 'machine learning'],
        ['java', 'python', 'aws'],
        ['sql', 'python', 'tableau'],
        ['agile', 'sql', 'excel'],
        ['python', 'spark', 'aws'],
        ['python', 'tensorflow', 'sql'],
        ['java', 'docker', 'kubernetes'],
        ['python', 'deep learning', 'pytorch'],
        ['sql', 'power bi', 'excel'],
        ['docker', 'kubernetes', 'aws']
    ] * 5
}

df = pd.DataFrame(data)

top_jobs = df['title'].value_counts().head(5)
top_locations = df['location'].value_counts().head(5)
all_skills = [skill for skills_list in df['skills'] for skill in skills_list]
top_skills = pd.Series(all_skills).value_counts().head(5)
top_companies = df['company'].value_counts().head(5)


fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Top 5 Job Titles',
        'Top 5 Skills in Demand',
        'Top 5 Hiring Cities',
        'Top 5 Hiring Companies'
    ),
    vertical_spacing=0.15,
    horizontal_spacing=0.1
)

colors = px.colors.qualitative.Set3

fig.add_trace(
    go.Bar(
        x=top_jobs.index,
        y=top_jobs.values,
        marker_color=colors[0],
        showlegend=False
    ),
    row=1, col=1
)


fig.add_trace(
    go.Bar(
        x=top_skills.index,
        y=top_skills.values,
        marker_color=colors[1],
        showlegend=False
    ),
    row=1, col=2
)


fig.add_trace(
    go.Bar(
        x=top_locations.index,
        y=top_locations.values,
        marker_color=colors[2],
        showlegend=False
    ),
    row=2, col=1
)

fig.add_trace(
    go.Bar(
        x=top_companies.index,
        y=top_companies.values,
        marker_color=colors[3],
        showlegend=False
    ),
    row=2, col=2
)


fig.update_layout(
    height=800,
    title={
        'text': "Job Market Analysis Dashboard",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24}
    },
    plot_bgcolor='white',
    showlegend=False
)


for i in fig['layout']['annotations']:
    i['font'] = dict(size=16, color='#0066cc')

fig.update_xaxes(
    tickangle=45,
    showgrid=True,
    gridwidth=1,
    gridcolor='#f0f0f0'
)

fig.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor='#f0f0f0'
)


fig.show()

# Return DataFrame for reference
df