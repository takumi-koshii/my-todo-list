import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

pymysql.version_info = (1, 4, 6, 'final', 0)
pymysql.install_as_MySQLdb()

# データベースへの接続設定
#
# MySQL を使用します。データベースを Amazon RDS へ移植後は設定を変更してください。
# あらかじめローカルに mysql サーバーを建て mysql/init.sql をロードしてください。
# ```
# > cd mysql
# > mysql -u root -p < init.sql
# ```

# データベースエンジンの作成
SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(
    "mytodolist",
    "MyTodoListTest",
    "localhost",
    "todolist"
)

engine = create_engine(SQLALCHEMY_DATABASE_URI)

# セッションの作成
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
