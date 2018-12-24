from connectDB import *

name_dict = {'jxf': '孙悟空', 'nbb': '牛哔哔', 'bb': '无名'}
def modifyData(session, games, nickname):
    for game in games:
        name_zh_home = getnameZh(session, nickname, game.home)
        if name_zh_home:
            game.home = name_zh_home
        name_zh_away = getnameZh(session, nickname, game.away)
        if name_zh_away:
            game.away = name_zh_away

        game.hdp = eval(game.handicap)
        game.tot = eval(game.total)

        #printInfo(game, name_dict[nickname])
def getPairs(session):
    jxf_games = getrecords(session, jxfGame)
    nbb_games = getrecords(session, newbbGame)

    modifyData(session, jxf_games, 'jxf')
    modifyData(session, nbb_games, 'nbb')

    for jxf_game in jxf_games:

        for nbb_game in nbb_games:

            if jxf_game.game_league == nbb_game.game_league and \
                jxf_game.game_league == nbb_game.game_league and \
                (jxf_game.home in nbb_game.home or nbb_game.home in jxf_game.home or
                 jxf_game.away in nbb_game.away or nbb_game.away in jxf_game.away):

                printParisTitle('jxf', 'nbb', nbb_game)
                print("*" * 50)
                for jxf_hdp, jxf_odds in jxf_game.hdp.items():

                    for nbb_hdp, nbb_odds in nbb_game.hdp.items():


                        if rev(jxf_hdp) == nbb_hdp:

                            ret = 1 / (1 / float(jxf_odds[0]) + 1 / float(nbb_odds[0]))

                            printPairsInfo(jxf_hdp, nbb_hdp, jxf_odds[0], nbb_odds[0], ret, 0.989)

                for jxf_tot, jxf_odds in jxf_game.tot.items():

                    for nbb_tot, nbb_odds in nbb_game.tot.items():


                        if rev(jxf_tot) == nbb_tot:

                            ret = 1 / (1 / float(jxf_odds[0]) + 1 / float(nbb_odds[0]))

                            printPairsInfo(jxf_tot, nbb_tot, jxf_odds[0], nbb_odds[0], ret, 0.989)
                print("*" * 50)

def rev(str):
    rev_str = ''
    for i in str:
        if i == 'h':
            i = 'a'
        elif i == 'a':
            i = 'h'
        elif i == '+':
            i = '-'
        elif i == '-':
            i = '+'
        elif i == 'o':
            i = 'u'
        elif i == 'u':
            i = 'o'
        rev_str += i
    return rev_str


def printSingleInfo(game, nickename):
    print("平台: {}".format(nickename))
    print("联赛: {}".format(game.game_league))
    print("日期: {}".format(game.game_date))
    print("主队: {:^6}       客队: {:^6}".format(game.home, game.away))

    print("\n让球盘:")

    i = 0
    for hdp, odds in game.hdp.items():
        if i % 2 == 0 and i != 0:
            print()
        print("{:^6}: {:^6}".format(hdp, odds[0]), end='    ')
        i += 1

    print("\n\n大小盘:")
    i = 0

    for tot, odds in game.tot.items():
        if i % 2 == 0 and i != 0:
            print()
        print("{:^6}: {:^6}".format(tot, odds[0]), end='    ')
        i += 1
    print("\n" + "-"*32)

def printParisTitle(name1, name2, game):
    print("配偶: {} && {}".format(name_dict[name1], name_dict[name2]))
    print("联赛: {}".format(game.game_league))
    print("日期: {}".format(game.game_date))
    print("主队: {:^6}        客队: {:^6}".format(game.home, game.away))

def printPairsInfo(hdp1, hdp2, odd1, odd2, ret, threshold):
    print("{:^6} : {:^6}   {:^6} : {:^6}   Ret = {:^6.5f}| ".format(hdp1, odd1, hdp2, odd2, ret), end='')
    if ret > threshold:
        print('good!', end='')
    print()
def main():
    session = connectDB('10.210.82.148')
    getPairs(session)
    pass

if __name__ == '__main__':
    main()