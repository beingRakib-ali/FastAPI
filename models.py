from sqlalchemy import Column, Integer, String, ForeignKey,Boolean
from sqlalchemy.orm import sessionmaker
from database import Base


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer,primary_key=True,index=True)
    question_text = Column(String,index=True)


class Choice(Base):
    __tablename__ = 'choices'

    id = Column(Integer,primary_key=True,index=True)
    choice_text = Column(String,index= True)
    is_correct = Column(Boolean,default= False)
    question_id = Column(Integer, ForeignKey("questions.id"))


class Users(Base):
    __tablename__='users'
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    hashed_password = Column(String)