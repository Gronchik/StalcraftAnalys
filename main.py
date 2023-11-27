#from requests import get, post, request
from json import loads
import aiohttp
import asyncio
import time
import aiosqlite as sql
import matplotlib.pyplot as plt


region = 'RU'
item_id = 'qjqw9'
start = 0
end = 3458601
limit = 200


client = {
    'client_id': 300,
    'client_secret': 'rUSQWHitKelgErnoFnRFiex0ammxbTYqAQFrFGgL',
    'grant_type': 'client_credentials',
    'score': ''
}

# INFO = post('https://exbo.net/oauth/token', client)
#
# AUTH_TOKEN = loads(INFO.text)
url = "https://eapi.stalcraft.net/" + region + "/auction/" + item_id + "/history"

headers = {
          "Content-Type": "application/json",
          "Authorization": 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzMDAiLCJqdGkiOiJhZGVmNzYyNjQ3OTY4MjRlZTg5NTlhN2ViMzhlMDdmZmY2NTRjZWFkNzI1YmZkNmUwMTNmMmQ1ZmY4MzA0NmQ3ZWJjZTIwYmZiN2ZiNDg4OCIsImlhdCI6MTcwMDI4MDgxMS4yOTM3MTcsIm5iZiI6MTcwMDI4MDgxMS4yOTM3MiwiZXhwIjoxNzMxOTAzMjExLjEwODg5NSwic3ViIjoiIiwic2NvcGVzIjpbXX0.l0yE3voC_S2djQ6h4Wf7Pt-hNigCFduiJM7ZXOroysHStKRYrlIUTGWX61J659LIziE4qr8jNo1E8hmDME2P0V_VtCJaN-Q4E9qqF8ZQI3JbJA9jlL190sz6OaVvTnQRiQzJQ0i5WtUj5srRd0KxA6HD_JUCLNXpR8QBDeb-tGSZCK8tcVMOysw1RddgRmBo56OFwgHiexTt_bynChBRBxEnFZft56xK4A-uPd2LhGg0falo37a9XhNmuEkrrvkps85jw27ADcRmFf3TCju5Ie819XmnAmh3DrSdPa7jCKQlOjKnNMnwrIBKRy5yGxuURZb2kuN412rQNQ-_JG9L-aEBYgggC2f8oOWFYs0q6X1QAqtK3oC8AX_DKl3xOTwiY6G1XpUz_F6fLgEn99QhPOi3zKFZRML1dYNYp_bvnbyVH2rliiE990_a-EoeIj_rbDsz8evr102M4AVbKps9DPg7695Sub7zQbRM16I-ruZw7WH8BXCYaN0CFEjMBaP5PzpXECdw0LFIm57MIYTIPEG--Y7j0mUW76UCsC8KA2tROg3ksjlMj4t46F5qxkqrsHfuEgBWN0WUNT5Vw4yNNcCG6nmAwKBlTo7wTArtyCaChnjw690oJH8fhiH21-lk4WSfyTeyld8ZqLmkj0pfks_dqnclCb9jDb4HEN_GDtA'
          }


async def add_in_db(request):
    data = []
    request = loads(request)
    for slot in request['prices']:
        if slot['amount'] == 1:
            data.append((slot['time'], slot['price']))
    async with sql.connect('DataBase.db') as db:
        await db.executemany("""
                             INSERT INTO stand_2_month(date, price)
                             VALUES(?, ?)
                             """, data)
        await db.commit()


async def fetch_data(offset):
    querystring = {"offset": str(offset), "limit": str(limit)}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, params=querystring) as response:
            status = response.status
            if status == 200:
                await add_in_db(await response.text())
            return status


async def main():
    print(f'All CHUNCKs: {end // limit}')
    for chunck in range(0, end // limit, 25):
        print(f'CHUNCKs {chunck}-{chunck + 25}')
        fstart = chunck * limit
        fend = fstart + 25 * limit + 1
        start_time = time.time()
        tasks = [fetch_data(offset) for offset in range(fstart, fend, limit)]
        results = await asyncio.gather(*tasks)
        elapsed_time = time.time() - start_time
        print(elapsed_time)

        for offset, result in zip(range(fstart, fend, limit), results):
            print(f'Data from offset: {offset}: {result}')


async def get_data():
    data = {
        'dates': [],
        'prices': []
    }
    async with sql.connect('DataBase.db') as db:
        cur = await db.execute("""SELECT strftime('%Y-%m-%d %H:00:00', date) AS hour, 
                                  CAST(AVG(price) / 100 AS INTEGER) * 100 AS average_price
                                  FROM stand_2_month
                                  GROUP BY hour
                                  ORDER BY hour;""")
        for slot in await cur.fetchall():
            data['dates'].append(slot[1])
            data['prices'].append(slot[0])
        return data


async def create_chart():
    data = await get_data()

    plt.plot(data['prices'], data['dates'], label='Линия 1')

    # Добавляем заголовок и метки осей
    plt.title('График цены стандарток за эти три месяца')
    plt.xlabel('Дата')
    plt.ylabel('Цена')

    # Добавляем легенду
    plt.legend()

    # Показываем график
    plt.show()


if __name__ == '__main__':
    asyncio.run(main())













# for offset in range(start, end, limit):
#     querystring = {"offset": str(offset), "limit": str(limit)}
#
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": AUTH_TOKEN["token_type"] + ' ' + AUTH_TOKEN["access_token"]
#     }
#
#     response = request("GET", url, headers=headers, params=querystring)
#
#     print(response.text)

