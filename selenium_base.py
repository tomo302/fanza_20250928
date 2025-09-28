
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pyperclip
import subprocess
import json
import pprint
import progressbar
import requests
from tqdm import tqdm





sakujyo = "のエロ動画・アダルトビデオ一覧｜FANZA動画"
# クリップボードにコピーするURLは、ジャンルページURL,出演作品ページURLのみ対応コード。20250118

#chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# ChromeOptionsのインスタンスを作成

def download_file(url, local_filename):
    # リクエストを送り、レスポンスを得る
    with requests.get(url, stream=True) as response:
        # レスポンスが成功かチェック
        response.raise_for_status()
        
        # コンテンツのサイズを取得
        total_size = int(response.headers.get('content-length', 0))
        
        # プログレスバーの初期化
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024)
        
        # ファイルを書き込むために開く
        with open(local_filename, 'wb') as file:
            # ストリームからデータをチャンクごとに読み込み
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        
        # プログレスバーを終了
        progress_bar.close()



def get_script_jsonData(soup):
    #print(soup.find("div", class_="flex items-center gap-2 text-xs").span.text.replace(",", "").replace("タイトル", "")) # 作品総数
    json_data = soup.find("script", type="application/ld+json")
    data_text = json_data.text

    json_dict = json.loads(data_text)
    return json_dict
    
    

url = pyperclip.paste()
print(url)
url_plus = "&page="
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")


# User-Agentを設定
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# 他の必要なオプションがあれば、ここで追加

# WebDriverを初期化
driver = webdriver.Chrome(options=chrome_options)

# ChromeDriverのパスを適切に設定してください
driver.get(url)

# Age Check ボタンクリック---------------------------------
#element = driver.find_element(By.LINK_TEXT, "はい")
#time.sleep(5)
# #画像のリンクをクリック
#element.click()

# 年齢確認ボタンを待機し、クリック
try:
    wait = WebDriverWait(driver,2)
    #age_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class=\"turtle-component turtle-Button large fill css-w5doa7\" and @aria-disabled=\"false\"]/a[text()=\"はい\"]')))
    age_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="turtle-component turtle-Button large fill css-w5doa7"]/a[text()="はい"]')))
    time.sleep(1)
    age_button.click()
    # ページの読み込みを待機
    time.sleep(2) # ここのtime.sleepは超重要！！設定しないと読み込めない
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    # ページのHTMLを取得
    html = driver.page_source

    # BeautifulSoupで解析
    
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.title.text)
    json_data = get_script_jsonData(soup)

    print()
    #pprint.pprint(soup)
    #print(json_data)
    print()
    print()

    # print(json_data["name"])                        # 作品名
    print(json_data["description"])                                     # 作品詳細
    # ["sku"]                          # cid
    video_title = json_data["subjectOf"]["name"]

    video_title = video_title.replace(sakujyo, '').replace('/', '_').replace('!', '！').replace('-', '_').replace(' ', '_').replace('*', '_').replace(':', '：')
    
    # video_titleが５０文字以上なら短く処理する
    if len(video_title) > 50:
        video_title = video_title[:30] + '＊＊＊＊' + video_title[-15:]     #作品名
    # ["subjectOf"]["description"]
    try:                                      # 作品詳細
        print(json_data["subjectOf"]["contentUrl"])                         # サンプルビデオsm解像度URL
        video_url = json_data["subjectOf"]["contentUrl"]
        file_name = video_title + ".mp4"                                    # サンプルビデオ最高解像度URL
        download_file(video_url, file_name)
    except KeyError:
        print("サンプル動画はありません")
    # ["subjectOf"]["thumbnailUrl"]                                     # サンプル画像に１番目URL
    # print(json_data["subjectOf"]["uploadDate"])                         # 配信開始日
    # print(json_data["subjectOf"]["actor"]["name"])                      # 女優名
    # print(json_data["subjectOf"]["actor"]["alternateName"])             # ふりがな
    # print(json_data["subjectOf"]["genre"])                              # ジャンル
    # print(json_data["aggregateRating"]["ratingValue"])                  # レイティング
    # print(json_data["aggregateRating"]["ratingCount"])                  # レイティング回数


    


except TimeoutException:
    print("タイムアウトが発生しました")

driver.quit()