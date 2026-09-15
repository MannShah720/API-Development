from dotenv import load_dotenv
import os
from fastapi import FastAPI, Response, Body, status, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# .env details
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
        
    except Exception as error:
        print("Database connection failed")
        print("Error:", error)
        time.sleep(2)


my_posts = [
    {"title": "post 1", "content": "content of post 1", "id": 1},
    {"title": "post 2", "content": "content of post 2", "id": 2}
]

def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post

@app.get("/")
def root():
    return {"message": "Welcome to my api"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = random.randint(1, 1000000)
    my_posts.append(post_dict)
    return {"new_post": post_dict}

@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    my_posts.remove(post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    post_index = my_posts.index(post)
    updated_post_dict = updated_post.dict()
    updated_post_dict['id'] = id
    my_posts[post_index] = updated_post_dict
    return {"updated_post": updated_post_dict}