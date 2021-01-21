"""Основной модуль, корень проекта с логикой"""
from objects import *
from options import *
from datetime import  datetime


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
    world_map[x_e // CELL_W, y_e // CELL_W], world_map[x_s // CELL_W, y_s // CELL_W] = 2, 2
    start.kill(), end.kill()

    sgs = []
    sgs.append(SG(random.choice(double_maybe(2, 2)), ((x_e, y_e), (x_s, y_s))))
    sgs.append(SG(random.choice(double_maybe((MAZE_S * 2 + 1) - 3, (MAZE_S * 2 + 1) - 3)), ((x_e, y_e), (x_s, y_s))))
    sgs.append(SG(random.choice(double_maybe(2, (MAZE_S * 2 + 1) - 3)), ((x_e, y_e), (x_s, y_s))))
    sgs.append(SG(random.choice(double_maybe((MAZE_S * 2 + 1) - 3, 2)), ((x_e, y_e), (x_s, y_s))))
    sgs.append(SG(random.choice(double_maybe(MAZE_S + 1, MAZE_S + 1)), ((x_e, y_e), (x_s, y_s))))
    sg_handler = SGHandler(sgs)
    return (x_s, y_s), (x_e, y_e), world_map, sg_handler


def generate_entity():
    """Создание основных объектов"""
    pos_p, pos_e, wmap, sg_handler = generate_level(Maze(MAZE_S, MAZE_S).get_maze())
    exit_doors = Door(pos_p[0] // CELL_W, pos_p[1] // CELL_W), Door(pos_e[0] // CELL_W, pos_e[1] // CELL_W)
    player = Player(pos_p, wmap, exit_doors)
    monster = Enemy(pos_e, player)
    sg_handler.set_monster(monster)
    player.set_monster(monster)
    player.set_sg_handler(sg_handler)

    return player, monster, exit_doors, sg_handler


def restart():
    """Перезапуск всей сессии"""
    # Очистка всех спрайтовых групп
    all_groups.empty()
    walls_groups.empty()
    doors_groups.empty()
    player_group.empty()
    enemy_group.empty()
    sg_group.empty()
    item_group.empty()
    meat_group.empty()
    # Создаём сущности
    return generate_entity()


# Окно Pygame
player = None
menu = True
run_pause = False
run_game = True
while menu:
    if run_pause:
        random.seed(SEED_BAR.seed)
        player, monster, exit_doors, sg_handler = restart()
        play_doorsound = True
    while run_pause:
        if run_game:
            pygame.mouse.set_visible(False)
        while run_game:
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
                elif event.type == ITEMSPAWN:
                    player.item_spawner.spawn()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        monster.change_behave()
                    elif event.key == pygame.K_BACKSPACE:
                        # Мини-карта для дебага
                        DO2D = not DO2D
                    elif event.key == pygame.K_ESCAPE:
                        run_game = False
                    elif event.key == pygame.K_KP_PLUS:
                        player.score_bar.update(1)
                        monster.change_speed()
                    elif event.key == pygame.K_KP_MINUS:
                        player.score_bar.update(-1)
                        monster.change_speed()
                    elif event.key == pygame.K_F2:
                        # Скриншот
                        filename = f'data/screenshots/{str(datetime.now()).split(".")[0].replace(":", "-")}.png'
                        pygame.image.save(screen, filename)
                elif event.type == pygame.MOUSEWHEEL:
                    player.inventory.update(event.y)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        player.inventory.use()
            player.inventory.update()

            # Открываем дверь по достижению 5 очков
            if player.score_bar.score == 5:
                for door in exit_doors:
                    door.is_open = True
                    player.w_map[door.pos] = 3
                if play_doorsound:
                    DOOR_SOUND.play()
                    play_doorsound = False
            else:
                for door in exit_doors:
                    door.is_open = False
                    player.w_map[door.pos] = 2
                play_doorsound = True

            # Меняем угол направления взгляда с помощью мышки
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos != CENTER and 0 < mouse_pos[0] < WIDTH - 1 and 0 < mouse_pos[1] < HEIGHT - 1:
                player.change_angle(mouse_pos)
                pygame.mouse.set_pos(CENTER)

            # Рестарт уровня
            if player.win or player.lost:
                run_game = False
                run_pause = False

            all_groups.update()

            if DO2D:
                screen.fill((0, 0, 0))
                all_groups.draw(screen)
                doors_groups.draw(screen)
                player_group.draw(screen)
                x = player.x + CELL_W * math.cos(player.angle)
                y = player.y + CELL_W * math.sin(player.angle)
                pygame.draw.line(screen, (255, 255, 255), player.pos, (x, y))
            else:
                # Отрисовка Псевдо 3д
                screen.fill((45, 45, 45))
                player.draw_world()

            # Отрисовка инвенторя
            player.draw_inventory()
            update_fps()

            if player.is_interacting:
                screen.blit(player.interact_text(), (0, 0))
            pygame.display.flip()
            clock.tick(FPS)

        ########## GAME PAUSED ##########

        pygame.mouse.set_visible(True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                run_pause = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run_game = True
                    pygame.mouse.set_pos(CENTER)
                elif event.key == pygame.K_F2:
                    # Скриншот
                    filename = f'data/screenshots/{str(datetime.now()).split(".")[0].replace(":", "-")}.png'
                    pygame.image.save(screen, filename)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if RECT_PLAY.collidepoint(event.pos):
                    BTN_SOUND.play()
                    run_game = True
                    pygame.mouse.set_pos(CENTER)
                elif RECT_SETTINGS.collidepoint(event.pos):
                    BTN_SOUND.play()
                    args = settings()
                    if not args:
                        menu = False
                    elif args[0] is None:
                        pass
                    else:
                        with open("settings.txt", 'w') as f:
                            f.write(f'SENSITIVITY={args[0]}\n')
                            f.write(f'BTN_F={args[1]}\n')
                            f.write(f'BTN_L={args[2]}\n')
                            f.write(f'BTN_R={args[3]}\n')
                            f.write(f'BTN_B={args[4]}\n')
                            f.write(f'BTN_INTERACT={args[5]}\n')
                            f.write(f'WIDTH={args[6][1]}\n')
                            f.write(f'HEIGHT={args[6][0]}\n')
                elif RECT_EXIT.collidepoint(event.pos):
                    BTN_SOUND.play()
                    run_pause = False

        screen.fill((0, 0, 0))
        player.draw_world()

        # Отрисовываем pause-баннер
        [screen.blit(banner, (0, 0)) for banner in pause_banners()]
        # отрисовка менюшки
        work_with_menu('game')
        SEED_BAR.draw()
        pygame.display.flip()
        clock.tick(FPS)

    ########## GAME MENU ##########
    screen.fill((0, 0, 0))

    # Картинка с лого
    screen.blit(pygame.transform.scale(LOGO, (RECT_GAME_WINDOW.w, RECT_GAME_WINDOW.h)), (0, 0))
    work_with_menu('menu')

    player = game_over_message(player)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if RECT_PLAY.collidepoint(event.pos):
                BTN_SOUND.play()
                menu, run_pause, seed = choose_session(SEED_BAR)
                if seed:
                    SEED_BAR.seed = seed
            elif RECT_SETTINGS.collidepoint(event.pos):
                BTN_SOUND.play()
                args = settings()
                if not args:
                    menu = False
                elif args[0] is None:
                    pass
                else:
                    with open("settings.txt", 'w') as f:
                        f.write(f'SENSITIVITY={args[0]}\n')
                        f.write(f'BTN_F={args[1]}\n')
                        f.write(f'BTN_L={args[2]}\n')
                        f.write(f'BTN_R={args[3]}\n')
                        f.write(f'BTN_B={args[4]}\n')
                        f.write(f'BTN_INTERACT={args[5]}\n')
                        f.write(f'WIDTH={args[6][1]}\n')
                        f.write(f'HEIGHT={args[6][0]}\n')
            elif RECT_EXIT.collidepoint(event.pos):
                menu = False
                BTN_SOUND.play()

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
