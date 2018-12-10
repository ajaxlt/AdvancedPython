import socket
import connectDB
import time
import fetch.start as myfetch





def operate(_mf, conn):
    if not _mf.driver_flag:
        _mf.openDriver()
    _mf.selectLeague()

    while True:
        _mf.getGameNode()
        _mf.fetch()

        print("Finished.")
        conn.send(str("Finished.").encode())
        message = conn.recv(1024).decode()
        if message == 'stop':
            print("Brute-force Break.")
            conn.send(str("Break successfully.").encode())
            break
        conn.send(str("Sleep 30s.").encode())
        time.sleep(30)
    pass

HOST = ''  # null
PORT = 21567
busy = False
svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
svr.bind((HOST, PORT))
svr.listen(1)

mf = myfetch.myFecth()
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
        if not data:
            break

        ''' db test '''
        if data == 'close':
            mf.closeDriver()
        else:
            mf.setAttribute(conn, session, data)
            operate(mf, conn)
        ''' db test '''

    conn.close()
svr.close()
