import smtplib

import requests
from utils.logger import setup_logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.configManager import ConfigManager

logger = setup_logger()

class BaseSender:
    def send(self, subject, body):
        raise NotImplementedError("子类必须实现 send 方法")

class EmailSender(BaseSender):
    def __init__(self, config):
        self.config = config
    
    def send(self, subject, body):
        smtp_config = self.config['smtp']
        try:
            server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'])
            server.login(smtp_config['sender_email'], smtp_config['password'])
            for receiver_email in smtp_config['receiver_emails']:
                msg = MIMEMultipart()
                msg['From'] = f"{smtp_config['sender_name']} <{smtp_config['sender_email']}>"
                msg['To'] = receiver_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                text = msg.as_string()
                server.sendmail(smtp_config['sender_email'], receiver_email, text)
                logger.info(f"邮件已成功发送给 {receiver_email}")
            logger.info("所有邮件发送成功！")
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
        finally:
            try:
                server.quit()
            except:
                pass

class WeChatSender:
    def __init__(self, config):
        self.webhook_url = config.get('wechat', {}).get('webhook_url')

    def send(self, subject, body):
        if not self.webhook_url:
            logger.warning("未配置企业微信机器人 Webhook URL，跳过发送")
            return

        content = f"【{subject}】\n{body}"
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }

        try:
            response = requests.post(self.webhook_url, json=data)
            if response.status_code == 200:
                logger.info("企业微信消息发送成功")
            else:
                logger.error(f"企业微信消息发送失败，状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            logger.error(f"企业微信发送异常: {e}")

class SenderManager:
    def __init__(self, config):
        self.config = config
        self.enabled_senders = config.get('enabled_senders', [])
        self.senders = []
        self._init_senders()

    def _init_senders(self):
        # 根据配置决定启用哪些发送方式
        for sender_name in self.enabled_senders:
            if sender_name == 'email':
                self.senders.append(EmailSender(self.config))
            elif sender_name == 'wechat':
                self.senders.append(WeChatSender(self.config))
            else:
                logger.warning(f"未知的发送器类型: {sender_name}")

    def send_all(self, subject, body):
        if not self.senders:
            logger.warning("没有启用任何发送方式，通知未发送")
            return
        for sender in self.senders:
            sender.send(subject, body)

def send_notification(subject, body):
    config = ConfigManager.get_config()
    manager = SenderManager(config)
    manager.send_all(subject, body)
