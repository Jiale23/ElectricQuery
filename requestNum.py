import yaml
import requests
from bs4 import BeautifulSoup
from utils.logger import setup_logger
from utils.configManager import ConfigManager

logger = setup_logger()

config = ConfigManager.get_config()

power_cfg = config['power_checker']

session = requests.Session()
session.headers.update({'User-Agent': power_cfg['user_agent']})

url = power_cfg['login_url']

def get_viewstate(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
        return viewstate, viewstategenerator
    except (TypeError, KeyError):
        logger.error("无法提取 __VIEWSTATE 或 __VIEWSTATEGENERATOR")
        raise

def post_event(html, event_target, extra_fields):
    viewstate, viewstategenerator = get_viewstate(html)
    data = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__EVENTTARGET': event_target,
        '__EVENTARGUMENT': '',
        'radio': 'buyR',
        'ImageButton1.x': '10',
        'ImageButton1.y': '10',
    }
    data.update(extra_fields)
    return session.post(url, data=data)

def check_power(building=None, floor=None, room=None):
    building = building or power_cfg['building']
    floor = floor or power_cfg['floor']
    room = room or power_cfg['room']

    logger.info(f"开始获取电量（楼栋={building}, 楼层={floor}, 房间={room}）")

    try:
        resp1 = session.get(url)
        resp2 = post_event(resp1.text, 'drlouming', {'drlouming': building})
        resp3 = post_event(resp2.text, 'ablou', {'drlouming': building, 'ablou': floor})
        resp4 = post_event(resp3.text, 'drceng', {'drlouming': building, 'ablou': floor, 'drceng': room})

        soup = BeautifulSoup(resp4.text, 'html.parser')
        h6_tags = soup.find_all('h6')
        if len(h6_tags) >= 2:
            spans = h6_tags[1].find_all('span', {'class': 'number orange'})
            if len(spans) >= 3:
                remaining = spans[2].text.strip()
                logger.info(f"获取成功，剩余电量：{remaining} 度")
                return remaining
            else:
                logger.warning("未找到足够的 <span> 标签")
        else:
            logger.warning("未找到足够的 <h6> 标签")
    except Exception as e:
        logger.error(f"查询出错: {e}")

    return None
