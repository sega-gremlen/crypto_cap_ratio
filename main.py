import json
import pprint
import re
import time
from datetime import datetime
import os

from dotenv import load_dotenv
import requests
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError

load_dotenv()


class Crypter:
    filter_coin_laucnch_date = datetime(year=2021, month=1, day=1)
    filter_toggle = False
    res_file_name = 'test.json'
    top_coins_count = 100
    cryptorank_api_key = os.getenv('CRYPTORANK_API_KEY')
    cmc_api_key = os.getenv('CMC_API_KEY')

    @classmethod
    def make_main_data(cls):
        """
        Collects primary data from Cryptorank API
        """
        url = "https://api.cryptorank.io/v2/currencies"

        headers = {
            "X-Api-Key": cls.cryptorank_api_key
        }

        params = {
            "limit": cls.top_coins_count
        }

        response = requests.get(url, headers=headers, params=params)

        coin_datas = response.json()

        with open(cls.res_file_name, 'w') as file:
            json.dump(coin_datas, file, indent=4)

    @classmethod
    def parse_ath_market_cap(cls):
        """
        Collects ATH market cap data from Cryptorank and adds it to the final JSON
        """

        def text_number_to_number(text_number):
            """
            Converts a text abbreviation number to int
            """
            result = float(re.search(r'\d+.*\d', text_number).group())

            if 'B' in text_number:
                return int(result * 1_000_000_000)
            elif 'M' in text_number:
                return int(result * 1_000_000)
            elif 'K' in text_number:
                return int(result * 100_000)
            elif 'T' in text_number:
                return int(result * 1_000_000_000_000)

        def parse_coin_page(cls, pw_page, coin_data):
            """
            Parses ATH market cap from the Cryptorank page
            """
            key = coin_data['key']
            current_mc = float(coin_data['marketCap'])
            link = f"https://cryptorank.io/price/{key}"

            with open(cls.res_file_name, 'r') as file:
                current_main_data = json.load(file)
                coin_index_in_main_data = current_main_data['data'].index(coin_data)

            print(f'{index}/{len(coin_datas)} Parsing ATH Market Cap for the coin {key}...')

            pw_page.goto(link)
            pw_page.wait_for_load_state("networkidle")
            ath_mc_div = pw_page.locator("text=ATH Market Cap").locator("xpath=../..")
            ath_mc_p = ath_mc_div.locator("p").nth(1)
            ath_mc_p_value = ath_mc_p.inner_text()
            ath_mc_value = text_number_to_number(ath_mc_p_value)

            with open(cls.res_file_name, 'r+') as file:
                main_data = json.load(file)
                if not coin_data['symbol'].isalnum():
                    main_data['data'].pop(coin_index_in_main_data)
                else:
                    main_data['data'][coin_index_in_main_data]['athMarketCap'] = int(ath_mc_value)
                file.seek(0)
                file.truncate()
                json.dump(main_data, file, indent=4)

        with open(cls.res_file_name, 'r') as f:
            coin_datas = json.load(f)['data']

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                pw_page = browser.new_page()

                for index, coin_data in enumerate(coin_datas, 1):
                    if 'athMarketCap' in coin_data.keys():
                        continue
                    parse_coin_page(cls, pw_page, coin_data)

        except TimeoutError:
            print('Timeout error, retrying in 5 seconds')
            time.sleep(5)
            cls.parse_ath_market_cap()

    @classmethod
    def take_launch_date_from_cmc(cls):
        """
        Collects launch date and initial data date from CoinMarketCap API and adds it to the final JSON
        """

        with open(cls.res_file_name, 'r') as f:
            main_data: list = json.load(f)['data']

        symbols = ','.join([i['symbol'] for i in main_data[:int(len(main_data) / 2)]])

        headers = {
            'X-CMC_PRO_API_KEY': cls.cmc_api_key,
            'Accept': 'application/json',
        }
        params = {
            'symbol': symbols,
        }
        url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
        response = requests.get(url, headers=headers, params=params)
        cmc_datas = response.json()

        for cmc_data in cmc_datas['data']:
            date_launched = cmc_datas['data'][cmc_data][0]['date_launched']
            date_cmc_added = cmc_datas['data'][cmc_data][0]['date_added']

            for coin_data in main_data:
                if cmc_datas['data'][cmc_data][0]['symbol'].lower() == coin_data['symbol'].lower():
                    coin_data['date_launched'] = date_launched
                    coin_data['date_cmc_added'] = date_cmc_added

        with open(cls.res_file_name, 'w') as f:
            json.dump(main_data, f, indent=4)

    @classmethod
    def filter_launch_date(cls):
        """
        Filters coins by launch date from 01.01.2021
        """

        def filter_func(item):
            current_keys = item.keys()

            if 'date_launched' in current_keys and item['date_launched']:
                coin_launched = item['date_launched']
            elif 'date_cmc_added' in current_keys and item['date_cmc_added']:
                coin_launched = item['date_cmc_added']
            else:
                return False

            coin_launched = datetime.strptime(coin_launched, "%Y-%m-%dT%H:%M:%S.%fZ")

            return coin_launched >= cls.filter_coin_laucnch_date

        with open(cls.res_file_name, 'r') as f:
            data = json.load(f)

        if cls.filter_toggle is False:
            return data
        else:
            filtered_coins = list(filter(filter_func, data))
            return filtered_coins

    @classmethod
    def sort_max_capa_ratio(cls, coin_list):
        """
        Sorts coins by the ratio of current market cap to all-time high market cap
        """

        sorted_data = sorted(coin_list, key=lambda i: i['athMarketCap'] / float(i['marketCap']), reverse=True)

        for number, item in enumerate(sorted_data, 1):
            print(f'{number}. Ratio: {(item['athMarketCap'] / float(item['marketCap'])):.2f}, '
                  f'https://cryptorank.io/price/{item['key']}')

    @classmethod
    def main(cls):
        cls.make_main_data()
        cls.parse_ath_market_cap()
        cls.take_launch_date_from_cmc()
        filtered_coins = cls.filter_launch_date()
        cls.sort_max_capa_ratio(filtered_coins)


if __name__ == '__main__':
    Crypter.main()
