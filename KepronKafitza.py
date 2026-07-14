import pygame

pygame.init()       

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Loading screen
loading_image = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\loadingCover.png").convert_alpha()
loading_image = pygame.transform.scale(loading_image, (475, SCREEN_HEIGHT))
loading_alpha = 255
loading_start_time = pygame.time.get_ticks()
loading_hold_duration = 2000  # keep cover and side bars fully solid for 1.5 seconds
loading_fade_duration = 1000  # fade out over the next 1.5 seconds
loading_duration = loading_hold_duration + loading_fade_duration
loading_active = True
# precompute centered position for loading image
loading_rect = loading_image.get_rect()
loading_rect.left = (SCREEN_WIDTH - loading_rect.width) // 2
loading_rect.top = 0

kepron_image = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\baldwinTemporary.png").convert_alpha()
kepron = pygame.transform.scale(kepron_image, (100, 70))

lebron_image = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\lebron.png").convert_alpha()
lebron = pygame.transform.scale(lebron_image, (100, 70))

background_image = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\backgroundTemporary3.jpg").convert()
background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

ground1_image = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\ground1.png").convert()

player = kepron
selected_character = 'kepron'

music = r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\test-original-gangster.mp3"
pygame.mixer.music.load(music)
volume = 0.8
pygame.mixer.music.set_volume(volume)

# kepron sprite sheets
kepron_walk_right_sheet = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\kepron-walk-right.png").convert_alpha()
kepron_walk_left_sheet = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\kepron-walk-left.png").convert_alpha()
kepron_idle = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\kepron-idle.png").convert_alpha()

# kepron idle sprites (sheet is 704x1408 -> 1 column x 2 rows of 704x704)
KEPRON_IDLE_FRAME_W = 704
KEPRON_IDLE_FRAME_H = 704
kepron_idle_sprites = []
for row in range(2):
    sprite = kepron_idle.subsurface(
        pygame.Rect(0, row * KEPRON_IDLE_FRAME_H, KEPRON_IDLE_FRAME_W, KEPRON_IDLE_FRAME_H)
    ).copy()
    crop = sprite.get_bounding_rect()
    sprite = sprite.subsurface(crop).copy()
    kepron_idle_sprites.append(sprite)

rockroll_attack_sheet = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\rockroll-attack.png").convert_alpha()

ROCKROLL_FRAME_WIDTH = 704
ROCKROLL_FRAME_HEIGHT = 704
rockroll_attack_sprites = []

for row in range(3):
    for col in range(2):
        sprite = rockroll_attack_sheet.subsurface(
            pygame.Rect(col * ROCKROLL_FRAME_WIDTH,
                        row * ROCKROLL_FRAME_HEIGHT,
                        ROCKROLL_FRAME_WIDTH,
                        ROCKROLL_FRAME_HEIGHT)
        ).copy()
        crop = sprite.get_bounding_rect()
        sprite = sprite.subsurface(crop).copy()
        rockroll_attack_sprites.append(sprite)

rockRoll = None
rockroll_sprite_index = 0
rockroll_animation_timer = pygame.time.get_ticks()
ROCKROLL_ANIMATION_INTERVAL = 120
rockRoll_x = 100
rockRoll_y = 0
enemy_health = 5
enemy_alive = True
points = 0

SPRITE_SIZE = 704
kepron_walk_sprites = []

for row in range(3):
    for col in range(3):
        # Skip the empty bottom-right square
        if row == 2 and col == 2:
            continue

        sprite = kepron_walk_right_sheet.subsurface(
            pygame.Rect(col * SPRITE_SIZE,
                        row * SPRITE_SIZE,
                        SPRITE_SIZE,
                        SPRITE_SIZE)
        ).copy()

        # Crop away transparent pixels
        crop = sprite.get_bounding_rect()
        sprite = sprite.subsurface(crop).copy()

        kepron_walk_sprites.append(sprite)

# use first frame from spritesheet as the player image so kepronWalkLeft appears
if len(kepron_walk_sprites) > 0:
    try:
        # prefer idle first frame when available for default standing image
        if len(kepron_idle_sprites) > 0:
            player = pygame.transform.scale(kepron_idle_sprites[0].copy().convert_alpha(), (100, 100))
        else:
            player = pygame.transform.scale(kepron_walk_sprites[0].copy().convert_alpha(), (100, 100))
    except Exception:
        # fallback to previously loaded kepron image
        player = kepron

sprite_index = 0
idle_sprite_index = 0
sprite_animation_timer = pygame.time.get_ticks()
idle_animation_timer = pygame.time.get_ticks()
SPRITE_ANIMATION_INTERVAL = 100
IDLE_ANIMATION_INTERVAL = 400

custom_font = pygame.font.Font("C:/Users/Pc/Documents/Columbia/Kepron_Kafitza/assets/LowresPixel-Regular.otf", 32)

def draw_points_hud(surface):
    score_text = custom_font.render(f'Points: {points}', True, (255, 255, 255))
    padding = 12
    margin_right = 18
    margin_top = 12
    text_rect = score_text.get_rect()
    box_w = text_rect.width + padding * 2
    box_h = text_rect.height + padding * 2
    box_x = SCREEN_WIDTH - box_w - margin_right
    box_y = margin_top
    box = pygame.Rect(box_x, box_y, box_w, box_h)

    panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 160))
    surface.blit(panel, box.topleft)
    surface.blit(score_text, (box_x + padding, box_y + padding))

ground_y = 500
player_x = (SCREEN_WIDTH - player.get_width()) // 2
player_y = ground_y - player.get_height()
player_speed = 0.5
player_vy = 0
gravity = 0.00225
jump_strength = -1
on_ground = True

if len(rockroll_attack_sprites) > 0:
    rockRoll_y = ground_y - 80

running = True

show_quit_dialog = False
quit_dialog_mode = 'quit'
game_started = False
store_open = False
settings_open = False
controls_open = False
clicked_button = None
click_time = 0
volume_slider_active = False
CLICK_DURATION = 150  # ms
# main menu buttons (centered)
BTN_W, BTN_H = 240, 40
BTN_PADDING = 10
MENU_OFFSET = -40  # move main menu (title + buttons) up by this many pixels
def get_main_menu_buttons():
    x = (SCREEN_WIDTH - BTN_W) // 2
    total_height = 5 * BTN_H + 4 * BTN_PADDING
    y = (SCREEN_HEIGHT - total_height) // 2 + MENU_OFFSET
    # stack downward: Start, Settings, Store, Quit
    start_btn = pygame.Rect(x, y, BTN_W, BTN_H)
    settings_btn = pygame.Rect(x, y + BTN_H + BTN_PADDING, BTN_W, BTN_H)
    controls_btn = pygame.Rect(x, y + 2*(BTN_H + BTN_PADDING), BTN_W, BTN_H)
    store_btn = pygame.Rect(x, y + 3*(BTN_H + BTN_PADDING), BTN_W, BTN_H)
    quit_btn = pygame.Rect(x, y + 4*(BTN_H + BTN_PADDING), BTN_W, BTN_H)
    return start_btn, settings_btn, controls_btn, store_btn, quit_btn

def get_quit_dialog_buttons():
    w, h = 400, 180
    x = (SCREEN_WIDTH - w) // 2
    y = (SCREEN_HEIGHT - h) // 2
    btn_w, btn_h = 120, 40
    padding = 20
    btn_y = y + h - btn_h - padding
    quit_btn = pygame.Rect(x + w - btn_w - padding, btn_y, btn_w, btn_h)
    cancel_btn = pygame.Rect(x + padding, btn_y, btn_w, btn_h)
    return quit_btn, cancel_btn

def draw_quit_dialog(surface):
    # dialog rect
    w, h = 400, 180
    x = (SCREEN_WIDTH - w) // 2
    y = (SCREEN_HEIGHT - h) // 2
    dialog_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, (200, 200, 200), dialog_rect)
    pygame.draw.rect(surface, (0, 0, 0), dialog_rect, 2)

    # text
    font = pygame.font.SysFont(None, 28)
    if quit_dialog_mode == 'main_menu':
        text = font.render('Main menu?', True, (0, 0, 0))
        button_label = 'Main Menu'
    else:
        text = font.render('Quit game?', True, (0, 0, 0))
        button_label = 'Quit'
    surface.blit(text, (x + 20, y + 20))

    quit_btn, cancel_btn = get_quit_dialog_buttons()
    pygame.draw.rect(surface, (255, 255, 255), quit_btn)
    pygame.draw.rect(surface, (255, 255, 255), cancel_btn)
    pygame.draw.rect(surface, (0, 0, 0), quit_btn, 2)
    pygame.draw.rect(surface, (0, 0, 0), cancel_btn, 2)

    qtext = font.render(button_label, True, (0, 0, 0))
    ctext = font.render('Cancel', True, (0, 0, 0))
    surface.blit(qtext, (quit_btn.centerx - qtext.get_width() // 2, quit_btn.centery - qtext.get_height() // 2))
    surface.blit(ctext, (cancel_btn.centerx - ctext.get_width() // 2, cancel_btn.centery - ctext.get_height() // 2))

    return quit_btn, cancel_btn

while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_started:
                    show_quit_dialog = True
                    quit_dialog_mode = 'main_menu'
                else:
                    show_quit_dialog = True
                    quit_dialog_mode = 'quit'
            elif event.key == pygame.K_SPACE and on_ground:
                player_vy = jump_strength
                on_ground = False
        elif event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # record click for visual feedback; will set id later depending on which button
            click_ticks = pygame.time.get_ticks()
            # quit dialog buttons
            if show_quit_dialog:
                qd_qbtn, qd_cbtn = get_quit_dialog_buttons()
                if qd_qbtn.collidepoint((mx, my)):
                    if quit_dialog_mode == 'main_menu':
                        game_started = False
                        store_open = False
                        settings_open = False
                    else:
                        running = False
                    show_quit_dialog = False
                elif qd_cbtn.collidepoint((mx, my)):
                    show_quit_dialog = False
            # main menu button clicks (only when not started and dialog not open)
            elif not game_started and not show_quit_dialog:
                sbtn, setbtn, cbtn, stobtn, qbtn = get_main_menu_buttons()
                if sbtn.collidepoint((mx, my)):
                    clicked_button = ('main', 'start')
                    click_time = click_ticks
                    game_started = True
                    enemy_health = 5
                    enemy_alive = True
                    enemy_health = 5
                    enemy_alive = True
                    try:
                        if len(kepron_idle_sprites) > 0:
                            player = pygame.transform.scale(kepron_idle_sprites[0].copy().convert_alpha(), (100, 130))
                        elif len(kepron_walk_sprites) > 0:
                            player = pygame.transform.scale(kepron_walk_sprites[0].copy().convert_alpha(), (100, 130))
                        else:
                            player = kepron
                    except Exception:
                        player = kepron
                elif setbtn.collidepoint((mx, my)):
                    clicked_button = ('main', 'settings')
                    click_time = click_ticks
                    settings_open = True
                    print('Settings pressed')
                elif cbtn.collidepoint((mx, my)):
                    # open controls window
                    clicked_button = ('main', 'controls')
                    click_time = click_ticks
                    controls_open = True
                elif stobtn.collidepoint((mx, my)):
                    # open store: hide main menu and game
                    clicked_button = ('main', 'store')
                    click_time = click_ticks
                    store_open = True
                elif qbtn.collidepoint((mx, my)):
                    clicked_button = ('main', 'quit')
                    click_time = click_ticks
                    show_quit_dialog = True
                    quit_dialog_mode = 'quit'
            elif game_started and not show_quit_dialog:
                if rockRoll:
                    rock_rect = rockRoll.get_rect(topleft=(rockRoll_x, rockRoll_y))
                    if rock_rect.collidepoint((mx, my)):
                        points += 1

    # only allow player movement after game has started
    keys = pygame.key.get_pressed()
    if game_started:
        moved = False
        now = pygame.time.get_ticks()
        if keys[pygame.K_a]:
            player_x -= player_speed
            moved = True
            # animate sprite sheet while moving left
            if len(kepron_walk_sprites) > 0 and now - sprite_animation_timer >= SPRITE_ANIMATION_INTERVAL:
                sprite_animation_timer = now
                sprite_index = (sprite_index + 1) % len(kepron_walk_sprites)
                try:
                    player = pygame.transform.scale(pygame.transform.flip(kepron_walk_sprites[sprite_index].copy(), True, False).convert_alpha(), (100, 130))
                except Exception:
                    if len(kepron_idle_sprites) > 0:
                        player = pygame.transform.scale(kepron_idle_sprites[0].copy().convert_alpha(), (100, 130))
                    else:
                        player = kepron
        if keys[pygame.K_d]:
            player_x += player_speed
            moved = True
            # animate sprite sheet while moving right
            if len(kepron_walk_sprites) > 0 and now - sprite_animation_timer >= SPRITE_ANIMATION_INTERVAL:
                sprite_animation_timer = now
                sprite_index = (sprite_index + 1) % len(kepron_walk_sprites)
                try:
                    player = pygame.transform.scale(kepron_walk_sprites[sprite_index].copy().convert_alpha(), (100, 130))
                except Exception:
                    if len(kepron_idle_sprites) > 0:
                        player = pygame.transform.scale(kepron_idle_sprites[0].copy().convert_alpha(), (100, 130))
                    else:
                        player = kepron

        # when not moving, play idle animation from the sprite sheet
        if not moved:
            if len(kepron_idle_sprites) > 0:
                if now - idle_animation_timer >= IDLE_ANIMATION_INTERVAL:
                    idle_animation_timer = now
                    idle_sprite_index = (idle_sprite_index + 1) % len(kepron_idle_sprites)
                try:
                    player = pygame.transform.scale(kepron_idle_sprites[idle_sprite_index].copy().convert_alpha(), (100, 130))
                except Exception:
                    player = kepron
            elif len(kepron_walk_sprites) > 0:
                try:
                    player = pygame.transform.scale(kepron_walk_sprites[0].copy().convert_alpha(), (100, 130))
                except Exception:
                    player = kepron
            else:
                player = kepron

        player_vy += gravity
        player_y += player_vy
        if player_y >= ground_y - player.get_height():
            player_y = ground_y - player.get_height()
            player_vy = 0
            on_ground = True

    if player_x < 0:
        player_x = 0
    elif player_x > SCREEN_WIDTH - player.get_width():
        player_x = SCREEN_WIDTH - player.get_width()

    if loading_active:
        elapsed = pygame.time.get_ticks() - loading_start_time
        if elapsed >= loading_duration:
            loading_active = False
            try:
                # start background music when loading finishes
                pygame.mixer.music.play(-1)
            except Exception:
                pass
        else:
            # compute fade alpha (255 -> 0)
            loading_alpha = max(0, 255 - int(255 * elapsed / loading_duration))
            # draw background first so loading image fades over it
            screen.blit(background, (0, 0))
            # draw black side panels and loading image with the same fade rate
            loading_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            left_bar_width = loading_rect.left
            right_bar_x = loading_rect.left + loading_rect.width
            if loading_alpha > 0:
                if left_bar_width > 0:
                    loading_surface.fill((0, 0, 0, loading_alpha), (0, 0, left_bar_width, SCREEN_HEIGHT))
                    loading_surface.fill((0, 0, 0, loading_alpha), (right_bar_x, 0, left_bar_width, SCREEN_HEIGHT))
            image_surface = loading_image.copy().convert_alpha()
            image_surface.set_alpha(loading_alpha)
            loading_surface.blit(image_surface, (loading_rect.left, loading_rect.top))
            screen.blit(loading_surface, (0, 0))
            draw_points_hud(screen)
            pygame.display.flip()
            continue

    screen.blit(background, (0, 0))

    # sym:ground1_image - draw ground using loaded image instead of a solid rect
    ground_rect_height = 200
    try:
        ground_scaled = pygame.transform.scale(ground1_image, (SCREEN_WIDTH, ground_rect_height))
        screen.blit(ground_scaled, (0, ground_y))
    except Exception:
        # fallback to solid rect if image scaling/blitting fails
        pygame.draw.rect(screen, (50, 50, 50), (0, ground_y, SCREEN_WIDTH, ground_rect_height))

    screen.blit(player, (player_x, player_y))

    if game_started and len(rockroll_attack_sprites) > 0:
        now = pygame.time.get_ticks()
        if now - rockroll_animation_timer >= ROCKROLL_ANIMATION_INTERVAL:
            rockroll_animation_timer = now
            rockroll_sprite_index = (rockroll_sprite_index + 1) % len(rockroll_attack_sprites)

        try:
            rockRoll = pygame.transform.scale(
                rockroll_attack_sprites[rockroll_sprite_index].copy().convert_alpha(),
                (100, 80)
            )
        except Exception:
            rockRoll = rockroll_attack_sprites[rockroll_sprite_index]

        if rockRoll:
            screen.blit(rockRoll, (rockRoll_x, rockRoll_y))

    # draw main menu buttons only when game not started
    if not game_started:
        start_btn, settings_btn, controls_btn, store_btn, quit_btn = get_main_menu_buttons()
        title_font = pygame.font.SysFont(None, 48)
        title_text = custom_font.render('Kepron Kafitza', True, (255, 0, 0))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, start_btn.top - 70))
        pygame.draw.rect(screen, (255, 255, 255), start_btn)
        pygame.draw.rect(screen, (0, 0, 0), start_btn, 2)
        pygame.draw.rect(screen, (255, 255, 255), settings_btn)
        pygame.draw.rect(screen, (0, 0, 0), settings_btn, 2)
        pygame.draw.rect(screen, (255, 255, 255), controls_btn)
        pygame.draw.rect(screen, (0, 0, 0), controls_btn, 2)
        pygame.draw.rect(screen, (255, 255, 255), store_btn)
        pygame.draw.rect(screen, (0, 0, 0), store_btn, 2)
        pygame.draw.rect(screen, (255, 255, 255), quit_btn)
        pygame.draw.rect(screen, (0, 0, 0), quit_btn, 2)
        font = pygame.font.SysFont(None, 24)
        screen.blit(font.render('Start', True, (0,0,0)), (start_btn.centerx - 24, start_btn.centery - 10))
        screen.blit(font.render('Settings', True, (0,0,0)), (settings_btn.centerx - 36, settings_btn.centery - 10))
        screen.blit(font.render('Controls', True, (0,0,0)), (controls_btn.centerx - 36, controls_btn.centery - 10))
        screen.blit(font.render('Store', True, (0,0,0)), (store_btn.centerx - 24, store_btn.centery - 10))
        screen.blit(font.render('Quit', True, (0,0,0)), (quit_btn.centerx - 20, quit_btn.centery - 10))

    if show_quit_dialog:
        draw_quit_dialog(screen)

    draw_points_hud(screen)
    pygame.display.flip()

    # draw store window on top when open
    if store_open:
        # simple store surface
        store_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        store_surf.fill((255, 255, 255))
        sf_font = pygame.font.SysFont(None, 40)
        sf_text = sf_font.render('Store', True, (0,0,0))
        store_surf.blit(sf_text, (SCREEN_WIDTH//2 - sf_text.get_width()//2, 40))
        # back button (visible on white background)
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(store_surf, (200, 200, 200), back_btn)  # light gray fill
        pygame.draw.rect(store_surf, (0, 0, 0), back_btn, 2)
        bf = pygame.font.SysFont(None, 24)
        back_text = bf.render('Back', True, (0, 0, 0))
        store_surf.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - back_text.get_height() // 2))
        
        # 3 store buttons in lower half, centered
        btn_w, btn_h = 120, 40
        btn_spacing = 20
        total_btn_width = 3 * btn_w + 2 * btn_spacing
        start_x = (SCREEN_WIDTH - total_btn_width) // 2
        btn_y = SCREEN_HEIGHT - 150
        
        store_btn1 = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        store_btn2 = pygame.Rect(start_x + btn_w + btn_spacing, btn_y, btn_w, btn_h)
        store_btn3 = pygame.Rect(start_x + 2 * (btn_w + btn_spacing), btn_y, btn_w, btn_h)
        item2_enabled = points > 1
        store_btn_colors = [
            (160, 255, 160) if selected_character == 'kepron' else (200, 200, 200),
            (160, 255, 160) if selected_character == 'lebron' else ((200, 200, 200) if item2_enabled else (120, 120, 120)),
            (200, 200, 200)
        ]
        for btn, color in zip([store_btn1, store_btn2, store_btn3], store_btn_colors):
            pygame.draw.rect(store_surf, color, btn)
            pygame.draw.rect(store_surf, (0, 0, 0), btn, 2)
        
        # display item image above item 1 button
        item_image = pygame.image.load(r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\baldwinTemporary.png").convert_alpha()
        item_image_scaled = pygame.transform.scale(item_image, (80, 80))
        store_surf.blit(item_image_scaled, (store_btn1.centerx - 40, store_btn1.top - 100))
        # display lebron image above item 2 button
        lebron_image_store = pygame.transform.scale(lebron, (80, 80))
        store_surf.blit(lebron_image_store, (store_btn2.centerx - 40, store_btn2.top - 100))
        
        store_surf.blit(bf.render('Item 1', True, (0, 0, 0)), (store_btn1.centerx - 32, store_btn1.centery - 10))
        store_surf.blit(bf.render('Item 2' if item2_enabled else 'Locked', True, (0, 0, 0)), (store_btn2.centerx - 32, store_btn2.centery - 10))
        store_surf.blit(bf.render('Item 3', True, (0, 0, 0)), (store_btn3.centerx - 32, store_btn3.centery - 10))

        # blit store surface and draw quit dialog if active
        screen.blit(store_surf, (0,0))
        if show_quit_dialog:
            draw_quit_dialog(screen)
        draw_points_hud(screen)
        pygame.display.flip()
        # handle simple event loop for store until closed
        in_store = True
        while in_store:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                    in_store = False
                    store_open = False
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if show_quit_dialog:
                        qd_qbtn, qd_cbtn = get_quit_dialog_buttons()
                        if qd_qbtn.collidepoint(ev.pos):
                            running = False
                            in_store = False
                            store_open = False
                            show_quit_dialog = False
                        elif qd_cbtn.collidepoint(ev.pos):
                            show_quit_dialog = False
                    elif back_btn.collidepoint(ev.pos):
                        clicked_button = ('store', 'back')
                        click_time = pygame.time.get_ticks()
                        store_open = False
                        in_store = False
                    # store item clicks
                    elif store_btn1.collidepoint(ev.pos):
                        clicked_button = ('store', 'item1')
                        click_time = pygame.time.get_ticks()
                        player = kepron
                        selected_character = 'kepron'
                    elif store_btn2.collidepoint(ev.pos) and item2_enabled:
                        clicked_button = ('store', 'item2')
                        click_time = pygame.time.get_ticks()
                        player = lebron
                        selected_character = 'lebron'
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        if show_quit_dialog:
                            show_quit_dialog = False
                        else:
                            store_open = False
                            in_store = False
            screen.blit(store_surf, (0,0))
            if show_quit_dialog:
                draw_quit_dialog(screen)
            pygame.display.flip()
            # small delay to avoid maxing CPU
            pygame.time.delay(10)

    if settings_open:
        settings_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        settings_surf.fill((240, 240, 240))
        sf_font = pygame.font.SysFont(None, 40)
        sf_text = sf_font.render('Settings', True, (0, 0, 0))
        settings_surf.blit(sf_text, (SCREEN_WIDTH//2 - sf_text.get_width()//2, 40))

        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(settings_surf, (200, 200, 200), back_btn)
        pygame.draw.rect(settings_surf, (0, 0, 0), back_btn, 2)
        bf = pygame.font.SysFont(None, 24)
        back_text = bf.render('Back', True, (0, 0, 0))
        settings_surf.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - back_text.get_height() // 2))

        volume_bar_rect = pygame.Rect(150, 220, SCREEN_WIDTH - 300, 12)

        def draw_settings_screen():
            settings_surf.fill((240, 240, 240))
            settings_surf.blit(sf_text, (SCREEN_WIDTH//2 - sf_text.get_width()//2, 40))
            pygame.draw.rect(settings_surf, (200, 200, 200), back_btn)
            pygame.draw.rect(settings_surf, (0, 0, 0), back_btn, 2)
            settings_surf.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - back_text.get_height() // 2))
            volume_label = bf.render(f'Volume: {int(volume * 100)}%', True, (0, 0, 0))
            settings_surf.blit(volume_label, (SCREEN_WIDTH//2 - volume_label.get_width()//2, 140))
            pygame.draw.rect(settings_surf, (200, 200, 200), volume_bar_rect)
            handle_x = volume_bar_rect.left + int(volume * volume_bar_rect.width)
            handle_rect = pygame.Rect(handle_x - 10, volume_bar_rect.centery - 12, 20, 24)
            pygame.draw.rect(settings_surf, (100, 100, 100), handle_rect)
            pygame.draw.rect(settings_surf, (0, 0, 0), handle_rect, 2)
            screen.blit(settings_surf, (0, 0))
            if show_quit_dialog:
                draw_quit_dialog(screen)
            draw_points_hud(screen)
            pygame.display.flip()

        draw_settings_screen()

        in_settings = True
        while in_settings:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                    in_settings = False
                    settings_open = False
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if show_quit_dialog:
                        qd_qbtn, qd_cbtn = get_quit_dialog_buttons()
                        if qd_qbtn.collidepoint(ev.pos):
                            running = False
                            in_settings = False
                            settings_open = False
                            show_quit_dialog = False
                        elif qd_cbtn.collidepoint(ev.pos):
                            show_quit_dialog = False
                    elif back_btn.collidepoint(ev.pos):
                        clicked_button = ('settings', 'back')
                        click_time = pygame.time.get_ticks()
                        settings_open = False
                        in_settings = False
                    elif volume_bar_rect.collidepoint(ev.pos):
                        volume = max(0.0, min(1.0, (ev.pos[0] - volume_bar_rect.left) / volume_bar_rect.width))
                        pygame.mixer.music.set_volume(volume)
                        volume_slider_active = True
                elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                    volume_slider_active = False
                elif ev.type == pygame.MOUSEMOTION and volume_slider_active and ev.buttons[0]:
                    volume = max(0.0, min(1.0, (ev.pos[0] - volume_bar_rect.left) / volume_bar_rect.width))
                    pygame.mixer.music.set_volume(volume)
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        if show_quit_dialog:
                            show_quit_dialog = False
                        else:
                            settings_open = False
                            in_settings = False
            draw_settings_screen()
            pygame.time.delay(10)

    if controls_open:
        controls_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        controls_surf.fill((240, 240, 240))
        sf_font = pygame.font.SysFont(None, 40)
        sf_text = sf_font.render('Controls', True, (0, 0, 0))
        controls_surf.blit(sf_text, (SCREEN_WIDTH//2 - sf_text.get_width()//2, 40))

        # controls description text
        bf = pygame.font.SysFont(None, 24)
        lines = [
            'A / D : Move left / right',
            'Space : Jump',
            'Esc : Quit / Back'
        ]
        start_y = 120
        for i, line in enumerate(lines):
            txt = bf.render(line, True, (0,0,0))
            controls_surf.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, start_y + i*30))

        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(controls_surf, (200, 200, 200), back_btn)
        pygame.draw.rect(controls_surf, (0, 0, 0), back_btn, 2)
        back_text = bf.render('Back', True, (0, 0, 0))
        controls_surf.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - back_text.get_height() // 2))

        screen.blit(controls_surf, (0,0))
        if show_quit_dialog:
            draw_quit_dialog(screen)
        draw_points_hud(screen)
        pygame.display.flip()

        in_controls = True
        while in_controls:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                    in_controls = False
                    controls_open = False
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if show_quit_dialog:
                        qd_qbtn, qd_cbtn = get_quit_dialog_buttons()
                        if qd_qbtn.collidepoint(ev.pos):
                            running = False
                            in_controls = False
                            controls_open = False
                            show_quit_dialog = False
                        elif qd_cbtn.collidepoint(ev.pos):
                            show_quit_dialog = False
                    elif back_btn.collidepoint(ev.pos):
                        clicked_button = ('controls', 'back')
                        click_time = pygame.time.get_ticks()
                        controls_open = False
                        in_controls = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        if show_quit_dialog:
                            show_quit_dialog = False
                        else:
                            controls_open = False
                            in_controls = False
            screen.blit(controls_surf, (0,0))
            if show_quit_dialog:
                draw_quit_dialog(screen)
            draw_points_hud(screen)
            pygame.display.flip()
            pygame.time.delay(10)

pygame.quit()