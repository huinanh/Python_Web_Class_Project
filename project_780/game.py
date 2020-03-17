# Developed from the example code in Making Games with Python & Pygame
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# features added:
# Starting Interface
# ScoreBoard
# Pause Game
# Red Elixir and Growth Elixir
# Using mana to become invulnerable temporarily

import random, sys, time, math, pygame
import requests
import pygame.locals

FPS = 30 # frames per second to update the screen
WINWIDTH = 640 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

GRASSCOLOR = (34, 255, 100)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LIGHT_RED = (200, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (0, 0, 200)


CAMERASLACK = 90     # how far from the center the squirrel moves before moving the camera
MOVERATE = 9         # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 30    # how high the player bounces
STARTSIZE = 35       # how big the player starts off
WINSIZE = 200        # how big the player needs to be to win
INVULNTIME = 2       # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3        # how much health the player starts with
MAXMANA = 3          # how much mana the player starts with

NUMGRASS = 80        # number of grass objects in the active area
NUMSQUIRRELS = 30    # number of squirrels in the active area
NUMITEMS = 4         # number of items in the active area
SQUIRRELMINSPEED = 3 # slowest squirrel speed
SQUIRRELMAXSPEED = 7 # fastest squirrel speed
DIRCHANGEFREQ = 2    # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'
PAUSE = False
INTRO = True
USR_NAME = "Anonymous"
HAS_SENT = False


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES, RED_IMG, GROW_IMG

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('kumiko.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Squirrel Eat Squirrel')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)



    # load the image files
    R_SQUIR_IMG = pygame.image.load('sq.png')
    L_SQUIR_IMG = pygame.transform.flip(R_SQUIR_IMG, True, False)
    RED_IMG = pygame.image.load('red.png')
    GROW_IMG = pygame.image.load('growth.png')
    GRASSIMAGES = []


    for i in range(1, 4):
        GRASSIMAGES.append(pygame.image.load('flower%s.png' % i))
    if INTRO:
        intro()
    while True:
        runGame()


def runGame():
    global PAUSE, HAS_SENT
    HAS_SENT = False
    # set up variables for the start of a new game
    invulnerableMode = False  # if the player is invulnerable
    invulnerableStartTime = 0 # time the player became invulnerable
    gameOverMode = False      # if the player has lost
    gameOverStartTime = 0     # time the player lost
    winMode = False           # if the player has won


    # record the start time
    gameStartTime = time.time()
    # create the surfaces to hold game text
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('You have achieved OMEGA SQUIRREL!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # camerax and cameray are the top left of where the camera view is
    camerax = 0
    cameray = 0

    grassObjs = []    # stores all the grass objects in the game
    squirrelObjs = [] # stores all the non-player squirrel objects
    redObjs = []
    growObjs = []
    # stores the player object:
    playerObj = {'surface': pygame.transform.scale(L_SQUIR_IMG, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0,
                 'health': MAXHEALTH,
                 'mana': MAXMANA}

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False

    # start off with some random grass images on the screen
    for i in range(10):
        grassObjs.append(makeNewGrass(camerax, cameray))
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True: # main game loop
        # Check if we should turn off invulnerability
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        # move all the squirrels
        for sObj in squirrelObjs:
            # move the squirrel, and adjust for their bounce
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0 # reset bounce amount

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()
                sObj['movey'] = getRandomVelocity()
                if sObj['movex'] > 0: # faces right
                    sObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sObj['width'], sObj['height']))
                else: # faces left
                    sObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sObj['width'], sObj['height']))


        # go through all the objects and see if any need to be deleted.
        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(squirrelObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, squirrelObjs[i]):
                del squirrelObjs[i]
        for i in range(len(redObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, redObjs[i]):
                del redObjs[i]
        for i in range(len(growObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, growObjs[i]):
                del growObjs[i]

        # add more grass & squirrels if we don't have enough.
        while len(grassObjs) < NUMGRASS:
            grassObjs.append(makeNewGrass(camerax, cameray))
        while len(squirrelObjs) < NUMSQUIRRELS:
            squirrelObjs.append(makeNewSquirrel(camerax, cameray))
        while len(redObjs) + len(growObjs) < NUMITEMS:
            index = random.randint(1,3)
            if index == 1:
                redObjs.append(makeNewRed(camerax, cameray))
            if index == 2:
                growObjs.append(makeNewGrow(camerax,cameray))

        # adjust camerax and cameray if beyond the "camera slack"
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # draw the green background
        DISPLAYSURF.fill(GRASSCOLOR)

        # draw all the grass objects on the screen
        for gObj in grassObjs:
            gRect = pygame.Rect( (gObj['x'] - camerax,
                                  gObj['y'] - cameray,
                                  gObj['width'],
                                  gObj['height']) )
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)

        # draw all the red objects on the screen
        for rObj in redObjs:
            rObj['rect'] = pygame.Rect((rObj['x'] - camerax,
                                        rObj['y'] - cameray,
                                        rObj['width'],
                                        rObj['height']))
            DISPLAYSURF.blit(rObj['surface'], rObj['rect'])

        for gObj in growObjs:
            gObj['rect'] = pygame.Rect((gObj['x'] - camerax,
                                        gObj['y'] - cameray,
                                        gObj['width'],
                                        gObj['height']))
            DISPLAYSURF.blit(gObj['surface'], gObj['rect'])
        # draw the other squirrels
        for sObj in squirrelObjs:
            sObj['rect'] = pygame.Rect( (sObj['x'] - camerax,
                                         sObj['y'] - cameray - getBounceAmount(sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']),
                                         sObj['width'],
                                         sObj['height']) )
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])


        # draw the player squirrel
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray - getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])


        # draw the health meter
        drawHealthMeter(playerObj['health'])
        drawManaMeter(playerObj['mana'])

        for event in pygame.event.get(): # event handling loop
            if event.type == pygame.locals.QUIT:
                terminate()

            elif event.type == pygame.locals.KEYDOWN:
                if event.key in (pygame.locals.K_UP, pygame.locals.K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (pygame.locals.K_DOWN, pygame.locals.K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (pygame.locals.K_LEFT, pygame.locals.K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != LEFT: # change player image
                        playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = LEFT
                elif event.key in (pygame.locals.K_RIGHT, pygame.locals.K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != RIGHT: # change player image
                        playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                elif event.key == pygame.locals.K_p:
                    PAUSE = True
                    pause()
                elif event.key == pygame.locals.K_SPACE and not invulnerableMode:
                    if playerObj['mana'] > 0:
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['mana'] -= 1

                elif winMode and event.key == pygame.locals.K_r:
                    return

            elif event.type == pygame.locals.KEYUP:
                # stop moving the player's squirrel
                if event.key in (pygame.locals.K_LEFT, pygame.locals.K_a):
                    moveLeft = False
                elif event.key in (pygame.locals.K_RIGHT, pygame.locals.K_d):
                    moveRight = False
                elif event.key in (pygame.locals.K_UP, pygame.locals.K_w):
                    moveUp = False
                elif event.key in (pygame.locals.K_DOWN, pygame.locals.K_s):
                    moveDown = False

                elif event.key == pygame.locals.K_ESCAPE:
                    terminate()

        if not gameOverMode:
            # actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE
            if moveRight:
                playerObj['x'] += MOVERATE
            if moveUp:
                playerObj['y'] -= MOVERATE
            if moveDown:
                playerObj['y'] += MOVERATE

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0 # reset bounce amount

            # check if the player has collided with any squirrels
            for i in range(len(squirrelObjs)-1, -1, -1):
                sqObj = squirrelObjs[i]
                if 'rect' in sqObj and playerObj['rect'].colliderect(sqObj['rect']):
                    # a player/squirrel collision has occurred

                    if sqObj['width'] * sqObj['height'] <= playerObj['size']**2:
                        # player is larger and eats the squirrel
                        playerObj['size'] += int( (sqObj['width'] * sqObj['height'])**0.2 ) + 1
                        del squirrelObjs[i]

                        if playerObj['facing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (playerObj['size'], playerObj['size']))

                        if playerObj['size'] > WINSIZE:
                            winMode = True # turn on "win mode"

                    elif not invulnerableMode:
                        # player is smaller and takes damage
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode = True # turn on "game over mode"
                            gameOverStartTime = time.time()

            # check if the player has collided with any items
            for i in range(len(redObjs) - 1, -1, -1):
                rObj = redObjs[i]
                if 'rect' in rObj and playerObj['rect'].colliderect(rObj['rect']):
                    if playerObj['health'] < MAXHEALTH:
                        playerObj['health'] += 1
                        del redObjs[i]

            for i in range(len(growObjs) - 1, -1, -1):
                gObj = growObjs[i]
                if 'rect' in gObj and playerObj['rect'].colliderect(gObj['rect']):
                    if math.sqrt(playerObj['size']) > 10:
                        playerObj['size'] += 10
                    else:
                        playerObj['size'] += int(math.sqrt(playerObj['size']))

                    if playerObj['facing'] == LEFT:
                        playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG,
                                                                      (playerObj['size'], playerObj['size']))
                    if playerObj['facing'] == RIGHT:
                        playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG,
                                                                      (playerObj['size'], playerObj['size']))
                    del growObjs[i]

        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return # end the current game

        # check if the player has won.
        if winMode:
            if not HAS_SENT:
                HAS_SENT = True
                elapse = round(time.time() - gameStartTime)
                URL = "http://127.0.0.1:8000/addRecord"
                data = {'UserID': USR_NAME,
                        'Time': elapse
                }
                try:
                    requests.get(url=URL, params=data)
                except:
                    print("No Connection!")
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)




def drawHealthMeter(currentHealth):
    for i in range(currentHealth): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)

def drawManaMeter(currentMana):
    for i in range(currentMana): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, BLUE,   (45, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXMANA): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (45, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # Returns the number of pixels to offset based on the bounce.
    # Larger bounceRate means a slower bounce.
    # Larger bounceHeight means a higher bounce.
    # currentBounce will always be less than bounceRate
    return int(math.sin( (math.pi / float(bounceRate)) * currentBounce ) * bounceHeight)

def getRandomVelocity():
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # create a Rect object with the random coordinates and use colliderect()
        # to make sure the right edge isn't in the camera view.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewSquirrel(camerax, cameray):
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width']  = (generalSize + random.randint(0, 10)) * multiplier
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = getRandomOffCameraPos(camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = getRandomVelocity()
    sq['movey'] = getRandomVelocity()
    if sq['movex'] < 0: # squirrel is facing left
        sq['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sq['width'], sq['height']))
    else: # squirrel is facing right
        sq['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq


def makeNewGrass(camerax, cameray):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width']  = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr

def makeNewRed(camerax, cameray):
    red = {}
    red['width'] = int(RED_IMG.get_width()/3)
    red['height'] = int(RED_IMG.get_height()/3)
    red['x'], red['y'] = getRandomOffCameraPos(camerax, cameray, red['width'], red['height'])
    red['rect'] = pygame.Rect((red['x'], red['y'], red['width'], red['height']))
    red['surface'] = pygame.transform.scale(RED_IMG, (red['width'], red['height']))
    return red

def makeNewGrow(camerax, cameray):
    grow = {}
    grow['width'] = int(RED_IMG.get_width()/3)
    grow['height'] = int(RED_IMG.get_height()/3)
    grow['x'], grow['y'] = getRandomOffCameraPos(camerax, cameray, grow['width'], grow['height'])
    grow['rect'] = pygame.Rect((grow['x'], grow['y'], grow['width'], grow['height']))
    grow['surface'] = pygame.transform.scale(GROW_IMG, (grow['width'], grow['height']))
    return grow

def isOutsideActiveArea(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)

def intro():
    # developed from pygame tutorials
    # on https://pythonprogramming.net/pygame-button-function-events/?completed=/pygame-button-function/
    global INTRO, USR_NAME
    name = ""  # user name
    # define dimensions and positions of buttons
    width = 100
    height = 50
    x1 = HALF_WINWIDTH - 200
    x2 = HALF_WINWIDTH + 200 - width
    y = 350
    # wait users to make a decision
    while INTRO:
        DISPLAYSURF.fill(GRASSCOLOR)
        pauseSurf = BASICFONT.render('Squirrel Eat Squirrel', True, WHITE)
        pauseRect = pauseSurf.get_rect()
        pauseRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT - 75)
        DISPLAYSURF.blit(pauseSurf, pauseRect)

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        # react if mouse hover on buttons
        if x1 < mouse[0] < x1 + width and y < mouse[1] < y + height:
            pygame.draw.rect(DISPLAYSURF, LIGHT_BLUE, (x1, y, width, height))
            if click[0] == 1:
                INTRO = False
        else:
            pygame.draw.rect(DISPLAYSURF, BLUE, (x1, y, width, height))

        if x2 < mouse[0] < x2 + width and y < mouse[1] < y + height:
            pygame.draw.rect(DISPLAYSURF, LIGHT_RED, (x2, y, width, height))
            if click[0] == 1:
                quit()
        else:
            pygame.draw.rect(DISPLAYSURF, RED, (x2, y, width, height))

        # display text on buttons
        playSurf = BASICFONT.render('Play', True, BLACK)
        playRect = playSurf.get_rect()
        playRect.center = (int(x1 + width/2), int(y + height/2))
        DISPLAYSURF.blit(playSurf, playRect)

        quitSurf = BASICFONT.render('Quit', True, BLACK)
        quitRect = quitSurf.get_rect()
        quitRect.center = (int(x2 + width/2), int(y + height/2))
        DISPLAYSURF.blit(quitSurf, quitRect)

        # get user name
        # developed from Devourant's post
        # on https://stackoverflow.com/questions/14111381/how-to-get-text-input-from-user-in-pygame
        for event in pygame.event.get():
            if event.type == pygame.locals.KEYDOWN:
                if event.unicode.isalpha():
                    name += event.unicode
                elif event.key == pygame.locals.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.locals.K_RETURN:
                    name = ""
        NAMEFONT = pygame.font.Font('freesansbold.ttf', 20)
        nameSurf = NAMEFONT.render('Player: ' + name, True, WHITE)
        nameRect = nameSurf.get_rect()
        nameRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT - 25)
        DISPLAYSURF.blit(nameSurf, nameRect)
        pygame.display.update()
        FPSCLOCK.tick(10)

    if name != "":
        USR_NAME = name
    return


def pause():
    global PAUSE
    pauseSurf = BASICFONT.render('Paused, press o to resume', True, WHITE)
    pauseRect = pauseSurf.get_rect()
    pauseRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
    DISPLAYSURF.blit(pauseSurf, pauseRect)

    while PAUSE:
        for event in pygame.event.get():
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_o:
                    PAUSE = False
                    break
            pygame.display.update()
            FPSCLOCK.tick(FPS)
    return


if __name__ == '__main__':
    main()