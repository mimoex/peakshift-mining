from requests import get
import sys
import json
from datetime import datetime, timedelta
import subprocess
import time
import os

today_list=[]

# APIからJSONデータを取得する関数
def get_prices(url):
    # GETリクエストを送信してJSONデータを取得
    response = get(url)
    
    # ステータスコードを確認
    if response.status_code == 200:
        # JSON文字列を取得
        return response.text
    else:
        print("APIリクエストが失敗しました。ステータスコード:", response.status_code)
        sys.exit(1)  # プログラムを終了

# 現在時刻を30分ごとに切り下げる関数
def time_move_down():
    # 現在の時刻を取得
    current_time = datetime.now()

    # 現在の分数を取得
    current_minute = current_time.minute

    # 30分ごとに切り下げ
    if current_minute >= 30:
        current_time -= timedelta(minutes=(current_minute - 30))
    else:
        current_time -= timedelta(minutes=current_minute)

    # 新しい時刻をHHMM形式で表示
    new_hhmm = current_time.strftime('%H%M')

    return new_hhmm

# 現在時刻とでんき日和データの照合
def get_flag_at_time(data_list, input_time):
    for hhmm, flag in data_list:
        if hhmm == input_time:
            return flag
    return None  # 時刻が見つからない場合はNoneを返す
    
# APIからでんき日和データを取得する関数
def get_api():
    # APIエンドポイントのURLを指定
    api_url = "https://looop-denki.com/api/prices?select_area=01"

    json_str=get_prices(api_url)
    # JSONデータを解析
    data = json.loads(json_str)

    # "1"の"level"を抽出(今日のでんき日和データの抽出)
    level_1 = data["1"]["level"] # -0.5が電気日和

    time_list = data["label"] # 30分ごとのリスト ['0', '0.5', '1', ...]

    date_format = "%H:%M"  # 時刻のフォーマット
    hhmm_list = []

    for time_str in time_list:
        hours = int(float(time_str))
        minutes = int((float(time_str) - hours) * 60)
        hhmm_str = f"{hours:02d}{minutes:02d}"
        hhmm_list.append(hhmm_str)
    today_list = [(hhmm_list[i], level_1[i]) for i in range(len(level_1))]
    


# 現在時刻のでんき日和データを取得する関数
def get_now_denkibiyori():
    
    # テストデータ
    """
    today_list = [
     ('0000', 0), ('0030', 0), ('0100', 0), ('0130', 0), ('0200', 0), ('0230', 0), ('0300', 0), ('0330', 0), ('0400', 0), ('0430', 0), 
     ('0500', 0), ('0530', 0), ('0600', 0), ('0630', 0), ('0700', 0), ('0730', 0), ('0800', 0), ('0830', 0), ('0900', 0.5), ('0930', 0.5), 
     ('1000', 0.5), ('1030', 0.5), ('1100', 0.5), ('1130', 0.5), ('1200', 0.5), ('1230', 0.5), ('1300', 0.5), ('1330', 0), ('1400', 0), 
     ('1430', 0), ('1500', 0), ('1530', 0), ('1600', 0), ('1630', 0.5), ('1700', 0), ('1730', 0.5), ('1800', 0.5), ('1830', 0.5), ('1900', 0.5), 
     ('1930', 0), ('2000', 0), ('2030', 0), ('2100', 0.5), ('2130', 0), ('2200', 9), ('2230', 0), ('2300', 0), ('2330', 0)
     ]
    """


    near_time=time_move_down()

    denki_biyori=get_flag_at_time(today_list, near_time)
    return denki_biyori
    
def show_now_time():
	current_time = datetime.now()
	return current_time.strftime("[%Y-%m-%d %H:%M:%S]")

def danbou_mining():
    xmrig_process = None  # マイニングプロセスを追跡するための変数
    print(today_list)

    # 24時間動作するループ
    while True:
        flag = get_now_denkibiyori()

        # データが0以下の場合
        if flag <= 0:
            # xmrigプロセスがない場合はマイニングを開始
            if xmrig_process is None or xmrig_process.poll() is not None:
                xmrig_process = subprocess.Popen(["C:\\Users\\hoge\\xmrig\\build\\Release\\xmrig.cmd"], shell=True)
                print(f"{show_now_time()} マイニングを開始しました.")
            else:
                pass

        # データが0より大きい場合
        else:
            # xmrigプロセスが実行中の場合はマイニングを停止
            if xmrig_process and xmrig_process.poll() is None:
                #xmrig_process.kill()
                print(f"{show_now_time()} マイニングを停止しました.")
                os.system("shutdown /r /t 30")
            else:
                pass
        time.sleep(60)
        

if __name__ == "__main__":
	today_list =get_api()
	danbou_mining()
	
