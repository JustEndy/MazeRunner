"""Основной модуль, корень проекта с логикой"""
import random
from objects import *
from options import *


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
    monster = Enemy(pos_e, player, wmap)
    Door(pos_p[0] // CELL_W, pos_p[1] // CELL_W, is_open=True, start=True)
    exit_door = Door(pos_e[0] // CELL_W, pos_e[1] // CELL_W)
    return player, monster, exit_door


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
player, monster, exit_door = generate_entity()

running = True
run_game = True
while running:
    if run_game:
        pygame.mouse.set_visible(False)
    while run_game:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == PATHTIME:
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
                    run_game = False
                elif event.key == pygame.K_KP_PLUS:
                    SCORE += 1 if SCORE + 1 <= 5 else 0
                    monster.change_speed(SCORE)
                elif event.key == pygame.K_KP_MINUS:
                    SCORE -= 1 if SCORE - 1 >= 0 else 0
                    monster.change_speed(SCORE)

        if SCORE == 5:
            exit_door.is_open = True

        # Меняем угол направления взгляда с помощью мышки
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos != CENTER and 0 < mouse_pos[0] < WIDTH - 1 and 0 < mouse_pos[1] < HEIGHT - 1:
            player.change_angle(mouse_pos)
            pygame.mouse.set_pos(CENTER)

        # Обновляем счёт
        if player.rect.x + player.rect.w > HEIGHT or player.lost:
            player, monster = restart()

        all_groups.update()
        all_groups.draw(screen)
        player_group.draw(screen)
        line_pos = math.degrees(math.sin(math.radians(player.angle))) + player.rect.x + player.rect.width // 2 + 1, \
                   math.degrees(math.cos(math.radians(player.angle))) + player.rect.y + player.rect.height // 2 + 1
        pygame.draw.line(screen, (100, 255, 100), (player.x + player.rect.width // 2,
                                                   player.y + player.rect.height // 2), line_pos)
        screen.blit(update_fps(), (850, 0))
        screen.blit(debug_font.render('SCORE: ' + str(SCORE), True, pygame.Color("White")), (850, 50))
        screen.blit(player.update_stamina(), (850, 100))
        pygame.display.flip()
        clock.tick(FPS)

    ########## GAME PAUSED ##########

    pygame.mouse.set_visible(True)
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run_game = True
    all_groups.draw(screen)
    player_group.draw(screen)
    line_pos = math.degrees(math.sin(math.radians(player.angle))) + player.rect.x + player.rect.width // 2 + 1,\
               math.degrees(math.cos(math.radians(player.angle))) + player.rect.y + player.rect.height // 2 + 1
    pygame.draw.line(screen, (100, 255, 100), (player.x + player.rect.width // 2 + 1,
                                               player.y + player.rect.height // 2 + 1), line_pos)

    ### TEXT DEBUG ###
    screen.blit(update_fps(), (850, 0))
    screen.blit(debug_font.render('SCORE: ' + str(SCORE), True, pygame.Color("White")), (850, 50))
    screen.blit(player.update_stamina(), (850, 100))

    # Отрисовываем pause-баннер
    [screen.blit(banner, (0, 0)) for banner in pause_banners()]
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
