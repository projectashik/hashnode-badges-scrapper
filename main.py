from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
  "http://localhost:3000",
  "https://hashnode-cards.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def scrap_data(blog_handle):
  badges = []
  hashnode_url = "https://" + blog_handle + ".hashnode.dev/badges"
  request = requests.get(hashnode_url)
  soup = BeautifulSoup(request.content, 'html.parser')
  badges_wrapper = soup.find_all('div', {'class':"css-1hzbns5"})
  for badge in badges_wrapper:
    img = badge.find('img')
    name = badge.find('h1', {'class': "css-1h3au74"}).text
    badge_detail = {
      'logo': img['src'],
      'name': name
    }
    badges.append(badge_detail)
  
  return badges

def get_blog_handle(username):
  hashnode_query = """query($username: String!) {
      user(username: $username) {
        blogHandle,
      }
    }"""

  hashnode_variables = {
    'username': username
  }
  request = requests.post('https://api.hashnode.com', json={'query': hashnode_query, 'variables': hashnode_variables})
  user_data = request.json()
  if(user_data['data']):
    return user_data['data']['user']['blogHandle']
  

@app.post('/')
def index(username: str):
  blog_handle = get_blog_handle(username)
  if(blog_handle != None):
    return scrap_data(blog_handle)
  else:
    return {"error": "Username doesn't exists."}