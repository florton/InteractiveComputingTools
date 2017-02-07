import sys, pygame, math
from pygame.locals import *
from gates import Evaluate
from generator import GenerateTruthTable, TruthTableError, GenerateTimingDiagram
from datetime import datetime
#from multiprocessing import Process


# A gate is a list [image, rect, gate_name_string, [connections_on_input_anchors], on/off, id] 
def makeGate(name):
    gate = pygame.image.load("gatePics\\" + name + ".png")
    gateRect = gate.get_rect()
    gateRect.center = mouseX,mouseY
    id = 0 if not loadedGates else loadedGates[-1][5]+1
    return([gate,gateRect,name,[],False,id])

# A switch is a list [image, rect, "SWITCH" , [dummy_array],on/off, id] 
def makeSwitch():
    switch = switchOff
    switchRect = switch.get_rect()
    switchRect.center = mouseX,mouseY 
    id = 0 if not loadedSwitches else loadedSwitches[-1][5]+1
    return([switch,switchRect,"SWITCH",[],False,id])

# A light is a list [image, rect, "LIGHT", [connections],on/off, id] 
def makeLight():
    light = lightOff
    lightRect = light.get_rect()
    lightRect.center = mouseX,mouseY 
    id = 0 if not loadedLights else loadedLights[-1][5]+1
    return([light,lightRect,"LIGHT",[],False,id])    

# A clock is a list [image, rect, "CLOCK", [dummy_array], on/off, id, freq, timestamp]    
def makeClock():
    clockRect = clockComponent.get_rect()
    clockRect.center = mouseX,mouseY
    freq = .5
    id = 0 if not loadedClocks else loadedClocks[-1][5]+1
    return([clockComponent, clockRect, "CLOCK", [], False, id, freq, datetime.utcnow()])
    
#A line is a matrix list [[start_target_anchor, start_target , start_coords],
#[end_target_anchor, end_target, end_coords],"LINE",id,on/off]    
def makeLine(mouseX,mouseY,target,drawingLine):
    mouseRelativeX = mouseX-target[1].left
    mouseRelativeY = mouseY-target[1].top
    anchor = None
    inputAnchors = [5,0,2,3]
    outputAnchors = [1,4,6]

    # if drawingLine == 1 -> set line start, if == 2 -> set line end,
    # if == 3 -> set drawingLine to 1 on next mouseup
    
    #check if switch
    if target[2] == 'SWITCH':
        anchor = 4
    #else check if light
    elif target[2] == 'LIGHT':
        anchor = 5
    #else check if clock
    elif target[2] == 'CLOCK':
        anchor = 6
    #otherwise its a gate    
    elif mouseRelativeX > 2*(target[1].width/3):
        #all gates' output
        anchor = 1
    elif mouseRelativeX < target[1].width/3:
        #gate inputs
        if target[2] == 'NOT':
            anchor = 0
        elif mouseRelativeY > target[1].height/2:
            anchor = 2
        else:
            anchor = 3
    #if user clicked a non-anchor part of the gate just return
    else:
        return drawingLine
    if drawingLine == 1:
        id = 0 if not loadedLines else loadedLines[-1][3]+1
        if anchor in outputAnchors:
            #make new line with start target info
            loadedLines.append([[anchor,target,(mouseX,mouseY)],[None,None,None],"LINE",id,False])
        else:
            #make new line with start target info
            loadedLines.append([[None,None,None],[anchor,target,(mouseX,mouseY)],"LINE",id,False])
            #add current line to end target connections array
            target[3].append(loadedLines[-1])
    #inputs must connect to outputs and vis versa
    elif ((anchor in inputAnchors and (loadedLines[-1][0][0] in outputAnchors or loadedLines[-1][1][0] in outputAnchors))
        or (anchor in outputAnchors and (loadedLines[-1][0][0] in inputAnchors or loadedLines[-1][1][0] in inputAnchors))):       
        if anchor in outputAnchors:
            #add end target info to current (last) line
            loadedLines[-1][0] = [anchor,target,(mouseX,mouseY)]
        else:
            #add start target info to current (last) line
            loadedLines[-1][1] = [anchor,target,(mouseX,mouseY)]
            #add current line to end target connections array
            target[3].append(loadedLines[-1])
            #print target
        UpdateLights()
        UpdateLines()
        return 3
    return 2
    
def Delete(object):
    for line in loadedLines[:]:
        if line[0][1] == object or line[1][1] == object:
            DeleteLine(line)
    try:
        loadedGates.remove(object)
    except:
        try:
            loadedSwitches.remove(object)
        except:
            try:
                loadedLights.remove(object)
            except:
                loadedClocks.remove(object)
    
def Distance(a,b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def IsBetween(startPoint,endPoint,newPoint):
    return Distance(startPoint,newPoint) + Distance(newPoint,endPoint) - Distance(startPoint,endPoint) < 1    
        
def DeleteLine(line):
    target = line[1][1]
    target2 = line[0][1]
    try:
        target[3].remove(line)
    except:
        pass
    try:
        target2[3].remove(target)
    except:
        pass
    loadedLines.remove(line)
    UpdateLights()
    UpdateLines()

def TurnLight(light, bool):
    if bool:
        light[0] = lightOn
        light[4] = True
    else:
        light[0] = lightOff
        light[4] = False
    
def Click(clickCoords):
    if not drawingLine:
        #Flip switch if clicked on
        for switch in loadedSwitches:
            if switch[1].collidepoint(mouseX,mouseY):
                if switch[4]:
                    switch[0] = switchOff
                    switch[4] = False
                else:
                    switch[0] = switchOn
                    switch[4] = True
                UpdateLights()
                UpdateLines()
        #Generate Truth Table & show in new window
        if truthTableButtonRect.collidepoint(mouseX,mouseY):
            for process in childProcesses:
                process.terminate()
            if(loadedLights and loadedSwitches):
                if(loadedClocks):
                    childProcesses.append(TruthTableError("Cannot generate accurate truth table with a clock"))
                else:
                    childProcesses.append(GenerateTruthTable(loadedLights,loadedSwitches,loadedLines))
            else:
                childProcesses.append(TruthTableError("Please add at least one input and one output"))
        #Generate Timing Diagram & show in new window
        if timingButtonRect.collidepoint(mouseX,mouseY):
            for process in childProcesses:
                process.terminate()
            result = GenerateTimingDiagram()
            childProcesses.append(result[0])
            global timingPipe
            timingPipe = result[1]
            timingPipe.send([loadedSwitches,loadedClocks,loadedLights])
        
def PositionLines():
    for line in loadedLines:
        newCoords = [(mouseX,mouseY),(mouseX,mouseY)]        
        for x in range(2):
            target = line[x][1]
            offset = target[1].width/10 if target else 0
            #if NOT gate input
            if line[x][0] == 0:
                newCoords[x] = target[1].midleft[0]+offset, target[1].midleft[1]
            #if gate output
            elif line[x][0] == 1:
                newCoords[x] = target[1].midright[0]-offset, target[1].midright[1]
            #if gate input bottom
            elif line[x][0] == 2:
                newCoords[x] = target[1].left+offset , target[1].topleft[1] + 3*(target[1].height/4)
            #if gate input top
            elif line[x][0] == 3:
                newCoords[x] = target[1].left+offset , target[1].topleft[1] + target[1].height/4
            #if switch or clock
            elif line[x][0] == 4 or line[x][0] == 6:
                newCoords[x] = target[1].midright
            #if light
            elif line[x][0] == 5:
                newCoords[x] = target[1].midleft
        line[0][2] = newCoords[0]
        line[1][2] = newCoords[1]

def UpdateLights():
    #Run Logic Simulation (turn lights on/off)
    for light in loadedLights:
        TurnLight(light, Evaluate(light,loadedLines))
    try:
        timingPipe.send([loadedSwitches,loadedClocks,loadedLights])
    except:
        pass

def UpdateLines():
    #Run Logic Simulation (turn lines on/off)
    for line in loadedLines:
        line[4] = Evaluate(line,loadedLines)
        
def UpdateClocks():
    newTime = datetime.utcnow()    
    for clock in loadedClocks:
        deltaTime = (newTime-clock[7]).total_seconds()
        if deltaTime >= clock[6]:
            clock[4] = not clock[4]
            clock[7] = newTime 
            UpdateLights()
            UpdateLines()
        screen.blit(clock[0],clock[1])
        clockID = font.render('C'+str(clock[5]), True, black)
        screen.blit(clockID, (clock[1].x+5, clock[1].y+30)) 
    
    
def Main():
        
    #Initialize variables 
    pygame.init()
    pygame.display.set_caption("Interactive Logic")
    
    global size, width, height, screen
    
    size = width, height = 800, 600
    screen=pygame.display.set_mode(size,HWSURFACE|DOUBLEBUF|RESIZABLE)
    
    global font, black
    
    font=pygame.font.Font(None,30)
    white = 255, 255, 255
    black = 0,0,0
    red = 255,0,0
    green = 0,255,0
    lightRed = 255, 180, 180
    
    global clickCoords,clickOffset,mouseX,mouseY, mouseKey

    clickCoords = 0,0
    clickOffset = 0,0
    mouseX,mouseY = 0,0
    mouseKey = 0
    
    global loadedGates,loadedLights,loadedLines,loadedSwitches,loadedClocks

    loadedGates = []
    loadedLines = []
    loadedSwitches = []
    loadedLights = []
    loadedClocks = []    
    
    timestamp = datetime.utcnow()
    
    global childProcesses, timingPipe
    
    childProcesses = []
    timingPipe = None
    
    global gatenames, draggingObject, drawingLine

    gateNames = ['AND','OR','NOT','NOR','NAND','XOR','XNOR']
    draggingObject = None
    drawingLine = False
    
    global switchOn,switchOff, lightOn, lightOff, clockComponent

    switchOn = pygame.image.load("gatePics\SWITCHON.png")
    switchOff = pygame.image.load("gatePics\SWITCHOFF.png")
    lightOff = pygame.image.load("gatePics\LIGHTOFF.png")
    lightOn = pygame.image.load("gatePics\LIGHTON.png")
    clockComponent = pygame.image.load("gatePics\CLOCK.png")
    
    global gateSelect, selectRect , lineButton , lineButtonRect
    global switchButton, switchButtonRect , lightButton, lightButtonRect
    global clockButton, clockButtonRect, truthTableButton, truthTableButtonRect
    global timingButton, timingButtonRect
    
    gateSelect = pygame.image.load("gatePics\GATES.png")
    selectRect = gateSelect.get_rect()

    lineButton = pygame.image.load("gatePics\LINE.png")
    lineButtonRect = lineButton.get_rect()

    switchButton = pygame.image.load("gatePics\SWITCHBUTTON.png")
    switchButtonRect = switchButton.get_rect()

    lightButton = pygame.image.load("gatePics\LIGHTBUTTON.png")
    lightButtonRect = lightButton.get_rect()

    clockButton = pygame.image.load("gatePics\CLOCKBUTTON.png")
    clockButtonRect = clockButton.get_rect()

    truthTableButton = pygame.image.load("gatePics\TRUTHTABLEBUTTON.png")
    truthTableButtonRect = truthTableButton.get_rect()
    
    timingButton = pygame.image.load("gatePics\TIMINGBUTTON.png")
    timingButtonRect = timingButton.get_rect()
    

    #Main Loop
    while True:
        width,height = size
        selectRect.midtop = (width/2,0)
        lineButtonRect.midleft = (0, height/2 -150)
        switchButtonRect.midleft = (0, height/2 -75)
        lightButtonRect.midleft = (0, height/2 +75)
        clockButtonRect.midleft = (0, height/2)
        truthTableButtonRect.midleft = (0, height/2 +150)
        timingButtonRect.midleft = (0, height/2 +225)

        
        #Get Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                for process in childProcesses:
                    process.terminate()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                size = event.size
                screen=pygame.display.set_mode(size,HWSURFACE|DOUBLEBUF|RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                tempbuttons = [0,0,0]
                if(event.button <4):
                    tempbuttons[event.button-1] = 1
                    mouseKey = tuple(tempbuttons)
                    clickCoords = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if drawingLine == 3:
                    drawingLine = 1
                tempbuttons = [0,0,0]
                if(event.button <4):
                    tempbuttons[event.button-1] = 0
                    mouseKey = tuple(tempbuttons)
                if(Distance(clickCoords, event.pos)<10):  
                    Click(clickCoords)
            if event.type == pygame.MOUSEMOTION: 
                mouseX,mouseY = event.pos
                mouseKey = event.buttons
                
        #Move gate/switch if cursor clicks&drags     
        if draggingObject and not drawingLine:
            draggingObject[1].topleft = mouseX - clickOffset[0] , mouseY - clickOffset[1] 
        elif mouseKey[0] == 1:
            for target in loadedGates+loadedSwitches+loadedLights+loadedClocks:
                if target[1].collidepoint(mouseX,mouseY):
                    #maybe draw a line instead
                    if drawingLine and drawingLine!=3:
                        drawingLine = makeLine(mouseX,mouseY,target,drawingLine)                   
                    else:
                        clickOffset = mouseX-target[1].left , mouseY-target[1].top
                        draggingObject = target
        if mouseKey[0] == 0 and draggingObject:
            if draggingObject and selectRect.collidepoint(draggingObject[1].center):
                Delete(draggingObject)
            draggingObject = None
        
        #Right Click
        if mouseKey[2] == 1:
            #Delete any partially drawn line and stop drawing new lines
            if drawingLine == 1 or drawingLine == 2:
                if loadedLines and not loadedLines[-1][1]:
                    loadedLines.pop()
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
                drawingLine = False
                continue
            #Delete existing line
            for line in loadedLines:
                if IsBetween(line[0][2],line[1][2],(mouseX,mouseY)):
                    DeleteLine(line)
            #Delete gate, light, or switch
            for object in loadedGates+loadedLights+loadedSwitches+loadedClocks:
                if object[1].collidepoint(mouseX,mouseY):
                    Delete(object)
        
        if mouseKey[0] == 1 and not draggingObject and not drawingLine:
            #Spawn new gates
            if selectRect.collidepoint(mouseX,mouseY):
                select = (mouseX-selectRect.left)/(selectRect.width/7) 
                select = int(math.floor(select))
                newGate = makeGate(gateNames[select])
                clickOffset = newGate[1].width/2,newGate[1].height/2
                loadedGates.append(newGate)
                draggingObject = newGate
            #Spawn lines between components
            if lineButtonRect.collidepoint(mouseX,mouseY):
                drawingLine = 1
                pygame.mouse.set_cursor(*pygame.cursors.diamond)
            #Spawn switches
            if switchButtonRect.collidepoint(mouseX,mouseY):
                loadedSwitches.append(makeSwitch())
            #Spawn lights
            if lightButtonRect.collidepoint(mouseX,mouseY):
                loadedLights.append(makeLight())
            #Spawn Clock
            if clockButtonRect.collidepoint(mouseX,mouseY):
                loadedClocks.append(makeClock())  
        
        #Start Drawing
        screen.fill(white) 
        #draw selection bar & buttons
        screen.blit(gateSelect,selectRect)   
        screen.blit(lineButton,lineButtonRect)  
        screen.blit(switchButton,switchButtonRect)     
        screen.blit(lightButton,lightButtonRect)
        screen.blit(clockButton,clockButtonRect)
        screen.blit(truthTableButton,truthTableButtonRect)
        screen.blit(timingButton,timingButtonRect)
        #draw all gates, switches & Lines
        for target in loadedGates+loadedSwitches+loadedLights+loadedClocks:
            screen.blit(target[0], target[1])  
        #draw all switches & IDs
        for switch in loadedSwitches:
            screen.blit(switch[0],switch[1])
            switchID = font.render('S'+str(switch[5]), True, black)
            screen.blit(switchID, (switch[1].x, switch[1].y+30))
        #draw all lights & IDs
        for light in loadedLights:
            screen.blit(light[0],light[1])
            lightID = font.render('L'+str(light[5]), True, black)
            screen.blit(lightID, (light[1].x, light[1].y+30))
        #draw and update all lines
        if draggingObject or drawingLine:
            PositionLines()
        for line in loadedLines:
            color = red if line[4] else lightRed
            pygame.draw.line(screen, color, line[0][2], line[1][2], 2)
        #update clocks
        if loadedClocks:
            UpdateClocks()
        
        #draw text
        #info1 = font.render("MousePos: "+str(mouseX) + ", "+str(mouseY), False, black)
        #info2 = font.render(str(size)+', ' +  str(width) + ', ' + str(height), False, black)
        #info3 = font.render("MouseKey:" + str(mouseKey), False, black)
        #screen.blit(info1, (0, height-40))
        #screen.blit(info2, (0, height-40))
        #screen.blit(info3, (0, height-20))
        
        #Update Screen
        pygame.display.flip()
        pygame.time.wait(10)
        
if __name__ == '__main__':
    Main()

    
    