"""Основной модуль, корень проекта с логикой"""
import random
from objects import *
from options import *
random.seed(SEED)
print(SEED)


def generate_level(world_map):
    """Создание уровня"""
    def maybe(x, y):
        """Проверка, есть ли вокруг данной точки ещё свободные пути"""
        return any([world_map[x - 1][y], world_map[x + 1][y],
                    world_map[x][y - 1], world_map[x][y + 1]])

    def double_maybe(x, y):
        """Проверка, есть ли вокруг данной точки ещё свободные пути + диагонали"""
        ans = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
               (x, y - 1), (x, y), (x, y + 1),
               (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
        isit = [world_map[x - 1][y - 1], world_map[x - 1][y], world_map[x - 1][y + 1],
                world_map[x][y - 1], world_map[x][y], world_map[x][y + 1],
                world_map[x + 1][y - 1], world_map[x + 1][y], world_map[x + 1][y + 1]]
        return list(filter(lambda x: isit[ans.index(x)], ans))

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
    world_map[x_s // CELL_W, y_s // CELL_W], world_map[x_e // CELL_W, y_e // CELL_W] = 1, 1
    Wall(-1, y_s // CELL_W)

    sgs = []
    sgs.append(SG(choice(double_maybe(2, 2))))
    sgs.append(SG(choice(double_maybe((MAZE_S * 2 + 1) - 3, (MAZE_S * 2 + 1) - 3))))
    sgs.append(SG(choice(double_maybe(2, (MAZE_S * 2 + 1) - 3))))
    sgs.append(SG(choice(double_maybe((MAZE_S * 2 + 1) - 3, 2))))
    sgs.append(SG(choice(double_maybe(MAZE_S + 1, MAZE_S + 1))))
    sg_handler = SGHandler(sgs)
    return (x_s, y_s), (x_e, y_e), world_map, sg_handler


def generate_entity():
    """Создание основных объектов"""
    pos_p, pos_e, wmap, sg_handler = generate_level(Maze(MAZE_S, MAZE_S).get_maze())
    player = Player(pos_p)
    monster = Enemy(pos_e, player, wmap)
    Door(pos_p[0] // CELL_W, pos_p[1] // CELL_W, is_open=True, start=True)
    exit_door = Door(pos_e[0] // CELL_W, pos_e[1] // CELL_W)
    sg_handler.set_monster(monster)

    return player, monster, exit_door, sg_handler


def restart():
    """Перезапуск всей сессии"""
    global SCORE
    # Очистка всех спрайтовых групп
    all_groups.empty()
    walls_groups.empty()
    doors_groups.empty()
    player_group.empty()
    enemy_group.empty()
    sg_group.empty()
    # Очищаем SCORE
    SCORE = 0
    # Создаём сущности
    return generate_entity()


# Окно Pygame

menu = True
run_pause = False
run_game = True
while menu:
    if run_pause:
        player, monster, exit_door, sg_handler = restart()
    while run_pause:
        if run_game:
            pygame.mouse.set_visible(False)
        while run_game:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu = False
                    run_pause = False
                    run_game = False
                if event.type == PATHTIME:
                    monster.update_goal()
                elif event.type == HEARTBEAT:
                    player.heartbeat((monster.rect.x + monster.rect.w // 2,
                                      monster.rect.y + monster.rect.h // 2))
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

            # Открываем дверь по достижению 5 очков
            if SCORE == 5:
                exit_door.is_open = True
            else:
                exit_door.is_open = False

            # Добавляем очко
            if sg_handler.changed:
                SCORE += 1 if SCORE + 1 <= 5 else 0
                sg_handler.update_sg()
                monster.change_speed(SCORE)

            # Меняем угол направления взгляда с помощью мышки
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos != CENTER and 0 < mouse_pos[0] < WIDTH - 1 and 0 < mouse_pos[1] < HEIGHT - 1:
                player.change_angle(mouse_pos)
                pygame.mouse.set_pos(CENTER)

            # Рестарт уровня
            if player.rect.x + player.rect.w > HEIGHT or player.lost:
                player, monster, exit_door, sg_handler = restart()

            all_groups.update()
            all_groups.draw(screen)
            doors_groups.draw(screen)
            player_group.draw(screen)
            line_pos = math.degrees(math.sin(math.radians(player.angle))) + player.rect.x + player.rect.width // 2 + 1, \
                       math.degrees(math.cos(math.radians(player.angle))) + player.rect.y + player.rect.height // 2 + 1
            pygame.draw.line(screen, (100, 255, 100), (player.x + player.rect.width // 2,
                                                       player.y + player.rect.height // 2), line_pos)

            # Отрисовка инвенторя
            player.draw_inventory(SCORE)
            update_fps()

            if player.is_interacting:
                screen.blit(player.interact_text(), (0, 0))
            pygame.display.flip()
            clock.tick(FPS)

        ########## GAME PAUSED ##########

        pygame.mouse.set_visible(True)
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                run_pause = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run_game = True
                    pygame.mouse.set_pos(CENTER)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if RECT_PLAY.collidepoint(event.pos):
                    BTN_SOUND.play()
                    run_game = True
                    pygame.mouse.set_pos(CENTER)
                elif RECT_SETTINGS.collidepoint(event.pos):
                    BTN_SOUND.play()
                    menu = settings()
                elif RECT_EXIT.collidepoint(event.pos):
                    BTN_SOUND.play()
                    run_pause = False

        all_groups.draw(screen)
        player_group.draw(screen)
        line_pos = math.degrees(math.sin(math.radians(player.angle))) + player.rect.x + player.rect.width // 2 + 1,\
                   math.degrees(math.cos(math.radians(player.angle))) + player.rect.y + player.rect.height // 2 + 1
        pygame.draw.line(screen, (100, 255, 100), (player.x + player.rect.width // 2 + 1,
                                                   player.y + player.rect.height // 2 + 1), line_pos)

        ### TEXT DEBUG ###
        player.draw_inventory(SCORE)
        update_fps()

        # Отрисовываем pause-баннер
        [screen.blit(banner, (0, 0)) for banner in pause_banners()]
        # отрисовка менюшки
        work_with_menu('game')
        pygame.display.flip()
        clock.tick(FPS)

    ########## GAME MENU ##########
    screen.fill((0, 0, 0))

    # Картинка с лого
    screen.blit(pygame.transform.scale(NOIMAGE, (RECT_GAME_WINDOW.w, RECT_GAME_WINDOW.h)), (0, 0))
    work_with_menu('menu')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if RECT_PLAY.collidepoint(event.pos):
                BTN_SOUND.play()
                menu, run_pause, run_game = choose_session()
            elif RECT_SETTINGS.collidepoint(event.pos):
                BTN_SOUND.play()
                menu, run_pause, run_game = settings()
            elif RECT_EXIT.collidepoint(event.pos):
                menu = False
                BTN_SOUND.play()

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
