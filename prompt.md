지금의 main.py는 다음과 같아
# test03/main.py

from fastapi import Depends, FastAPI, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
# fastapi 객체 생성
app = FastAPI()
# jinja2 템플릿 객체 생성 (templates 파일들이 어디에 있는지 알려야 한다.)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        # 응답에 필요한 data를 context로 전달 할 수 있다.
        context={
            "fortuneToday":"동쪽이 굳"
        }
    )

# get 방식 /post 요청 처리
@app.get("/post", response_class=HTMLResponse)
def getPosts(request: Request, db:Session = Depends(get_db)):
    # DB 에서 글목록을 가져오기 위한 sql 문 준비
    query = text("""
        SELECT num, writer, title, content, created_at
        FROM post
        ORDER BY num DESC
    """)
    # 글 목록을 얻어와사 
    result = db.execute(query)
    posts = result.fetchall()
    # 응답하기
    return templates.TemplateResponse(
        request=request,
        name="post/list.html", # templates/post/list.html jinja2 를 해석한 결과를 응답
        context={
            "posts":posts
        }
    )

@app.get("/post/new", response_class=HTMLResponse)
def postNewForm(request: Request):
    return templates.TemplateResponse(request=request, name="post/new-form.html")

@app.post("/post/new")
def postNew(writer: str = Form(...), title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    # DB에 저장할 SQL문 준비
    query = text("""
        INSERT INTO post
        (writer, title, content)
        VALUES(:writer, :title, :content)
        """)
    db.execute(query, {"writer":writer, "title":title, "content":content})
    db.commit()

    #특정 경로로 다시 응답하도록
    return RedirectResponse("/post", status_code=302)

지금 로우쿼리를 쓰면서 게시물을 보고, 새글을 등록하고 하고 있는데
이 코딩 스타일을 그대로 따르면서
게시물을 삭제하는 기능도 만들어줘.

