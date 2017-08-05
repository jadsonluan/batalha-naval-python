# coding: utf-8
# (C) 2017, Jadson Luan / UFCG, Programação I e Laboratório de Programação I
# Batalha Naval

import pygame, sys, socket, threading
from pygame.locals import *
from enum import Enum

class Piece:
	def __init__(self, name, size, color):
		self.name = name
		self.size = size
		self.color = color

class Ship(Enum):
	CARRIER = 0
	BATTLESHIP = 1
	CRUISER = 2
	DESTROYER = 3 
	SUBMARINE = 4

class Settings:
	# Matchmaking
	TIMEOUT = 0.5
	PORT = 5000

	# Sizing
	CELL_SIZE = 35
	PADDING = 4
	TOTAL_PADDING = 11 * PADDING
	BOARD_SIZE = [10 * CELL_SIZE + TOTAL_PADDING, 10 * CELL_SIZE + TOTAL_PADDING]
	OFFSET_BETWEEN_BOARD = CELL_SIZE * 8
	
	SCREEN_TOP_OFFSET = 6
	SCREEN_LEFT_OFFSET = 2

	SCREEN_WIDTH = (2 * BOARD_SIZE[0]) + OFFSET_BETWEEN_BOARD + (SCREEN_LEFT_OFFSET * CELL_SIZE)
	SCREEN_HEIGHT = BOARD_SIZE[1] + (SCREEN_TOP_OFFSET * CELL_SIZE)

	BOARD1_TOP_OFFSET = CELL_SIZE
	BOARD1_LEFT_OFFSET = CELL_SIZE

	BOARD2_TOP_OFFSET = CELL_SIZE
	BOARD2_LEFT_OFFSET = BOARD_SIZE[0] + OFFSET_BETWEEN_BOARD + BOARD1_LEFT_OFFSET

	SHIPS = {}
	SHIPS[Ship.CARRIER] = Piece(u"Porta-aviões", 5, (229,0,0)) # 0
	SHIPS[Ship.BATTLESHIP] = Piece("Navio de Guerra", 4, (255,170,64)) # 1
	SHIPS[Ship.CRUISER] = Piece("Cruzador", 3, (174,253,61)) # 2
	SHIPS[Ship.DESTROYER] = Piece("Contratorpedeiro", 2, (253,255,48)) # 3
	SHIPS[Ship.SUBMARINE] = Piece("Submarino", 1, (255,106,6)) # 4
	
class Color:
	BACKGROUND = (25,28,30)
	SEA = (22,141,255)
	GRID = (0,0,0)
	MENU_BG = (38,58,114)

class GameState(Enum):
	PREPARATION = 0
	MATCH_RUNNING = 1
	SHOOTING = 2
	GAMEOVER = 3
	MENU = 4

class Code(Enum):
	PREPARED = "P"
	BOARD = "B"

class Message(Enum):
	PREPARED = "P"

class Cell:
	def __init__(self, location, player, shooted=False, ship=None):
		self.shooted = shooted
		self.player = player

		self.ship_id = ship
		self.ship = Settings.SHIPS[ship] if ship else None
		
		self.image = pygame.Surface([Settings.CELL_SIZE, Settings.CELL_SIZE])
		self.sync_color()
		self.rect = self.image.get_rect()

		row, col = location
		x = Settings.CELL_SIZE * col
		y = Settings.CELL_SIZE * row
		x += Settings.PADDING * (col+1)
		y += Settings.PADDING * (row+1)

		if player == 1:
			x += Settings.BOARD1_LEFT_OFFSET
			y += Settings.BOARD1_TOP_OFFSET
		else:
			x += Settings.BOARD2_LEFT_OFFSET
			y += Settings.BOARD2_TOP_OFFSET

		self.rect.x, self.rect.y = x, y

	def set_ship(self, ship):
		self.ship = Settings.SHIPS[ship]
		self.ship_id = ship
		if self.player == 1:
			self.sync_color()

	def sync_color(self):
		color = self.ship.color if self.ship else Color.SEA
		self.image.fill(color)

	def shoot(self):
		if not self.shooted:
			self.shooted = True
			pos = Settings.CELL_SIZE/2, Settings.CELL_SIZE/2
			pygame.draw.circle(self.image, (0,0,0), pos, Settings.CELL_SIZE/4)

class Matchmaking:
	@staticmethod
	def connect(HOSTNAME, PORT):
		"""
		Realiza (ou não) conexão com um host
		"""
		dest = (HOSTNAME, PORT)

		tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcp.settimeout(Settings.TIMEOUT)

		try:
			tcp.connect(dest)
			result = True
			return tcp
		except:
			return None

	@staticmethod
	def search_opponent():
		'''
		Varre toda a rede local em busca de algum oponente
		'''
		# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# s.connect(("8.8.8.8", 80))
		# myip = s.getsockname()[0]
		# s.close()

		# # Pegando a mask
		# bcast = myip.split(".")
		# myip_end = bcast.pop(3)
		# bcast = ".".join(bcast)
		# bcast += "."

		# timeout_secs = 0.25

		# # Procurando
		# print "Max. waiting time: %d secs" % int(Settings.TIMEOUT * 255)
		# for i in range(1, 256):
		# 	hostname = bcast + str(i)
		# 	print "checking:", hostname

		# 	#and then check the response...
		con = Matchmaking.connect("192.168.25.53", Settings.PORT)
		# 	if con:
		return con

		# return None

	@staticmethod
	def wait_opponent():
		# getting local ip
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		host = s.getsockname()[0]
		s.close()

		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		origin = (host, Settings.PORT)
		server.bind(origin)
		server.listen(1)

		# while True:
		con, client = server.accept()
		print "Opponent found!", client

		# while True:
			# print "Esperando mensagem"
			# msg = con.recv(1024)
			# if not msg: break
			# print client, msg
		# print "Finalizando conexão do cliente", client
		# con.close()
		# con, client = server.accept()
		# data = con.recv(1024)
		# matrix = [[x for x in line.split("-")] for line in data.split('/')]
		# print len(matrix)
		# con.close()
		# server.close()
		return con

class Connection(threading.Thread):
	def __init__(self, con, states):
		threading.Thread.__init__(self)
		self.con = con
		self.prepared = False
		self.board = []
		self.states = states

	def run(self):
		con = self.con

		while self.states['game_running']:
			try:
				msg = con.recv(1024)
				if msg:
					message = msg.split("#")
					code = message[0]

					if code == Code.BOARD.value:
						data = message[1]
						board = [[x for x in line.split("|")] for line in data.split('/')]

						self.board = []
						for i in range(10):
							self.board.append([])
							for j in range(10):
								for ship in Ship:
									if ship.value == board[i][j]:
										cell_ship = ship
										break
								else:
									cell_ship = None

								shooted = False
								cell = Cell((i,j), 2, shooted, cell_ship)
								self.board[i].append(cell)
						print len(self.board)

					elif code == Code.PREPARED.value:
						self.prepared = True

			except socket.timeout:
				pass

class Match:
	board1 = []
	board2 = []
	ships = 0

	def __init__(self, screen):
		self.screen = screen
		self.setup_boards()
		self.board1_surface = pygame.Surface(Settings.BOARD_SIZE)
		self.board2_surface = pygame.Surface(Settings.BOARD_SIZE)
		self.state = GameState.PREPARATION

	def setup_boards(self):
		for row in range(10):
			self.board1.append([])
			self.board2.append([])
			for col in range(10):
				self.board1[row].append(Cell((row, col), 1))
				# self.board2[row].append(Cell((row, col), 2))

		# self.put_ship((0,0), Ship.SUBMARINE, "H", 2)
		# self.put_ship((1,0), Ship.DESTROYER, "H", 2)
		# self.put_ship((2,0), Ship.CRUISER, "H", 2)
		# self.put_ship((3,0), Ship.BATTLESHIP, "H", 2)
		# self.put_ship((4,0), Ship.CARRIER, "H", 2)

	def put_ship(self, position, ship_type, direction, player=1):
		board = self.board1 if player == 1 else self.board2

		ship = Settings.SHIPS[ship_type]
		row, col = position
		cell = board[row][col]
		# Horizontal
		if cell.ship is None:
			if direction == "H":
				if col + ship.size > len(board[0]):
					return False

				can = True

				for i in range(1, ship.size):
					if cell.ship is not None:
						can = False
					
				if can:
					for i in range(ship.size):
						board[row][col+i].set_ship(ship_type)
					return True
				else:
					return False
			else:
				if row + ship.size > len(board):
					return False

				can = True

				for i in range(1, ship.size):
					if cell.ship is not None:
						can = False
					
				if can:
					for i in range(ship.size):
						board[row+i][col].set_ship(ship_type)
					return True
				else:
					return False

		return False

	def count_ships(self, owner):
		if owner == 1:
			board = self.board1
		else:
			board = self.board2

		counter = 0
		for row in range(len(board)):
			for col in range(len(board[0])):
				cell = board[row][col]
				if cell.ship and not cell.shooted:
					counter += 1

		return counter

	def render(self):
		screen = self.screen
		board1 = self.board1
		board1_surface = self.board1_surface

		board2 = self.board2
		board2_surface = self.board2_surface

		screen.fill(Color.BACKGROUND)
		board1_surface.fill((0,0,255))
		board2_surface.fill((0,0,255))
		
		# board background
		screen.blit(board1_surface, (Settings.BOARD1_LEFT_OFFSET, Settings.BOARD1_TOP_OFFSET))
		screen.blit(board2_surface, (Settings.BOARD2_LEFT_OFFSET, Settings.BOARD2_TOP_OFFSET))
		
		for row in range(len(board1)):
			for col in range(len(board1[0])):
				cell1 = board1[row][col]
				screen.blit(cell1.image, cell1.rect)
				
				if self.state != GameState.PREPARATION and board2 != []:
					cell2 = board2[row][col]
					screen.blit(cell2.image, cell2.rect)

		grid1_width = Settings.BOARD_SIZE[0]
		grid1_height = (Settings.SCREEN_TOP_OFFSET - 3) * Settings.CELL_SIZE

		grid1 = pygame.Surface([grid1_width, grid1_height])
		grid1.fill(Color.GRID)
		grid1.set_alpha(75)
		screen.blit(grid1, (Settings.BOARD1_LEFT_OFFSET, Settings.BOARD_SIZE[1] + 2 * Settings.CELL_SIZE))

class Game:
	connection = None
	connection_th = None
	you_ready = False
	states = {}

	def __init__(self):
		pygame.init()
		
		self.width = Settings.SCREEN_WIDTH
		self.height = Settings.SCREEN_HEIGHT

		self.states["game_running"] = True

		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Batalha Naval em Python")
		self.selected_ship = None
		self.ship_orientation = "H"
		self.show_menu()

	def loop(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					self.states["game_running"] = False
					sys.exit()

				if event.type == KEYDOWN and event.key == K_SPACE:
					# tab = self.match.board1
					print self.match.count_ships(2)
					# for row in range(len(tab)):
						# line = []
						# for col in range(len(tab[0])):
						# 	line.append(tab[row][col])
						# print line

				if self.gamestate == GameState.MATCH_RUNNING:
					if self.match.state == GameState.PREPARATION:
						if self.connection_th.prepared and self.you_ready:
							self.send_board()
							self.match.state = GameState.SHOOTING

					if self.match.state == GameState.PREPARATION and event.type == KEYDOWN:
						if event.key == K_q:
							self.selected_ship = Ship.SUBMARINE
						elif event.key == K_w:
							self.selected_ship = Ship.DESTROYER
						elif event.key == K_e:
							self.selected_ship = Ship.CRUISER
						elif event.key == K_r:
							self.selected_ship = Ship.BATTLESHIP
						elif event.key == K_t:
							self.selected_ship = Ship.CARRIER
						elif event.key == K_SPACE:
							self.ship_orientation = "H" if self.ship_orientation == "V" else "V"

					pressed = pygame.mouse.get_pressed()
					l_click, m_click, r_click = pressed


					if self.match.state == GameState.SHOOTING:
						self.match.board2 = self.connection_th.board
						board = self.match.board2
						self.match.render()

					if l_click:
						mouse_pos = pygame.mouse.get_pos()
						if self.match.state == GameState.PREPARATION:
							board = self.match.board1
							for row in range(len(board)):
								for col in range(len(board[0])):
									cell = board[row][col]
									if cell.rect.collidepoint(mouse_pos):
										if self.selected_ship:
											if self.match.put_ship((row, col), self.selected_ship, self.ship_orientation):
												self.selected_ship = None
												self.match.ships += 1

												if self.match.ships >= 5:
													self.you_ready = True
													self.connection.send(Message.PREPARED.value)
											else:
												print "não foi possivel por o ship em %d,%d" % (row, col)
						elif self.match.state == GameState.SHOOTING:
							self.match.board2 = self.connection_th.board
							board = self.match.board2
							for row in range(len(board)):
								for col in range(len(board[0])):
									cell = board[row][col]
									if cell.rect.collidepoint(mouse_pos):
										if not cell.shooted:
											if cell.ship is None:
												print "[%d,%d] Tiro na água!" % (row, col)
											else:
												print "[%d,%d] Acertou um %s!" % (row, col, cell.ship.name)
												cell.sync_color()
											cell.shoot()

											if self.match.count_ships(2) <= 0:
												self.match.state = GameState.GAMEOVER
												self.gamestate = GameState.GAMEOVER
				elif self.gamestate == GameState.MENU:
					if event.type == KEYDOWN:
						if event.key == K_w:
							print "Esperando por outro jogador."
							opponent = Matchmaking.wait_opponent()
							if opponent:
								self.connection = opponent
								self.connection_th = Connection(self.connection, self.states)
								self.connection_th.start()
								self.start_match()
							else:
								print "No opponent found."
							# esperando
						elif event.key == K_s:
							print "Procurando por um adversario."
							opponent = Matchmaking.search_opponent()

							if opponent:
								self.connection = opponent
								self.connection_th = Connection(self.connection, self.states)
								self.connection_th.start()
								self.start_match()
							else:
								print "No opponents at time."

			self.render()

	def send_board(self):
		matrix = []

		for i in range(10):
			matrix.append([])
			for j in range(10):
				cell = self.match.board1[i][j]
				representation = cell.ship_id.value if cell.ship_id is not None else -1
				matrix[i].append(str(representation))

		data = Code.BOARD.value + "#"
		for i in range(10):
			data += "|".join(matrix[i])
			if i < 9: data += "/"
		self.connection.send(data)

	def show_menu(self):
		self.gamestate = GameState.MENU
		screen = self.screen
		screen.fill(Color.MENU_BG)

		# menu stuff
		pygame.display.flip()

	def start_match(self):
		self.gamestate = GameState.MATCH_RUNNING
		self.match = Match(self.screen)
		self.match.board2 = self.connection_th.board
		# bla bla

	def render(self):
		if self.gamestate == GameState.MATCH_RUNNING:
			self.match.render()
			pygame.display.flip()
		elif self.gamestate == GameState.GAMEOVER:
			self.screen.fill((255,255,0))
			# Colocar tela de vitoria
			pygame.display.flip()
		elif self.gamestate == GameState.MENU:
			pass

if __name__ == "__main__":
	game = Game()
	game.loop()
	game.states["game_running"] = False