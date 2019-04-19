# -*- coding: utf-8 -*-
import random
import matplotlib.pyplot as plot
import numpy

color_book = {1: "♠", 2: "♥", 3: "♣", 4: "♦"}
num_book = {"J": 11, 11: "J", "Q": 12, 12: "Q", "K": 13, 13: "K", "A": 14, 14: "A"}
type_book = {100: "豹子", 101: "顺金", 102: "金花", 103: "顺子", 104: "对子",
             14: "散A", 13: "散K", 12: "散Q", 11: "散J", 10: "散10", 9: "散9", 8: "散8", 7: "散7", 6: "散6", 5: "散5"}
lvl_book = [100, 101, 102, 103, 104, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5]
card_book = list()
'''单张牌'''
class Card:
    def __init__(self, num, color = 1):
        self.num = num
        self.color = color
'''手牌'''
class Hand:
    def __init__(self, cardList):
        self.hand = sorted(cardList, key=lambda x: x.num, reverse=True)
    def parseType(self) -> int:
        #100. 豹子
        if self.hand[0].num == self.hand[1].num and self.hand[0].num == self.hand[2].num:
            return 100

        # 金花 & 顺金
        elif self.hand[0].color == self.hand[1].color and self.hand[0].color == self.hand[2].color:
            # 101. 顺金
            if  (self.hand[2].num + 1 == self.hand[1].num and self.hand[1].num + 1 == self.hand[0].num \
                     or self.hand[2].num == 2 and self.hand[1].num == 3 and self.hand[0].num == 14):
            # 因为 A 是以数字 14 存储的，因此 A23 顺要额外考虑
                return 101
            # 102. 金花
            else:
                return 102
        # 103 顺子
        # 因为上个 if 已经除去了顺金部分，因此只要是公差为1的等差数列则一定是顺子
        elif self.hand[2].num + 1 == self.hand[1].num and self.hand[1].num + 1 == self.hand[0].num \
                     or self.hand[2].num == 2 and self.hand[1].num == 3 and self.hand[0].num == 14:
            return 103
        # 104. 对子, 对子要额外记录一下对子和单牌，以便比较大小
        elif self.hand[2].num == self.hand[1].num or self.hand[1].num == self.hand[0].num:
            if self.hand[2].num == self.hand[1].num:
                self.pair, self.single = self.hand[2].num, self.hand[0].num
            else:
                self.pair, self.single = self.hand[0].num, self.hand[2].num
            return 104
        # 散牌
        else:
            return self.hand[0].num
'''初始化牌堆'''
def initCard():
    # 1 表示 A
    # 13 表示 K
    for i in range(2, 15):
        for j in range(1, 5):
            card_book.append(Card(i, j))
'''打印手牌'''
def printHand(handCard: Hand):
    for h in handCard.hand:
        print(h.num, end='') if 1 < h.num <= 10 else print(num_book[h.num], end='')
        print(color_book[h.color], end=' ')
    print(type_book[handCard.parseType()])

'''比较辅助函数'''
def cmpCard(h1: Hand, h2: Hand):
    for i in range(len(h1.hand)):
        if h1.hand[i].num != h2.hand[i].num:
            if h1.hand[i].num > h2.hand[i].num:
                return 0
            else:
                return 2
    return 1

'''比较手牌函数'''
def cmpHand(h1: Hand, h2: Hand):
    lvl1 = h1.parseType()
    lvl2 = h2.parseType()
    #printHand(h1)
    #printHand(h2)
    # 先比较牌种
    if lvl_book.index(lvl1) < lvl_book.index(lvl2):
        return 0
    elif lvl_book.index(lvl1) > lvl_book.index(lvl2):
        return 2
    # 对子，要先比对子
    elif lvl1 == 104:
        if h1.pair == h2.pair:
            return cmpCard(Hand([Card(h1.single)]), Hand([Card(h2.single)]))
        else:
            return cmpCard(Hand([Card(h1.pair)]), Hand([Card(h2.pair)]))

    # 其余情况，挨个比就行
    else:
        return cmpCard(h1, h2)

'''作图函数'''
def plotRects(x_list, y_list):
    rects = plot.bar(range(len(y_list)), y_list, color=[numpy.random.random(3) for i in range(len(y_list))])

    plot.ylabel("概率(%)")
    plot.xticks([i for i in range(len(x_list))], x_list)
    for rect in rects:
        height = rect.get_height()
        plot.text(rect.get_x() + rect.get_width() / 2, height, "{:.3f}%".format(height), ha='center', va='bottom')
    plot.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    plot.rcParams['axes.unicode_minus'] = False
    plot.show()

'''获得全部牌型的概率'''
def getPr(cap: int):
    cnt = dict()
    tot = int(cap)
    for i in range(tot):
        hand1 = Hand(random.sample(card_book, 3))
        type = hand1.parseType()
        cnt[hand1.parseType()] = 1 if type not in cnt else cnt[hand1.parseType()] + 1

    cnt = dict(sorted(cnt.items(), key=lambda x: x[1]))
    '''分组画图'''
    sub1 = dict([(key, cnt[key]) for key in range(100, 105)])
    sub2 = dict([(key, cnt[key]) for key in range(5, 15)])
    name_list1 = [type_book[k] for k in sub1.keys()]
    val_list1 = [v / tot * 100 for v in sub1.values()]
    name_list2 = [type_book[k] for k in sub2.keys()]
    val_list2 = [v / tot * 100 for v in sub2.values()]
    plotRects(name_list1, val_list1)
    plotRects(name_list2, val_list2)

'''获得全部牌型的胜率'''
def getWinning(cap: int):
    result = {}
    tot = int(cap)
    for i in range(tot):
        hand = random.sample(card_book, 6)
        hand1 = Hand(hand[:3])
        hand2 = Hand(hand[-3:])
        type = hand1.parseType()                            
        if type in result.keys():
            # print(type, cmpHand(hand1, hand2))
            result[type][cmpHand(hand1, hand2)] += 1
        else:
            result[type] = [0] * 3
            result[type][cmpHand(hand1, hand2)] = 1

    '''分组画图'''
    sub1 = dict([(key, result[key]) for key in range(100, 105)])
    sub2 = dict([(key, result[key]) for key in range(5, 15)])

    name_list1 = [type_book[k] for k in sub1.keys()]
    val_list1 = [v[0] / sum(v) * 100 for v in sub1.values()]
    name_list2 = [type_book[k] for k in sub2.keys()]
    val_list2 = [v[0] / sum(v) * 100 for v in sub2.values()]
    plotRects(name_list1, val_list1)
    plotRects(name_list2, val_list2)
if __name__ == '__main__':
    initCard()
    getWinning(1e7)






