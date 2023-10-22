import aiohttp
import asyncio
import platform
import typing as t
import sys
from datetime import datetime, timedelta

LINK_API_PRIVAT = 'https://api.privatbank.ua/p24api/exchange_rates?date='
DELTA_D_POSITION = 1


class HttpError(Exception):
    pass


async def parser_api_privat(pr_data, currency_list: t.Iterable[str] | None = None):
    if currency_list is None:
        currency_list = ['EUR', "USD"]
    result_dict = {}

    for item in pr_data["exchangeRate"]:
        currency = item["currency"]
        if currency in currency_list:
            if pr_data['date'] not in result_dict:
                result_dict[pr_data['date']] = {}
            result_dict[pr_data["date"]][currency] = {"sale": item.get('saleRate'), "purchase": item.get('saleRate')}

    return result_dict


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()

                else:
                    raise HttpError(f'Error status: {resp.status} for {url}')
        except (aiohttp.ClientConnectionError, aiohttp.InvalidURL) as err:
            raise HttpError(f'Error status: {url}', str(err))


def urls_lists(index_day):
    days_for_url = [datetime.now().strftime("%d.%m.%Y")]
    d = datetime.now() - timedelta(days=int(index_day))
    days_for_url.append(d.strftime("%d.%m.%Y"))
    return [f'{LINK_API_PRIVAT}{day}' for day in days_for_url]


async def fetch_and_parse(url, currency_list=None):
    data_json = await request(url)
    return await parser_api_privat(data_json, currency_list)


async def main():
    days = sys.argv[DELTA_D_POSITION]
    try:
        futures = [fetch_and_parse(url) for url in urls_lists(days)]
        return await asyncio.gather(*futures, return_exceptions=True)
    except HttpError as err:
        print(err)
        return None


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
    print(r)
