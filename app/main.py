from dotenv import load_dotenv
import os
from fastapi import FastAPI, Response, Body, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from . database import engine, get_db

# .env details
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

# Database connection
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

# Root
@app.get("/")
def root():
    return {"message": "Welcome to my api"}

# Get all posts
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

# Create a new post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}

# Get a single post by id
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    
    return {"post_detail": post}

# Delete a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    post.delete(synchronize_session=False)

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update a post
@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return {"updated_post": post_query.first()}