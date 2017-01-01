import sys, pygame, math

def makeGate(name):
    gate = pygame.image.load("gatePics\\" + name + ".png")
    gateRect = gate.get_rect()
    gateRect.center = mouseX,mouseY 
    return(gate,gateRect)

pygame.init()

size = width, height = 800, 600
screen = pygame.display.set_mode(size)

white = 255, 255, 255
black = 0,0,0

mouseX,mouseY = 0,0
mouseKey = 0;

gateNames = ['AND','OR','NOT','NOR','NAND','XOR','XNOR']
draggingObject = None
loadedGates = []

gateSelect = pygame.image.load("gatePics\GATES.png")
selectRect = gateSelect.get_rect()
selectRect.midtop = (width/2,0)

#Main Loop
while True:
    #Get Input Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.MOUSEMOTION: 
            mouseX,mouseY = event.pos
            mouseKey = event.buttons
            
    #Move gate if cursor clicks&drags it          
    if draggingObject:
        draggingObject[1].center = mouseX,mouseY  
    elif mouseKey[0] == 1:
        for gate in loadedGates:
            if gate[1].collidepoint(mouseX,mouseY):
                draggingObject = gate
    if mouseKey[0] == 0:
        if draggingObject and selectRect.collidepoint(draggingObject[1].center):
            loadedGates.remove(draggingObject)
        draggingObject = None
        
    #Spawn new gates
    if mouseKey[0] == 1 and not draggingObject:
        if selectRect.collidepoint(mouseX,mouseY):
            select = (mouseX-selectRect.left)/(selectRect.width/7) 
            select = int(math.floor(select))
            newGate = makeGate(gateNames[select])
            loadedGates.append(newGate)
            draggingObject = newGate
            
    #Start Drawing
    screen.fill(white) 
    #draw selection bar
    screen.blit(gateSelect,selectRect)   
    #draw all gates
    for gate in loadedGates:
        screen.blit(gate[0], gate[1])       
    #draw text
    font=pygame.font.Font(None,30)
    info1 = font.render("MousePos: "+str(mouseX) + ", "+str(mouseY), False, black)
    info3 = font.render("MouseKey:" + str(mouseKey), False, black)
    screen.blit(info1, (0, height-40))
    screen.blit(info3, (0, height-20))
   
    #Update Screen
    pygame.display.flip()
    
    

    
    