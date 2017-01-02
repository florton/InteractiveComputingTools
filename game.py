import sys, pygame, math

def makeGate(name):
    gate = pygame.image.load("gatePics\\" + name + ".png")
    gateRect = gate.get_rect()
    gateRect.center = mouseX,mouseY 
    return(gate,gateRect,name)

def makeLine(mouseX,mouseY,gate,drawingLine):
    mouseRelativeX = mouseX-gate[1].left
    mouseRelativeY = mouseY-gate[1].top
    coord = None
    
    if mouseRelativeX > 2*(gate[1].width/3):
        coord = 1
    elif mouseRelativeX < gate[1].width/3:
        if mouseRelativeY > gate[1].height/2:
            coord = 2
        else:
            coord = 3
    if drawingLine == 1:        
        loadedLines.append([[coord,gate],[None,None]])
    elif coord != loadedLines[-1][0][0]:
        loadedLines[-1][1] = [coord,gate]
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        return False
    return 2
    
pygame.init()

size = width, height = 800, 600
screen = pygame.display.set_mode(size)

white = 255, 255, 255
black = 0,0,0

mouseX,mouseY = 0,0
mouseKey = 0;

gateNames = ['AND','OR','NOT','NOR','NAND','XOR','XNOR']
draggingObject = None
drawingLine = False
loadedGates = []
loadedLines = []

gateSelect = pygame.image.load("gatePics\GATES.png")
selectRect = gateSelect.get_rect()
selectRect.midtop = (width/2,0)

lineButton = pygame.image.load("gatePics\LINE.png")
lineButtonRect = lineButton.get_rect()
lineButtonRect.midleft = (0, height/4)

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
            tempbuttons = [0,0,0]
            if(event.button <4):
                tempbuttons[event.button-1] = 0
                mouseKey = tuple(tempbuttons)
        if event.type == pygame.MOUSEMOTION: 
            mouseX,mouseY = event.pos
            mouseKey = event.buttons
            
    #Move gate if cursor clicks&drags it Or draw lines       
    if draggingObject:
        draggingObject[1].center = mouseX,mouseY  
    elif mouseKey[0] == 1:
        for gate in loadedGates:
            if gate[1].collidepoint(mouseX,mouseY):
                if drawingLine:
                    drawingLine = makeLine(mouseX,mouseY,gate,drawingLine)                   
                else:
                    draggingObject = gate
    if mouseKey[0] == 0:
        if draggingObject and selectRect.collidepoint(draggingObject[1].center):
            loadedGates.remove(draggingObject)            
        draggingObject = None     
    
    #Right Click
    if mouseKey[2] == 1:
        if drawingLine:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            drawingLine = False
            if not loadedLines[-1][2]:
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
        
            
    #Start Drawing
    screen.fill(white) 
    #draw selection bar & buttons
    screen.blit(gateSelect,selectRect)   
    screen.blit(lineButton,lineButtonRect)      
    #draw all gates
    for gate in loadedGates:
        screen.blit(gate[0], gate[1])    
    #draw and update all lines
    for line in loadedLines:
        newCoords = [None,(mouseX,mouseY)]
        for x in range(2):
            gate = line[x][1]
            if line[x][0] == 1:
                newCoords[x] = gate[1].midright
            if line[x][0] ==2:
                newCoords[x] = gate[1].left , gate[1].topleft[1] + 3*(gate[1].height/4)
            if line[x][0] == 3:
                newCoords[x] = gate[1].left , gate[1].topleft[1] + gate[1].height/4
        pygame.draw.line(screen, (255,0,0), newCoords[0], newCoords[1], 2)
    #draw text
    font=pygame.font.Font(None,30)
    info1 = font.render("MousePos: "+str(mouseX) + ", "+str(mouseY), False, black)
    info3 = font.render("MouseKey:" + str(mouseKey), False, black)
    screen.blit(info1, (0, height-40))
    screen.blit(info3, (0, height-20))
   
    #Update Screen
    pygame.display.flip()
    
    

    
    