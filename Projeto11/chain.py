import time
import pygame
from factories import GridFactory, TaskFactory, ObstacleFactory, VH_A_Star_Factory, Diag_A_Star_Factory, Factory_Dijkstra, Factory_Hex_A_Star, Factory_Dijkstra_Diag
from abc import *

class Handler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, app):
        if self._next_handler:
            self._next_handler.handle(app)

class PygameInitHandler(Handler):
    def handle(self, app):
        print("Inicializando")
        app.W, app.H = 1200, 800
        pygame.init()
        pygame.font.init()
        app.tela = pygame.display.set_mode((app.W, app.H))
        pygame.display.set_caption("SAD 3")
        app.clock = pygame.time.Clock()
        super().handle(app)

class GridConfigHandler(Handler):
    def handle(self, app):
        print("Configurando")
        app.blockSize, app.COLS, app.ROWS = 35, 21, 15
        app.GRID_WIDTH = app.COLS * app.blockSize
        app.GRID_HEIGHT = app.ROWS * app.blockSize
        app.off_x = (app.W - app.GRID_WIDTH) // 2
        app.off_y = (app.H - app.GRID_HEIGHT) // 2
        super().handle(app)

class AssetsInitHandler(Handler):
    def handle(self, app):
        print("Carregando fabricas e configuracoes")
        app.colors = {
            "start": (0, 215, 0),
            "goal": (215, 0, 0),
            "free": (255, 255, 255),
            "text": (8, 8, 8),
            "path": [
        (0, 0, 200),
        (0, 150, 0),
        (150, 0, 150),
        (0, 180, 180),
        (200, 100, 0),
        (100, 100, 255),
        (180, 50, 180),
        (0, 100, 200),
        (100, 200, 50),
        (255, 100, 150)
    ]
        }
        app.grid_factory = GridFactory()
        app.obstacle_factory = ObstacleFactory()
        app.path_factories = {
            "A*_HV": VH_A_Star_Factory(),
            "A*_DIAG": Diag_A_Star_Factory(),
            "DIJKSTRA_HV": Factory_Dijkstra(),
            "DIJKSTRA_DIAG": Factory_Dijkstra_Diag(),
            "A*_HEX": Factory_Hex_A_Star()
        }
        app.task_factory = TaskFactory(app.path_factories, app.colors["path"])
        app.grid_type = "rect"
        super().handle(app)