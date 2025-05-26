from typing import Optional, Dict
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

HEADERS = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'referer': 'https://www.wildberries.ru',
}


def fetch_product_data(article: str) -> Optional[dict]:
    """Выполняет запрос к API Wildberries по артикулу и возвращает JSON-ответ."""
    url = (
        f'https://card.wb.ru/cards/v2/detail'
        f'?appType=1&curr=rub&dest=-1257786&hide_dtype=13&spp=30'
        f'&ab_testing=false&lang=ru&nm={article}'
    )
    try:
        logging.debug(f'Отправка запроса к URL: {url}')
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        logging.debug(f'Ответ: {response.status_code} — {response.text[:100]}...')
        return response.json()
    except requests.HTTPError as e:
        logging.warning(f'HTTP ошибка для артикула {article}: {e}')
    except requests.RequestException as e:
        logging.error(f'Ошибка запроса для артикула {article}: {e}')
    except ValueError as e:
        logging.error(f'Ошибка декодирования JSON для артикула {article}: {e}')
    return None


def get_wb_info(article: str) -> Optional[Dict[str, str]]:
    """Возвращает название и цену товара по артикулу Wildberries."""
    logging.info(f'Обработка артикула: {article}')
    data = fetch_product_data(article)
    if not data:
        logging.info(f'Нет данных для артикула {article}')
        return None

    products = data.get("data", {}).get("products", [])
    if not products:
        logging.info(f'Товар не найден для артикула {article}')
        return None

    product = products[0]
    title = product.get("name", "")
    price_info = product.get("sizes", [{}])[0].get("price", {})
    price = price_info.get("product", "")

    if title is None or price is None:
        logging.warning(f'Некорректные данные для артикула {article}')
        return None

    result = {
        "Title": title,
        "Price": price // 100  # Цена указана в копейках
    }

    logging.info(f'Найден товар: {result}')
    return result


if __name__ == '__main__':
    articles = ['15163742', '196139209', '10']
    for art in articles:
        info = get_wb_info(art)
        logging.info(f'Результат для {art}: {info}')
