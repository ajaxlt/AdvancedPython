import time
import connectDB
import copy
from datetime import datetime


def getWellbet(_driver, url, iframe):

    _driver.get(url)
    _driver.implicitly_wait(10)

    while True:
        try:
            _driver.switch_to_frame(_driver.find_element_by_tag_name('iframe'))
            break
        except Exception as e:
            print(e)
            _driver.refresh()
            time.sleep(15)

    time.sleep(10)


def selectLeague(_driver, league_info, league_flag, time_flag):

    if not time_flag:  # early
        _driver.find_element_by_css_selector("[class='early filters']").click()
        time.sleep(3)
        _driver.find_element_by_css_selector("[class='dsp-iblk t-va-m lht-0p3 pd-l-10 pd-r-10 filters ft-c-6']").click()
        time.sleep(5)
    try:

        _driver.find_element_by_css_selector("[class='competitions fts-12 bg-c-5 radius ft-c-3 mg-r-10 lht-14']").click()
        time.sleep(3)

        if league_flag:
            all_select = _driver.find_element_by_xpath('//*[@id="cnr-comps"]/div[1]/div[1]/span[2]/span')
            all_select.click()
            time.sleep(1)
            all_select.click()
            time.sleep(1)

        for ele in league_info:
            try:
                _driver.find_element_by_xpath('//span[text()="' + ele.league_name_jxf + '"]').click()
                time.sleep(0.5)
            except Exception as e:
                print(e)
                try:
                    _driver.find_element_by_xpath('//span[text()="' + ele.league_country_jxf + '"]').click()
                    time.sleep(1)
                    _driver.find_element_by_xpath('//span[text()="' + ele.league_name_jxf + '"]').click()
                    time.sleep(0.5)
                except:
                    continue

        _driver.find_element_by_id('comp-submit').click()
        time.sleep(5)

    except Exception as e:
        print(e)


def getGameNode(_driver, leagues, jxf_game_node):
    for league in leagues:
        try:
            cur_node = '//*[@id="cnr-odds"]/div/div/div[3]/div//*[@id="{}"]'.format(league.league_id_jxf)
            all_games = _driver.find_elements_by_xpath(cur_node + '/table')
            for i in range(len(all_games)):
                cur_xpath = '{}/table[{}]'.format(cur_node, i + 1)
                jxf_game_node.append([cur_xpath, league.league_name_zh])
        except Exception as e:
            print(e)
            continue



def fetchOdds(_driver, toutou_rlt, cur_game_xpath):
    item = connectDB.jxfGame()
    ''' game_id '''
    cur_game_node = _driver.find_element_by_xpath(cur_game_xpath[0])
    item.game_league = cur_game_xpath[1]
    item.game_id = cur_game_node.get_attribute('id')

    try:
        trash_info = cur_game_node.get_attribute('pid')
        if trash_info:
            return
    except:
        print('err!')
        return

    try:
        game_node = '//table[@id="' + item.game_id + '"]'
        ''' game_date '''
        cur_year = time.strftime("%Y", time.localtime())
        game_date = _driver.find_element_by_xpath(game_node + '/tbody[1]/tr[1]/td[1]/div[1]').text + ' / {} '.format(cur_year) + \
                         _driver.find_element_by_xpath(game_node + '/tbody[1]/tr[1]/td[1]/div[2]').text
        item.game_date = datetime.strptime(game_date, '%d / %m / %Y %H:%M')
        ''' home '''
        item.home = _driver.find_element_by_xpath(game_node + '/tbody[1]/tr[1]/td[2]').text
        ''' away '''
        item.away = _driver.find_element_by_xpath(game_node + '/tbody[1]/tr[2]/td[1]').text
    except Exception as e:
        print(e)
        return

    all_hdps = {}
    all_tots = {}
    numOfHdp = len(_driver.find_elements_by_xpath(game_node + '/tbody'))
    for k in range(1, numOfHdp + 1):
        try:
            home_handicap = _driver.find_elements_by_xpath(game_node + '/tbody[' + str(k) + ']/tr[1]/td[5]/span/span')
            if len(home_handicap) == 2:
                if home_handicap[0].text == '0':
                    h_hdp = 'h0'
                    a_hdp = 'a0'
                else:
                    h_hdp = 'h-' + modifyHdp(home_handicap[0].text)
                    a_hdp = 'a+' + modifyHdp(home_handicap[0].text)

                h_odds = "{:.2f}".format(float(home_handicap[1].text) + 1)
                h_odds_id = home_handicap[1].get_attribute('id')

            else:
                h_odds = "{:.2f}".format(float(home_handicap[0].text) + 1)
                h_odds_id = home_handicap[0].get_attribute('id')

            away_handicap = _driver.find_elements_by_xpath(game_node + '/tbody[' + str(k) + ']/tr[2]/td[4]/span/span')
            if len(away_handicap) == 2:
                h_hdp = 'h+' + modifyHdp(away_handicap[0].text)
                a_hdp = 'a-' + modifyHdp(away_handicap[0].text)

                a_odds = "{:.2f}".format(float(away_handicap[1].text) + 1)
                a_odds_id = away_handicap[1].get_attribute('id')

            else:
                a_odds = "{:.2f}".format(float(away_handicap[0].text) + 1)
                a_odds_id = away_handicap[0].get_attribute('id')

            all_hdps[h_hdp] = [h_odds, h_odds_id]
            all_hdps[a_hdp] = [a_odds, a_odds_id]

        except Exception as e:
            print(e)
            continue



        try:
            over_handicap = _driver.find_elements_by_xpath(game_node + '/tbody[' + str(k) + ']/tr[1]/td[7]/span/span')

            o_hdp = 'o' + modifyHdp(over_handicap[0].text)
            u_hdp = 'u' + modifyHdp(over_handicap[0].text)
            o_odds = "{:.2f}".format(float(over_handicap[1].text) + 1)
            o_odds_id = over_handicap[1].get_attribute('id')

            under_handicap = _driver.find_elements_by_xpath(game_node + '/tbody[' + str(k) + ']/tr[2]/td[6]/span/span')

            if k == 1:
                u_odds = "{:.2f}".format(float(under_handicap[1].text) + 1)
                u_odds_id = under_handicap[1].get_attribute('id')
            else:
                u_odds = "{:.2f}".format(float(under_handicap[0].text) + 1)
                u_odds_id = under_handicap[0].get_attribute('id')

            all_tots[o_hdp] = [o_odds, o_odds_id]
            all_tots[u_hdp] = [u_odds, u_odds_id]
        except Exception as e:
            print(e)
            continue

    item.handicap = str(copy.deepcopy(all_hdps))
    item.total = str(copy.deepcopy(all_tots))

    toutou_rlt.append(copy.deepcopy(item))


def modifyHdp(hdp):
    if '/' in hdp:
        hdp = hdp.split('/')
        return str((float(hdp[0]) + float(hdp[1])) / 2)

    else:
        return hdp
