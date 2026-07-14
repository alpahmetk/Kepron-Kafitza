import pygame

pygame.init()

# -------------------------
# GAME RESOLUTION
# -------------------------

GAME_WIDTH = 800
GAME_HEIGHT = 600

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    pygame.FULLSCREEN
)

# Internal game surface
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))


# -------------------------
# PLAYER
# -------------------------

player_image = pygame.image.load(
    r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\baldwinTemporary.png"
).convert_alpha()

player = pygame.transform.scale(player_image, (100, 100))


ground_y = 500

player_x = 100
player_y = ground_y - player.get_height()

player_speed = 0.5
player_vy = 0

gravity = 0.00225
jump_strength = -1

on_ground = True


# -------------------------
# GAME STATES
# -------------------------

running = True

show_quit_dialog = False
game_started = False
store_open = False


# -------------------------
# STORE IMAGE
# -------------------------

item_image = pygame.image.load(
    r"C:\Users\Pc\Documents\Columbia\Kepron_Kafitza\assets\baldwinTemporary.png"
).convert_alpha()

item_image_scaled = pygame.transform.scale(
    item_image,
    (80, 80)
)


# -------------------------
# MENU BUTTONS
# -------------------------

BTN_W = 240
BTN_H = 40
BTN_PADDING = 10


def get_main_menu_buttons():

    x = (GAME_WIDTH - BTN_W) // 2

    total_height = (
        4 * BTN_H +
        3 * BTN_PADDING
    )
    y = (GAME_HEIGHT - total_height) // 2
    start_btn = pygame.Rect(
        x,
        y,
        BTN_W,
        BTN_H
    )
    settings_btn = pygame.Rect(
        x,
        y + BTN_H + BTN_PADDING,
        BTN_W,
        BTN_H
    )
    store_btn = pygame.Rect(
        x,
        y + 2*(BTN_H + BTN_PADDING),
        BTN_W,
        BTN_H
    )
    quit_btn = pygame.Rect(
        x,
        y + 3*(BTN_H + BTN_PADDING),
        BTN_W,
        BTN_H
    )

    return (
        start_btn,
        settings_btn,
        store_btn,
        quit_btn
    )

def get_quit_dialog_buttons():
    w = 400
    h = 180

    x = (GAME_WIDTH - w)//2
    y = (GAME_HEIGHT - h)//2

    btn_w = 120
    btn_h = 40
    padding = 20
    btn_y = y + h - btn_h - padding
    quit_btn = pygame.Rect(
        x+w-btn_w-padding,
        btn_y,
        btn_w,
        btn_h
    )
    cancel_btn = pygame.Rect(
        x+padding,
        btn_y,
        btn_w,
        btn_h
    )

    return quit_btn, cancel_btn

# -------------------------
# DRAW QUIT DIALOG
# -------------------------

def draw_quit_dialog(surface):

    w = 400
    h = 180

    x = (GAME_WIDTH - w)//2
    y = (GAME_HEIGHT - h)//2


    dialog_rect = pygame.Rect(
        x,
        y,
        w,
        h
    )


    pygame.draw.rect(
        surface,
        (200,200,200),
        dialog_rect
    )

    pygame.draw.rect(
        surface,
        (0,0,0),
        dialog_rect,
        2
    )


    font = pygame.font.SysFont(None,28)


    text = font.render(
        "Quit game?",
        True,
        (0,0,0)
    )

    surface.blit(
        text,
        (x+20,y+20)
    )


    quit_btn, cancel_btn = get_quit_dialog_buttons()


    for btn in [quit_btn,cancel_btn]:

        pygame.draw.rect(
            surface,
            (255,255,255),
            btn
        )

        pygame.draw.rect(
            surface,
            (0,0,0),
            btn,
            2
        )


    qtext = font.render(
        "Quit",
        True,
        (0,0,0)
    )

    ctext = font.render(
        "Cancel",
        True,
        (0,0,0)
    )


    surface.blit(
        qtext,
        (
            quit_btn.centerx - qtext.get_width()//2,
            quit_btn.centery - qtext.get_height()//2
        )
    )


    surface.blit(
        ctext,
        (
            cancel_btn.centerx - ctext.get_width()//2,
            cancel_btn.centery - ctext.get_height()//2
        )
    )


    return quit_btn,cancel_btn



# -------------------------
# MAIN LOOP
# -------------------------

while running:


    # calculate scaling
    scale = min(
        SCREEN_WIDTH / GAME_WIDTH,
        SCREEN_HEIGHT / GAME_HEIGHT
    )


    for event in pygame.event.get():


        if event.type == pygame.QUIT:

            running = False



        elif event.type == pygame.KEYDOWN:


            if event.key == pygame.K_ESCAPE:

                show_quit_dialog = True



            elif event.key == pygame.K_SPACE and on_ground:

                player_vy = jump_strength
                on_ground = False



        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:


            # convert mouse to game coordinates

            mx,my = event.pos

            mx = int(mx / scale)
            my = int(my / scale)



            # menu buttons

            sbtn,setbtn,stobtn,qbtn = get_main_menu_buttons()



            if sbtn.collidepoint(mx,my):

                game_started = True



            elif setbtn.collidepoint(mx,my):

                print("Settings pressed")



            elif stobtn.collidepoint(mx,my):

                store_open = True



            elif qbtn.collidepoint(mx,my):

                show_quit_dialog = True



            # quit dialog

            if show_quit_dialog:


                qd_qbtn,qd_cbtn = get_quit_dialog_buttons()


                if qd_qbtn.collidepoint(mx,my):

                    running = False



                elif qd_cbtn.collidepoint(mx,my):

                    show_quit_dialog = False



    # -------------------------
    # PLAYER MOVEMENT
    # -------------------------


    keys = pygame.key.get_pressed()


    if game_started:


        if keys[pygame.K_a]:

            player_x -= player_speed



        if keys[pygame.K_d]:

            player_x += player_speed



        player_vy += gravity

        player_y += player_vy



        if player_y >= ground_y-player.get_height():

            player_y = ground_y-player.get_height()

            player_vy = 0

            on_ground = True



    # keep player inside game area

    if player_x < 0:

        player_x = 0


    elif player_x > GAME_WIDTH-player.get_width():

        player_x = GAME_WIDTH-player.get_width()

    # -------------------------
    # DRAW GAME
    # -------------------------

    game_surface.fill((255,255,255))


    # ground

    pygame.draw.rect(
        game_surface,
        (150,150,150),
        (
            0,
            ground_y,
            GAME_WIDTH,
            GAME_HEIGHT-ground_y
        )
    )


    # player

    game_surface.blit(
        player,
        (player_x,player_y)
    )


    # quit dialog

    if show_quit_dialog:

        draw_quit_dialog(game_surface)



    # -------------------------
    # MAIN MENU
    # -------------------------

    if not game_started:


        start_btn,settings_btn,store_btn,quit_btn = get_main_menu_buttons()


        title_font = pygame.font.SysFont(
            None,
            48
        )


        title_text = title_font.render(
            "Kepron Kafitza",
            True,
            (0,0,0)
        )


        game_surface.blit(
            title_text,
            (
                GAME_WIDTH//2 - title_text.get_width()//2,
                start_btn.top - 70
            )
        )


        buttons = [
            start_btn,
            settings_btn,
            store_btn,
            quit_btn
        ]


        for button in buttons:

            pygame.draw.rect(
                game_surface,
                (255,255,255),
                button
            )

            pygame.draw.rect(
                game_surface,
                (0,0,0),
                button,
                2
            )


        font = pygame.font.SysFont(
            None,
            24
        )


        texts = [
            ("Start",start_btn),
            ("Settings",settings_btn),
            ("Store",store_btn),
            ("Quit",quit_btn)
        ]


        for text,button in texts:

            rendered = font.render(
                text,
                True,
                (0,0,0)
            )


            game_surface.blit(
                rendered,
                (
                    button.centerx-rendered.get_width()//2,
                    button.centery-rendered.get_height()//2
                )
            )



    # -------------------------
    # STORE
    # -------------------------

    if store_open:


        store_surf = pygame.Surface(
            (GAME_WIDTH,GAME_HEIGHT)
        )


        store_surf.fill(
            (255,255,255)
        )


        sf_font = pygame.font.SysFont(
            None,
            40
        )


        sf_text = sf_font.render(
            "Store",
            True,
            (0,0,0)
        )


        store_surf.blit(
            sf_text,
            (
                GAME_WIDTH//2-sf_text.get_width()//2,
                40
            )
        )


        back_btn = pygame.Rect(
            20,
            20,
            100,
            40
        )


        pygame.draw.rect(
            store_surf,
            (200,200,200),
            back_btn
        )


        pygame.draw.rect(
            store_surf,
            (0,0,0),
            back_btn,
            2
        )


        bf = pygame.font.SysFont(
            None,
            24
        )


        back_text = bf.render(
            "Back",
            True,
            (0,0,0)
        )


        store_surf.blit(
            back_text,
            (
                back_btn.centerx-back_text.get_width()//2,
                back_btn.centery-back_text.get_height()//2
            )
        )


        # item buttons

        btn_w = 120
        btn_h = 40

        spacing = 20


        total_width = (
            3*btn_w +
            2*spacing
        )


        start_x = (
            GAME_WIDTH-total_width
        )//2


        btn_y = GAME_HEIGHT-150


        store_btn1 = pygame.Rect(
            start_x,
            btn_y,
            btn_w,
            btn_h
        )


        store_btn2 = pygame.Rect(
            start_x+btn_w+spacing,
            btn_y,
            btn_w,
            btn_h
        )


        store_btn3 = pygame.Rect(
            start_x+2*(btn_w+spacing),
            btn_y,
            btn_w,
            btn_h
        )


        for btn in [
            store_btn1,
            store_btn2,
            store_btn3
        ]:

            pygame.draw.rect(
                store_surf,
                (200,200,200),
                btn
            )

            pygame.draw.rect(
                store_surf,
                (0,0,0),
                btn,
                2
            )



        # item image

        store_surf.blit(
            item_image_scaled,
            (
                store_btn1.centerx-40,
                store_btn1.top-100
            )
        )


        labels = [
            ("Item 1",store_btn1),
            ("Item 2",store_btn2),
            ("Item 3",store_btn3)
        ]


        for label,button in labels:

            text = bf.render(
                label,
                True,
                (0,0,0)
            )


            store_surf.blit(
                text,
                (
                    button.centerx-text.get_width()//2,
                    button.centery-text.get_height()//2
                )
            )


        game_surface.blit(
            store_surf,
            (0,0)
        )



    # -------------------------
    # SCALE TO MONITOR
    # -------------------------

    scale = min(
        SCREEN_WIDTH/GAME_WIDTH,
        SCREEN_HEIGHT/GAME_HEIGHT
    )


    new_width = int(
        GAME_WIDTH*scale
    )

    new_height = int(
        GAME_HEIGHT*scale
    )


    scaled_surface = pygame.transform.scale(
        game_surface,
        (
            new_width,
            new_height
        )
    )


    screen.fill(
        (0,0,0)
    )


    screen.blit(
        scaled_surface,
        (
            (SCREEN_WIDTH-new_width)//2,
            (SCREEN_HEIGHT-new_height)//2
        )
    )


    pygame.display.flip()



pygame.quit()