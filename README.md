# クラウドプラットフォーム実習Ⅰ
『オンプレミスとクラウドの連携』

## テーマ
AWS上で動くRedmineとローカルとの連携を行う。

ローカルでWebClassから課題等の情報を取得し、
Pythonのサードパーティライブラリである `python-redmine` を用いて
AWS等のクラウド上で動くRedmineに対してデータをインポートします。

Redmineは、汎用性の高いプロジェクト管理ツールとして有名で、
アカウントごとに権限を設定して認証認可を行ったり、登録したタスクに期限や優先度、担当者を設定したり、
タスク同士に入れ子関係を定義したりできます。

一方WebClassは、大学の講義資料や課題に関する内容が一覧で掲載されていますが、
REST API等は無く、ブラウザから手動でアクセスして課題の管理を行う必要があります。

WebClassの個々人のデータを、個々人がローカルに一括で取り込み、
クラウドで稼働するRedmineに対してAPI経由で流し込むことで、
複数人が使えるタスク管理アプリを実現できます。

## システム構成図
[システム構成図](./sys_diagram.png)

## はじめかた
1. 本リポジトリをクローンします。(以下は`cpp1_report1`というディレクトリ名でクローンしています)
```
$ git clone https://github.com/Taipoon/cpp1-webclass-redmine.git cpp1_report1
```

2. クローンしたプロジェクトのディレクトリに移動し、`requirements.txt`を用いて必要なライブラリをインストールします。
```
$ cd cpp1_report1
$ pip install -r requirements.txt
```

3. .env.example をコピーして .env を作成します。

4. .env を以下を手本にして編集します。
```text:.env
# RedmineにアクセスするURLを指定します
REDMINE_URL=http://x.x.x.x 

# Redmineにアクセスするためのポート番号を指定します
REDMINE_PORT=3000

# Redmineにログイン後、APIを有効にして、アカウントページから取得したAPIキーを指定します
REDMINE_API_KEY=

# Web Class にログインするための学籍番号とパスワードを指定します
WEBCLASS_USER_ID=
WEBCLASS_PASSWORD=
```
> Redmine でREST APIを有効する方法は、以下のサイトを参考にしてください。
> https://redmine.jp/glossary/r/rest-api/

5. main.py を実行します
```
$ python main.py
```
初期実行時は`webdriver-manager`によって`Chrome Driver`がダウンロードされ自動実行されます。

それにより、ターミナルに以下のような出力が表示される場合があります。
```
[WDM] - ====== WebDriver manager ======
```

6. WebClassから講義情報を取得し、プロジェクトおよびチケットを作成します
```
キャリアデザインⅢ A (2022-第2学期-水4) のチケットを作成します
「6月15日　第１回　レポート課題」を作成しました
「6月22日　第２回　レポート課題」を作成しました
...
...
...
```
上記のように表示されればエクスポートが開始されています。
