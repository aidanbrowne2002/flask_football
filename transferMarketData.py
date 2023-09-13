import requests # to make the request to the web address
from bs4 import BeautifulSoup as bs # to pull data from HTML
import csv # to put the data in the csv file
import re # to handle regex
import pandas as pd # to show result

'''
1. format_text function that takes a string and removes some chars like double with spaces or escape sequences
'''


def format_text(text):
    regex = re.compile(r'[\n\r\t]')
    text = regex.sub('', text)
    return " ".join(text.split())


'''
2. format_currency function process the currency
'''


def format_currency(value):
    value = value.replace('€', '')
    value = value.replace('-', '0')
    value = value.replace('Loan fee:', '')
    value = value.replace('-', '0')
    value = value.replace('?', '0')
    value = value.replace('loan transfer', '0')
    value = value.replace('free transfer', '0')

    if value[-1] == 'm':
        value = value.replace('m', '')
        return float(value)

    if value[-1] == '.':
        value = value.replace('.', '')
        if value[-2:] == 'Th':
            value = value.replace('Th', '')
            return float(value) / 1000
    return value


'''
3. create a new column loan
'''


def loan_transform(value):
    if bool(re.match('loan', value, re.I)):
        bool_value = True
        return bool_value
    else:
        bool_value = False
        return bool_value


'''
4. get_data function responsible for accessing the pages, transforming the HTML into a soup object, looking for an element
with the responsive-table class,  iterate all the even and odd classes to get the ‘tds’ or cell and then create
a dictionary with the information we need, appending the var player to the players_list and finally return on
'''


def get_data(pages):
    players_list = []
    for page in range(1, pages + 1):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
        url = f'https://www.transfermarkt.com/transfers/saisontransfers/statistik/top/plus/1/galerie/0?saison_id=2023&transferfenster=sommertransfers&land_id=&ausrichtung=&spielerposition_id=&altersklasse=&leihe=&page={page}'
        # print(url)

        html = requests.get(url, headers=headers)
        soup = bs(html.content)
        soup = soup.select('.responsive-table > .grid-view > .items > tbody')[0]

        try:
            for cells in soup.find_all(True, {"class": re.compile("^(even|odd)$")}):
                fee = cells.find_all('td')[16].text
                loan = cells.find_all('td')[16].text
                position = cells.find_all('td')[4].text
                age = cells.find_all('td')[5].text
                market_value = cells.find_all('td')[6].text
                try:
                    country_from = cells.find_all('td')[11].img['title']
                except:
                    country_from = None
                    pass
                league_from = cells.find_all('td')[11].a.text if cells.find_all('td')[
                                                                     11].a != None else 'Without League'
                club_from = cells.find_all('td')[9].img['alt']
                country_to = cells.find_all('td')[15].img['alt']
                league_to = cells.find_all('td')[15].a.text if cells.find_all('td')[15].a != None else 'Without League'
                club_to = cells.find_all('td')[13].img['alt']

                player = {
                    'name': cells.find_all('td')[1].select('td > img')[0]['title'],
                    'position': position,
                    'age': age,
                    'market_value': format_currency(market_value),
                    'country_from': country_from,
                    'league_from': format_text(league_from),
                    'club_from': club_from,
                    'country_to': country_to,
                    'league_to': format_text(league_to),
                    'club_to': club_to,
                    'fee': format_currency(fee),
                    'loan': loan_transform(loan),
                }

                players_list.append(player)
        except IndexError:
            pass

    return players_list


'''
5. data_to_csv function which receives a list to save a csv output file
'''


def data_to_csv(data):
    keys = data[0].keys()
    with open('data.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)



data = get_data(80)

df = pd.DataFrame(data=data)
df.head(1)

print(f'Number of rows is {df.shape[0]}')
#print(f'Number of Nones is {df.isna().sum().sum()} in a column {df.columns[df.isna().any()].tolist()[0]}')
data_to_csv(data)