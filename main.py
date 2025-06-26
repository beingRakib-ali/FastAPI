from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engin,sessionlocal
from sqlalchemy.orm import Session
import auth
from auth import get_current_user

app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engin)


class ChoiceBase(BaseModel):
    
    choice_text : str
    is_correct: bool
  

class QuestionBase(BaseModel):

    question_text: str
    choices: List[ChoiceBase]

class UsersBase(BaseModel):
    username: str
    hashed_password: str

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
db_dependency_user = Annotated[dict,Depends(get_current_user)]



@app.get('/')
async def user(db:db_dependency,user:db_dependency_user):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    return {"User": user}






@app.get('/get_All_questions/')
async def get_All_question(db:db_dependency):
    result = db.query(models.Question).all()
    if not result:
        raise HTTPException(status_code=404,detail="Question not found")
    return result


@app.get('/get_single_questions/{question_id}')

async def get_question(question_id:int, db:db_dependency):
    result = db.query(models.Question).filter(models.Question.id==question_id).first()
    if not result:
        raise HTTPException(status_code=404,detail="Question not found")
    return result


@app.put('/questions/{question_id}')
async def update_question(question_id: int, updated_data: QuestionBase, db: db_dependency):
    # Find the question
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Update question text
    question.question_text = updated_data.question_text
    db.commit()

    # Update each choice
    for updated_choice in updated_data.choices:
        choice = db.query(models.Choice).filter(models.Choice.question_id == question_id).first()
        if choice:
            choice.choice_text = updated_choice.choice_text
            choice.is_correct = updated_choice.is_correct
    db.commit()

    return {"message": "Question updated successfully"}


@app.get('/choice/{question_id}')
async def get_Choice(question_id:int , db:db_dependency):
    result = db.query(models.Choice).filter(models.Choice.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choice not found")
    return result

@app.get('/get_All_choice/')
async def get_Choice(db:db_dependency):
    result = db.query(models.Choice).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choice not found")
    return result


@app.post('/Insert_questions/')
async def create_questions(question: QuestionBase, db: db_dependency):
    db_question = models.Question(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = models.Choice(choice_text = choice.choice_text, is_correct = choice.is_correct, question_id = db_question.id)
        db.add(db_choice)
    db.commit()



@app.delete('/questions/{question_id}')

async def delete_question(question_id:int, db:db_dependency):
    db.query(models.Choice).filter(models.Choice.question_id == question_id).delete()
    result = db.query(models.Question).filter(models.Question.id==question_id).first()
    if not result:
        raise HTTPException(status_code=404,detail="Question not found")
    db.delete(result)
    db.commit()

    return result

