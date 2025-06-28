import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://postgres:root@localhost:5432/QuizApplicationYT"
)
engin = create_engine(URL_DATABASE)
sessionlocal = sessionmaker(autoflush=False, autocommit = False, bind=engin)
Base = declarative_base()
