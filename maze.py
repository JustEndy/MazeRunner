import numpy as np
from random import randint, shuffle
import collections


class Maze():
    def __init__(self, row_count, col_count):
        self.row_count, self.col_count = row_count, col_count
        self.row_count_with_walls, self.col_count_with_walls = row_count + 2, col_count + 2
        self.maze = np.zeros((2 * row_count + 1, 2 * col_count + 1, 3), dtype=np.uint8)

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

        self._range = list(range(4))
        self._recursive_backtracking()

    def _recursive_backtracking(self):
        """Creates a maze using the recursive backtracking algorithm."""
        stack = collections.deque()  # List of visited cells [(x, y), ...]

        x = 2 * randint(0, self.row_count - 1) + 1
        y = 2 * randint(0, self.col_count - 1) + 1
        self.maze[x, y] = [255, 255, 255]  # Mark as visited

        while x and y:
            while x and y:
                stack.append((x, y))
                x, y = self._create_walk(x, y)
            x, y = self._create_backtrack(stack)

    def _create_walk(self, x, y):
        """Randomly walks from one pointer within the maze to another one."""
        for idx in self._random:  # Check adjacent cells randomly
            tx, ty = self._dir_two[idx](x, y)
            if not self._out_of_bounds(tx, ty) and self.maze[tx, ty, 0] == 0:  # Check if unvisited
                self.maze[tx, ty] = self.maze[self._dir_one[idx](x, y)] = [255, 255, 255]  # Mark as visited
                return tx, ty  # Return new cell

        return None, None  # Return stop values

    def _create_backtrack(self, stack):
        """Backtracks the stack until walking is possible again."""
        while stack:
            x, y = stack.pop()
            for direction in self._dir_two:  # Check adjacent cells
                tx, ty = direction(x, y)
                if not self._out_of_bounds(tx, ty) and self.maze[tx, ty, 0] == 0:  # Check if unvisited
                    return x, y  # Return cell with unvisited neighbour

        return None, None  # Return stop values if stack is empty

    def _out_of_bounds(self, x, y):
        """Checks if indices are out of bounds."""
        return x < 0 or y < 0 or x >= self.row_count_with_walls or y >= self.col_count_with_walls

    @property
    def _random(self):
        """Returns a random range to iterate over."""
        shuffle(self._range)
        return self._range