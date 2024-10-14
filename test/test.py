import requests
from hashlib import sha256
import json

HOST = "localhost"
PORT = 8000
HEADERS = {'Content-Type': 'application/json'}


def request_base_url():
    return f"http://{HOST}:{PORT}"


def get_response(url, code, json_data=None):
    if json_data is None:
        response = requests.get(url)
    else:
        response = requests.get(url, headers=HEADERS, data=json_data)
    assert response.status_code == code, f"status_code incorrect: {response.status_code}"
    return response.json()


def post_response(url, code, json_data):
    response = requests.post(url, headers=HEADERS, data=json_data)
    assert response.status_code == code, f"status_code incorrect: {response.status_code}"
    return response.json()


def put_response(url, code, json_data):
    response = requests.put(url, headers=HEADERS, data=json_data)
    assert response.status_code == code, f"status_code incorrect: {response.status_code}"
    return response.json()


def delete_response(url, code, json_data=None):
    if json_data is None:
        response = requests.delete(url)
    else:
        response = requests.delete(url, headers=HEADERS, data=json_data)
    assert response.status_code == code, f"status_code incorrect: {response.status_code}"
    return response.json()


SALT = "aaaaaaaaaa"
USERNAME = "testtesttest"
PASSWORD = sha256(("MyTodoListTest" + SALT).encode()).hexdigest()
ASSERT_MESSAGE = "invalid response"

# ユーザーを削除してテスト環境を初期化
user_url = request_base_url() + "/user"
json_data_user = json.dumps({
    "name": USERNAME,
    "password": PASSWORD,

})
requests.delete(user_url, headers=HEADERS, data=json_data_user).json()

# ユーザーを作成するテスト
body = post_response(user_url, 200, json_data_user)
assert 'id' in body, ASSERT_MESSAGE
user_id = body['id']  # 以降のテストのために user_id を覚えておく

# ユーザー名の重複
PASSWORD2 = sha256(("a" + SALT).encode()).hexdigest()
json_data_user2 = json.dumps({
    "name": USERNAME,
    "password": PASSWORD2,
})
body = post_response(user_url, 400, json_data_user2)
assert 'msg' in body, "message does not exist"
assert body['msg'] == "user already registered", ASSERT_MESSAGE

# 存在しないユーザーに対してユーザー ID の GET リクエストを出す
USERNAME_INVALID = "username_invalid"
json_data_user_invalid = json.dumps({
    "name": USERNAME_INVALID,
    "password": PASSWORD,
})
body = get_response(user_url, 404, json_data_user_invalid)
assert 'id' in body, ASSERT_MESSAGE
assert body['id'] == -1, ASSERT_MESSAGE

# パスワード誤り
body = get_response(user_url, 404, json_data_user2)
assert 'id' in body, ASSERT_MESSAGE
assert body['id'] == -1, ASSERT_MESSAGE

# ユーザー ID 取得
body = get_response(user_url, 200, json_data_user)
assert 'id' in body, ASSERT_MESSAGE
assert body['id'] == user_id, ASSERT_MESSAGE

# ユーザー更新
json_data_user_put = json.dumps({
    "name": USERNAME,
    "password": PASSWORD,
    "new_password": PASSWORD2,
})
body = put_response(user_url, 200, json_data_user_put)
assert 'id' in body, ASSERT_MESSAGE
assert body['id'] == user_id, ASSERT_MESSAGE

# ユーザー更新（戻す）
json_data_user_put2 = json.dumps({
    "name": USERNAME,
    "password": PASSWORD2,
    "new_password": PASSWORD,
})
body = put_response(user_url, 200, json_data_user_put2)
assert 'id' in body, ASSERT_MESSAGE
assert body['id'] == user_id, ASSERT_MESSAGE

# 存在しないユーザーに対してアイテムの GET リクエストを出す
USER_ID_INVALID = 999999
item_url_get_post_invalid = request_base_url() + f"/item/{USER_ID_INVALID}"
body = get_response(item_url_get_post_invalid, 200)
assert len(body['list']) == 0, "result should be empty"

# リストに何も登録していないときアイテムが空であることを確認
item_url_get_post = request_base_url() + f"/item/{user_id}"
body = get_response(item_url_get_post, 200)
assert len(body['list']) == 0, "result should be empty"

# アイテムを登録
json_data_item = json.dumps({
    "title": "aaa",
    "deadline": "2024-12-31"
})
body = post_response(item_url_get_post, 200, json_data_item)
assert 'user_id' in body, ASSERT_MESSAGE
assert 'id' in body, ASSERT_MESSAGE
assert body['user_id'] == user_id, ASSERT_MESSAGE
item_id = body['id']  # 以降のテストのために item_id を覚えておく

# アイテムの存在チェック
body = get_response(item_url_get_post, 200)
assert len(body['list']) > 0, "result is empty"
assert body['list'][0]['id'] == item_id, ASSERT_MESSAGE
assert body['list'][0]['title'] == "aaa", ASSERT_MESSAGE

# 登録されているアイテムの取得
item_url_get_specifically = request_base_url() + f"/item/{user_id}?item_id={item_id}"
body = get_response(item_url_get_specifically, 200)
assert len(body['list']) > 0, "list is empty"
assert body['list'][0]['id'] == item_id, ASSERT_MESSAGE
assert body['list'][0]['title'] == "aaa", ASSERT_MESSAGE

# アイテムの検索
item_url_get_specifically = request_base_url() + f"/item/{user_id}?search=a"
body = get_response(item_url_get_specifically, 200)
assert len(body['list']) > 0, "list is empty"
assert body['list'][0]['id'] == item_id, ASSERT_MESSAGE
assert body['list'][0]['title'] == "aaa", ASSERT_MESSAGE

# アイテムの検索（見つからない）
item_url_get_specifically = request_base_url() + f"/item/{user_id}?search=b"
body = get_response(item_url_get_specifically, 200)
assert len(body['list']) == 0, "list should be empty"

# 登録されていないアイテムを取得しようとする
ITEM_ID_INVALID = 999999
item_url_get_specifically = request_base_url() + f"/item/{user_id}?item_id={ITEM_ID_INVALID}"
body = get_response(item_url_get_specifically, 200)
assert len(body['list']) == 0, "list should be empty"

# アイテムの更新
item_url_put_delete = request_base_url() + f"/item/{user_id}/{item_id}"
json_data_item2 = json.dumps({
    "title": "bbb",
    "deadline": "2025-1-31"
})
body = put_response(item_url_put_delete, 200, json_data_item2)
assert 'user_id' in body, ASSERT_MESSAGE
assert 'id' in body, ASSERT_MESSAGE
assert body['user_id'] == user_id, ASSERT_MESSAGE
assert body['id'] == item_id, ASSERT_MESSAGE

# 登録されているアイテムの取得
item_url_get_specifically = request_base_url() + f"/item/{user_id}?item_id={item_id}"
body = get_response(item_url_get_specifically, 200)
assert len(body['list']) > 0, "list is empty"
assert body['list'][0]['id'] == item_id, ASSERT_MESSAGE
assert body['list'][0]['title'] == "bbb", ASSERT_MESSAGE

# 項目の削除
body = delete_response(item_url_put_delete, 200)
assert 'user_id' in body, ASSERT_MESSAGE
assert 'id' in body, ASSERT_MESSAGE
assert body['user_id'] == user_id, ASSERT_MESSAGE
assert body['id'] == item_id, ASSERT_MESSAGE

# ユーザーの削除
body = delete_response(user_url, 200, json_data_user)
assert 'id' in body, ASSERT_MESSAGE
assert body['id'] == user_id, ASSERT_MESSAGE
