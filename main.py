from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, status, Depends
import langchain_proj
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import models, tokens, oauth2
from database import engine
from sqlalchemy.orm import Session
from hashing import Hash
from database import get_db
from fastapi.middleware.cors import CORSMiddleware

bot = langchain_proj.bedrock_chatbot()

models.Base.metadata.create_all(engine)

myApp = FastAPI()

myApp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@myApp.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@myApp.get("/create_user")
def create_user(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})


@myApp.post("/user_db_entry")
def user_db_entry(db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    try:
        new_user = models.User(user_name=username, password=Hash.bcrypt(password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        res = { 'meta': { 'status': 200, }, }
        content = jsonable_encoder(res)
        return JSONResponse(content=content, status_code=200)
    except Exception as e:
        res = { 'meta': { 'status': 400, }, }
        content = jsonable_encoder(res)
        return JSONResponse(content=content, status_code=400)


@myApp.post("/token")
def fetch_token(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_name == username).first()
    if user and Hash.verify(user.password, password):
        access_token = tokens.create_access_token(data={"sub": user.user_name})
        return {"access_token": access_token, "token_type": "bearer"}
    res = { 'meta': { 'status': 400, }, }
    content = jsonable_encoder(res)
    return JSONResponse(content=content, status_code=400)


@myApp.get("/homepage")
def home_page(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


@myApp.post('/chat', dependencies=[Depends(oauth2.get_current_user)], status_code=200)
def chat(user_text = Form(...)):
    # text = bot(input = user_text)
    try:
        text = bot.run(user_text)
        return text
    except Exception as e:
        return e




