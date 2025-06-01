from datetime import datetime
from requestNum import check_power
from utils.dataManager import init_db, save_power_data, get_recent_three_days_consumption
from utils.senderManager import send_notification
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger()

def main():
    init_db()  # 先初始化数据库

    remaining_power = check_power()
    if remaining_power:
        save_power_data(remaining_power)

        subject = f"{datetime.now().strftime('%Y-%m-%d')} 最新电量通知"
        body_lines = [f"当前剩余电量为: {remaining_power} 度\n"]

        data = get_recent_three_days_consumption()

        if not data:
            body_lines.append("暂无三天内数据")
        else:
            body_lines.append("最近三天电量记录：")
            for record in data:
                cons_str = (f"{record['consumption_since_prev_day']} 度"
                            if record['consumption_since_prev_day'] is not None else "暂无数据")
                body_lines.append(f"{record['date']} 剩余电量: {record['remaining_power']}，当天消耗: {cons_str}")

        body = "\n".join(body_lines)

        print(body)
        send_notification(subject, body)
    else:
        logger.error("未能获取到电量数据")

if __name__ == "__main__":
    main()
