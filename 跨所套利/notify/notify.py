from enum import Enum
from loguru import logger
import json
import urllib.parse
import telegram as tg
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import toml
from datetime import datetime
from ._util import *

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>|</red> <level>{level: <6}</level> <red>|</red> <level>{message}</level>")


class Platform(Enum):
    Lark = "lark"
    Weixin = "weixin"
    Dingtalk = "dingtalk"
    Telegram = "telegram"
    Discord = "discord"
    Bark = "bark"
    Mail = "mail"


class Notify:  # notify main class
    def set_platforms(self, platforms):
        self.__platforms = platforms

    def set_platforms_with_file(self, filepath):
        _platforms = toml.load(filepath)
        self.set_platforms(_platforms)

    def notify(self, title, text, platform="", file_path=None):
        if platform == "":
            if len(self.__platforms) != 1:
                raise ValueError("配置不正确")
            else:
                platform = list(self.__platforms)[0]

        if isinstance(platform, Enum):
            platform = platform.value

        if platform not in self.__platforms:
            logger.debug("self.__platforms:{}", self.__platforms)
            raise ValueError("环境未设置")

        if platform == Platform.Lark.value:  # assign platform
            self.lark(title, text, **self.__platforms[platform])
        elif platform == Platform.Weixin.value:
            self.weixin(title, text, **self.__platforms[platform])
        elif platform == Platform.Dingtalk.value:
            self.dingtalk(title, text, **self.__platforms[platform])
        elif platform == Platform.Telegram.value:
            self.telegram(title, text, **self.__platforms[platform])
        elif platform == Platform.Discord.value:
            self.discord(title, text, **self.__platforms[platform])
        elif platform == Platform.Bark.value:
            self.bark(title, text, **self.__platforms[platform])
        elif platform == Platform.Mail.value:
            self.mail(title, text, file_path=file_path, **self.__platforms[platform])
        else:
            logger.error(f"platform={platform},{type(platform)}")
            raise ValueError("未知通知平台")

    @staticmethod
    def lark(title, text, bot_url):  # for kark
        content = f"{title}\n{text}"
        data = json.dumps({
            "msg_type": "text",
            "content": {
                "text": content
            }
        })
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            target_url = bot_url
            req = get_content_from_internet(url=target_url, method="POST", headers=headers, data=data)
            logger.info("notify.lark:{}", req.text)
        except Exception as e:
            logger.error("notify.lark:{}", e)

    @staticmethod
    def weixin(title, text, bot_url):  # for weixin
        content = f"{title}\n{text}"
        data = json.dumps({
            "msgtype": "text",
            "text": {
                "content": content
            }
        })
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            target_url = bot_url
            req = get_content_from_internet(url=target_url, method="POST", headers=headers, data=data)
            logger.info("notify.weixin:{}", req.text)
        except Exception as e:
            logger.error("notify.weixin:{}", e)

    @staticmethod
    def dingtalk(title, text, bot_url, secret):  # for dingtalk
        content = f"{title}\n{text}"
        data = json.dumps({
            "msgtype": "text",
            "text": {
                "content": content
            }
        })
        headers = {
            'Content-Type': 'application/json'
        }
        timestamp, sign_str = cal_dingtalk_timestamp_sign(secret)
        params = {
            "timestamp": timestamp,
            "sign": sign_str
        }

        try:
            target_url = bot_url
            req = get_content_from_internet(url=target_url, method="POST", headers=headers, data=data,
                                            params=params)
            logger.info("notify.dingtalk:{}", req.text)
        except Exception as e:
            logger.error("notify.dingtalk:{}", e)

    @staticmethod
    def telegram(title, text, token, chat_id):  # for telegram
        content = f"{title}\n{text}"

        try:
            req = tg.Bot(token).send_message(chat_id, content)
            logger.info("notify.telegram:{}", req)
        except Exception as e:
            logger.error("notify.telegram:{}", e)

    @staticmethod
    def discord(title, text, bot_url):  # for discord
        content = f"{title}\n{text}"
        data = json.dumps({
            "content": content
        })
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            target_url = bot_url
            req = get_content_from_internet(url=target_url, method="POST", headers=headers, data=data)
            logger.info("notify.discord:{}", req.status_code)
        except Exception as e:
            logger.error("notify.discord:{}", e)

    @staticmethod
    def bark(title, text, server_url, token):  # bark for discord
        target_url = f"{server_url}/{token}/{urllib.parse.quote(title)}/{urllib.parse.quote(text)}"

        try:
            req = get_content_from_internet(url=target_url, method="GET")
            logger.info("notify.discord:{}", req.text)
        except Exception as e:
            logger.error("notify.discord:{}", e)

    @staticmethod
    def mail(title, text, smtp_server, smtp_port, username, password, to_address, file_path=None):  # for sending email
        content = f"{title}\n{text}"

        try:
            target_address = to_address  # target mail address to send
            msg = MIMEMultipart()
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            msg['From'] = username
            msg['To'] = target_address[0]
            msg['Subject'] = Header(title, 'utf-8')  # .encode()

            if file_path != None:
                # 创建带附件的
                file = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
                file["Content-Type"] = 'application/octet-stream'
                # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
                file["Content-Disposition"] = f'attachment; filename="{file_path}"'
                msg.attach(file)

            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(username, password)  # 登陆邮箱
                smtp.sendmail(username, target_address, msg.as_string())

                logger.info(f'notify.mail:success {datetime.now()}')

        except Exception as e:
            logger.error("notify.mail:{}", e)
