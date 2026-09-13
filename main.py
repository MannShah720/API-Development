from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
import random

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [
    {"title": "post 1", "content": "content of post 1", "id": 1},
    {"title": "post 2", "content": "content of post 2", "id": 2}
]

@app.get("/")
def root():
    return {"message": "Welcome to my api"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts")
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = random.randint(1, 1000000)
    my_posts.append(post_dict)
    return {"new_post": post_dict}

@app.get("/posts/{id}")
def get_post(id: int):
    post = next((post for post in my_posts if post['id'] == id), None)
    if not post:
        return {"error": "Post not found"}
    return {"post_detail": post}