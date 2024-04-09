import requests
from bs4 import BeautifulSoup
import json
import os
import codecs
import time
from tqdm import tqdm
headers_get = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Cookie': 'FSize=M; FSize=M; __RequestVerificationToken=0x4WQ2_ArLMaBclx-C-gvDpzg2b5wb1ch-UhNcGOxWMuY8ABMrp-jrSolVTOP5RlKMJTPxbwoiiTLnFBQKGfWoXUwjI1',
}
headers_post = {
    'authority': 'www.cpbl.com.tw',
    'method': 'POST',
    'path': '/team/getfollowscore',
    'scheme': 'https',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-TW,zh;q=0.5',
    'Content-Length': '78',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'FSize=M; FSize=M; __RequestVerificationToken=0x4WQ2_ArLMaBclx-C-gvDpzg2b5wb1ch-UhNcGOxWMuY8ABMrp-jrSolVTOP5RlKMJTPxbwoiiTLnFBQKGfWoXUwjI1',
    'Origin': 'https://www.cpbl.com.tw',
    'Referer': 'https://www.cpbl.com.tw/team/follow?Acnt=0000000929',
    'Requestverificationtoken': 'F6CBjz9VyZlfeRni9RVDSYsi1uifrBmXopone1rK8Oq5OSwkT-d7ShNDj9Hw_xUlXcHiS4c3owAieoYG_JYACf4fElA1:Wb_PysN7xSmagp77Hygx6gDWjgbwD6dTGCsxzSgh7_DvG30eMY6ebf8Ah80rJGpq4_LHIbeDyK80S2tUYjO05I1y6Yc1',
    'Sec-Ch-Ua': '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Gpc': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
def get_player_acnt():
    player_acnt_list = {}
    url = 'https://www.cpbl.com.tw/player'
    response = requests.get(url, headers=headers_get)
    soup = BeautifulSoup(response.text, 'html.parser')
    teams_list = soup.find_all(name = 'div', attrs={'class':'PlayersList'})
    for team in teams_list:
        players = team.find_all('a')
        for player in players:
            acnt = player['href'].split('=')[-1]
            player_name = player.text
            player_acnt_list[player_name] = acnt
    with open('player_acnt_list.json', 'w', encoding='utf-8') as file:
        json.dump(player_acnt_list, file, ensure_ascii=False, indent=4)
def get_player_performance(player_name,acnt):
    dir = './player_performance/'
    url = f'https://www.cpbl.com.tw/team/person?acnt={acnt}'
    response = requests.get(url, headers=headers_get)
    soup = BeautifulSoup(response.text, 'html.parser')
    defendStation = soup.find('div', class_='desc').text
    data = {
            'acnt': f'{acnt}',
            'defendStation': f'{defendStation}',
            'year': '2024',
            'kindCode': 'A'
    }

    url = 'https://www.cpbl.com.tw/team/getfollowscore'
    response = requests.post(url,headers=headers_post,data=data)
    if response.status_code == 200:
        # Decode the JSON string
        decoded_data = json.loads(response.text)
        # Print the decoded data
        tables = decoded_data['FollowScore']
        if tables=="[]":
            #print('No data',player_name)
            return
        # Convert the string type dictionary to a dictionary
        tables = json.loads(tables)
        for key in ['SId', 'KindCode', 'FightTeamCode']:
            tables[0].pop(key, None)
        if defendStation == '投手':
            player_name = tables[0]['PitcherName']
        else:
            player_name = tables[0]['HitterName']
        # Load JSON from file if it exists
        if os.path.exists(dir+player_name+'.json'):
            with open(dir+player_name+'.json', 'r',encoding='utf-8') as file:
                json_data = json.load(file)
        else:
            # Create an empty dictionary
            json_data = {}
            # Iterate over the keys in tables
            for key in tables[0]:
                # Add the key to the dictionary with an empty list as the value
                json_data[key] = []
        if tables[0]['GameDate'] in json_data['GameDate']:
            #print('Data already exists',player_name)
            return
        for i in tables[0]:
            json_data[i].append(tables[0][i])
        # Save the dictionary to a JSON file with Chinese characters
        with open(dir+player_name+'.json', 'w', encoding='utf-8') as file:
            json.dump(json_data, file, ensure_ascii=False, indent=4)
    else:
        print('Request failed. Status code:', response.status_code)


def main():
    start_time = time.time()
    if not os.path.exists('./player_performance/'):
        os.makedirs('./player_performance/')
    if not os.path.exists('player_acnt_list.json'):
        get_player_acnt()
    with open('player_acnt_list.json', 'r', encoding='utf-8') as file:
        player_acnt_list = json.load(file)
    for player_name, acnt in player_acnt_list.items():
        get_player_performance(player_name,acnt)
        time.sleep(0.1)
    end_time = time.time()
    execution_time = end_time - start_time
    execution_hours = execution_time // 3600
    execution_minutes = (execution_time % 3600) // 60
    execution_seconds = execution_time % 60
    print(f"Execution time: {execution_hours} hours, {execution_minutes} minutes, {execution_seconds} seconds")
if __name__ == '__main__':
    main()    
