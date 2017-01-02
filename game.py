import sys, pygame, math

def makeGate(name):
    gate = pygame.image.load("gatePics\\" + name + ".png")
    gateRect = gate.get_rect()
    gateRect.center = mouseX,mouseY 
    return(gate,gateRect,name)

def makeSwitch():
    switch = pygame.image.load("gatePics\OFF.png")
    switchRect = switch.get_rect()
    switchRect.center = mouseX,mouseY 
    return(switch,switchRect,False)
    
def makeLine(mouseX,mouseY,target,drawingLine):
    mouseRelativeX = mouseX-target[1].left
    mouseRelativeY = mouseY-target[1].top
    coord = None
    # if drawingLine == 1 -> set line start, if == 2 -> set line end,
    # if == 3 -> set drawingLine to False on next mouseup
    if mouseRelativeX > 2*(target[1].width/3):
        coord = 1
    elif mouseRelativeX < target[1].width/3:
        if target[2] == 'NOT':
            coord = 0
        elif mouseRelativeY > target[1].height/2:
            coord = 2
        else:
            coord = 3
    if drawingLine == 1:        
        loadedLines.append([[coord,target],[None,None]])
    elif coord != loadedLines[-1][0][0]:
        loadedLines[-1][1] = [coord,target]
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        return 3
    return 2
    
def moveObject(objectRect, mouseX, mouseY):
    relativeX = mouseX-objectRect.left
    relativeY = mouseY-objectRect.top
    objectRect.topleft = (mouseX+relativeX,mouseY+relativeY)

def Delete(object):
    for line in loadedLines[:]:
        if line[0][1] == object or line[1][1] == object:
            loadedLines.remove(line)
    loadedGates.remove(object)
    
    
pygame.init()

size = width, height = 800, 600
screen = pygame.display.set_mode(size)

white = 255, 255, 255
black = 0,0,0
red = 255,0,0

mouseX,mouseY = 0,0
mouseKey = 0;

gateNames = ['AND','OR','NOT','NOR','NAND','XOR','XNOR']
draggingObject = None
drawingLine = False

loadedGates = []
loadedLines = []
loadedSwitches = []

gateSelect = pygame.image.load("gatePics\GATES.png")
selectRect = gateSelect.get_rect()
selectRect.midtop = (width/2,0)

lineButton = pygame.image.load("gatePics\LINE.png")
lineButtonRect = lineButton.get_rect()
lineButtonRect.midleft = (0, height/4)

switchButton = pygame.image.load("gatePics\SWITCH.png")
switchButtonRect = switchButton.get_rect()
switchButtonRect.midleft = (0, 3*(height/8))

#Main Loop
while True:
    #Get Input Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            tempbuttons = [0,0,0]
            if(event.button <4):
                tempbuttons[event.button-1] = 1
                mouseKey = tuple(tempbuttons)
        if event.type == pygame.MOUSEBUTTONUP:
            if drawingLine == 3: drawingLine = False
            tempbuttons = [0,0,0]
            if(event.button <4):
                tempbuttons[event.button-1] = 0
                mouseKey = tuple(tempbuttons)
        if event.type == pygame.MOUSEMOTION: 
            mouseX,mouseY = event.pos
            mouseKey = event.buttons
            
    #Move gate/switch if cursor clicks&drags     
    if draggingObject and not drawingLine:
        draggingObject[1].center = mouseX, mouseY
        #moveObject(draggingObject[1], mouseX, mouseY) 
    elif mouseKey[0] == 1:
        for gate in loadedGates:
            if gate[1].collidepoint(mouseX,mouseY):
                #maybe draw a line instead
                if drawingLine:
                    drawingLine = makeLine(mouseX,mouseY,gate,drawingLine)                   
                else:
                    draggingObject = gate
        #move and flip switches
        for switch in loadedSwitches:
            if switch[1].collidepoint(mouseX,mouseY):
                draggingObject = switch
    if mouseKey[0] == 0 and draggingObject:
        if draggingObject and selectRect.collidepoint(draggingObject[1].center):
            Delete(draggingObject)
        draggingObject = None     
    
    #Right Click
    if mouseKey[2] == 1:
        if drawingLine:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            drawingLine = False
            if loadedLines and not loadedLines[-1][1]:
                loadedLines.pop()
    
    if mouseKey[0] == 1 and not draggingObject:
        #Spawn new gates
        if selectRect.collidepoint(mouseX,mouseY):
            select = (mouseX-selectRect.left)/(selectRect.width/7) 
            select = int(math.floor(select))
            newGate = makeGate(gateNames[select])
            loadedGates.append(newGate)
            draggingObject = newGate
        #Spawn lines between components
        if lineButtonRect.collidepoint(mouseX,mouseY):
            drawingLine = 1
            pygame.mouse.set_cursor(*pygame.cursors.diamond)
        #Spawn switches
        if switchButtonRect.collidepoint(mouseX,mouseY):
            loadedSwitches.append(makeSwitch())
            
    #Start Drawing
    screen.fill(white) 
    #draw selection bar & buttons
    screen.blit(gateSelect,selectRect)   
    screen.blit(lineButton,lineButtonRect)  
    screen.blit(switchButton,switchButtonRect)     
    #draw all gates
    for gate in loadedGates:
        screen.blit(gate[0], gate[1])  
    #draw all switches
    for switch in loadedSwitches:
        screen.blit(switch[0],switch[1])
    #draw and update all lines
    for line in loadedLines:
        newCoords = [None,(mouseX,mouseY)]
        offset = gate[1].width/10
        for x in range(2):
            target = line[x][1]
            if line[x][0] == 1:
                newCoords[x] = target[1].midright[0]-offset, target[1].midright[1]
            elif line[x][0] == 2:
                newCoords[x] = target[1].left+offset , target[1].topleft[1] + 3*(target[1].height/4)
            elif line[x][0] == 3:
                newCoords[x] = target[1].left+offset , target[1].topleft[1] + target[1].height/4
            elif line[x][0] == 0:
                newCoords[x] = target[1].midleft[0]+offset, target[1].midleft[1]
        pygame.draw.line(screen, red, newCoords[0], newCoords[1], 2)
    #draw text
    font=pygame.font.Font(None,30)
    info1 = font.render("MousePos: "+str(mouseX) + ", "+str(mouseY), False, black)
    info3 = font.render("MouseKey:" + str(mouseKey), False, black)
    screen.blit(info1, (0, height-40))
    screen.blit(info3, (0, height-20))
    #Update Screen
    pygame.display.flip()
    
    

    
    