import sys
import aiohttp
import asyncio
import platform

from datetime import datetime, timedelta


class HttpError(Exception):
    pass


async def parser_api_privat(pr_data):
    result_dict = {}
    currency_list = ['EUR', "USD", "PLN"]
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
                    data = await resp.json()
                    return await parser_api_privat(data)
                else:
                    raise HttpError(f'Error status: {resp.status} for {url}')
        except (aiohttp.ClientConnectionError, aiohttp.InvalidURL) as err:
            raise HttpError(f'Error status: {url}', str(err))


def urls_lists(index_day):
    days_for_url = [datetime.now().strftime("%d.%m.%Y")]
    d = datetime.now() - timedelta(days=int(index_day))
    days_for_url.append(d.strftime("%d.%m.%Y"))
    return ['https://api.privatbank.ua/p24api/exchange_rates?date=' + day for day in days_for_url]


async def main(days):
    try:
        futures = [request(url) for url in urls_lists(days)]
        return await asyncio.gather(*futures, return_exceptions=True)
    except HttpError as err:
        print(err)
        return None


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main(sys.argv[1]))
    print(r)
