import socket
from time import sleep
import threading
import sys
import logging
import re

ServerIP = sys.argv[1]
ServerPort = int(sys.argv[2])
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ServerIP, ServerPort))
server.listen()
clientsList = []
sktUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sktUDP.bind(('127.0.0.1', 65534))
sktUdpEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientsListLock = threading.Lock()

def Server():

    print(f'Se creo el socket UDP')

    threading.Thread(target=sendData, args=()).start()
    threading.Thread(target=addConections, args=()).start()

    while True:
        sleep(1)

def addConections():
     print(f'Aceptando clientes')
     while True:
        try:
            client, addr = server.accept()
            print(f'Se acepta el cliente {addr}')
            threading.Thread(target=clientConection, args=(client,)).start()
        except socket.timeout:
            pass



def sendData():
    while(True):
        try:
            datagram, (ip, port) = sktUDP.recvfrom(65000)
            with clientsListLock: #Para mutuoexcluir la lista
                for c in clientsList:
                    if c[2]==True:
                        sktUdpEnvio.sendto(datagram, (c[0], c[1]))
        except socket.timeout:
            print(f'El socket sufrió timeout al recibir el datagrama')
            pass
        except socket.error as e:
            print(f'El socket sufrió un error de tipo {e} al recibir el datagrama')




def clientConection(client):
    clientIp, clientPort = client.getpeername()


    while True:
        data = ""
        buffer = client.recv(4096).decode("utf-8")
        if not buffer:  # Si el buffer está vacío, el cliente se ha desconectado
            client.close()
            break
        data += buffer
        if ("CONECTAR" in data) and ("DESCONECTAR" not in data):
            print(f'Agregando cliente a los conectados')
            patron = r'\d+'
            resultado = re.search(patron, data)
            if resultado:
                numero = resultado.group()
            clientPort = int(numero)
            print(f'El puerto elegido es {numero}')
            with clientsListLock: #Para mutuoexcluir la lista
                if not any([c for c in clientsList if c[0] == clientIp]):
                    clientsList.append((clientIp, clientPort, True))
                    print(f'La lista actual de conectados es {clientsList}')

        if "DESCONECTAR"==data:
            print(f'Desconectando cliente')
            with clientsListLock: #Para mutuoexcluir la lista
                clientsList[:] = [c for c in clientsList if c[0] != clientIp]
            
            message = "OK"
            while message:
                sent = client.send(message.encode())
                message = message[sent:]

            client.close()
            break

        if "INTERRUMPIR"==data:
            print(f'Interrumpiendo conexion del cliente')
            with clientsListLock: #Para mutuoexcluir la lista
                for index, (ip, port, ready) in enumerate(clientsList):
                    if ip == clientIp:
                        clientsList[index] = (ip, port, False)
                        print(f'Cliente {clientIp} Interrumpido')

        if "CONTINUAR"==data:
            print(f'Reanudando conexion del cliente')
            with clientsListLock: #Para mutuoexcluir la lista
                for index, (ip, port, ready) in enumerate(clientsList):
                    if ip == clientIp:
                        clientsList[index] = (ip, port, True)

        if any(word in data for word in ["CONTINUAR","INTERRUMPIR", "CONECTAR"]):
            message = "OK"
            while message:
                    try:
                        sent = client.send(message.encode())
                        message = message[sent:]
                    except socket.error as e:
                        client.close()
                        return               


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Debe escribir : python Server.py <ServerIP> <ServerPort>")
        sys.exit(1)
    print(f'Se creo el socket TCP, bindeado en : {ServerIP} y {ServerPort}')
    Server()