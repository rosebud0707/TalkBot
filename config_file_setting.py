"""config_file_setting.py
    初期設定ファイルのデータエンティティクラス
    初期設定ファイルの読み込みを行う
"""
import configparser
import dataclasses
import os


@dataclasses.dataclass
class ConfigFileEntity:
    """データエンティティ
        configファイルの内容保持用エンティティクラス
    """
    server_name: str
    misskey_api_key: str
    talk_api_base_url: str
    talk_api_key: str

class SetConfigFileData:
    """外部設定ファイル設定
        外部設定ファイルを読み込み、設定する。
    """
    def __init__(self):
        """コンストラクタ
        """
        self.config = None
        # 外部設定ファイル読み込み
        self.__read_config_file()
    
    def set_config_datas(self):
        """外部設定ファイル設定
            外部設定ファイルを読み込み、設定する。
        """
        try:
            # 内容設定
            return ConfigFileEntity(
                                    server_name = str(self.config['Setting']['server_name']),
                                    misskey_api_key = str(self.config['Setting']['misskey_api_key']),
                                    talk_api_base_url = str(self.config['TalkAPI']['talk_api_base_url']),
                                    talk_api_key = str(self.config['TalkAPI']['talk_api_key'])
                                    )

        except Exception as e:
            print("Configファイル設定エラー" + str(e))
            exit()
    
    def __read_config_file(self):
        """外部設定ファイル読み込み
        """
        try:
            # 外部設定ファイル読み込み
            self.config = configparser.ConfigParser()
            self.config.read(os.path.dirname(os.path.abspath(__file__)) + r'/Config.ini', 'UTF-8')
        except Exception as e:
            print("外部設定ファイル読み込みエラー。" + str(e))
            exit()