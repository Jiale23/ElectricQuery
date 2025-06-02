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

def get_recent_power_logs(limit=3):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT date, remaining_power FROM power_log
            ORDER BY date DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"查询电量记录失败: {e}")
        return []
    finally:
        conn.close()

def get_latest_power():
    logs = get_recent_power_logs(limit=1)
    if logs:
        return float(logs[0][1])
    return None
