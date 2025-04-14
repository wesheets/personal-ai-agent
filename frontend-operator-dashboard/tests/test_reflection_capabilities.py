import os
import asyncio
import json
from dotenv import load_dotenv
from app.core.rationale_logger import get_rationale_logger
from app.core.self_evaluation import SelfEvaluationPrompt
from app.core.memory_context_reviewer import get_memory_context_reviewer
from app.core.task_tagger import get_task_tagger
from app.providers import process_with_model

# Load environment variables
load_dotenv()

async def test_reflection_capabilities():
    """Test the agent reflection and reasoning capabilities"""
    print("Testing Agent Reflection and Reasoning Capabilities")
    print("=" * 80)
    
    # Test data
    agent_type = "builder"
    model = "gpt-4"  # Use a smaller model for testing if needed
    input_text = "I need to create a REST API for a blog with users, posts, and comments."
    output_text = """
I'll help you create a REST API for a blog with users, posts, and comments. Here's a comprehensive approach:

## Data Models

```python
# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # Store hashed password
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
```

## API Endpoints with FastAPI

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud
from database import get_db
from auth import get_current_user

app = FastAPI(title="Blog API")

# User routes
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Post routes
@app.post("/posts/", response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    return crud.create_post(db=db, post=post, user_id=current_user.id)

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Comment routes
@app.post("/posts/{post_id}/comments/", response_model=schemas.Comment)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    return crud.create_comment(db=db, comment=comment, post_id=post_id, user_id=current_user.id)

@app.get("/posts/{post_id}/comments/", response_model=List[schemas.Comment])
def read_comments(post_id: int, db: Session = Depends(get_db)):
    comments = crud.get_comments_by_post(db, post_id=post_id)
    return comments
```

## Authentication with JWT

```python
# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
import schemas, crud

# Secret key and algorithm
SECRET_KEY = "your-secret-key"  # Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
```

## Database Setup

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
# For PostgreSQL: SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Schemas with Pydantic

```python
# schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Post schemas
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    author: User
    comments: List["Comment"] = []
    
    class Config:
        orm_mode = True

# Comment schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int
    user_id: int
    created_at: datetime
    author: User
    
    class Config:
        orm_mode = True

# Update Post schema references
Post.update_forward_refs()
```

## CRUD Operations

```python
# crud.py
from sqlalchemy.orm import Session
import models, schemas
from auth import get_password_hash

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Post operations
def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Comment operations
def get_comments_by_post(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

def create_comment(db: Session, comment: schemas.CommentCreate, post_id: int, user_id: int):
    db_comment = models.Comment(**comment.dict(), post_id=post_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
```

## Running the Application

```python
# Run with: uvicorn main:app --reload
```

This implementation provides a complete REST API for a blog with:
- User registration and authentication with JWT
- CRUD operations for posts and comments
- Proper relationships between users, posts, and comments
- Input validation with Pydantic
- SQLAlchemy ORM for database operations

You can extend this by adding:
- Pagination for posts and comments
- Search functionality
- User roles and permissions
- Post categories or tags
- API documentation with Swagger UI (built into FastAPI)

Let me know if you need any clarification or have specific requirements for your blog API!
"""
    
    print("\n1. Testing Rationale Generation")
    print("-" * 50)
    rationale_data = await SelfEvaluationPrompt.generate_rationale(
        model=model,
        agent_type=agent_type,
        input_text=input_text,
        output_text=output_text
    )
    
    print(f"Rationale: {rationale_data.get('rationale', '')[:200]}...")
    print(f"Assumptions: {rationale_data.get('assumptions', '')[:200]}...")
    print(f"Improvement Suggestions: {rationale_data.get('improvement_suggestions', '')[:200]}...")
    
    print("\n2. Testing Self-Evaluation")
    print("-" * 50)
    evaluation_data = await SelfEvaluationPrompt.generate_self_evaluation(
        model=model,
        agent_type=agent_type,
        input_text=input_text,
        output_text=output_text
    )
    
    print(f"Confidence Level: {evaluation_data.get('confidence_level', '')[:200]}...")
    print(f"Failure Points: {evaluation_data.get('failure_points', '')[:200]}...")
    
    print("\n3. Testing Memory Context Review")
    print("-" * 50)
    memory_reviewer = get_memory_context_reviewer()
    
    # First, we need to add a memory to test with
    from app.core.shared_memory import get_shared_memory
    shared_memory = get_shared_memory()
    
    # Add a test memory
    memory_id = await shared_memory.store_memory(
        content="The user previously asked about creating a REST API for a social media application with users, posts, and likes.",
        metadata={"agent_name": agent_type, "topic": "API development"},
        scope="agent",
        agent_name=agent_type,
        topics=["API", "development", "backend"]
    )
    
    # Now retrieve and analyze memories
    memory_analysis = await memory_reviewer.retrieve_and_analyze_memories(
        model=model,
        agent_type=agent_type,
        input_text=input_text
    )
    
    print(f"Memory Context: {memory_analysis.get('memory_context', '')[:200]}...")
    print(f"Memory Analysis: {memory_analysis.get('analysis', '')[:200]}...")
    
    print("\n4. Testing Task Tagging")
    print("-" * 50)
    task_tagger = get_task_tagger()
    
    task_metadata = await task_tagger.categorize_task(
        input_text=input_text,
        output_text=output_text,
        model=model
    )
    
    print(f"Task Category: {task_metadata.task_category}")
    print(f"Suggested Next Step: {task_metadata.suggested_next_step}")
    print(f"Priority: {task_metadata.priority}")
    print(f"Tags: {', '.join(task_metadata.tags)}")
    
    print("\n5. Testing Rationale Logging")
    print("-" * 50)
    rationale_logger = get_rationale_logger()
    
    rationale_log_id = await rationale_logger.log_rationale(
        agent_name=agent_type,
        input_text=input_text,
        output_text=output_text,
        rationale=rationale_data.get("rationale", ""),
        assumptions=rationale_data.get("assumptions", ""),
        improvement_suggestions=rationale_data.get("improvement_suggestions", ""),
        confidence_level=evaluation_data.get("confidence_level", ""),
        failure_points=evaluation_data.get("failure_points", ""),
        task_category=task_metadata.task_category,
        suggested_next_step=task_metadata.suggested_next_step,
        metadata={"test": True},
        execution_log_id="test-execution-log-id"
    )
    
    print(f"Rationale Log ID: {rationale_log_id}")
    
    # Retrieve the log to verify
    log_entry = await rationale_logger.get_rationale_log(rationale_log_id)
    print(f"Log Entry ID: {log_entry.get('id')}")
    print(f"Agent Name: {log_entry.get('agent_name')}")
    print(f"Task Category: {log_entry.get('task_metadata', {}).get('task_category')}")
    
    print("\nAll reflection capabilities tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_reflection_capabilities())
