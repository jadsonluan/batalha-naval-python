# coding: utf-8
# (C) 2017, Jadson Luan / UFCG, Programação I e Laboratório de Programação I
# Batalha Naval

import pygame, sys
from pygame.locals import *

from helper import *

# constants
SEA, SUBMARINE, DESTROYER, TANKER, AIRCRAFT_CARRIER = 1, 2, 3, 4, 5

# game settings
cell_size = 50
padding = 4
total_padding = 9 * padding

## Colors 
bg_color = (25,28,30)

class Piece:
	def __init__(self, name, size, color):
		self.name = name
		self.size = size
		self.color = color

class Match:
	board1 = []
	board2 = []

	def __init__(self, screen):
		self.screen = screen
		self.setup_boards()
		self.board_surface = pygame.Surface([10 * cell_size + total_padding, 10 * cell_size + total_padding])

	def setup_boards(self):
		for row in range(10):
			self.board1.append([])
			self.board2.append([])
			for col in range(10):
				self.board1[row].append(Piece("SEA", 1, (19,126,229)))
				self.board2[row].append(Piece("SEA", 1, (19,126,229)))

	def render(self):
		board1 = self.board1
		board_surface = self.board_surface
		screen = self.screen

		board_surface.fill((22,141,255))

		for row in range(len(board1)):
			for col in range(len(board1[0])):
				piece = board1[row][col]

				x = cell_size * col
				y = cell_size * row

				if col > 0:
					x += padding * (col)

				if row > 0:
					y += padding * (row)

				position = x, y

				cell = pygame.Surface([cell_size, cell_size])
				cell.fill(piece.color)
				board_surface.blit(cell, position)

		self.grid1 = pygame.Surface([cell_size * 7, cell_size * 5])
		self.grid1.fill((255,0,0))
		pos = cell_size + (cell_size * 10 + total_padding) + cell_size, cell_size
		screen.blit(self.grid1, pos)

		self.grid2 = pygame.Surface([cell_size * 7, cell_size * 5])
		self.grid2.fill((255,0,0))
		pos = cell_size + (cell_size * 10 + total_padding) + cell_size, total_padding + cell_size * 6
		screen.blit(self.grid2, pos)

		screen.blit(board_surface, (cell_size, cell_size))


class Game:
	def __init__(self):
		pygame.init()
		total_padding = 9 * padding
		self.width, self.height = 20 * cell_size + total_padding, 12 * cell_size + total_padding
		self.screen = create_window(self.width, self.height)
		rename_window("Batalha Naval em Python")
		self.match = Match(self.screen)

	def loop(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

			self.render()

	def render(self):
		self.screen.fill(bg_color)
		self.match.render()
		pygame.display.flip()

if __name__ == "__main__":
	game = Game()
	game.loop()