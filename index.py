# coding: utf-8
# (C) 2017, Jadson Luan / UFCG, Programação I e Laboratório de Programação I
# Batalha Naval

import pygame, sys
from pygame.locals import *
from enum import Enum

class Settings:
	CELL_SIZE = 50
	PADDING = 4
	TOTAL_PADDING = 9 * PADDING

class Color:
	BACKGROUND = (25,28,30)
	SEA = (19,126,229)

class Piece:
	def __init__(self, name, size, color):
		self.name = name
		self.size = size
		self.color = color

class Ship(Enum):
	CARRIER = Piece(u"Porta-aviões", 5, (19,126,229))
	BATTLESHIP = Piece("Navio de Guerra", 4, (19,126,229))
	CRUISER = Piece("Cruzador", 3, (19,126,229))
	DESTROYER = Piece("Contratorpedeiro", 2, (19,126,229))
	SUBMARINE = Piece("Submarino", 1, (19,126,229))

class GameState:
	PREPARATION = 0
	MATCH_RUNNING = 1

class Match:
	board1 = []
	board2 = []

	def __init__(self, screen):
		self.screen = screen
		self.setup_boards()
		self.board_surface = pygame.Surface([10 * Settings.CELL_SIZE + Settings.TOTAL_PADDING, 10 * Settings.CELL_SIZE + Settings.TOTAL_PADDING])

	def setup_boards(self):
		for row in range(10):
			self.board1.append([])
			self.board2.append([])
			for col in range(10):
				self.board1[row].append("S")
				self.board2[row].append("S")

	def render(self):
		board1 = self.board1
		board_surface = self.board_surface
		screen = self.screen

		board_surface.fill((22,141,255))

		for row in range(len(board1)):
			for col in range(len(board1[0])):
				# piece = board1[row][col]

				x = Settings.CELL_SIZE * col
				y = Settings.CELL_SIZE * row

				if col > 0:
					x += Settings.PADDING * (col)

				if row > 0:
					y += Settings.PADDING * (row)

				position = x, y

				cell = pygame.Surface([Settings.CELL_SIZE, Settings.CELL_SIZE])
				cell.fill(Color.SEA)
				board_surface.blit(cell, position)

		self.grid1 = pygame.Surface([Settings.CELL_SIZE * 7, Settings.CELL_SIZE * 5])
		self.grid1.fill((255,0,0))
		pos = Settings.CELL_SIZE + (Settings.CELL_SIZE * 10 + Settings.TOTAL_PADDING) + Settings.CELL_SIZE, Settings.CELL_SIZE
		screen.blit(self.grid1, pos)

		self.grid2 = pygame.Surface([Settings.CELL_SIZE * 7, Settings.CELL_SIZE * 5])
		self.grid2.fill((255,0,0))
		pos = Settings.CELL_SIZE + (Settings.CELL_SIZE * 10 + Settings.TOTAL_PADDING) + Settings.CELL_SIZE, Settings.TOTAL_PADDING + Settings.CELL_SIZE * 6
		screen.blit(self.grid2, pos)

		screen.blit(board_surface, (Settings.CELL_SIZE, Settings.CELL_SIZE))

class Game:
	def __init__(self):
		pygame.init()
		self.width, self.height = 20 * Settings.CELL_SIZE + Settings.TOTAL_PADDING, 12 * Settings.CELL_SIZE + Settings.TOTAL_PADDING
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Batalha Naval em Python")
		self.match = Match(self.screen)

	def loop(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == KEYDOWN:
					print "pressed", event

			self.render()

	def render(self):
		self.screen.fill(Color.BACKGROUND)
		self.match.render()
		pygame.display.flip()

if __name__ == "__main__":
	game = Game()
	game.loop()