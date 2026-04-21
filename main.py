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
def postNew(request: Request, writer: str = Form(...), title: str = Form(...), content: str = Form(...),
            db: Session = Depends(get_db)):
    # DB 에 저장할 sql 문  준비
    query = text("""
        INSERT INTO post
        (writer, title, content)
        VALUES(:writer, :title, :content)
    """)
    # query 문을 실행하면서 같이 전달한 dict 의 키값과  :writer , :title, :content 동일한 위치에 값이 바인딩되어서 실행된다.
    db.execute(query, {"writer":writer, "title":title, "content":content})
    db.commit()

    # 특정 경로로 요청을 다시 하도록 리다일렉트 응답을 준다. 
    return templates.TemplateResponse(
        request=request, 
        name="post/alert.html",
        context={
            "msg":"글 정보를 추가 했습니다!",
            "url":"/post"
        }
    )

@app.get("/post/delete")
def postDelete(num: int = Query(...), db: Session = Depends(get_db)):
    # DB에서 글을 삭제하기 위한 sql 문 준비
    query = text("""
        DELETE FROM post
        WHERE num = :num
    """)
    # SQL 실행
    db.execute(query, {"num": num})
    db.commit()

    # 삭제 후 글 목록 페이지로 리다이렉트
    return RedirectResponse("/post", status_code=302)

@app.get("/post/edit", response_class=HTMLResponse)
def postEditForm(request: Request, num: int = Query(...), db: Session = Depends(get_db)):
    # 수정을 위해 기존 데이터를 가져옴
    query = text("SELECT num, writer, title, content FROM post WHERE num = :num")
    result = db.execute(query, {"num": num})
    post = result.fetchone()

    return templates.TemplateResponse(
        request=request,
        name="post/edit-form.html",
        context={"post": post}
    )

@app.post("/post/edit")
def postEdit(
    request: Request,
    num: int = Form(...),
    writer: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    # DB 내용을 업데이트하는 SQL문
    query = text("""
        UPDATE post
        SET writer = :writer, title = :title, content = :content
        WHERE num = :num
    """)
    db.execute(query, {"num": num, "writer": writer, "title": title, "content": content})
    db.commit()

    return templates.TemplateResponse(
        request=request, 
        name="post/alert.html",
        context={
            "msg":"글 정보를 수정 했습니다!",
            "url":"/post"
        }
    )

