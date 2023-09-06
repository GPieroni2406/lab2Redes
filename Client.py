import socket
import threading

def Client(serverIP, serverPort, vlcPort):
    buff = ""

    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master.bind(('localhost', 0))
    
    sktUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        master.connect((serverIP, serverPort))
    except socket.error as e:
        master.close()
        return

    while True:
        data = input()
        if "CONECTAR" in data:
            clientPort = int(data.split('<')[1].split('>')[0])
            sktUDP.bind(('localhost', clientPort))
            threading.Thread(target=transmissionVLC, args=(sktUDP, vlcPort)).start()

        if "DESCONECTAR" in data:
            sktUDP.close()
            break
        
        while data:
            try:
                sent = master.send(data.encode())
                data = data[sent:]
            except socket.error as e:
                master.close()
                return

        if any(word in data for word in ["DESCONECTAR", "CONECTAR", "INTERRUMPIR", "CONTINUAR"]):
            try:
                data = master.recv(1024).decode()
                buff += data
            except socket.error as e:
                master.close()
                return
            
            if "OK" not in data:
                break

def transmissionVLC(sktUDP, vlcPort):
    while True:
        try:
            data, addr = sktUDP.recvfrom(1024)
            sktUDP.sendto(data, ('localhost', vlcPort))
        except socket.error as e:
            sktUDP.close()
            break
