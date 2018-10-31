#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading

# Nomes (value) e enderecos IPs dos clientes (key)
listaNomesClientes = {}

# Sockets dos clientes que se conectam (value) e o IP (key)
listaSocketsClientes = {}

#Sockets de clientes (value) que estão em conversas privadas e o IP (key)
listaSocketsPrivados = {}

#guardar endereço da pessoa que vai conversar no privado
posicaoEnd = 0
posicaoEnd2 = 0

#Booleana para dizer que a pessoa aceita conversar no privado
aceito = False

# funcao que sera executada na thread
def receivedMessages(socketClient, address):
	global listaSocketsClientes
	global posicaoEnd
	global posicaoEnd2
	global listaSocketsPrivados
	global listaNomesClientes
	global aceito

	for key in listaSocketsClientes:
		if not key in listaNomesClientes:
			listaSocketsClientes[key].sendall(bytes('Informe o seu nome: ', 'utf-8'))

	message = socketClient.recv(1024)
	#o nome é a primeira mensagem
	name = message.decode("utf-8")

	# usa o IP como chave para achar os nomes dos usuarios do chat
	listaNomesClientes[address] = name

	#lista de quem esta no chat
	for key in listaNomesClientes:
		print('<' + str(key[0]) + ', ' + str(key[1]) + ', '+ str(listaNomesClientes[key]) + '>')

	message = listaNomesClientes[address] + ' entrou no chat'

	# envia mensagem de que um novo usuario entrou na sala
	for key in listaSocketsClientes:
		if key is not address:
			listaSocketsClientes[key].sendall(bytes(message, 'utf-8'))

	while(True):

		message = socketClient.recv(1024)
		#print(message)
		message = message.decode("utf-8")
		#print(message)
		
		if listaSocketsClientes[address] in listaSocketsPrivados and aceito:
			if message == 'sairprivado()':
				for key in listaSocketsPrivados:
					if key is not listaSocketsClientes[address] and listaSocketsPrivados[key] == 'p':
						key.sendall(bytes(listaNomesClientes[address] + ' saiu do modo privado com voce', "utf-8"))
				tmplistaSocketsPrivados = listaSocketsPrivados.copy()
				for key in tmplistaSocketsPrivados:
					del(listaSocketsPrivados[key])
				aceito = False
				listaNomesClientes[posicaoEnd] = listaNomesClientes[posicaoEnd].split("-")[0]
				listaNomesClientes[posicaoEnd2] = listaNomesClientes[posicaoEnd2].split("-")[0]
				posicaoEnd = 0
				posicaoEnd2 = 0

			elif message[:len('nome(')] == 'nome(':
				nome_antigo = listaNomesClientes[address]
				novo_nome = message.split('(')
				novo_nome = (novo_nome[1].split(')'))[0]
				listaNomesClientes[address] = novo_nome + "-privado"

				# Envia mensagem para demais clientes sobre a mudança de nomes
				for key in listaSocketsPrivados:
					if key is not listaSocketsClientes[address] and listaSocketsPrivados[key] == 'p':
						key.sendall(bytes(nome_antigo + ' mudou de nome para ' + novo_nome, "utf-8"))

			elif message == 'lista()':
				enviaListaConectados(address)
			
			else:
				for key in listaSocketsPrivados:
					if key is not listaSocketsClientes[address] and listaSocketsPrivados[key] == 'p':
						key.sendall(bytes(listaNomesClientes[address] + ' disse: ' + message, "utf-8"))
		else:
			# ['privado()', 'lista()', 'nome()', 'sair()']
			if message[:len('privado(')] == 'privado(':
				nomeOutroUsuario = message.split('(')

				# aqui eu estou obtendo o nome do usuario para conversar sem os ()
				nomeOutroUsuario = (nomeOutroUsuario[1].split(')'))[0]

				print(nomeOutroUsuario)
				print('Conversar com ' + str(nomeOutroUsuario))
				# nesse for eu acho qual a chave (IP) do cliente cujo nome foi passado no privado
				for key in listaNomesClientes:
					if listaNomesClientes[key] == nomeOutroUsuario:
						# chave encontrada
						posicaoEnd = key
						listaSocketsPrivados[listaSocketsClientes[key]] = 'p'
						listaSocketsPrivados[listaSocketsClientes[address]] = 'p'
						break
				#print(posicaoEnd)
				#print(listaSocketsPrivados)
				posicaoEnd2 = address
				msg_aux = 'Deseja iniciar uma conversa privada com ' + listaNomesClientes[address] + "? digite 'aceito()' para aceitar ou 'recuso()' para recusar"
				listaSocketsClientes[posicaoEnd].sendall(bytes(msg_aux, 'utf-8'))

			elif message[:len('nome(')] == 'nome(':
				nome_antigo = listaNomesClientes[address]
				novo_nome = message.split('(')
				novo_nome = (novo_nome[1].split(')'))[0]
				listaNomesClientes[address] = novo_nome

				# Envia mensagem para demais clientes sobre a mudança de nomes
				for key in listaSocketsClientes:
					if key is not address:
						listaSocketsClientes[key].sendall(bytes(nome_antigo + ' mudou de nome para ' + novo_nome, 'utf-8'))

			elif message == 'lista()':
				enviaListaConectados(address)

			elif message == 'sair()':
				for key in listaSocketsClientes:
					if key is not address:
						listaSocketsClientes[key].sendall(bytes(name.split("'")[1] + ' saiu do chat', 'utf-8'))
				del(listaNomesClientes[address])
				#print(listaSocketsClientes)
				tmplistaSocketsClientes = listaSocketsClientes.copy()
				for key in tmplistaSocketsClientes:
					if key is address:
						del(listaSocketsClientes[key])
				#print(listaSocketsClientes)
				break

			elif address == posicaoEnd:
				if message == 'aceito()':
					aceito = True
					listaNomesClientes[posicaoEnd] += "-privado)"
					listaNomesClientes[posicaoEnd2] += "-privado)"
				elif message == 'recuso()':
					tmplistaSocketsPrivados = listaSocketsPrivados.copy()
					for key in tmplistaSocketsPrivados:
						del(listaSocketsPrivados[key])
					posicaoEnd = 0
					aceito = False
				else:
					aceito = False

			elif message != name :
				sendMessages(listaSocketsClientes, message, address)
	socketClient.close()

# envia mensagens na sala de chat
def sendMessages(listSockets, message, sender):
	listConnected = listSockets

	for key in listConnected:
		if key is not sender:
			msg = str(listaNomesClientes[sender]) + ' disse: ' + str(message)
			listSockets[key].sendall(bytes(msg, 'utf-8'))

def enviaListaConectados(address):

	listaNomes = []

	for key in listaNomesClientes:
		listaNomes.append(listaNomesClientes[key])

	listaSocketsClientes[address].sendall(bytes(str(listaNomes), 'utf-8'))

#Servidor

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', 8080))

serverSocket.listen(5)
print('Servidor esperando conexoes na porta 8080')

while(True):
	(clientSocket, address) = serverSocket.accept()

	listaSocketsClientes[address] = clientSocket

	listen_thread = threading.Thread(target=receivedMessages, args = (clientSocket, address))
	listen_thread.start()
