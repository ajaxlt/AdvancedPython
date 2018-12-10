from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, func, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import and_
from settings import *
Base = declarative_base()

# c0. url
class url(Base):
    __tablename__ = "url"

    url_id = Column(primary_key=True)
    url = Column()
    iframe = Column()
    nickname = Column()

# c1. league to name
class leagueNum2Name(Base):
    __tablename__ = "league_num2name"

    league_id = Column(primary_key=True)
    league_name_zh = Column()

    league_country_jxf = Column()
    league_name_jxf = Column()
    league_id_jxf = Column()

    league_name_bb = Column()
    league_name_newbb = Column()
    is_select = Column()
    is_used = Column()

# c2. jxf game
class jxfGame(Base):
    __tablename__ = "jxf_game"

    uuid = Column(Integer, primary_key=True, autoincrement=True)
    game_date = Column()
    game_id = Column()
    game_league = Column()
    home = Column()
    away = Column()
    handicap = Column()
    total = Column()
    overdue = Column()

    hdp = {}
    tot = {}
# c4. new game
class bbGame(Base):
    __tablename__ = "bb_game"

    uuid = Column(Integer, primary_key=True, autoincrement=True)
    game_date = Column()
    game_id = Column()
    game_league = Column()
    home = Column()
    away = Column()
    handicap = Column()
    total = Column()
    overdue = Column()

    hdp = {}
    tot = {}
# c5. new game
class newbbGame(Base):
    __tablename__ = "newbb_game"

    uuid = Column(Integer, primary_key=True, autoincrement=True)
    game_date = Column()
    game_id = Column()
    game_league = Column()
    home = Column()
    away = Column()
    handicap = Column()
    total = Column()
    overdue = Column()

    hdp = {}
    tot = {}
class teamEn2Zh(Base):
    __tablename__ = "team_en2zh"


    uuid = Column(Integer, primary_key=True, autoincrement=True)
    name_zh = Column()
    league_zh = Column()
    name_jxf = Column()
    name_bb = Column()
    name_newbb = Column()

def connectDB(host):
    engine = create_engine('mysql+pymysql://' +
                           MYSQL_USER + ':' +
                           MYSQL_PASSWD + '@' +
                           host + '/' +
                           MYSQL_DBNAME +
                           '?charset=utf8')
    DBSession = sessionmaker(bind=engine)
    return DBSession()



def getUrl(session, name):
    return session.query(url).filter(url.nickname == name).first()


def getleague(session, league_zh):

    return session.query(leagueNum2Name).filter(leagueNum2Name.league_name_zh.in_(league_zh)).all()

def getrecords(session, type):
    return session.query(type).filter(type.overdue == 0).all()

def getnameZh(session, nickname, nameEn):
    if nickname == 'jxf':
        return session.query(teamEn2Zh.name_zh).filter(teamEn2Zh.name_jxf == nameEn).scalar()
    elif nickname == 'nbb':
        return session.query(teamEn2Zh.name_zh).filter(teamEn2Zh.name_newbb == nameEn).scalar()
    else:
        return session.query(teamEn2Zh.name_zh).filter(teamEn2Zh.name_bb == nameEn).scalar()

def submitOdds(session, item):

    session.query(type(item)).filter(and_(type(item).game_id == item.game_id,
                                          type(item).overdue == 0)
                                     ).update({type(item).overdue: 1})
    item.overdue = 0
    session.add(item)
    session.commit()





def testDB(session):
    item = jxfGame(
        game_date=None,
        game_id="a1",
        game_league="",
        home="d",
        away="c",
        handicap="{}",
        total="{}"
    )
    session.add(item)
    session.commit()


def main():
    session = connectDB('10.210.82.148')
    demo = jxfGame()
    submitOdds(session, demo)
    pass

if __name__ == '__main__':
    main()