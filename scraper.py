import time
import requests
from bs4 import BeautifulSoup
import pandas as pd  # ← データを表にするための道具をインポート

# 1. データを取得したいURL
url = "https://www.westmetall.com/en//markdaten.php?action=table&field=LME_Cu_cash"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    # 2. ページを取得
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # 3. HTMLを解析
    soup = BeautifulSoup(response.text, "html.parser")
    table_rows = soup.find_all("tr")
    
    # データを一時的に溜めておくための空のリスト
    all_data = []
    
    # 4. 表の行を上から順番に読み込む
    for row in table_rows:
        cells = row.find_all("td")
        
        # 必要な4つのデータ（日付、現物、3ヶ月、在庫）が揃っているかチェック
        if len(cells) >= 4:
            date = cells[0].text.strip()
            
            # 見出し行を無視して、ちゃんと日付が入っている行だけを対象にする
            if any(month in date for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                cash_price = cells[1].text.strip()
                three_month_price = cells[2].text.strip()
                stock = cells[3].text.strip()
                
                # 1日分のデータをリストにまとめる
                day_data = [date, cash_price, three_month_price, stock]
                # 全体リストに追加
                all_data.append(day_data)

    # 5. 【ここがポイント！】過去1ヶ月分（約22営業日分）のデータに絞る
    month_data = all_data[:22]
    
    # 6. Pandasを使って、データを綺麗な表（データフレーム）に変換
    columns = ["日付", "現物価格(USD/t)", "3ヶ月先物(USD/t)", "LME在庫量(t)"]
    df = pd.DataFrame(month_data, columns=columns)
    
    # 7. Excelで開いても文字化けしない設定（utf-8-sig）でCSVファイルに保存
    csv_filename = "lme_copper_1month.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
    
    print(f"成功しました！「{csv_filename}」という名前でファイルが保存されました。")
    print("\n--- 保存されたデータの先頭5件 ---")
    print(df.head())  # 最初の5件だけ画面に表示して確認

except Exception as e:
    print(f"エラーが発生しました: {e}")

# サーバー負荷軽減のため、最後に2秒休む
time.sleep(2)