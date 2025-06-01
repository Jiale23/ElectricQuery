import sqlite3
from datetime import datetime
from utils.logger import setup_logger
from utils.configManager import ConfigManager

logger = setup_logger()
config = ConfigManager.get_config()

DB_PATH = config['db_name']

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS power_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            remaining_power TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_power_data(remaining_power, date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO power_log (date, remaining_power) VALUES (?, ?)
        ''', (date_str, remaining_power))
        conn.commit()
        logger.info(f"成功保存电量数据：{date_str} -> {remaining_power}")
    except Exception as e:
        logger.error(f"保存电量数据失败: {e}")
    finally:
        conn.close()

def get_recent_three_days_consumption():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT date, remaining_power FROM power_log
            ORDER BY date DESC
            LIMIT 3
        ''')
        rows = cursor.fetchall()
        if len(rows) < 1:
            logger.warning("暂无三天内数据")
            return None

        rows = sorted(rows, key=lambda x: x[0])
        consumptions = []
        for i in range(len(rows)):
            curr_date, curr_power = rows[i]
            consumption = None
            if i > 0:
                try:
                    prev_power = float(rows[i-1][1])
                    curr_power_float = float(curr_power)
                    consumption = prev_power - curr_power_float
                except Exception:
                    consumption = None
            consumptions.append({
                'date': curr_date,
                'remaining_power': curr_power,
                'consumption_since_prev_day': consumption
            })
        return consumptions
    except Exception as e:
        logger.error(f"查询最近三天电量消耗失败: {e}")
        return None
    finally:
        conn.close()
