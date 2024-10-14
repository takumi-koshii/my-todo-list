# Todo リスト REST API

## 概要

ユーザーごとに Todo リスト項目の操作が可能な API です。AWS 環境へのデプロイを容易にするため、 App 部分は Python で実装し、 DB 部分には MySQL を使用しています。

## Todo リスト API の使い方

test/test.py を参考にしてください。

### 準備

MySQL サーバーを建て、初期設定ファイル (mysql/init.sql) を適用してください。
``` bash
$ cd mysql
$ mysql -u $USERNAME$ -p < init.sql
```

Python 環境に、 requirements.txt の内容をインストールしてください。
``` bash
$ pip install -r requirements.txt
```

### ユーザーの登録
URI: \<baseurl\>/user  
METHOD: POST  
HEADER: Content-Type: application/json  
REQUEST:  
``` json
{
    "name": "ユーザー名", 
    "password": "パスワード"
}
```
RESPONSE:
``` json
{
    "status_code": 200,
    "content": {
        "id": "ユーザー ID"
    }
},
{
    "status_code": 400,
    "content": {
        "msg": "user already registered"
    }
}
```

ユーザーをシステムに登録します。すでに同名のユーザーが存在するとき登録に失敗します。パスワードは sha256 で格納されます。

### ユーザーの取得
URI: \<baseurl\>/user  
METHOD: GET  
HEADER: Content-Type: application/json  
REQUEST:  
``` json
{
    "name": "ユーザー名",
    "password": "パスワード"
}
```
RESPONSE:
``` json
{
    "status_code": 200,
    "content": {
        "id": "ユーザー ID",
        "name": "ユーザー名",
        "password": "パスワード",
        "created_at": "作成日時",
        "updated_at": "更新日時"
    }
},
{
    "status_code": 404,
    "content": {
        "id": -1,
    }
}
```

ユーザー情報をシステムから取得します。ユーザーが存在しない、または、パスワードが誤っているとき id = -1 のユーザーオブジェクトを返します。

### ユーザーの更新
URI: \<baseurl\>/user  
METHOD: PUT  
HEADER: Content-Type: application/json  
REQUEST:  
``` json
{
    "name": "以前のユーザー名",
    "new_name": "新しいユーザー名（オプション）"
    "password": "以前のパスワード"
    "new_password": "新しいパスワード（オプション）"
}
```
RESPONSE:
``` json
{
    "status_code": 200,
    "content": {
        "id": "ユーザー ID"
    }
},
{
    "status_code": 404,
    "content": {
        "id": "ユーザー ID"
    }
}
```

既に登録されたユーザー情報を更新します。ユーザーが存在しない、または、パスワードが誤っているとき 404 エラーとなります。

### ユーザーの削除
URI: \<baseurl\>/user  
METHOD: DELETE  
HEADER: Content-Type: application/json  
REQUEST:  
``` json
{
    "name": "ユーザー名",
    "password": "パスワード"
}
```
RESPONSE:
``` json
{
    "status_code": 200,
    "content": {
        "id": "ユーザー ID"
    }
},
{
    "status_code": 404,
    "content": {
        "id": "ユーザー ID"
    }
}
```

既に登録されたユーザー情報を削除します。ユーザーが存在しない、または、パスワードが誤っているとき 404 エラーとなります。

### Todo リストへのアイテムの追加
URI: \<baseurl\>/item/{user_id}  
METHOD: POST  
HEADER: Content-Type: application/json  
REQUEST:  
``` json
{
    "content": "Todo リストアイテムの内容",
    "deadline": "〆切日"
}
```
RESPONSE:
``` json
{
    "status_code": 200,
    "content": {
        "user_id": "ユーザー ID",
        "id": "アイテム ID"
    }
},
{
    "status_code": 404,
    "content": {
        "user_id": "ユーザー ID"
    }
}
```

指定されたユーザー ID の Todo リストにアイテムを追加します。ユーザー ID が見つからないとき 404 エラーとなります。

### Todo リストのアイテムの取得
URI: \<baseurl\>/item/{user_id}?item_id={item_id}  
METHOD: GET  
RESPONSE:
``` json
{
    "status_code": 200,
    "content": {
        "list": [
            {
                "id": "アイテム ID",
                "user_id": "ユーザー ID",
                "content": "Todo リストアイテムの内容",
                "deadline": "〆切日",
                "created_at": "作成日時",
                "updated_at": "更新日時"
            }
        ]
    }
}
```

指定されたユーザー ID の Todo リストのアイテム一覧を取得します。 URI で item_id を指定すると特定の item_id の情報のみ取得します。

### Todo リストのアイテムの更新
URI: \<baseurl\>/item/{user_id}/{item_id}  
METHOD: PUT  
HEADER: Content-Type: application/json  
REQUEST:  
``` json
{
    "content": "Todo リストアイテムの内容",
    "deadline": "〆切日"
}
```
RESPONSE:
``` json
{
    "status_code": 200,
    "user_id": "ユーザー ID",
    "id": "アイテム ID",
},
{
    "status_code": 404,
    "user_id": "ユーザー ID",
},
{
    "status_code": 404,
    "user_id": "ユーザー ID",
    "id": "アイテム ID"
}
```

指定されたユーザー ID の Todo リストのアイテムを更新します。ユーザーが見つからない、または、アイテムが見つからないとき 404 エラーとなります。

### Todo リストのアイテムの削除
URI: \<baseurl\>/item/{user_id}/{item_id}  
METHOD: DELETE  
RESPONSE:
``` json
{
    "status_code": 200,
    "user_id": "ユーザー ID",
    "id": "アイテム ID",
},
{
    "status_code": 404,
    "user_id": "ユーザー ID",
}
```

指定されたユーザー ID の Todo リストのアイテムを更新します。ユーザーが見つからないとき 404 エラーとなります。


