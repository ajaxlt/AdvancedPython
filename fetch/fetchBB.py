import time
import datetime
import requests
import random
import json
import copy

import connectDB


def getHTMLText(url):
    try:
        ip = ['121.31.159.197', '170.30.238.78', '124.202.247.110', '122.156.129.201', '120.2.28.44', '218.8.204.12', '121.26.67.240', '221.193.83.116']
        brower = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'
        head = {'user-agent': brower,
                'X-Forwared-For': ip[random.randint(0, len(ip)-1)],
                'Accept-Language': 'en'}
        r = requests.get(url, headers=head, timeout=5)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print(e)
        print("Failed to getHTML: " + url)
        return None

def fetchOdds(time_flag, league_name, bb_rlt):

    if not time_flag:
        date = time.strftime("%Y-%m-%d", time.localtime())
        url = "https://cc9288.com/sport/rest/odds/getOddsListBasic.json?odds_type=0&period=future&game_type=FT&play_type=S&cb=N&modify_ts=0&date%5B%5D={}&gid_list=%5B%5D&_=1522293922816".format(date)

    else:
        url = "https://cc9288.com/sport/rest/odds/getOddsListBasic.json?odds_type=0&period=today&game_type=FT&play_type=S&cb=N&modify_ts=0&gid_list=%5B%5D&_=1522232273865"

    myHtml = getHTMLText(url)
    myJson = json.loads(myHtml)

    league_id_info = myJson["data"]["league"]

    games_id = []
    for id, name in league_id_info.items():
        if name in league_name.keys():
            games_id += (myJson["data"]["insert"][id])

    for game_id in games_id:
        if '(' in myJson["data"]["game"][game_id]["tid_h"]:
            continue
        item = connectDB.bbGame()

        item.game_id = game_id
        cur_node = myJson["data"]["game"][game_id]

        league_id = cur_node["lid"]

        item.home = cur_node["tid_h"]
        item.away = cur_node["tid_a"]
        item.game_date = datetime.datetime.strptime(cur_node["game_date"] + ' ' + cur_node["game_time"], '%Y-%m-%d %H:%M') + datetime.timedelta(hours=12)
        item.game_league = league_name[myJson["data"]["league"][league_id]]

        odds_node = myJson["data"]["insert"][league_id][game_id]["S"]
        # only need 16
        handicap = {}

        '''handicap'''
        if odds_node[0]:
            hdp = modifyHdp(str(odds_node[0]))
            if hdp == '0':
                hdp_home = 'h0'
                hdp_away = 'a0'
            else:
                hdp_home = 'h-' + hdp
                hdp_away = 'a+' + hdp
            xpath_home = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[1]/td[4]/div[2]/div[1]/a"
            xpath_away = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[1]/td[4]/div[2]/div[2]/a"

            handicap[hdp_home] = ["{:.3f}".format(float(odds_node[2]) + 1), xpath_home]
            handicap[hdp_away] = ["{:.3f}".format(float(odds_node[3]) + 1), xpath_away]

        elif odds_node[1]:
            hdp = modifyHdp(str(odds_node[1]))
            hdp_home = 'h+' + hdp
            hdp_away = 'a-' + hdp
            xpath_home = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[1]/td[4]/div[2]/div[1]/a"
            xpath_away = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[1]/td[4]/div[2]/div[2]/a"
            handicap[hdp_home] = ["{:.3f}".format(float(odds_node[2]) + 1), xpath_home]
            handicap[hdp_away] = ["{:.3f}".format(float(odds_node[3]) + 1), xpath_away]

        if odds_node[4]:
            hdp = modifyHdp(str(odds_node[4]))
            if hdp == '0':
                hdp_home = 'h0'
                hdp_away = 'a0'
            else:
                hdp_home = 'h-' + hdp
                hdp_away = 'a+' + hdp
            xpath_home = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[2]/td[3]/div[2]/div[1]/a"
            xpath_away = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[2]/td[3]/div[2]/div[2]/a"
            handicap[hdp_home] = ["{:.3f}".format(float(odds_node[6]) + 1), xpath_home]
            handicap[hdp_away] = ["{:.3f}".format(float(odds_node[7]) + 1), xpath_away]

        elif odds_node[5]:
            hdp = modifyHdp(str(odds_node[5]))
            hdp_home = 'h+' + hdp
            hdp_away = 'a-' + hdp
            xpath_home = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[1]/td[4]/div[2]/div[1]/a"
            xpath_away = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[1]/td[4]/div[2]/div[2]/a"
            handicap[hdp_home] = ["{:.3f}".format(float(odds_node[6]) + 1), xpath_home]
            handicap[hdp_away] = ["{:.3f}".format(float(odds_node[7]) + 1), xpath_away]


        total = {}
        '''total'''
        if odds_node[8]:
            tot = modifyHdp(str(odds_node[8]))
            over = 'o' + tot
            under = 'u' + tot
            xpath_over = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[1]/td[5]/div[2]/div[1]/a"
            xpath_under = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[1]/td[5]/div[2]/div[2]/a"
            total[over] = ["{:.3f}".format(float(odds_node[10]) + 1), xpath_over]
            total[under] = ["{:.3f}".format(float(odds_node[11]) + 1), xpath_under]

        if odds_node[12]:
            tot = modifyHdp(str(odds_node[12]))
            over = 'o' + tot
            under = 'u' + tot
            xpath_over = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[2]/td[4]/div[2]/div[1]/a"
            xpath_under = "//*[@id=\"js-order-" + league_id + "-" + game_id + "\"]/tr[2]/td[4]/div[2]/div[2]/a"
            total[over] = ["{:.3f}".format(float(odds_node[14]) + 1), xpath_over]
            total[under] = ["{:.3f}".format(float(odds_node[15]) + 1), xpath_under]

        item.handicap = str(handicap)
        item.total = str(total)

        '''need to delete'''
        session = connectDB.connectDB('10.210.82.148')
        connectDB.submitOdds(session, item)

def modifyHdp(hdp):
    if '/' in hdp:
        hdp = hdp.split('/')
        return str((float(hdp[0]) + float(hdp[1])) / 2)

    else:
        return hdp

def main():
    bb_rlt = []
    fetchOdds(1, {'Italy Serie A': '意甲'}, bb_rlt)

if __name__ == '__main__':
    main()
