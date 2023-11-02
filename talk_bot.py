import asyncio
import json
import logging
import os

import requests
import websocket
from misskey import Misskey

from config_file_setting import SetConfigFileData


def log_set():
	'''ログ初期設定
		ログ出力の各種設定を行う。
		Returns:
			logger:loggerオブジェクト
	'''
	# カレントディレクトリと同階層のLogフォルダ
	log_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Log", "talk_bot.log")

	# loggerオブジェクト生成
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)

	# Fileハンドラクラスをインスタンス化
	fl_handler = logging.FileHandler(filename=log_filepath, encoding="utf-8")

	# ログ出力のフォーマットを作成
	formatter = logging.Formatter('%(asctime)s : %(levelname)s - %(filename)s - %(message)s')
	fl_handler.setFormatter(formatter)

	# ハンドラセット
	logger.addHandler(fl_handler)

	return logger

async def main(config_params, mk):
	'''メイン処理
		メイン処理を行うメソッド
		Params
			config_params:初期設定ファイル内容
			mk:Misskey.py インスタンス
	'''
	# Websocketコネクト用値設定
	server = config_params.server_name
	API = config_params.misskey_api_key
	
	try:
		mk.notes_create(text='今起きた。', visibility='home')
		# コネクション作成
		logger.info('コネクション生成')
		ws = websocket.create_connection(f'wss://{server}//streaming?i={API}')

		# mainチャンネルに接続(ストリームにJSONをsend)
		logger.info('ストリームへJSON送信')
		ws.send(json.dumps({
			"type": "connect",
			"body": {
						"channel": "main",
						"id": "oshaberi_monster"
					}
			}))
		
		while True:
			await receive_mention(config_params, ws, mk)

	except Exception as e:
		logger.error('エラー発生。' + str(e))
		raise
	
	finally:
		# 切断
		logger.info('ストリームClose')
		ws.close()

async def receive_mention(config_params, ws, mk):
	'''メンション受信
		メンションの受信待受。
		Params
			config_params:初期設定ファイル内容
			ws:Websocket通信用インスタンス
			mk:Misskey.py インスタンス
	'''
	try:
		# 受信
		result =  ws.recv()

		# JSONデシリアライズ
		json_dict = json.loads(result)
		
		if json_dict['body']['type'] == 'unreadNotification' and (json_dict['body']['body']['type'] == 'mention' or json_dict['body']['body']['type'] == 'reply'):
			# 未読の通知、かつmentionまたはreplyを受け取った場合
			# mentionの抜き出し
			mention_raw = json_dict['body']['body']['note']['text']
			mention_wk = mention_raw.split()
			mention_wk.pop(0)

			# mention本文
			mention = ''.join(mention_wk)

			files = {
						'apikey': (None, config_params.talk_api_key),
						'query': (None, mention),
					}
			
			# POST
			response = requests.post(config_params.talk_api_base_url, files=files)

			# responseより回答分を抽出する
			if response.status_code == 200:
				logger.info('レスポンス受信')
				# ステータスコード:200(正常)の場合
				res = response.json()
				# 返信文
				note = ((res['results'])[0])['reply']
				# 返信先ID
				to_id = json_dict['body']['body']['note']['id']

				# 返信
				mk.notes_create(text=note, reply_id=to_id, visibility='home')

			else:
				logger.error('レスポンスエラー' + str(response.status_code))

	except Exception as e:
		raise 

if __name__ == '__main__':
	# ログ設定
	logger = log_set()

	# 初期設定ファイル読み込み
	config = SetConfigFileData()
	config_params = config.set_config_datas()

	# MisskeyAPI インスタンス化
	logger.info('MisskeyAPIインスタンス化')
	mk = Misskey(config_params.server_name, i=config_params.misskey_api_key)

	try:
		logger.info('メイン処理呼出')
		asyncio.run(main(config_params, mk))

	except Exception as e:
		logger.error('処理終了。')
		exit()