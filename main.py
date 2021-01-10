"""Основной модуль, корень проекта с логикой"""
import random
from objects import *
from options import *
score = 0


def generate_level(world_map):
    """Создание уровня"""
    def maybe(x, y):
        """Проверка, есть ли вокруг данной точки ещё свободные пути"""
        return any([world_map[x - 1][y], world_map[x + 1][y],
                    world_map[x][y - 1], world_map[x][y + 1]])

    potential_start, potential_end = [], []
    for x in range(len(world_map)):
        for y in range(len(world_map[x])):
            if not world_map[x][y]:
                cell = Wall(x, y)
                if x == 0:
                    if world_map[x + 1][y]:
                        potential_start.append(cell)
                elif x == len(world_map) - 1:
                    if world_map[x - 1][y]:
                        potential_end.append(cell)
                elif y != 0 and y != len(world_map[x]) - 1:
                    if random.random() <= 0.1 and maybe(x, y):
                        world_map[x, y] = 1
                        cell.kill()
    start, end = random.choice(potential_start), random.choice(potential_end)
    x_s, y_s, x_e, y_e = start.rect.x, start.rect.y, end.rect.x, end.rect.y
    start.kill(), end.kill()
    world_map[x_s // CELL_W, y_s // CELL_W], world_map[x_e // CELL_W, y_e // CELL_W] = 1, 1
    Wall(-1, y_s // CELL_W)
    return (x_s, y_s), (x_e, y_e), world_map


def generate_entity():
    """Создание основных объектов"""
    pos_p, pos_e, wmap = generate_level(Maze(MAZE_S, MAZE_S).get_maze())
    player = Player(pos_p)
    monster = Enemy(pos_e, player, wmap) if not score else Enemy(pos_e, player, wmap, 0.4 + score * 0.1)
    Door(pos_p[0] // CELL_W, pos_p[1] // CELL_W, is_open=True, start=True)
    return player, monster


def restart():
    """Перезапуск всей сессии"""
    # Очистка всех спрайтовых групп
    all_groups.empty()
    walls_groups.empty()
    doors_groups.empty()
    player_group.empty()
    enemy_group.empty()
    # Создаём сущности
    return generate_entity()


# Окно Pygame
player, monster = generate_entity()
running = True
pygame.mouse.set_visible(False)
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == PATHTIME:
            monster.update_goal()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                monster.change_behave()
            elif event.key == pygame.K_BACKSPACE:
                # Блок отладки по нажатию на Бэкспейс
                print(player.angle)
                print(monster.aggressive)
                print(monster.speed, monster.speed_coef)
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Меняем угол направления взгляда с помощью мышки
    mouse_pos = pygame.mouse.get_pos()
    if mouse_pos != CENTER and 0 < mouse_pos[0] < WIDTH and 0 < mouse_pos[1] < HEIGHT:
        player.change_angle(mouse_pos)
        pygame.mouse.set_pos(CENTER)

    # Обновляем счёт
    if player.rect.x + player.rect.w > HEIGHT or player.lost:
        score += player.score()
        player, monster = restart()

    all_groups.update()
    all_groups.draw(screen)
    player_group.draw(screen)
    line_pos = math.degrees(math.sin(math.radians(player.angle))) + player.rect.x + player.rect.width // 2,\
               math.degrees(math.cos(math.radians(player.angle))) + player.rect.y + player.rect.height // 2
    pygame.draw.line(screen, (100, 255, 100), (player.x + player.rect.width // 2,
                                               player.y + player.rect.height // 2), line_pos)
    screen.blit(update_fps(), (850, 0))
    screen.blit(font.render('SCORE: ' + str(score), True, pygame.Color("White")), (850, 50))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
