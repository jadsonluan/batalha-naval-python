import pygame, sys
from pygame.locals import *

# Helper functions

def create_window(width, height):
	return pygame.display.set_mode((width, height))

def rename_window(title):
	pygame.display.set_caption(title)