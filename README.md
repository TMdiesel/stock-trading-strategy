# stock-trading-strategy
- 深層強化学習を用いて株売買戦略を決定します。

## 実行環境
- 下記コマンドで必要なPythonパッケージをインストールできます。
   ```
   poetry install
   ```
- sqlite3をインストールします。

## 構成
### 全体概要
- 下記のフローで株売買戦略を決定します。
    - [株価データ収集](#株価データ収集)
      - 本リポジトリではテクニカル分析を対象とします。
      - 必要な株データをWebから収集し、データベースで管理します。
    - [バックテスト](#バックテスト)
    - [売買戦略](#売買戦略)
### 株価データ収集
- 株の銘柄情報や株価情報を保存するテーブルを作成します。
    ```
    sqlite3 data/stock.db < ./src/data_collect/create_table.sql
    ```
### バックテスト
### 売買戦略

## LICENSE
MIT

## 参考文献
- [株とPython─自作プログラムでお金儲けを目指す本](https://www.amazon.co.jp/%E6%A0%AA%E3%81%A8Python%E2%94%80%E8%87%AA%E4%BD%9C%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%A0%E3%81%A7%E3%81%8A%E9%87%91%E5%84%B2%E3%81%91%E3%82%92%E7%9B%AE%E6%8C%87%E3%81%99%E6%9C%AC-%E6%8A%80%E8%A1%93%E3%81%AE%E6%B3%89%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA%EF%BC%88NextPublishing%EF%BC%89-%E5%AE%AE%E9%83%A8-%E4%BF%9D%E9%9B%84-ebook/dp/B07LFXXPNZ)
- [Pythonで学ぶ強化学習 入門から実践まで](https://www.amazon.co.jp/%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%88%E3%82%A2%E3%83%83%E3%83%97%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA-Python%E3%81%A7%E5%AD%A6%E3%81%B6%E5%BC%B7%E5%8C%96%E5%AD%A6%E7%BF%92-%E5%85%A5%E9%96%80%E3%81%8B%E3%82%89%E5%AE%9F%E8%B7%B5%E3%81%BE%E3%81%A7-KS%E6%83%85%E5%A0%B1%E7%A7%91%E5%AD%A6%E5%B0%82%E9%96%80%E6%9B%B8-%E4%B9%85%E4%BF%9D/dp/4065142989)
- [人工市場と深層強化学習の融合による株式投資戦略学習](https://www.jstage.jst.go.jp/article/pjsai/JSAI2020/0/JSAI2020_2L4GS1304/_pdf/-char/ja)
- [深層強化学習による株式売買戦略の構築](https://ipsj.ixsq.nii.ac.jp/ej/?action=repository_action_common_download&item_id=180938&item_no=1&attribute_id=1&file_no=1)
- [金融取引戦略獲得のための複利型深層強化学習](https://sigfin.org/?plugin=attach&refer=SIG-FIN-016-01&openfile=SIG-FIN-016-01.pdf)
- [強化学習を用いたブーム検知型株トレーディングシステムの構築](https://sigfin.org/?plugin=attach&refer=SIG-FIN-011-04&openfile=SIG-FIN-011-04.pdf)