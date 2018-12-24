import socket
import time
import connectDB
import fetch.start as myfetch






HOST = ''  # null
PORT = 21567
busy = False
svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
svr.bind((HOST, PORT))
svr.listen(1)
mf = myfetch.myFecth()


def operate(_mf):
    _mf.getGameNode()
    _mf.fetch()
    pass


while True:
    print('--------Waiting for connection-------')
    [conn, addr] = svr.accept()
    session = connectDB.connectDB(addr[0])
    print('Connected by', addr)
    while True:
        try:
            data = conn.recv(1024).decode()
        except Exception as e:
            print(e)
            break

        '''receive data'''
        if data == 'begin':
            conn.send(str('connect successful.').encode())
            league_name = conn.recv(1024).decode()
            mf.setAttribute(conn, session, league_name)
            mf.openDriver()
            mf.selectLeague()
            operate(mf)
            conn.send(str('Finished.').encode())
        elif data == 'continue':
            print('sleep 30s..')
            time.sleep(30)
            operate(mf)
            conn.send(str('Finished.').encode())
        elif data == 'close':
            mf.closeDriver()

            pass
    conn.close()
svr.close()
