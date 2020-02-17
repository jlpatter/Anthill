import random

from anthill.plants import Leafy
from anthill.structures import Hill
from anthill.utils.graphics import GraphicComponent
from anthill.utils.vectors import Vector2
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class State:
    """This is an enum"""
    SEARCH = 1
    GET_FOOD = 2
    RETURN_TO_HILL = 3


class Ant(GraphicComponent):
    MAX_SPEED = 40
    MAX_SEARCH_SECONDS = 0.5
    MAX_SEARCH_RADIUS = 20
    WIDTH = 4
    HEIGHT = 4

    def __init__(self, x, y, width=WIDTH, height=HEIGHT):
        self.velocity = Vector2.zero()
        self.speed = Ant.MAX_SPEED
        self.search_seconds = random.uniform(0.0, Ant.MAX_SEARCH_SECONDS)
        self.state = State.SEARCH

        self.approaching = None
        self.carrying = None
        self.direction_to_go = 0
        super().__init__(x, y, width, height)

    def _update_position(self):
        old_x = self.x
        old_y = self.y
        self.x = round(old_x + self.velocity.x)
        self.y = round(old_y + self.velocity.y)

        # Stay in the screen
        if not 0 < self.x < SCREEN_WIDTH:
            self.x = old_x
        if not 0 < self.y < SCREEN_HEIGHT:
            self.y = old_y

    def _search(self, leafies, hill, delta_time):
        self.search_seconds -= delta_time
        if self.search_seconds <= 0.0:
            self.direction_to_go = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).get_normalized_vector()
            self.velocity = self.direction_to_go * self.speed * delta_time
            self.search_seconds = random.uniform(0.0, Ant.MAX_SEARCH_SECONDS)
        for leafy in leafies:
            if self.x - Ant.MAX_SEARCH_RADIUS <= leafy.x <= self.x + Ant.MAX_SEARCH_RADIUS and \
                    self.y - Ant.MAX_SEARCH_RADIUS <= leafy.y <= self.y + Ant.MAX_SEARCH_RADIUS and \
                    leafy.being_approached_by is None and leafy.being_carried_by is None and leafy not in hill.food_store:
                self.state = State.GET_FOOD
                self.approaching = leafy
                leafy.being_approached_by = self
                break

    def _get_food(self, delta_time):
        self.direction_to_go = Vector2(self.approaching.x - self.x, self.approaching.y - self.y).get_normalized_vector()
        self.velocity = self.direction_to_go * self.speed * delta_time
        if self.approaching.x <= self.x + Ant.WIDTH and self.approaching.x + Leafy.WIDTH >= self.x and self.approaching.y <= self.y + Ant.HEIGHT and self.approaching.y + Leafy.HEIGHT >= self.y:
            self.state = State.RETURN_TO_HILL
            self.carrying = self.approaching
            self.approaching = None
            self.carrying.being_carried_by = self
            self.carrying.being_approached_by = None

    def _return_to_hill(self, hill, delta_time):
        self.direction_to_go = Vector2(hill.x - self.x, hill.y - self.y).get_normalized_vector()
        self.carrying.x = self.x - Ant.WIDTH
        self.carrying.y = self.y
        self.velocity = self.direction_to_go * self.speed * delta_time
        if hill.x <= self.x + Ant.WIDTH and hill.x + Hill.WIDTH >= self.x and hill.y <= self.y + Ant.HEIGHT and hill.y + Hill.HEIGHT >= self.y:
            self.state = State.SEARCH
            hill.food_store.append(self.carrying)
            self.carrying.being_carried_by = None
            self.carrying = None

    def update(self, leafies, hill, delta_time):
        if self.state == State.SEARCH:
            self._search(leafies, hill, delta_time)
        elif self.state == State.GET_FOOD:
            self._get_food(delta_time)
        elif self.state == State.RETURN_TO_HILL:
            self._return_to_hill(hill, delta_time)
        self._update_position()
