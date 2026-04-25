from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from app.database import engine,Base,get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title = "Blog API",version = "1.0")

@app.get('/')
def root():
	return {"message":"Welcome to the Blog API!"}

@app.post('/user/', response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
	db_user = User(username=user.username,email=user.email, password=user.password)
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

@app.get("/user")
def list_users(db: Session = Depends(get_db)):
	users = db.query(User).all()
	return users
