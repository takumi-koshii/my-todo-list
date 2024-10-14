from fastapi import FastAPI, Depends, Query, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from hashlib import sha256

from settings import Session
from models import TodoListItem
from models import TodoListUser


class UserRequest(BaseModel):
    name: str = Query(..., max_length=64)
    new_name: str = Query(None, max_length=64)
    password: str = Query(..., max_length=64)
    new_password: str = Query(None, max_length=64)


class ItemRequest(BaseModel):
    title: str = Query(..., max_length=64)
    content: str = Query(None, max_length=1024)
    deadline: str = Query(None, max_length=16)


def session():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# コントローラ

SALT = "MyTodoList"
INVALID_USER_ID = -1

# ローカルでは FastAPI を利用する。将来的には AWS Lambda に移植する想定
app = FastAPI()


def get_user_id(
        name: str,
        password: str,
        db: Session):
    user = db.query(TodoListUser).filter(TodoListUser.name == name).first()
    if user is None:
        return INVALID_USER_ID

    salted = password + SALT
    hashed = sha256(salted.encode()).hexdigest()
    if hashed != user.password:
        return INVALID_USER_ID

    return user.id


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError):
    return JSONResponse(content=jsonable_encoder({"msg": exc}), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


# ユーザー

# ユーザー取得
@app.get("/user")
def get_user(
        request: UserRequest,
        db: Session = Depends(session)):
    name = request.name
    password = request.password
    user_id = get_user_id(name, password, db)
    if user_id == INVALID_USER_ID:
        user = TodoListUser(id=INVALID_USER_ID)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(user))
    else:
        user = db.query(TodoListUser).filter(TodoListUser.id == user_id).first()
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(user))


# ユーザー登録
@app.post("/user")
def post_user(
        request: UserRequest,
        db: Session = Depends(session)):
    name = request.name
    password = request.password
    user_already_registered = db.query(TodoListUser).filter(TodoListUser.name == name).first()
    if user_already_registered is not None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=jsonable_encoder({"msg": "user already registered"}))

    salted = password + SALT
    hashed = sha256(salted.encode()).hexdigest()
    new_user = TodoListUser(
        name=name,
        password=hashed
    )
    db.add(new_user)
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder({"id": new_user.id}))


# ユーザー更新
@app.put("/user")
def put_user(
        request: UserRequest,
        db: Session = Depends(session)):
    name = request.name
    old_password = request.password
    user_id = get_user_id(name, old_password, db)
    if user_id == INVALID_USER_ID:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder({"id": user_id}))

    user = db.query(TodoListUser).filter(TodoListUser.id == user_id).first()
    if request.new_name:
        user.name = request.new_name
    if request.new_password:
        salted = request.new_password + SALT
        hashed = sha256(salted.encode()).hexdigest()
        user.password = hashed

    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder({"id": user_id}))


# ユーザー削除
@app.delete("/user")
def delete_user(
        request: UserRequest,
        db: Session = Depends(session)):
    name = request.name
    password = request.password
    user_id = get_user_id(name, password, db)
    if user_id == INVALID_USER_ID:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder({"id": user_id}))

    items = db.query(TodoListItem).filter(TodoListItem.id == user_id)
    items.delete()
    users = db.query(TodoListUser).filter(TodoListUser.id == user_id)
    users.delete()
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder({"id": user_id}))


# アイテム

# Todo リストからアイテムを取得
@app.get("/item/{user_id}")
def get_item(
        user_id: int,
        item_id: int = None,
        search: str = Query(None, max_length=64),
        db: Session = Depends(session)):
    if item_id:
        result_set = db.query(TodoListItem).filter(TodoListItem.user_id == user_id).filter(
            TodoListItem.id == item_id).all()
    else:
        result_set = db.query(TodoListItem).filter(TodoListItem.user_id == user_id).all()

    if search:
        result_set = list(filter(lambda x: search.lower() in x.title.lower(), result_set))

    response_body = jsonable_encoder({"list": result_set})
    return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)


# Todo リストにアイテムを追加
@app.post("/item/{user_id}")
def post_item(
        user_id: int,
        request: ItemRequest,
        db: Session = Depends(session)):
    user = db.query(TodoListUser).filter(TodoListUser.id == user_id).first()
    if user is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder({"user_id": user_id}))

    item = TodoListItem(
        user_id=user_id,
        title=request.title,
        content=request.content,
        deadline=request.deadline
    )
    db.add(item)
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder({"user_id": user_id,
                                                                                  "id": item.id}))


# Todo リストのアイテムを更新
@app.put("/item/{user_id}/{item_id}")
def put_item(
        user_id: int,
        item_id: int,
        request: ItemRequest,
        db: Session = Depends(session)):
    user = db.query(TodoListUser).filter(TodoListUser.id == user_id).first()
    if user is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder({"user_id": user_id}))

    item = db.query(TodoListItem).filter(TodoListItem.user_id == user_id).filter(
        TodoListItem.id == item_id).first()
    if item is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder({"user_id": user_id,
                                                                                             "id": item_id}))
    item.title = request.title
    item.content = request.content
    item.deadline = request.deadline
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder({"user_id": user_id,
                                                                                  "id": item_id}))


# Todo リストのアイテムを削除
@app.delete("/item/{user_id}/{item_id}")
def delete_item(
        user_id: int,
        item_id: int,
        db: Session = Depends(session)):
    user = db.query(TodoListUser).filter(TodoListUser.id == user_id).first()
    if user is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder({"user_id": user_id}))

    items = db.query(TodoListItem).filter(TodoListItem.user_id == user_id).filter(
        TodoListItem.id == item_id)
    items.delete()
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder({"user_id": user_id,
                                                                                  "id": item_id}))
