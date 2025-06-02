from datetime import datetime
from requestNum import check_power
from utils.chart import generate_power_plot
from utils.dataManager import init_db, save_power_data, get_recent_power_logs
from utils.analyzer import compute_consumption
from utils.senderManager import send_notification
from utils.logger import setup_logger
from utils.configManager import ConfigManager

logger = setup_logger()
config = ConfigManager.get_config()

threshold = config['alert_threshold']
report_day = config['weekly_report_day']  # 0=Monday, 6=Sunday


def check_and_alert(remaining_power):
    if float(remaining_power) < threshold:
        send_notification(
            "电量告警 | 剩余电量过低",
            f"当前剩余电量为 {remaining_power} 度，低于设定阈值 {threshold} 度，请及时充值。"
        )
        logger.info("已发送电量过低告警邮件")
    else:
        logger.info("电量在安全范围内，无需发送告警")


def send_weekly_report_if_today():
    today_weekday = datetime.now().weekday()
    if today_weekday != report_day:
        logger.info(f"今天不是设定的周报发送日（今天是周{today_weekday}），不发送周报")
        return

    data = get_recent_power_logs(limit=7)
    analysis = compute_consumption(data)

    if analysis:
        lines = ["本周电量记录如下：", "-" * 28]
        for record in analysis:
            cons = record.get('consumption_since_prev_day')
            cons_str = f"{cons} 度" if cons is not None else "暂无数据"
            remaining = record.get('remaining_power', '未知')
            date = record.get('date', '未知日期')
            lines.append(f"{date} | 剩余电量: {remaining} | 当天消耗: {cons_str}")
        body = "\n".join(lines)
        image_path = generate_power_plot(analysis)
    else:
        body = "暂无本周电量记录数据。"
        image_path = None

    send_notification("每周电量报告", body, image_path)
    logger.info("已发送本周电量报告")



def main():
    init_db()
    remaining_power = check_power()

    if remaining_power:
        save_power_data(remaining_power)
        check_and_alert(remaining_power)
        send_weekly_report_if_today()
    else:
        logger.error("未能获取到电量数据")


if __name__ == "__main__":
    main()
