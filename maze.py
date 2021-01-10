"""Ворованный и переработанный модуль для генерации лабиринта :)"""
import numpy as np
from random import randint, shuffle
import collections


class Maze:
    def __init__(self, row_count, col_count):
        self.row_count, self.col_count = row_count, col_count
        self.row_count_with_walls, self.col_count_with_walls = 2 * row_count + 1, 2 * col_count + 1
        self.maze = np.zeros((2 * row_count + 1, 2 * col_count + 1), dtype=np.uint8)

        self._dir_one = [
            lambda x, y: (x + 1, y),
            lambda x, y: (x - 1, y),
            lambda x, y: (x, y - 1),
            lambda x, y: (x, y + 1)]
        self._dir_two = [
            lambda x, y: (x + 2, y),
            lambda x, y: (x - 2, y),
            lambda x, y: (x, y - 2),
            lambda x, y: (x, y + 2)]

        self.range = [0, 1, 2, 3]
        self.recursive_backtracking()

    def recursive_backtracking(self):
        """Генератор лабиринта, алгоритм 'Поиск с возвратом'"""
        stack = collections.deque()  # Список посещённых клеток [(x, y), ...]

        x = 2 * randint(0, self.row_count - 1) + 1
        y = 2 * randint(0, self.col_count - 1) + 1
        self.maze[x, y] = 1  # Помечаем как посещённую (дорога)

        while x and y:
            while x and y:
                stack.append((x, y))
                x, y = self.create_walk(x, y)
            x, y = self.create_backtrack(stack)

    def create_walk(self, x, y):
        """Рандомно гуляет от одной точки лабиринта до другой"""
        shuffle(self.range)
        for idx in self.range:  # выбираем случайное направление
            tx, ty = self._dir_two[idx](x, y)
            if not self.out_of_bounds(tx, ty) and self.maze[tx, ty] == 0:  # Если не посещали, то
                self.maze[tx, ty] = self.maze[self._dir_one[idx](x, y)] = 1  # помечаем посещённой
                return tx, ty  # возвращаем новую клетку

        return None, None  # Конечные значения

    def create_backtrack(self, stack):
        """Возвращаемся по стаку, пока не будет доступна ходьба"""
        while stack:
            x, y = stack.pop()
            for direction in self._dir_two:  # Проверяем случайное направление
                tx, ty = direction(x, y)
                if not self.out_of_bounds(tx, ty) and self.maze[tx, ty] == 0:  # Если не посещали, то
                    return x, y  # Возвращаем клетку с непосещённым соседом

        return None, None  # Конечные значения, на случай если стак пустой

    def out_of_bounds(self, x, y):
        """Проверка, выходят ли координаты за границу лабиринта"""
        return x < 0 or y < 0 or x >= self.row_count_with_walls or y >= self.col_count_with_walls

    def get_maze(self):
        """Возвращает готовый лабиринт"""
        return self.maze
