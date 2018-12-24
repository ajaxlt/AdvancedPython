from selenium import webdriver
import threading
import re


import connectDB
import fetch.fetchWellbet as wb
import fetch.fetchNewBB as nb
import fetch.fetchBB as bb

driver_path = r'/home/bupt334/Application/calculator2.0/spider/chromedriver'
class myThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        global connect
        if self.name:
            connect.send(str("Begin to " + self.name + '.').encode())
        self.func(*self.args)
        if self.name:
            connect.send(str(self.name + " done.").encode())


class myFecth():
    def __init__(self):
        self.driver_flag = False
        self.league_flag = False

        # todo

        self.time_flag = 1
    def setAttribute(self, conn, session, league_zh_str):
        global connect
        connect = conn
        self.session = session
        self.league_zh_str = league_zh_str


    def getDemand(self):
        global connect
        try:
            league_zh_list = re.split(',', self.league_zh_str)
            return connectDB.getleague(self.session, league_zh_list)
        except Exception as e:
            connect.send(str(e).encode())
            print(e)

    def openDriver(self):
        global connect
        toutou = connectDB.getUrl(self.session, 'toutou')
        newbb = connectDB.getUrl(self.session, 'newbb')

        self.driver_nbb = webdriver.Chrome(executable_path=driver_path)
        self.driver_tou = webdriver.Chrome(executable_path=driver_path)

        '''surf'''
        try:
            threads = []
            t1 = myThread(nb.getNewBB, [self.driver_nbb, newbb.url, newbb.iframe], 'open NewBB')
            t2 = myThread(wb.getWellbet, [self.driver_tou, toutou.url, toutou.iframe], 'open toutou')

            threads.append(t1)
            threads.append(t2)

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            self.driver_flag = True
        except Exception as e:
            connect.send(str(e).encode())
            print(e)

    def closeDriver(self):
        global connect
        if self.driver_flag:
            try:
                self.driver_tou.close()
                self.driver_nbb.close()
            except Exception as e:
                connect.send(str(e).encode())
                print(e)

            self.driver_flag = False
            self.league_flag = False

        else:
            connect.send(str('Driver is not open,').encode())


    def selectLeague(self):
        global connect

        '''league'''
        try:
            self.league_info = self.getDemand()

            threads = []
            t1 = myThread(nb.selectLeague, [self.driver_nbb, self.league_info, self.league_flag, self.time_flag], 'select newbb league')
            t2 = myThread(wb.selectLeague, [self.driver_tou, self.league_info, self.league_flag, self.time_flag], 'select toutou league')

            threads.append(t1)
            threads.append(t2)

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            self.league_flag = True
        except Exception as e:
            connect.send(str(e).encode())
            print(e)

    def getGameNode(self):
        global connect

        '''get game node'''
        self.newbb_game_xpath = []
        self.toutou_game_xpath = []
        nb.getGameNode(self.driver_nbb, self.league_info, self.newbb_game_xpath)
        wb.getGameNode(self.driver_tou, self.league_info, self.toutou_game_xpath)

    def fetch(self):
        global connect

        '''fetch'''
        try:
            threads = []
            newbb_rlt = []
            toutou_rlt = []
            bb_rlt = []

            '''toutou'''
            for i in self.toutou_game_xpath:
                thread = myThread(wb.fetchOdds, [self.driver_tou, toutou_rlt, i])
                threads.append(thread)

            '''newbb'''
            for i in self.newbb_game_xpath:
                thread = myThread(nb.fetchOdds, [self.driver_nbb, newbb_rlt, i])
                threads.append(thread)

            '''bb'''
            league_name_bb = {}
            for item in self.league_info:
                league_name_bb[item.league_name_bb] = item.league_name_zh
            threads.append(myThread(bb.fetchOdds, [self.time_flag, bb_rlt, league_name_bb]))

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            for rlt in toutou_rlt:
                connectDB.submitOdds(self.session, rlt)

            for rlt in newbb_rlt:
                connectDB.submitOdds(self.session, rlt)

            for rlt in bb_rlt:
                connectDB.submitOdds(self.session, rlt)

        except Exception as e:
            connect.send(str(e).encode())
            print(e)
        pass
