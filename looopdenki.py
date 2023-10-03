from requests import get
import sys
import json
from datetime import datetime, timedelta
import subprocess

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

# サブプロセス実行用の関数
def run_subprocess():
    # ここに実行したいコマンドを記述
    subprocess.run(["your_command_here"])

def time_move_up():
    # 現在の時刻を取得
    current_time = datetime.now()

    # 現在の分数を取得
    current_minute = current_time.minute

    # 30分ごとに切り上げる
    if current_minute >= 30:
        current_time += timedelta(minutes=(60 - current_minute))
    else:
        current_time += timedelta(minutes=(30 - current_minute))

    # 新しい時刻をHHMM形式で表示
    new_hhmm = current_time.strftime('%H%M')

    return new_hhmm

def get_flag_at_time(data_list, input_time):
    for hhmm, flag in data_list:
        if hhmm == input_time:
            return flag
    return None  # 時刻が見つからない場合はNoneを返すか、適切なデフォルト値を返すことができます

def get_now_denkibiyori():
    # APIエンドポイントのURLを指定
    api_url = "https://looop-denki.com/api/prices?select_area=01"

    json_str=get_prices(api_url)
    # JSONデータを解析
    data = json.loads(json_str)

    # "1"の"level"を抽出
    level_1 = data["1"]["level"] # -0.5 電気日和

    time_list = data["label"] # 30分ごとのリスト ['0', '0.5', '1', ...]

    date_format = "%H:%M"  # 時刻のフォーマット
    hhmm_list = []

    for time_str in time_list:
        hours = int(float(time_str))
        minutes = int((float(time_str) - hours) * 60)
        hhmm_str = f"{hours:02d}{minutes:02d}"
        hhmm_list.append(hhmm_str)

    merged_list = [(hhmm_list[i], level_1[i]) for i in range(len(level_1))]

    # テストデータ
    #merged_list = [('0000', 0), ('0030', 0), ('0100', 0), ('0130', 0), ('0200', 0), ('0230', 0), ('0300', 0), ('0330', 0), ('0400', 0), ('0430', 0), ('0500', 0), ('0530', 0), ('0600', 0), ('0630', 0), ('0700', 0), ('0730', 0), ('0800', 0), ('0830', -0.5), ('0900', -0.5), ('0930', -0.5), ('1000', -0.5), ('1030', -0.5), ('1100', -0.5), ('1130', -0.5), ('1200', -0.5), ('1230', -0.5), ('1300', -0.5), ('1330', 0), ('1400', 0), ('1430', 0), ('1500', 0), ('1530', 0), ('1600', 0.5), ('1630', 0.5), ('1700', 0.5), ('1730', 0.5), ('1800', 0.5), ('1830', 0.5), ('1900', 0.5), ('1930', 0), ('2000', 0), ('2030', 0), ('2100', 0.5), ('2130', 0), ('2200', 9), ('2230', 0), ('2300', 0), ('2330', 0)]

    near_time=time_move_up()

    denki_biyori=get_flag_at_time(merged_list, near_time)
    return denki_biyori


import time

# マイニングプログラムを実行するコマンド
command = ["sh", "/home/user/mining/lolminer1.76/1nicehash_nexa.sh"]

# サブプロセスを開始
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 20分ごとにフラグの値を調べて終了するかどうかを確認
while True:
    # サブプロセスの状態を調べる
    return_code = process.poll()
    if return_code is not None:
        # サブプロセスが終了している場合
        print(f"サブプロセスが終了しました。終了コード: {return_code}")
        break

    # 20分待つ
    time.sleep(5)  # 20分 = 1200秒

    # フラグの値を調べる（仮のコード、実際のコードに合わせて変更が必要）
    flag_value = get_now_denkibiyori()  # フラグの値を取得する関数を定義する必要があります

    if flag_value != -0.5:
        # フラグの値が-0.5以外の場合、サブプロセスを終了する
        print(f"フラグの値が-0.5以外 ({flag_value}) なので、サブプロセスを終了します。")
        process.terminate()  # サブプロセスを終了させる

# サブプロセスの終了を待つ
process.wait()
print("プログラムが完了しました。")