from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
origins = [
    "http://localhost:3000",
    "localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def scrap_data(blog_handle):
  badges = []
  print("Scraping Data for " + blog_handle)
  hashnode_url = "https://" + blog_handle + ".hashnode.dev/badges"
  request = requests.get(hashnode_url)
  soup = BeautifulSoup(request.content, 'html.parser')
  badges_wrapper = soup.find_all('div', {'class':"css-1hzbns5"})
  # print(badges_wrapper)
  for badge in badges_wrapper:
    name = badge.find('h1', {'class': "css-1h3au74"}).text
    # print(name)
    # print("\n")
    img = badge.find('img', {'alt': name})
    svg = badge.find('svg')

    def returnLogo():
      if(img):
        return img['src']
      else:
        return str(svg)
    # print(returnLogo())
    # print("\n")

    def checktype():
      if(img):
        return 'img'
      else:
        return 'svg'
    # print(checktype())
    # print("\n")
    badge_detail = {
      'logo': returnLogo(),
      'name': name,
      'type': checktype()
    }
    # print(badge_detail)
    # print("\n")
    badges.append(badge_detail)
  print(badges)
  return {
    "badges": badges
  }

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

class UsernameBody(BaseModel):
  username: str

@app.post('/')
def index(body: UsernameBody):
  blog_handle = get_blog_handle(body.username)
  if(blog_handle != None):
    return scrap_data(blog_handle)
  else:
    return {"error": "Username doesn't exists."}

@app.get('/')
def getIndex():
  return "Go to /docs."