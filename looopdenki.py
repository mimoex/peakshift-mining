from requests import get
import sys
import json
from datetime import datetime, timedelta
import subprocess
import time
import os

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

# APIからでんき日和を取得し、そうではなくなる時間を取得する関数
def get_now_denkibiyori():
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

    merged_list = [(hhmm_list[i], level_1[i]) for i in range(len(level_1))]
    print(merged_list)

    biyori_starttime=None
    for i in range(len(merged_list) - 1):
        if merged_list[i][1] != -0.5 and merged_list[i + 1][1] == -0.5:
            biyori_starttime = merged_list[i + 1][0]
            break

    # データが-0.5から0になる時間（HHMM形式）を取得
    biyori_endtime = None
    for i in range(len(merged_list) - 1):
        if merged_list[i][1] == -0.5 and merged_list[i + 1][1] != -0.5:
            biyori_endtime = merged_list[i + 1][0]
            break

    if biyori_starttime:
        print(f"でんき日和開始時刻は {biyori_starttime} です。")
        if biyori_endtime:
            print(f"終了時刻は {biyori_endtime} です。")
    else:
        print("該当する時間はありません。")
        # 1分以内にyキーを押すとプログラム終了
        # 放置するとシャットダウン
        print("1分以内にyキーを押すとプログラムを終了します。")
        # 1分後にシャットダウン。キャンセルするにはyキーを押す
        os.system("shutdown /s /t 60")
        key = input()
        if key == "y":
            os.system("shutdown /a")
            sys.exit() # プログラムを終了


    # テストデータ
    #merged_list = [
    # ('0000', 0), ('0030', 0), ('0100', 0), ('0130', 0), ('0200', 0), ('0230', 0), ('0300', 0), ('0330', 0), ('0400', 0), ('0430', 0), 
    # ('0500', 0), ('0530', 0), ('0600', 0), ('0630', 0), ('0700', 0), ('0730', 0), ('0800', 0), ('0830', -0.5), ('0900', -0.5), ('0930', -0.5), 
    # ('1000', -0.5), ('1030', -0.5), ('1100', -0.5), ('1130', -0.5), ('1200', -0.5), ('1230', -0.5), ('1300', -0.5), ('1330', 0), ('1400', 0), 
    # ('1430', 0), ('1500', 0), ('1530', 0), ('1600', 0.5), ('1630', 0.5), ('1700', 0.5), ('1730', 0.5), ('1800', 0.5), ('1830', 0.5), ('1900', 0.5), 
    # ('1930', 0), ('2000', 0), ('2030', 0), ('2100', 0.5), ('2130', 0), ('2200', 9), ('2230', 0), ('2300', 0), ('2330', 0)
    # ]

    near_time=time_move_down()

    denki_biyori=get_flag_at_time(merged_list, near_time)
    return denki_biyori, biyori_starttime, biyori_endtime

# 採掘開始 (end_time: 'HHMM')
def start_mining(start_time, end_time):
    while True:
            current_time = time.strftime("%H%M")

            # 終了時間に達したら待機終了
            if current_time >= start_time:
                break

            # 一定時間（例: 1分）待機して再度時刻を確認
            time.sleep(60)
    try:
        xmrig_process = subprocess.Popen(["C:\\Users\\hoge\\xmrig\\build\\Release\\xmrig.cmd"], shell=True)
        print("マイニングを開始しました。")
        print(f"{end_time}に終了します。")

        while True:
            current_time = time.strftime("%H%M")

            # 終了時間に達したらxmrigを終了
            if current_time >= end_time:
                #xmrig_process.kill()
                print("マイニングを終了しました。")
                os.system("shutdown /s /t 1")
                break

            # 一定時間（例: 1分）待機して再度時刻を確認
            time.sleep(60)

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    flag, start_time, end_time=get_now_denkibiyori()
    start_mining(start_time, end_time)
