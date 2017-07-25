# coding: utf-8
# (C) 2017, Jadson Luan / UFCG, Programação I e Laboratório de Programação I
# Batalha Naval

import pygame, sys
from pygame.locals import *
from enum import Enum

class Settings:
	CELL_SIZE = 50
	PADDING = 4
	TOTAL_PADDING = 11 * PADDING
	BOARD_SIZE = [10 * CELL_SIZE + TOTAL_PADDING, 10 * CELL_SIZE + TOTAL_PADDING]

class Color:
	BACKGROUND = (25,28,30)
	SEA = (22,141,255)

class GameState:
	PREPARATION = 0
	MATCH_RUNNING = 1

class Piece:
	def __init__(self, name, size, color):
		self.name = name
		self.size = size
		self.color = color

class Ship(Enum):
	CARRIER = Piece(u"Porta-aviões", 5, (229,0,0))
	BATTLESHIP = Piece("Navio de Guerra", 4, (255,170,64))
	CRUISER = Piece("Cruzador", 3, (174,253,61))
	DESTROYER = Piece("Contratorpedeiro", 2, (253,255,48))
	SUBMARINE = Piece("Submarino", 1, (255,106,6))

class Cell(pygame.sprite.Sprite):
	def __init__(self, location, ship=None):
		pygame.sprite.Sprite.__init__(self)
		
		self.ship_name = ship
		self.ship = ship.value if ship else None
		
		self.image = pygame.Surface([Settings.CELL_SIZE, Settings.CELL_SIZE])
		color = ship.value.color if ship else Color.SEA
		self.image.fill(color)
		self.rect = self.image.get_rect()

		row, col = location
		x = Settings.CELL_SIZE * col
		y = Settings.CELL_SIZE * row
		x += Settings.PADDING * (col+1)
		y += Settings.PADDING * (row+1)

		self.rect.x, self.rect.y = x, y

	def set_ship(self, ship):
		self.ship = ship
		color = ship.value.color if ship else Color.SEA
		self.image.fill(color)

class Match:
	board1 = []
	board2 = []

	def __init__(self, screen):
		self.screen = screen
		self.setup_boards()
		self.board_surface = pygame.Surface(Settings.BOARD_SIZE)

	def setup_boards(self):
		for row in range(10):
			self.board1.append([])
			self.board2.append([])
			for col in range(10):
				self.board1[row].append(Cell((row, col)))
				self.board2[row].append(Cell((row, col)))

	def put_ship(self, position, ship_type, direction):
		board = self.board1
		ship = ship_type.value
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

	def render(self):
		board1 = self.board1
		board_surface = self.board_surface
		screen = self.screen

		board_surface.fill((0,0,255))

		for row in range(len(board1)):
			for col in range(len(board1[0])):
				cell = board1[row][col]

				# x = Settings.CELL_SIZE * col
				# y = Settings.CELL_SIZE * row

				# if col > 0:
				# 	x += Settings.PADDING * (col)

				# if row > 0:
				# 	y += Settings.PADDING * (row)

				# position = x, y

				# cell = pygame.Surface([Settings.CELL_SIZE, Settings.CELL_SIZE])
				# cell.fill(Color.SEA)
				board_surface.blit(cell.image, cell.rect)

		# self.grid1 = pygame.Surface([Settings.CELL_SIZE * 8, Settings.CELL_SIZE * 4])
		# self.grid1.fill((255,0,0))
		# pos = Settings.CELL_SIZE + (Settings.CELL_SIZE * 10 + Settings.TOTAL_PADDING), Settings.CELL_SIZE
		# screen.blit(self.grid1, pos)

		# self.grid2 = pygame.Surface([Settings.CELL_SIZE * 8, Settings.CELL_SIZE * 4])
		# self.grid2.fill((255,0,0))
		# pos = Settings.CELL_SIZE + (Settings.CELL_SIZE * 10 + Settings.TOTAL_PADDING), Settings.TOTAL_PADDING + Settings.CELL_SIZE * 5
		# screen.blit(self.grid2, pos)

		screen.blit(board_surface, (0,0))

class Game:
	def __init__(self):
		pygame.init()
		self.width, self.height = 18 * Settings.CELL_SIZE + Settings.TOTAL_PADDING, 10 * Settings.CELL_SIZE + Settings.TOTAL_PADDING
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Batalha Naval em Python")
		self.selected_ship = None
		self.ship_orientation = "H"
		self.match = Match(self.screen)

	def loop(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == KEYDOWN:
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
				r_click, m_click, l_click = pressed

				if r_click:
					mouse_pos = pygame.mouse.get_pos()
					board = self.match.board1
					for row in range(len(board)):
						for col in range(len(board[0])):
							cell = board[row][col]
							if cell.rect.collidepoint(mouse_pos):
								if self.selected_ship:
									if self.match.put_ship((row, col), self.selected_ship, self.ship_orientation):
										self.selected_ship = None
										print "ship colocado em %d,%d" % (row, col)
									else:
										print "não foi possivel por o ship em %d,%d" % (row, col)
				
			self.render()

	def render(self):
		self.screen.fill(Color.BACKGROUND)
		self.match.render()
		pygame.display.flip()

if __name__ == "__main__":
	game = Game()
	game.loop()