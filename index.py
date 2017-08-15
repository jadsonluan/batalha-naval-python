# coding: utf-8
# (C) 2017, Jadson Luan / UFCG, Programação I e Laboratório de Programação I
# Batalha Naval

import pygame, sys, socket, threading, time
from pygame.locals import *
from enum import Enum

class Piece:
	def __init__(self, name, size, color, key):
		self.name = name
		self.size = size
		self.color = color
		self.key = key

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
	CELL_SIZE = 25
	PADDING = 2
	TOTAL_PADDING = 11 * PADDING
	BOARD_SIZE = [10 * CELL_SIZE + TOTAL_PADDING, 10 * CELL_SIZE + TOTAL_PADDING]
	OFFSET_BETWEEN_BOARD = CELL_SIZE * 8
	
	SCREEN_TOP_OFFSET = 7
	SCREEN_LEFT_OFFSET = 2

	SCREEN_WIDTH = (2 * BOARD_SIZE[0]) + OFFSET_BETWEEN_BOARD + (SCREEN_LEFT_OFFSET * CELL_SIZE)
	SCREEN_HEIGHT = BOARD_SIZE[1] + (SCREEN_TOP_OFFSET * CELL_SIZE)

	BOARD1_TOP_OFFSET = CELL_SIZE
	BOARD1_LEFT_OFFSET = CELL_SIZE

	BOARD2_TOP_OFFSET = CELL_SIZE
	BOARD2_LEFT_OFFSET = BOARD_SIZE[0] + OFFSET_BETWEEN_BOARD + BOARD1_LEFT_OFFSET

	MAX_SHIPS = 5
	SHIPS = {}
	SHIPS[Ship.CARRIER] = Piece(u"Porta-aviões", 5, (229,0,0), "T") # 0
	SHIPS[Ship.BATTLESHIP] = Piece("Navio de Guerra", 4, (255,170,64), "R") # 1
	SHIPS[Ship.CRUISER] = Piece("Cruzador", 3, (174,253,61), "E") # 2
	SHIPS[Ship.DESTROYER] = Piece("Contratorpedeiro", 2, (253,255,48), "W") # 3
	SHIPS[Ship.SUBMARINE] = Piece("Submarino", 1, (255,106,6), "Q") # 4
	
class Color:
	BACKGROUND = (25,28,30)
	SEA = (22,141,255)
	GRID = (0,0,0)
	SUCCESS = (45,199,45)
	FAIL = (203,17,38)

	# Backgrounds
	MENU_BG = (202,194,255) 

	# Texting
	TITLE = (0,45,143)  
	TEXT = (255,255,255)
	MENU_OPTION = (17,17,17)
	SELECTED = (74,199,204) 

	# State
	WIN = (74,199,204) 
	LOSE = (204,79,74)

	# Basic
	GRAY = (84,74,74)
	WHITE = (255,255,255)
	BLACK = (0,0,0)

class GameState(Enum):
	PREPARATION = 0
	MATCH_RUNNING = 1
	SHOOTING = 2
	GAMEOVER = 3
	
	MENU = 4
	CREDITS = 5
	HOWTOPLAY = 6

	WIN = 7
	LOSE = 8

class Code(Enum):
	PREPARED = "P"
	BOARD = "B"
	SHOT = "S"
	GAMEOVER = "G"
	EXIT = "E"

class Message(Enum):
	PREPARED = "P"

class Text:
	def __init__(self, text, color, size, left, top, centerx, centery, fontname):
		self.font = pygame.font.Font(fontname, int(Settings.CELL_SIZE/size))
		self.surface = self.font.render(text, 1, color)
		self.rect = self.surface.get_rect()
		self.left = left
		self.top = top
		self.centerx = centerx
		self.centery = centery
		
		size = self.font.size(text)
		self.width = size[0]
		self.height = size[1]

	def get_new_rect(self):
		s_rect = self.rect
		
		s_rect.left = self.left
		s_rect.top = self.top

		if self.centerx: s_rect.left += Settings.SCREEN_WIDTH/2 - self.width/2
		if self.centery: s_rect.top += Settings.SCREEN_HEIGHT/2 - self.height/2

		return s_rect

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

	def set_ship(self, ship, sync=True):
		self.ship = Settings.SHIPS[ship]
		self.ship_id = ship
		if self.player == 1 and sync:
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
	def connect(HOSTNAME, PORT, use_timeout=True):
		"""
		Realiza (ou não) conexão com um host
		"""
		dest = (HOSTNAME, PORT)

		tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		if use_timeout:
			tcp.settimeout(Settings.TIMEOUT)

		try:
			tcp.connect(dest)
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
		con = Matchmaking.connect("localhost", Settings.PORT)
		# 	if con:
		return con

		# return None

	@staticmethod
	def wait_opponent():
		# getting local ip
		# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# s.connect(("8.8.8.8", 80))
		# host = s.getsockname()[0]
		# s.close()
		host = "localhost"

		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		origin = (host, Settings.PORT)
		server.bind(origin)
		server.listen(1)

		con, client = server.accept()
		con.settimeout(Settings.TIMEOUT)
		return con

class Match(threading.Thread):
	def __init__(self, con, states, screen):
		threading.Thread.__init__(self)
		self.connection = con
		self.states = states
		self.screen = screen

		self.enemy_board = []
		self.board = []

		self.board_surface = pygame.Surface(Settings.BOARD_SIZE)
		self.enemy_board_surface = pygame.Surface(Settings.BOARD_SIZE)

		self.ships = []

		self.state = GameState.PREPARATION
		self.prepared = False
		self.enemy_prepared = False
		self.win = False
		self.lose = False
		self.turn = None

		self.setup_boards()

	def run(self):
		while self.states['thread_running']:
			if self.state == GameState.PREPARATION and self.prepared and self.enemy_prepared:
				time.sleep(1)
				self.send_board()
				self.state = GameState.SHOOTING

			try:
				msg = self.connection.recv(1024)
				if msg:
					self.analyse_message(msg)
				else:
					self.states['thread_running'] = False
			except socket.timeout:
				pass

		self.states['thread_running'] = False
		self.connection.close()

	def shot(self, cell, row, col):
		msg = Code.SHOT.value + "#%d,%d" % (row, col)
		self.turn = False
		cell.sync_color()
		cell.shoot()
		self.connection.send(msg)

	def analyse_message(self, msg):
		message = msg.split("#")
		code = message[0]

		if code == Code.BOARD.value:
			board = message[1]
			self.sync_enemy(board)
		elif code == Code.EXIT.value:
			self.connection.close()
			self.states["thread_running"] = False
		elif code == Code.PREPARED.value:
			self.enemy_prepared = True
		elif code == Code.SHOT.value:
			row, col = message[1].split(",")
			row, col = int(row), int(col)
			cell = self.board[row][col]
			
			if cell.ship is not None:
				cell.sync_color()
			cell.shoot()
			self.turn = True

			if self.count_ships() <= 0:
				self.gameover()
		elif code == Code.GAMEOVER.value:
			self.win = True
			# if self.match.count_ships(2) <= 0:
			# 	self.match.state = GameState.GAMEOVER
			# 	self.gamestate = GameState.GAMEOVER

	def sync_enemy(self, data):
		# Dá pra otimizar não reescrevendo o tabuleiro, apenas comparando o que mudou
		board = [[x for x in line.split("|")] for line in data.split('/')]

		for row in range(10):
			for col in range(10):
				for ship in Ship:
					if str(ship.value) == str(board[row][col])[0]:
						new_cell_ship = ship
						break
				else:
					new_cell_ship = None

				current_cell = self.enemy_board[row][col]

				if current_cell.ship != new_cell_ship:
					current_cell.set_ship(new_cell_ship)

				shooted = "X" in str(board[row][col])

				if current_cell.shooted != shooted:
					current_cell.shoot()


		self.render()

	def setup_boards(self):
		for row in range(10):
			self.board.append([])
			self.enemy_board.append([])
			for col in range(10):
				self.board[row].append(Cell((row, col), 1))
				self.enemy_board[row].append(Cell((row, col), 2))

	def put_ship(self, position, ship_type, direction, player=1):
		board = self.board if player == 1 else self.enemy_board

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
					aux_cell = board[row][col+i]
					if aux_cell.ship is not None:
						can = False
					
				if can:
					for i in range(ship.size):
						board[row][col+i].set_ship(ship_type)

					if player == 1: self.ship_allocated(ship_type)
					return True
				else:
					return False
			else:
				if row + ship.size > len(board):
					return False

				can = True

				for i in range(1, ship.size):
					aux_cell = board[row+i][col]
					if aux_cell.ship is not None:
						can = False
					
				if can:
					for i in range(ship.size):
						board[row+i][col].set_ship(ship_type)
					if player == 1: self.ship_allocated(ship_type)
					return True
				else:
					return False

		return False

	def ship_allocated(self, ship):
		self.ships.append(ship)

		if len(self.ships) >= Settings.MAX_SHIPS:
			self.connection.send(Message.PREPARED.value)
			self.prepared = True

	def count_ships(self):
		board = self.board

		counter = 0
		for row in range(len(board)):
			for col in range(len(board[0])):
				cell = board[row][col]
				if cell.ship and not cell.shooted:
					counter += 1

		return counter

	def send_board(self):
		matrix = []

		for i in range(10):
			matrix.append([])
			for j in range(10):
				cell = self.board[i][j]
				representation = cell.ship_id.value if cell.ship_id is not None else 5
				is_shooted = "X" if cell.shooted else ""
				matrix[i].append(str(representation) + is_shooted)

		data = Code.BOARD.value + "#"
		
		for i in range(10):
			data += "|".join(matrix[i])
			if i < 9: data += "/"

		self.connection.send(data)

	def gameover(self):
		self.connection.send(Code.GAMEOVER.value)
		self.lose = True

	def render(self):
		screen = self.screen
		board = self.board
		board_surface = self.board_surface

		enemy_board = self.enemy_board
		enemy_board_surface = self.enemy_board_surface

		screen.fill(Color.BACKGROUND)
		board_surface.fill((0,0,255))
		enemy_board_surface.fill((0,0,255))
		
		# board background
		screen.blit(board_surface, (Settings.BOARD1_LEFT_OFFSET, Settings.BOARD1_TOP_OFFSET))
		screen.blit(enemy_board_surface, (Settings.BOARD2_LEFT_OFFSET, Settings.BOARD2_TOP_OFFSET))
		
		for row in range(len(board)):
			for col in range(len(board[0])):
				cell1 = board[row][col]
				screen.blit(cell1.image, cell1.rect)
				
				# if self.state != GameState.PREPARATION and len(board2) == 10 and len(board2[0]) == 10:
				cell2 = enemy_board[row][col]
				screen.blit(cell2.image, cell2.rect)

class Game:
	states = {}
	running = True

	def __init__(self):
		pygame.init()
		pygame.font.init()
		self.width = Settings.SCREEN_WIDTH
		self.height = Settings.SCREEN_HEIGHT

		self.states["thread_running"] = True

		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Batalha Naval em Python")
		self.selected_ship = None
		self.ship_orientation = "H"
		self.buttons = []
		self.show_menu()
		self.match = None

	def loop(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.exit()

				if event.type == KEYDOWN and event.key == K_SPACE:
					# debug code
					pass

				esc_pressed = event.type == KEYDOWN and event.key == K_ESCAPE
				if self.match is None and (self.gamestate == GameState.WIN or self.gamestate == GameState.LOSE) and esc_pressed:
					self.show_menu()

				if esc_pressed and (self.gamestate == GameState.CREDITS or self.gamestate == GameState.HOWTOPLAY):
					self.show_menu()

				# W.O
				if self.gamestate == GameState.MATCH_RUNNING and not self.states["thread_running"]:
					time.sleep(1)
					self.win(True)
				elif self.gamestate == GameState.MATCH_RUNNING and self.match.lose:
					time.sleep(1)
					self.lose()
				elif self.gamestate == GameState.MATCH_RUNNING and self.match.win:
					time.sleep(1)
					self.win()

				if self.gamestate == GameState.MATCH_RUNNING:
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

						if self.selected_ship in self.match.ships:
								self.selected_ship = None

					pressed = pygame.mouse.get_pressed()
					l_click, m_click, r_click = pressed

					if l_click:
						mouse_pos = pygame.mouse.get_pos()
						if self.match.state == GameState.PREPARATION and not self.match.prepared:
							board = self.match.board
							for row in range(len(board)):
								for col in range(len(board[0])):
									cell = board[row][col]
									if cell.rect.collidepoint(mouse_pos):
										if self.selected_ship:
											if self.match.put_ship((row, col), self.selected_ship, self.ship_orientation):
												self.selected_ship = None
											else:
												print "não foi possivel por o ship em %d,%d" % (row, col)
						elif self.match.state == GameState.SHOOTING and self.match.turn:
							board = self.match.enemy_board
							for row in range(len(board)):
								for col in range(len(board[0])):
									cell = board[row][col]
									if cell.rect.collidepoint(mouse_pos):
										if not cell.shooted:
											self.match.shot(cell, row, col)
											
				elif self.gamestate == GameState.MENU: 
					pressed = pygame.mouse.get_pressed()
					left_click, m_click, r_click = pressed

					if left_click:
						mouse_pos = pygame.mouse.get_pos()
						for button in self.buttons:		
							if button.rect.collidepoint(mouse_pos):
								button.onclick()
				elif self.gamestate == GameState.CREDITS:
					pass
				elif self.gamestate == GameState.HOWTOPLAY:
					pass
			self.render()
	
	def wait_opponent(self):
		opponent = Matchmaking.wait_opponent()
		if opponent:
			self.states["thread_running"] = True
			self.connection = opponent
			self.match = Match(self.connection, self.states, self.screen)
			self.match.start()
			self.gamestate = GameState.MATCH_RUNNING
			self.match.turn = True
		else:
			print "No opponent found."

	def search_opponent(self):
		opponent = Matchmaking.search_opponent()

		if opponent:
			self.states["thread_running"] = True
			self.connection = opponent
			self.match = Match(self.connection, self.states, self.screen)
			self.match.start()
			self.gamestate = GameState.MATCH_RUNNING
			self.match.turn = False
		else:
			print "No opponents at time."

	def show_menu(self):
		self.gamestate = GameState.MENU
		screen = self.screen
		screen.fill(Color.MENU_BG)

		self.buttons = []

		top_offset = Settings.SCREEN_HEIGHT/6
		left_offset = Settings.CELL_SIZE
		title_obj = self.display_message("Batalha Naval", Color.TITLE, 0.3, top_offset, 0, True, False, "KBZipaDeeDooDah.ttf")

		# menu options
		left_offset += Settings.CELL_SIZE

		text_size = 0.8
		top_offset += title_obj.height
		btn_procurar = self.display_message("Procurar oponente", Color.MENU_OPTION, text_size, top_offset, 0, True, False, "KBZipaDeeDooDah.ttf")
		btn_procurar.onclick = self.search_opponent
		self.buttons.append(btn_procurar)

		top_offset += btn_procurar.height
		btn_esperar = self.display_message("Esperar oponente", Color.MENU_OPTION, text_size, top_offset, 0, True, False, "KBZipaDeeDooDah.ttf")
		btn_esperar.onclick = self.wait_opponent
		self.buttons.append(btn_esperar)

		top_offset += btn_esperar.height
		btn_comojogar = self.display_message("Como jogar", Color.MENU_OPTION, text_size, top_offset, 0, True, False, "KBZipaDeeDooDah.ttf")
		btn_comojogar.onclick = self.show_how_to_play
		self.buttons.append(btn_comojogar)

		top_offset += btn_comojogar.height
		btn_creditos = self.display_message(u"Creditos", Color.MENU_OPTION, text_size, top_offset, 0, True, False, "KBZipaDeeDooDah.ttf")
		btn_creditos.onclick = self.show_credits
		self.buttons.append(btn_creditos)

		top_offset += btn_creditos.height
		btn_sair = self.display_message("Sair", Color.MENU_OPTION, text_size, top_offset, 0, True, False, "KBZipaDeeDooDah.ttf")
		btn_sair.onclick = self.exit
		self.buttons.append(btn_sair)

		# menu stuff
		pygame.display.flip()

	def show_credits(self):
		self.gamestate = GameState.CREDITS
		self.screen.fill(Color.MENU_BG)

		top_offset = Settings.CELL_SIZE
		left_offset = Settings.CELL_SIZE
		obj = self.display_message("Creditos", Color.TITLE, 0.5, top_offset, left_offset, False, False, "KBZipaDeeDooDah.ttf")

		text_size = 1
		
		left_offset += Settings.CELL_SIZE
		top_offset += obj.height
		obj = self.display_message(u"Miniprojeto das disciplinas de Programação I e Laboratório de Programação I", Color.BLACK, text_size, top_offset, left_offset)

		top_offset += obj.height
		obj = self.display_message(u"Ciência da Computação, UFCG", Color.BLACK, text_size, top_offset, left_offset)

		top_offset += obj.height + Settings.CELL_SIZE
		obj = self.display_message(u"Desenvolvido por", Color.BLACK, text_size, top_offset, left_offset)

		left_offset += Settings.CELL_SIZE
		top_offset += obj.height
		obj = self.display_message(u"Jadson Luan Soares da Silva", Color.TITLE, text_size, top_offset, left_offset)

		left_offset -= Settings.CELL_SIZE
		top_offset += obj.height + Settings.CELL_SIZE
		obj = self.display_message(u"Agosto/2017", Color.BLACK, text_size, top_offset, left_offset)

		## final
		top_offset = Settings.SCREEN_HEIGHT - Settings.CELL_SIZE * 2
		obj = self.display_message(u"Pressione 'ESC' para retornar ao menu", Color.TITLE, text_size, top_offset, 0, True, False, "KBZipaDeeDooDah.ttf")

		pygame.display.flip()

	def show_how_to_play(self):
		self.gamestate = GameState.HOWTOPLAY
		self.screen.fill(Color.MENU_BG)

		top_offset = Settings.CELL_SIZE
		left_offset = Settings.CELL_SIZE
		obj = self.display_message("Como jogar", Color.TITLE, 0.5, top_offset, left_offset, False, False, "KBZipaDeeDooDah.ttf")

		text_size = 1
		
		left_offset += Settings.CELL_SIZE
		top_offset += obj.height
		obj = self.display_message(u"Genérico", Color.BLACK, text_size, top_offset, left_offset)

		left_offset += Settings.CELL_SIZE
		top_offset += obj.height
		obj = self.display_message(u"O jogador que destruir todos os návios adversários primeiro, vence.", Color.TITLE, text_size, top_offset, left_offset)

		top_offset += obj.height
		obj = self.display_message(u"Cada jogador só pode possuir um (1) návio de cada tipo.", Color.TITLE, text_size, top_offset, left_offset)

		##### especifico
		left_offset -= Settings.CELL_SIZE
		top_offset += obj.height + Settings.CELL_SIZE
		obj = self.display_message(u"Fase de preparação", Color.BLACK, text_size, top_offset, left_offset)

		left_offset += Settings.CELL_SIZE

		top_offset += obj.height
		obj = self.display_message(u"Para selecionar o navio a ser posicionado, utilize as teclas", Color.TITLE, text_size, top_offset, left_offset)

		keys_left_offset = left_offset + obj.width + Settings.CELL_SIZE/4
		obj = self.display_message(u"Q, W, E, R e T", Color.LOSE, text_size, top_offset, keys_left_offset)
		
		top_offset += obj.height
		obj = self.display_message(u"Para alternar a direção dos navios antes de posicioná-los pressione a tecla", Color.TITLE, text_size, top_offset, left_offset)

		keys_left_offset = left_offset + obj.width + Settings.CELL_SIZE/4
		obj = self.display_message(u"SPACE", Color.LOSE, text_size, top_offset, keys_left_offset)


		## final
		top_offset = Settings.SCREEN_HEIGHT - Settings.CELL_SIZE * 2
		obj = self.display_message(u"Pressione 'ESC' para retornar ao menu", Color.TITLE, text_size, top_offset, 0, True, False, "KBZipaDeeDooDah.ttf")

		pygame.display.flip()

	def win(self, is_wo=False):
		self.match = None
		self.gamestate = GameState.WIN
		screen = self.screen
		screen.fill(Color.WIN)

		self.display_message(u"Parabéns. Você venceu!", Color.WHITE, 0.5, 0, 0, True, True)
			
		if is_wo:
			self.display_message(u"Seu oponente desconectou.", Color.GRAY, 0.5, -30, 0, True, True)

		self.display_message(u"Pressione 'ESC' para retornar ao menu.", Color.WHITE, 1, Settings.SCREEN_HEIGHT - 30, 0, True, False)

		# win stuff
		pygame.display.flip()

	def lose(self):
		self.match = None
		self.gamestate = GameState.LOSE
		screen = self.screen
		screen.fill(Color.LOSE)

		self.display_message(u"Você perdeu!", Color.WHITE, 0.5, 0, 0, True, True)
		self.display_message(u"Pressione 'ESC' para retornar ao menu.", Color.WHITE, 1, Settings.SCREEN_HEIGHT - 30, 0, True, False)
		# lose stuff
		pygame.display.flip()

	def start_match(self):
		pass
		# bla bla

	def display_message(self, text, color, size, top_offset, left_offset, centerx=False, centery=False, fontname=None):
		text_obj = Text(text, color, size, left_offset, top_offset, centerx, centery, fontname)
		self.screen.blit(text_obj.surface, text_obj.get_new_rect())
		return text_obj

	def render(self):
		if self.gamestate == GameState.MATCH_RUNNING:
			self.match.render()

			if self.match.turn is not None and self.match.state == GameState.SHOOTING:
				top_offset = Settings.CELL_SIZE
				left_offset = Settings.BOARD1_LEFT_OFFSET + Settings.BOARD_SIZE[0] + Settings.CELL_SIZE
				text = "Turno: %s" % (u"você" if self.match.turn else "oponente")
				self.display_message(text, Color.TEXT, 1, top_offset, left_offset)
			else:
				# Preparação
				top_offset = Settings.CELL_SIZE
				left_offset = Settings.BOARD1_LEFT_OFFSET + Settings.BOARD_SIZE[0] + Settings.CELL_SIZE
				self.display_message(u"Preparação", Color.TEXT, 1, top_offset, left_offset)

				left_offset += Settings.CELL_SIZE

				top_offset += Settings.CELL_SIZE
				color_you = Color.SUCCESS if self.match.prepared else Color.FAIL
				self.display_message(u"Você", color_you, 1.25, top_offset, left_offset)

				top_offset += int(Settings.CELL_SIZE/1.5)
				color_enemy = Color.SUCCESS if self.match.enemy_prepared else Color.FAIL
				self.display_message(u"Oponente", color_enemy, 1.25, top_offset, left_offset)

				if self.match.prepared and self.match.enemy_prepared:
					left_offset -= Settings.CELL_SIZE
					top_offset += Settings.CELL_SIZE
					
					self.display_message(u"Iniciando...", Color.TEXT, 1, top_offset, left_offset)

				grid1_width = Settings.BOARD_SIZE[0]
				grid1_height = (Settings.SCREEN_TOP_OFFSET - 3) * Settings.CELL_SIZE

				grid1 = pygame.Surface([grid1_width, grid1_height])
				grid1.fill(Color.GRID)
				grid1.set_alpha(75)
				left_offset = Settings.BOARD1_LEFT_OFFSET
				top_offset = Settings.BOARD_SIZE[1] + 2 * Settings.CELL_SIZE
				self.screen.blit(grid1, (left_offset, top_offset))

				left_offset += Settings.CELL_SIZE/2
				top_offset += int(Settings.CELL_SIZE/4)
				for key in Settings.SHIPS:
					color = Color.SELECTED if key == self.selected_ship else Color.FAIL
					color = Color.SUCCESS if key in self.match.ships else color

					ship = Settings.SHIPS[key]
					self.display_message(u"[%s] %s (%d)" % (ship.key, ship.name, ship.size), color, 1.5, top_offset, left_offset)
					top_offset += Settings.CELL_SIZE/2


				top_offset += Settings.CELL_SIZE/2
				text_obj = self.display_message(u"[SPACE]", Color.GRAY, 1.5, top_offset, left_offset)

				color_h = Color.SELECTED if self.ship_orientation == "H" else Color.GRAY
				color_v = Color.SELECTED if self.ship_orientation == "V" else Color.GRAY

				left_offset += text_obj.width + Settings.CELL_SIZE
				size = self.display_message("Horizontal", color_h, 1.5, top_offset, left_offset)

				left_offset += text_obj.width + Settings.CELL_SIZE
				self.display_message("Vertical", color_v, 1.5, top_offset, left_offset)

			pygame.display.flip()
		elif self.gamestate == GameState.GAMEOVER:
			self.screen.fill((255,255,0))
			# Colocar tela de vitoria
			pygame.display.flip()
		elif self.gamestate == GameState.WIN:
			pass
		elif self.gamestate == GameState.MENU:
			pass
		elif self.gamestate == GameState.LOSE:
			pass

	def exit(self):
		self.running = False
		self.states["thread_running"] = False
		sys.exit()

if __name__ == "__main__":
	game = Game()
	game.loop()