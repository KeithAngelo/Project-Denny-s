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
        
        if self.playTimes > 0: # When Played a certain number of times
            if self.frame_index >= self.totalFrames-1:
                self.playTimes = self.playTimes - 1


            if current_time - self.last_update_time > frameDelay_ms:
                self.frame_index = (self.frame_index + 1) % (self.totalFrames)
                self.last_update_time = current_time
            return self.frames[self.frame_index]
        
        return self.frames[self.inactiveDefaultFrame] # Default frame
    
    def isLooping(self, bool):
        self.Looping = bool

    def play(self, timesPlayed):
        self.playTimes = timesPlayed

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

        self.AllowHold = True 
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

class GameManager: # Object that stores game state that can be passed around
    def __init__(self):
        # Game State Variables
        pass

    def resetGame(self):
        pass

class Scene:
    def __init__(self):
        self.sceneSurface = None

        # Use polymorphism to setup 

    def nextScene(self, newScene):
        self.sceneSurface.setVisible(False)
        newScene.sceneSurface.setVisible(True)
    
    def getSurface(self):
        return self.sceneSurface
    
    def addToMainSurface(self, mainSurface): # this will disable the scene surface
        mainSurface.addChildSurface(self)
        if self.sceneSurface is not None:
            self.sceneSurface.setVisible(False)
    
    def activate(self):
        if self.sceneSurface is not None:
            self.sceneSurface.setVisible(True)
    
class SceneManager:
    def __init__(self):
        pass
    


### END OF CLASS SETUP
myEventHandler = EventHandler()

main_surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)

blank_surface = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
blank_surface.fill('Black')

############## ---------- MAIN CODE ---------- ##############

class MainMenu(Scene):
    def __init__(self, mainGameplayScene, myGameManager):
        super().__init__()
        self.sceneSurface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)



class Gameplay(Scene):
    def __init__(self, myGameManager):
        super().__init__()
        self.sceneSurface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        self.mainMenuScene = None

        self.UI_Surface = Surface(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
    
    def addMainMenuScene(self, mainMenuScene):
        self.mainMenuScene = mainMenuScene


### Constructing Scenes ###
myGameManager = GameManager()

gamePlayScene = Gameplay(myGameManager)
mainMenuScene = MainMenu(myGameManager,gamePlayScene)

gamePlayScene.addMainMenuScene(mainMenuScene)

gamePlayScene.addToMainSurface(main_surface)
mainMenuScene.addToMainSurface(main_surface)

mainMenuScene.activate()

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

