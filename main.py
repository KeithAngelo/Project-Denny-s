import pygame
from sys import exit

###  SETUP
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_CAPTION = "Game"

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_CAPTION)

clock = pygame.time.Clock()
CLOCK_TICK = 60

###  End of SETUP

### CLASS SETUP
def log(text): # created a function for logging to make it easy to turn off
    print(text)

class EventHandler:
    def __init__(self):
        self.eventActions = set() # event action functions, must have 'event' as arguement
    
    def handleEvents(self, event): # for the event loop
        for action in self.eventActions:
            action(event)

    def addEventAction(self, action):
        self.eventActions.add(action)

    def removeEventAction(self, action):
        if action in self.eventActions:
            self.eventActions.remove(action)
    
class animation:
    def __init__(self, folderpath, frameRate, totalFrames, fileType, fileNameLeading, numLeadingZeroes, scale):
        self.frames = []

        self.Looping = True
        self.playTimes = 0 # how many times to play
        self.invisibleWhenInactive = True

        self.inactiveDefaultFrame = 0 # index of frame displayed when inactive

        self.folderpath = folderpath
        self.frameRate = frameRate # FRAME RATE IS CONSTRICTED TO THE GAME FRAME RATE
        self.totalFrames = totalFrames
        self.fileType = fileType #.png/.jpeg etc. include the period
        self.fileNameLeading = fileNameLeading # leading name of the filenames. ex. sequence001 : 'sequence'
        self.numLeadingZeroes = numLeadingZeroes # Number of extra zeros. For example, total of 10 frames, but has 4 digits (0010), has 2 leading zeroes

        self.scale = scale # Tuple of width and height

        self.frame_index = 0
        self.last_update_time = pygame.time.get_ticks()

        self.actionWhenFinished = None # function called when animation finishes
        self.FinishedPlaying = False

        self.loadFrames()

    
    def loadFrames(self):
        startTime =  pygame.time.get_ticks()
        log(f"Loading Animation {self.folderpath}/{self.fileNameLeading} ...")

        def format_with_leading_zeroes(max_number, current_number):
            max_length = len(str(max_number))
            return str(current_number).zfill(max_length)

        leadingzeroes = "0"*self.numLeadingZeroes
        self.frames = [pygame.image.load(f"{self.folderpath}/{self.fileNameLeading}{leadingzeroes}{format_with_leading_zeroes(self.totalFrames,i)}{self.fileType}") for i in range(self.totalFrames)] # You're welcome for the stroke

        for i in range(self.totalFrames):
            self.frames[i] = pygame.transform.scale(self.frames[i], self.scale)

        endTime = pygame.time.get_ticks() - startTime
        log(f"... Finished Loading Animation {self.folderpath}/{self.fileNameLeading} in {endTime} ms")
    
    def setScale(self,scale):
        self.scale = scale
        for i in range(self.totalFrames):
            self.frames[i] = pygame.transform.scale(self.frames[i], self.scale)

    def setFrameRate(self, frameRate):
        self.frameRate = frameRate
    
    # TODO: Add Variable framerates for animations
    # This function will only play the animations at the frame rate of the game

    def getCurrentFrame(self): # Returns a 'pygame.image.load()'
        current_time = pygame.time.get_ticks()
        frameDelay_ms = 1000 / self.frameRate

        
        if self.Looping: # When Looping
            if current_time - self.last_update_time > frameDelay_ms:
                self.frame_index = (self.frame_index + 1) % (self.totalFrames)
                self.last_update_time = current_time
   
            return self.frames[self.frame_index]
        
        if self.FinishedPlaying:
            return self.frames[self.inactiveDefaultFrame] # Default frame
        
        if self.playTimes > 0: # When Played a certain number of times
            if self.frame_index >= self.totalFrames-1:
                self.playTimes = self.playTimes - 1


            if current_time - self.last_update_time > frameDelay_ms:
                self.frame_index = (self.frame_index + 1) % (self.totalFrames)
                self.last_update_time = current_time
            return self.frames[self.frame_index]

        if self.actionWhenFinished is not None:
            self.actionWhenFinished() # function call when finished all frames

        return self.frames[self.inactiveDefaultFrame] # Default frame
    
    def isLooping(self, bool):
        self.Looping = bool

    def play(self, timesPlayed):
        self.playTimes = timesPlayed
        self.FinishedPlaying = False
    
    def setActionWhenFinished(self, action):
        self.actionWhenFinished = action

class text:
    def __init__(self, text):
        self.text = text
        self.font = None
        self.textColor = 'BLACK' # default color
        self.textSize = 10 # default font size
        self.antiAliased = True # antiAliasing set true by default

        self.renderedText = pygame.font.SysFont(self.font, self.textSize).render(self.text,self.antiAliased, self.textColor)
    
    def getRendered(self):
        return self.renderedText
    
    def setTextColor(self, Color):
        self.textColor = Color
        self.renderedText = pygame.font.SysFont(self.font, self.textSize).render(self.text,self.antiAliased, self.textColor)
            

    def setTextSize(self, size):
        self.textSize = size
        self.renderedText = pygame.font.SysFont(self.font, self.textSize).render(self.text,self.antiAliased, self.textColor)
    
    def setText(self, text):
        self.text = text
        self.renderedText = pygame.font.SysFont(self.font, self.textSize).render(self.text,self.antiAliased, self.textColor)
            

    def setFont(self, font):
        self.font = font
        self.renderedText = pygame.font.SysFont(self.font, self.textSize).render(self.text,self.antiAliased, self.textColor)
    
    def setFontSize(self, fontSize):
        self.textSize = fontSize
        self.renderedText = pygame.font.SysFont(self.font, self.textSize).render(self.text,self.antiAliased, self.textColor)

class Surface:
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        # Transform data
        self.Xpos = Xpos
        self.Ypos = Ypos
        self.Xscale = Xscale
        self.Yscale = Yscale

        self.image = None
        self.animation = None

        self.child_layers = []  # Child layers, contains other surfaces

        self.textObject = None

        self.isVisible = True

        self.hidden = False # Does not render visuals but keeos function active

        self.updateFunc = None # Function that runs every frame

    def setImage(self, image): # Accepts 'pygame.image.load(path)' as arguement
        self.image = image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.Xscale,self.Yscale))
    
    def setAnimation(self, animation): # Accepts an Animation Object
        self.animation = animation
    
    def clearImage(self):
        self.image = None
    
    def addText(self, text): # Builder pattern for easy preset text
        self.textObject = text
    
    def clearText(self):
        self.textObject = None
    
    def setScale(self, Xscale, Yscale):
        self.Xscale = Xscale
        self.Yscale = Yscale
        if self.image is not None:
            self.image = pygame.transform.scale(self.image, (Xscale,Yscale))
        if self.animation is not None:
            self.animation.setScale(self.getScale())
    
    def setVisible(self,bool):
        self.isVisible = bool

    def Hide(self, bool):
        self.hidden = bool

    def setCoord(self, x,y):
        XPosDelta = x - self.Xpos
        YPosDelta = y - self.Ypos
        
        self.Xpos = x
        self.Ypos = y

        for Surface in self.child_layers:
            Surface.MoveX(XPosDelta)
            Surface.MoveY(YPosDelta)
    
    def MoveX(self, amount):
        self.setCoord(self.Xpos + amount, self.Ypos) 
    
    def MoveY(self, amount):
        self.setCoord(self.Xpos, self.Ypos+ amount)
    
    def addChildSurface(self, Surface):
        self.child_layers.append(Surface)

        # Setting Relative coordinates
        Surface.MoveX(self.Xpos)
        Surface.MoveY(self.Ypos)
    
    def getCoord(self):
        return (self.Xpos,self.Ypos)

    def getScale(self):
        return (self.Xscale,self.Yscale)
    
    def setUpdateFunc(self, func):
        self.updateFunc = func
    
    def nextSurface(self, newSurface):
        self.setVisible(False)
        newSurface.setVisible(True)

    def render(self, screen):
        if self.updateFunc is not None:
            self.updateFunc()

        if self.isVisible is False:
            return
        
        if self.hidden:
            return
        
        

        # Order of rendering: Image, Animation, Text
        if self.image is not None:
            screen.blit(self.image, self.getCoord())
        
        if self.animation is not None:
            screen.blit(self.animation.getCurrentFrame(), self.getCoord())
        
        if self.textObject is not None:
            screen.blit(self.textObject.getRendered(), self.getCoord())

        for Surface in self.child_layers:
            Surface.render(screen)
        
class Button (Surface):
    def __init__(self,  Xpos, Ypos, Xscale, Yscale, EventHandler):
        super().__init__(Xpos, Ypos, Xscale, Yscale)
        self.myAction = None # Function to be called when button clicked

        self.rect = pygame.Rect(self.Xpos,self.Ypos,self.Xscale, self.Yscale)
        self.eventHandler = EventHandler

        self.eventHandler.addEventAction(self.handleEvent)

        self.last_update_time = pygame.time.get_ticks()
        self.clickDelayms = 0 # Delay between allowable clicks 

        self.AllowHold = False
        self.onHold = False

        self.Hovered = False
        
    
    def setCoord(self, x, y):
        super().setCoord(x, y)
        self.rect = pygame.Rect(self.Xpos,self.Ypos,self.Xscale, self.Yscale)
    
    def setScale(self, Xscale, Yscale):
        super().setScale(Xscale, Yscale)
        self.rect = pygame.Rect(self.Xpos,self.Ypos,self.Xscale, self.Yscale)

    def render(self, screen):
        # Check if hovered
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.Hovered = True
        else:
            self.Hovered = False

        super().render(screen)
    
    def handleEvent(self, event):
        if self.isVisible is False: # Dont do action if invisible
            return

        
        if event.type == pygame.MOUSEBUTTONUP:
            self.onHold = False
        
            
        if event.type == pygame.MOUSEBUTTONDOWN: # On Click
                if not self.AllowHold:
                    #print(self.onHold)
                    if self.onHold:
                        return
                    
                if event.button == 1: #Left mouse button click
                    if self.rect.collidepoint(event.pos):
                        if self.myAction is not None:
                            self.myAction()
                self.onHold = True
    
    # TODO: ADD HOVER ACTION

    def addHoverAction(self, action): # input function
        pass

    
    def setAction(self, action): # input a function
        self.myAction = action


class GameClock:

    def __init__(self):
        self.game_duration_ms = 600000 # one game is 10 minutes
        self.startTime_ms = None # if none, game has not started


        self.startHour = 9 # 9 am
        self.endHour = 17 # 5 pm

    def startClock(self):
        self.startTime_ms = pygame.time.get_ticks()
        self.gameStarted = True
    

    def resetClock(self):
        self.gameStarted = False
        self.gameOver = False

        self.startTime_ms = None

    def getHour(self): # returns military time (24 hour)
        if self.startTime_ms is None:
            return None
            
        
        startTime = self.startTime_ms
        currentTime = pygame.time.get_ticks()
        gameDuration_ms = self.game_duration_ms
         
        Timepassed_ms = currentTime - startTime
        ShiftDuration_ms = 0


        timeAdjustment = 0 if self.endHour > self.startHour else 24 # adjust time when shift loops into the morning

        ShiftDuration_ms = (self.endHour - self.startHour + timeAdjustment) * 3600000
        
        

        ShiftTimePassed_Hours = Timepassed_ms * (ShiftDuration_ms/gameDuration_ms) / 3600000

        return self.startHour + ShiftTimePassed_Hours
    
    def militaryToStandardTime(self, input):
        timeMilitary = int(input) # remove decimals
        # timeMilitary = input
        if timeMilitary > 23:
            timeMilitary = timeMilitary % 24
        if timeMilitary < 1:
            out = timeMilitary + 12
            return f"{out} AM"
        
        if timeMilitary < 13:
            if timeMilitary < 12:
                return f"{timeMilitary} AM"
            return f"{timeMilitary} PM"
        else:
            if timeMilitary >= 24:
                return f"{timeMilitary} AM"
            out = timeMilitary - 12
            return f"{out} PM"
    
    def getHourStandard(self):
        return self.militaryToStandardTime(self.getHour())


class Item:
    def __init__(self):
        pass

class GameManager: # Object that stores game state that can be passed around
    def __init__(self):

        # Game State Variables
        self.clock = GameClock()

        self.gameStarted = False
        self.gameOver = False
    
    def startGame(self):
        self.clock.startClock()
        self.gameStarted = True
    
    def CheckClockEnded(self): # Will return False if clock still running
        if self.gameStarted and not self.gameOver:
            endHour = self.clock.endHour if self.clock.endHour > self.clock.startHour else (self.clock.endHour + 24)

            if self.clock.getHour() >= endHour:
                self.gameOver = True
                return True
        
        return False
    
    def resetGame(self):
        self.gameStarted = False
        self.gameOver = False

        self.clock.resetClock()
    


### END OF CLASS SETUP
myEventHandler = EventHandler()

main_surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)

blank_surface = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
blank_surface.fill('Black')

############## ---------- MAIN CODE ---------- ##############

myGameManager = GameManager()


class MainMenuSurface(Surface):
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        super().__init__(Xpos, Ypos, Xscale, Yscale)

        self.myGameplaySurface = None

        MainMenuBG_Animation = animation("Assets/UI Elements/Title Screen",24,71,".jpg","Title Screen",0,(SCREEN_WIDTH,SCREEN_HEIGHT))
        

        MainMenuBG_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        MainMenuBG_Surface.setAnimation(MainMenuBG_Animation)

        MainMenuPlayGameButton = Button(270,380,300,100,myEventHandler)

        def toGameplay():
            if self.myGameplaySurface is None:
                log("Gameplay Surface not added to Main Menu Surface")
                return
            self.nextSurface(self.myGameplaySurface)

            myGameManager.resetGame()
            myGameManager.startGame()
        
        MainMenuPlayGameButton.setAction(toGameplay)

        self.addChildSurface(MainMenuBG_Surface)
        self.addChildSurface(MainMenuPlayGameButton)
    
    def addGameplaySurface(self, gameplaySurface):
        self.myGameplaySurface = gameplaySurface
    

class GameplaySurface(Surface):
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        super().__init__(Xpos, Ypos, Xscale, Yscale)

        self.winScreen = None
        self.loseScreen = None

        self.viewIndex = 0 # index for cycling views
        self.GameplayViews = [] 
        self.viewLabels = ["Counter","Kitchen","Drive Through","Storage Room"]
        

        self.counterSurface = CounterSurface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.storageRoomSurface = StorageRoomSurface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.kitchenSurface = KitchenSurface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.driveThroughSurface = DrivethroughSurface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)

        UI_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)

        # Views label
        self.view_label = text("Counter")
        self.view_label.setFont("Assets/FONTS/VCR_OSD.ttf")
        self.view_label.setTextColor("#FFFFFF")
        self.view_label.setFontSize(50)

        view_label_surface = Surface(520,630,100,100)
        view_label_surface.addText(self.view_label)

        UI_Surface.addChildSurface(view_label_surface)

        # Inventory Slot
        self.UI_ItemSlotSurface = Surface(100,100,200,200)
        
        # Change Views buttons
        leftButton = Button(100,620,50,50,myEventHandler)
        leftButton.setImage(pygame.image.load("Assets/UI Elements/arrow left.jpg"))
        leftButton.setAction(self.turnLeft)

        rightButton = Button(1130,620,50,50,myEventHandler)
        rightButton.setImage(pygame.image.load("Assets/UI Elements/arrow right.jpg"))
        rightButton.setAction(self.turnRight)

        UI_Surface.addChildSurface(rightButton)
        UI_Surface.addChildSurface(leftButton)

        # Clock
        self.clockText = text("clock")
        self.clockText.setFontSize(70)
        self.clockText.setTextColor("#FFFFFF")

        clockSurface = Surface(10,10,100,100)
        clockSurface.addText(self.clockText)

        def UpdateClock():
            self.clockText.setText(myGameManager.clock.getHourStandard())
            if(myGameManager.CheckClockEnded()):
                self.endShift()


        clockSurface.setUpdateFunc(UpdateClock)

        UI_Surface.addChildSurface(clockSurface)



        # Order of views added to list affect order of view rotation
        self.GameplayViews.append(self.counterSurface)
        self.GameplayViews.append(self.kitchenSurface)
        self.GameplayViews.append(self.driveThroughSurface)
        self.GameplayViews.append(self.storageRoomSurface)

        self.addChildSurface(self.counterSurface)
        self.addChildSurface(self.kitchenSurface)
        self.addChildSurface(self.driveThroughSurface)
        self.addChildSurface(self.storageRoomSurface)
        self.addChildSurface(UI_Surface)

        self.resetViews()
    
    def resetViews(self):
        if self.viewIndex < 0:
            self.viewIndex = 0
        
        if self.viewIndex >= len(self.GameplayViews):
            self.viewIndex = len(self.GameplayViews) - 1
        
        for i in range(len(self.GameplayViews)):
            if i == self.viewIndex:        
                self.GameplayViews[i].setVisible(True)
            else:
                
                self.GameplayViews[i].setVisible(False)
        
        self.view_label.setText(self.viewLabels[self.viewIndex])
    
    def turnRight(self):
        self.viewIndex = (self.viewIndex + 1) % len(self.GameplayViews)
        self.resetViews()

    def turnLeft(self):
        self.viewIndex = (self.viewIndex - 1) % len(self.GameplayViews)
        self.resetViews()
    
    def endShift(self): # When clock expires, transition to Win Screen
        self.nextSurface(self.winScreen)

    def gameLose(self): # transition to lose Screen
        pass

    


class CounterSurface(Surface):
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        super().__init__(Xpos, Ypos, Xscale, Yscale)

        self.aBG_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.aBG_Surface.setImage(pygame.image.load("Assets/Counter/CounterBG.jpg"))

        self.addChildSurface(self.aBG_Surface)
    
    

class StorageRoomSurface(Surface):
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        super().__init__(Xpos, Ypos, Xscale, Yscale)

        self.BG_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.BG_Surface.setImage(pygame.image.load("Assets/Storage Room/Storage_Room.png"))

        ### Storage Room Highlight ###
        self.StorageRoom_BurgerBunHighlight_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.StorageRoom_BurgerBunHighlight_Surface.setImage(pygame.image.load("Assets/Storage Room/Highlights/Storage Room Burger Bun Highlight.png"))

        self.StorageRoom_HotdogBunHighlight_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.StorageRoom_HotdogBunHighlight_Surface.setImage(pygame.image.load("Assets/Storage Room/Highlights/Storage Room Hotdog Bun Highlight.png"))


        self.StorageRoom_FreezerHighlight_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.StorageRoom_FreezerHighlight_Surface.setImage(pygame.image.load("Assets/Storage Room/Highlights/Storage Room Freezer Highlight.png"))

        self.BG_Surface.addChildSurface(self.StorageRoom_BurgerBunHighlight_Surface)
        self.BG_Surface.addChildSurface(self.StorageRoom_HotdogBunHighlight_Surface)
        self.BG_Surface.addChildSurface(self.StorageRoom_FreezerHighlight_Surface)

        # Storage Room Buttons
        surfaceGuide = pygame.Surface((100,100))
        surfaceGuide.fill('Red')

        def HotdogBunButtonAction():
            print("Hotdog Bun Acquired")
        self.HotdogBun_Button = Button(670,130,230,150,myEventHandler)
        self.HotdogBun_Button.setAction(HotdogBunButtonAction)

        def BurgerBunButtonAction():
            print("Burger Bun Acquired")
        self.BurgerBun_Button = Button(870,300,250,150,myEventHandler)
        self.BurgerBun_Button.setAction(BurgerBunButtonAction)


        def FreezerButtonAction():
            print("Freezer Opened")
        self.FreezerButton = Button(350,280,250,350,myEventHandler)
        self.FreezerButton.setAction(FreezerButtonAction)


        self.BG_Surface.addChildSurface(self.BurgerBun_Button)
        self.BG_Surface.addChildSurface(self.FreezerButton)
        self.BG_Surface.addChildSurface(self.HotdogBun_Button)

        def BG_Surface_updateFunc():
            self.StorageRoom_BurgerBunHighlight_Surface.setVisible(self.BurgerBun_Button.Hovered)
            self.StorageRoom_FreezerHighlight_Surface.setVisible(self.FreezerButton.Hovered)
            self.StorageRoom_HotdogBunHighlight_Surface.setVisible(self.HotdogBun_Button.Hovered)
        
        self.BG_Surface.setUpdateFunc(BG_Surface_updateFunc)


        # Freezer
        self.Freezer_BG_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.Freezer_BG_Surface.setImage(pygame.image.load("Assets/Storage Room/Freezer.png"))

        self.addChildSurface(self.BG_Surface)

class KitchenSurface(Surface):
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        super().__init__(Xpos, Ypos, Xscale, Yscale)

        self.BG_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.BG_Surface.setImage(pygame.image.load("Assets/Kitchen/KitchenBG.png"))

        self.addChildSurface(self.BG_Surface)

class DrivethroughSurface(Surface):
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        super().__init__(Xpos, Ypos, Xscale, Yscale)

        self.BG_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.BG_Surface.setImage(pygame.image.load("Assets/Drive Through/DrivethroughBG.jpg"))

        self.addChildSurface(self.BG_Surface)

class WinScreen(Surface):
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        super().__init__(Xpos, Ypos, Xscale, Yscale)

        self.BG_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.BG_Surface.setImage(pygame.image.load("Assets/UI Elements/winScreen.jpg")) # Temp Win Screen

        self.addChildSurface(self.BG_Surface)

class LoseScreen(Surface):
    def __init__(self, Xpos, Ypos, Xscale, Yscale):
        super().__init__(Xpos, Ypos, Xscale, Yscale)

        self.BG_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.BG_Surface.setImage(pygame.image.load("Assets/UI Elements/winScreen.jpg"))

        self.addChildSurface(self.BG_Surface)



# Surfaces Construction
MainMenuMainSurface = MainMenuSurface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
GameplayMainSurface = GameplaySurface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
winScreen = WinScreen(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)

# Connecting Surfaces
MainMenuMainSurface.addGameplaySurface(GameplayMainSurface)
GameplayMainSurface.winScreen = winScreen

# Adding Surfaces to main surface
main_surface.addChildSurface(MainMenuMainSurface)
main_surface.addChildSurface(GameplayMainSurface)
main_surface.addChildSurface(winScreen)

# Turning off Surfaces
GameplayMainSurface.setVisible(False)
winScreen.setVisible(False)


# ------------ MAIN LOOP ------------ #

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    

    screen.blit(blank_surface,(0,0)) # Reset Blank Screen
    main_surface.render(screen) # Render main surface

    # Event handler
    myEventHandler.handleEvents(event) # I have no idea why this works and is faster

    pygame.display.update()
    clock.tick(CLOCK_TICK)

