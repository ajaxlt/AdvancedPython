from selenium import webdriver
import time
import datetime
import copy

import connectDB

def getNewBB(_driver, url, iframe):

    _driver.get(iframe)
    _driver.implicitly_wait(10)

    time.sleep(10)

def selectLeague(_driver, league_info, league_flag, time_flag):

    if not time_flag:
        _driver.find_element_by_xpath('//p[text()="FUTURE "]').click()
        time.sleep(10)


    while True:
        try:
            _driver.find_element_by_xpath('//p[text()="Select competition"]').click()
            time.sleep(2)

        except Exception as e:
            print(e)
            _driver.refresh()
            time.sleep(10)

        try:
            if league_flag:
                _driver.find_element_by_xpath('//label[text()="Check all"]').click()
                time.sleep(1)
            _driver.find_element_by_xpath('//label[text()="Check all"]').click()
            time.sleep(1)
            for ele in league_info:
                _driver.find_element_by_xpath('//label[text()="{}"]'.format(ele.league_name_newbb)).click()

            _driver.find_element_by_xpath('//button[@ng-disabled="!enableFiltering"]').click()

            time.sleep(5)
            break
        except Exception as e:
            print(e)
            _driver.refresh()
            time.sleep(10)

def getGameNode(_driver, leagues, newbb_game_node):
    numOfleagues = len(leagues)
    for i in range(numOfleagues):
        cur_league_node = '//*[@id="asianView"]/div/div[3]/div[4]/div/ng-include/div[2]/div[2]/div[{}]'.format(i + 1)
        cur_league_name = _driver.find_element_by_xpath(cur_league_node + "/div/h3").text
        for league in leagues:
            try:
                if cur_league_name == league.league_name_newbb.upper():
                    cur_league_name = league.league_name_zh
                    break
            except:
                return
        cur_league_games = _driver.find_elements_by_xpath(cur_league_node + '/table/tbody')

        for j in range(len(cur_league_games)):
            cur_league_game_node = cur_league_node + '/table/tbody[{}]'.format(j + 1)
            newbb_game_node.append([cur_league_game_node, cur_league_name])

def fetchOdds(_driver, newbb_rlt, cur_game_xpath):
    item = connectDB.newbbGame()
    item.game_league = cur_game_xpath[1]

    '''date-time'''
    try:
        cur_year = time.strftime("%Y", time.localtime())
        game_date = _driver.find_element_by_xpath(cur_game_xpath[0] + '/tr[2]/td[1]/small[2]').text
        game_time = _driver.find_element_by_xpath(cur_game_xpath[0] + '/tr[2]/td[1]/small[4]').text
        item.game_date = datetime.datetime.strptime(cur_year + '/' + game_date + ' ' + game_time, '%Y/%m/%d %H:%M') + datetime.timedelta(hours=12)
    except Exception as e:
        print(e)
        return

    '''home-away'''
    try:
        item.home = _driver.find_element_by_xpath(cur_game_xpath[0] + '/tr[2]/td[2]/div/div[1]/p').text
        item.away = _driver.find_element_by_xpath(cur_game_xpath[0] + '/tr[3]/td[1]/div/div[1]/p').text
    except Exception as e:
        print(e)
        return

    '''numOfhandicap'''
    try:
        numOfhdp = int(len(_driver.find_elements_by_xpath(cur_game_xpath[0] + '/tr[@class="ng-scope"]')) / 2) + 1
        #print(item.game_date, item.game_league, item.home, item.away, "numOfhdp:", numOfhdp)
    except Exception as e:
        print(e)
        return

    handicap = {}
    total = {}

    '''handicap 1 && total1'''
    try:
        makeHdp(_driver, cur_game_xpath[0], [2, 4], [3, 3], handicap)
        makeTot(_driver, cur_game_xpath[0], [2, 5], [3, 4], total)
    except Exception as e:
        print(e)

    '''handicap 2-4 && total 2-4'''
    for i in range(1, numOfhdp):
        try:
            makeHdp(_driver, cur_game_xpath[0], [2 * i + 3, 4], [2 * i + 4, 4], handicap)
            makeTot(_driver, cur_game_xpath[0], [2 * i + 3, 5], [2 * i + 4, 5], total)
        except Exception as e:
            print(e)

    item.handicap = str(handicap)
    item.total = str(total)
    item.game_id = item.home + ' vs ' + item.away
    # print(item.handicap)
    # print(item.total)

    newbb_rlt.append(copy.deepcopy(item))

def makeHdp(_driver, root_node, ads1, ads2, handicap):
    hdp1_1 = _driver.find_element_by_xpath(root_node + '/tr[{}]/td[{}]/div/div/div[1]/div'.format(ads1[0], ads1[1])).text.replace(' ', '')
    hdp1_2 = _driver.find_element_by_xpath(root_node + '/tr[{}]/td[{}]/div/div/div[1]/div'.format(ads2[0], ads2[1])).text.replace(' ', '')

    if hdp1_1:
        if hdp1_1 == '0':
            hdp_home = 'h0'
            hdp_away = 'a0'
        else:
            hdp1_1 = modifyHdp(hdp1_1)
            hdp_home = 'h-' + hdp1_1
            hdp_away = 'a+' + hdp1_1

    elif hdp1_2:
        if hdp1_2 == '0':
            hdp_home = 'h0'
            hdp_away = 'a0'
        else:
            hdp1_2 = modifyHdp(hdp1_2)
            hdp_home = 'h+' + hdp1_2
            hdp_away = 'a-' + hdp1_2
    else:
        return

    hdp_odds_id_home = root_node + '/tr[{}]/td[{}]/div/div/div[2]'.format(ads1[0], ads1[1])
    hdp_odds_home = _driver.find_element_by_xpath(hdp_odds_id_home).text
    hdp_odds_home = "{:.2f}".format(float(hdp_odds_home) + 1)

    hdp_odds_id_away = root_node + '/tr[{}]/td[{}]/div/div/div[2]'.format(ads2[0], ads2[1])
    hdp_odds_away = _driver.find_element_by_xpath(hdp_odds_id_away).text
    hdp_odds_away = "{:.2f}".format(float(hdp_odds_away) + 1)

    handicap[hdp_home] = [hdp_odds_home, hdp_odds_id_home]
    handicap[hdp_away] = [hdp_odds_away, hdp_odds_id_away]

def makeTot(_driver, root_node, ads1, ads2, total):
    tot = _driver.find_element_by_xpath(root_node + '/tr[{}]/td[{}]/div/div/div[1]/div'.format(ads1[0], ads1[1])).text.replace(' ', '')[1:]

    tot = modifyHdp(tot)
    over = 'o' + tot
    under = 'u' + tot

    tot_odds_id_over = root_node + '/tr[{}]/td[{}]/div/div/div[2]'.format(ads1[0], ads1[1])
    tot_odds_over = _driver.find_element_by_xpath(tot_odds_id_over).text
    tot_odds_over = "{:.2f}".format(float(tot_odds_over) + 1)

    tot_odds_id_under = root_node + '/tr[{}]/td[{}]/div/div/div[2]'.format(ads2[0], ads2[1])
    tot_odds_under = _driver.find_element_by_xpath(tot_odds_id_under).text
    tot_odds_under = "{:.2f}".format(float(tot_odds_under) + 1)

    total[over] = [tot_odds_over, tot_odds_id_over]
    total[under] = [tot_odds_under, tot_odds_id_under]



def modifyHdp(hdp):
    if '/' in hdp:
        hdp = hdp.split('/')
        return str((float(hdp[0]) + float(hdp[1])) / 2)

    else:
        return hdp
def main():
    driver = webdriver.Chrome(executable_path=r'/home/bupt334/Application/calculator2.0/spider/chromedriver')
    getNewBB(driver, '', 'https://sportsbook4.betcoapps.com/#/sport/?containerID=bcsportsbookcontainer&lang=eng&type=0&sport=1&menuType=2&adpage=')

    league_zh = ['英超', '意甲', '意乙']
    session = connectDB.connectDB('10.210.82.148')

    league_info = connectDB.getleague(session, league_zh)
    #print(league_info)

    newbb_game_node = []
    selectLeague(driver, league_info, 0, 1)
    getGameNode(driver, league_info, newbb_game_node)

    for item in newbb_game_node:
        fetchOdds(driver, [], item)
    time.sleep(500)


if __name__ == '__main__':
    main()