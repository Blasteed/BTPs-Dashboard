import requests
from bs4 import BeautifulSoup as ws


class BTP:
    def __init__(self, isin, description, market_price, variation, coupon, maturity_date, nominal_value, gross_yield, net_yield):
        self.isin = isin
        self.description = description
        self.market_price = market_price
        self.variation = variation
        self.coupon = coupon
        self.maturity_date = maturity_date
        self.nominal_value = nominal_value
        self.gross_yield = gross_yield
        self.net_yield = net_yield
        # self.duration = duration


def clear_data(data):
    return data.replace('-', '').strip()


def ws_get_summary_price(scraping):
    summary_values = scraping.find('div', {'class': 'summary-value'})

    if summary_values:
        market_price = clear_data(summary_values.find_all('span')[0].text)
        variation = clear_data(summary_values.find_all('span')[1].text)

        return market_price, variation


def ws_get_specific_details(scraping):
    maturity_found = False
    coupon_found = False
    nominal_found = False
    gross_found = False
    net_found = False

    page_tables = scraping.find_all('article')

    coupon = 0
    maturity_date = ""
    nominal_value = 0
    gross_yield = 0
    net_yield = 0

    if not all([gross_found, net_found, nominal_found, maturity_found, coupon_found]):
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

                                    elif 'Scadenza' in cleared_title and not maturity_found:
                                        maturity_date = clear_data(entries[1].text)
                                        maturity_found = True

                                    elif "Tasso Cedola Periodale" in cleared_title and not coupon_found:
                                        coupon = clear_data(entries[1].text)
                                        coupon_found = True

            else:
                continue

    return coupon, maturity_date, nominal_value, gross_yield, net_yield


def ws_get_isin_codes():

    base_url = 'https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/lista.html?&page='
    page_number = 1
    isin_list = []

    while True:
        url = base_url + str(page_number)
        response = requests.get(url)
        scraping = ws(response.content, 'html5lib')

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


def ws_get_btp_details(isin):
    url = f'https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-in-euro/scheda/{isin}.html'
    response = requests.get(url)
    scraping = ws(response.content, 'html5lib')

    description = clear_data(scraping.find('a', {'href': f'/borsa/obbligazioni/mot/btp/scheda/{isin}.html?lang=it'}).text)
    market_price, variation = ws_get_summary_price(scraping)
    gross_yield, net_yield, coupon, maturity_date, nominal_value = ws_get_specific_details(scraping)
    # duration = scraping.find('span', {'id': 'id_duration'}).text.strip()

    return BTP(isin, description, market_price, variation, coupon, maturity_date, nominal_value, gross_yield, net_yield)


def main():
    isin_list = ws_get_isin_codes()
    btp_list = []

    for isin in isin_list:
        btp = ws_get_btp_details(isin)
        btp_list.append(btp)


if __name__ == "__main__":
    main()
