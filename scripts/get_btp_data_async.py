import aiohttp
import asyncio
from aiocache import cached, Cache
from bs4 import BeautifulSoup as ws


class BTP:
    def __init__(self, isin, description, market_price, variation, coupon_periodity, coupon, maturity_date, nominal_value, gross_yield, net_yield):
        self.isin = isin
        self.description = description
        self.market_price = market_price
        self.variation = variation
        self.coupon_periodity = coupon_periodity
        self.coupon = coupon
        self.maturity_date = maturity_date
        self.nominal_value = nominal_value
        self.gross_yield = gross_yield
        self.net_yield = net_yield


def clear_data(data):
    return data.replace('-', '').strip()


@cached(ttl=7200, cache=Cache.MEMORY)
async def ws_get_summary_price(scraping):
    summary_values = scraping.find('div', {'class': 'summary-value'})

    if summary_values:
        market_price = clear_data(summary_values.find_all('span')[0].text)
        variation = clear_data(summary_values.find_all('span')[1].text)

        if '-' not in variation and '+' not in variation:
            variation = '-' + variation

        return market_price, variation


@cached(ttl=7200, cache=Cache.MEMORY)
async def ws_get_specific_details(scraping):
    maturity_found = False
    periodity_found = False
    coupon_found = False
    nominal_found = False
    gross_found = False
    net_found = False

    page_tables = scraping.find_all('article')

    coupon = 0
    coupon_periodity = ""
    maturity_date = ""
    nominal_value = 0
    gross_yield = 0
    net_yield = 0

    if not all([gross_found, net_found, nominal_found, maturity_found, coupon_found, periodity_found]):
        for table in page_tables:
            title = table.find('h3', {'class': 't-text -flola -size-lg -uppercase'})

            if title:
                table_tile = clear_data(title.text)

                if "Rendimenti Effettivi" or "Info Strumento" in table_tile:
                    for row in table.find_all('tr'):
                        entries = row.find_all('td')

                        if entries:
                            for cell in entries:
                                cell_title = cell.find('strong')

                                if cell_title:
                                    cleared_title = clear_data(cell_title.text)

                                    if "Rendimento effettivo a scadenza lordo" in cleared_title and not gross_found:
                                        gross_yield = clear_data(entries[1].text)
                                        gross_found = True

                                    elif "Rendimento effettivo a scadenza netto" in cleared_title and not net_found:
                                        net_yield = clear_data(entries[1].text)
                                        net_found = True

                                    elif "Lotto Minimo" in cleared_title and not nominal_found:
                                        nominal_value = clear_data(entries[1].text)
                                        nominal_found = True

                                    elif "Scadenza" in cleared_title and not maturity_found:
                                        maturity_date = clear_data(entries[1].text)
                                        maturity_found = True

                                    elif "Periodicità cedola" in cleared_title and not periodity_found:
                                        coupon_periodity = clear_data(entries[1].text)
                                        periodity_found = True

                                    elif "Tasso Cedola Periodale" in cleared_title and not coupon_found:
                                        coupon = clear_data(entries[1].text)
                                        coupon_found = True

            else:
                continue

    return gross_yield, net_yield, coupon_periodity, coupon, maturity_date, nominal_value


@cached(ttl=7200, cache=Cache.MEMORY)
async def ws_get_isin_codes():
    base_url = 'https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/lista.html?&page='
    page_number = 1
    isin_list = []

    async with aiohttp.ClientSession() as session:
        while True:
            url = base_url + str(page_number)

            async with session.get(url) as response:
                if response.status == 429:
                    retry_cooldown = int(response.headers['Retry-After'])

                    print(f"Rate limit exceeded (ws_get_isin_code), waiting {retry_cooldown}secs for cooldown...")

                    await asyncio.sleep(retry_cooldown)

                    continue

                scraping = ws(await response.text(), 'html5lib')

                entries_find = False

                isin_table = scraping.find('table', {'class': 'm-table -firstlevel'})

                if isin_table.find_all('tr') and not entries_find:
                    for row in isin_table.find_all('tr'):
                        entries = row.find_all('td')

                        if entries:
                            entries_find = True

                            for cells in entries:
                                cell_title = cells.find_all('strong')

                                if cell_title and 'IT' in cell_title[0].text:
                                    isin_list.append(clear_data(cell_title[0].text))

                if not entries_find:
                    break

                page_number += 1

    return isin_list


@cached(ttl=7200, cache=Cache.MEMORY)
async def ws_get_btp_details(session, isin):
    url = f'https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-in-euro/scheda/{isin}.html'

    while True:
        async with session.get(url) as response:
            if response.status == 429:
                retry_cooldown = int(response.headers['Retry-After'])

                print(f"Rate limit exceeded (ws_get_btp_details), waiting {retry_cooldown}secs for cooldown...")

                await asyncio.sleep(retry_cooldown)

                continue

            scraping = ws(await response.text(), 'html5lib')

            description = clear_data(scraping.find('a', {'href': f'/borsa/obbligazioni/mot/btp/scheda/{isin}.html?lang=it'}))
            market_price, variation = await ws_get_summary_price(scraping)
            gross_yield, net_yield, coupon_periodity, coupon, maturity_date, nominal_value = await ws_get_specific_details(scraping)

            return BTP(isin, description, market_price, variation, coupon_periodity, coupon, maturity_date, nominal_value, gross_yield, net_yield)


async def get_btp_data():
    isin_list = await ws_get_isin_codes()

    async with aiohttp.ClientSession() as session:
        tasks = [ws_get_btp_details(session, isin) for isin in isin_list]
        btps = await asyncio.gather(*tasks)

        return btps


if __name__ == "__main__":
    asyncio.run(get_btp_data())
