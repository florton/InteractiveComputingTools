import sys, pygame, math, os
from pygame.locals import *
import pygame.gfxdraw
from gates import Evaluate
from generator import GenerateTruthTable, TruthTableError, GenerateTimingDiagram
from datetime import datetime
from saveload import SaveGame, LoadGame

#Extra code for PyInstaller building
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# A gate is a list [image, rect, gate_name_string, [connections_on_input_anchors], on/off, id]
def makeGate(name):
    gate = gatePics[gateNames.index(name)]
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

# A clock is a list [image, rect, "CLOCK", [dummy_array], on/off, id, freq, deadClickTimestamp]
def makeClock():
    clockRect = clockComponent.get_rect()
    clockRect.center = mouseX,mouseY
    freq = 1
    id = 0 if not loadedClocks else loadedClocks[-1][5]+1
    return([clockComponent, clockRect, "CLOCK", [], False, id, freq, datetime.utcnow()])

# A node is a list [image, rect, "NODE", [dummy_array], on/off, id, count]
def makeNode():
    nodeRect = nodePic.get_rect()
    nodeRect.center = mouseX,mouseY
    id = 0 if not loadedNodes else loadedNodes[-1][5]+1
    return([nodePic,nodeRect,"NODE",[],False,id, 1])

# when a node is clicked "merge" the current line and connected line
# merges node pointers into new line
def connectLines(clickedNode, currentLine):
    parentLine = next(line for line in loadedLines if clickedNode in line[5])
    firstIndex = parentLine[5].index(clickedNode)+1
    for node in parentLine[5][:firstIndex]:
        node[6] += 1
    newLine = [parentLine[0],currentLine[1],"LINE",currentLine[3],False,parentLine[5][:firstIndex]+currentLine[5]]
    return newLine
#A line is a matrix list [[start_target_anchor, start_target , start_coords],
#[end_target_anchor, end_target, end_coords],"LINE" ,id, on/off, [Nodes]]
def makeLine(mouseX,mouseY,target,drawingLine):
    mouseRelativeX = mouseX-target[1].left
    mouseRelativeY = mouseY-target[1].top
    anchor = None
    inputAnchors = [5,0,2,3]
    outputAnchors = [1,4,6]

    # if drawingLine == 1 -> set line start, if == 2 -> set line end,
    # if == 3 -> set drawingLine to 1 on next mouseup
    #check if node
    if target[2] == 'NODE':
        anchor = 7
    #check if switch
    elif target[2] == 'SWITCH':
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
    if anchor == 7:
        for node in loadedNodes:
            if node[1].collidepoint(mouseX,mouseY):
                if drawingLine == 1:
                    id = 0 if not loadedLines else loadedLines[-1][3]+1
                    loadedLines.append([[None,None,None],[None,None,None],"LINE",id,False,[]])
                    loadedLines[-1] = connectLines(node, loadedLines[-1])
                    return 2
                elif drawingLine == 2 and node not in loadedLines[-1][5] and loadedLines[-1][1][0] in inputAnchors:
                    loadedLines[-1] = connectLines(node, loadedLines[-1])
                    loadedLines[-1][1][1][3].append(loadedLines[-1])
                    return 3
    elif drawingLine == 1:
        id = 0 if not loadedLines else loadedLines[-1][3]+1
        if anchor in outputAnchors:
            #make new line with start target info
            loadedLines.append([[anchor,target,(mouseX,mouseY)],[None,None,None],"LINE",id,False,[]])
        elif anchor in inputAnchors:
            #make new line with end target info
            loadedLines.append([[None,None,None],[anchor,target,(mouseX,mouseY)],"LINE",id,False,[]])
    #inputs must connect to outputs and vis versa
    elif ((anchor in inputAnchors and (loadedLines[-1][0][0] in outputAnchors or loadedLines[-1][1][0] in outputAnchors))
        or (anchor in outputAnchors and (loadedLines[-1][0][0] in inputAnchors or loadedLines[-1][1][0] in inputAnchors))):
        if anchor in outputAnchors:
            #add end target info to current (last) line
            loadedLines[-1][0] = [anchor,target,(mouseX,mouseY)]
            #add current line to end target connections array
            loadedLines[-1][1][1][3].append(loadedLines[-1])
        elif anchor in inputAnchors:
            #add start target info to current (last) line
            loadedLines[-1][1] = [anchor,target,(mouseX,mouseY)]
            #add current line to end target connections array
            target[3].append(loadedLines[-1])
        UpdateLogic()
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
    for node in line[5]:
        if node[6] is 1:
            loadedNodes.remove(node)
        else:
            node[6] -= 1
    loadedLines.remove(line)
    UpdateLogic()

def TurnLight(light, bool):
    if bool:
        light[0] = lightOn
        light[4] = True
    else:
        light[0] = lightOff
        light[4] = False

def Click(clickCoords):
    global timingPipe,loadedGates,loadedLines,loadedSwitches,loadedLights
    global loadedClocks, loadedNodes, drawingLine
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
                UpdateLogic()

        #Save current circuit to file
        if saveButtonRect.collidepoint(mouseX,mouseY):
            SaveGame(loadedGates,loadedLines,loadedSwitches,loadedLights,loadedClocks,loadedNodes)

        #Load previous circuit from file
        if loadButtonrect.collidepoint(mouseX,mouseY):
            try:
                result = LoadGame(switchOn,switchOff,lightOn,lightOff,clockComponent,gatePics,nodePic)
                if result:
                    loadedGates = result[0]
                    loadedLines = result[1]
                    loadedSwitches = result[2]
                    loadedLights = result[3]
                    loadedClocks = result[4]
                    loadedNodes = result[5]

                    for process in childProcesses:
                        process.terminate()
                    timingPipe = None
            except:
                childProcesses.append(TruthTableError("Save data could not be loaded, may be corrupted"))

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

            timingPipe = result[1]
            timingPipe.send([loadedSwitches,loadedClocks,loadedLights,datetime.utcnow()])

def PositionLines():
    for line in loadedLines:
        newCoords = [(mouseX,mouseY),(mouseX,mouseY)]
        for x in range(2):
            target = line[x][1]
            offset = target[1].width/10 if target else 0
            anchor = line[x][0]
            #if NOT gate input
            if anchor == 0:
                newCoords[x] = target[1].midleft[0]+offset, target[1].midleft[1]
            #if gate output
            elif anchor == 1:
                    newCoords[x] = target[1].midright[0]-offset, target[1].midright[1]
                #if gate input bottom
            elif anchor == 2:
                    newCoords[x] = target[1].left+offset , target[1].topleft[1] + 3*(target[1].height/4)
                #if gate input top
            elif anchor == 3:
                    newCoords[x] = target[1].left+offset , target[1].topleft[1] + target[1].height/4
                #if clock
            elif anchor == 6:
                    newCoords[x] = target[1].midright
                #if light, switch or node
            elif anchor == 5 or anchor == 4 or anchor == 7:
                    newCoords[x] = target[1].center

        line[0][2] = newCoords[0]
        line[1][2] = newCoords[1]

def UpdateLogic():
    #Run Logic Simulation
    currentInputsOutputs = {}
    for component in loadedGates+loadedLines+loadedClocks+loadedSwitches+loadedLights:
        component[4] = Evaluate(component)
        if component[2] in ["SWITCH","LIGHT","CLOCK"]:
            currentInputsOutputs[component[2]+str(component[5])] = component[4]
    for light in loadedLights:
        TurnLight(light, light[4])

    if childProcesses and timingPipe and previousInputsOutputs != currentInputsOutputs:
        timingPipe.send([loadedSwitches,loadedClocks,loadedLights,datetime.utcnow()])
    return currentInputsOutputs

def UpdateClocks():
    newTime = datetime.utcnow()
    for clock in loadedClocks:
        deltaTime = (newTime-clock[7]).total_seconds()
        if deltaTime >= clock[6]:
            clock[4] = not clock[4]
            clock[7] = newTime
            UpdateLogic()
        screen.blit(clock[0],clock[1])
        clockID = font.render('C'+str(clock[5]), True, black)
        screen.blit(clockID, (clock[1].x+5, clock[1].y+30))

def Main():
    #Initialize variables
    pygame.init()
    pygame.display.set_caption("Interactive Logic")

    global size, width, height, screen

    size = width, height = 1000, 800
    screen=pygame.display.set_mode(size,HWSURFACE|DOUBLEBUF|RESIZABLE)

    global font, black

    font=pygame.font.Font(os.path.join(application_path, "gatePics/freesansbold.ttf"), 20)
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
    global loadedNodes,previousInputsOutputs

    loadedGates = []
    loadedLines = []
    loadedSwitches = []
    loadedLights = []
    loadedClocks = []
    loadedNodes = []

    previousInputsOutputs = {}
    deadClickTimestamp = datetime.min

    global childProcesses, timingPipe

    childProcesses = []
    timingPipe = None

    global gateNames, gatePics, draggingObject, drawingLine

    gateNames = ['AND','OR','NOT','NOR','NAND','XOR','XNOR']
    gatePics = [pygame.image.load(os.path.join(application_path, "gatePics\\" + name + ".png")) for name in gateNames]
    draggingObject = None
    drawingLine = False

    global switchOn,switchOff, lightOn, lightOff, clockComponent, nodePic

    switchOn = pygame.image.load(os.path.join(application_path, "gatePics\SWITCHON.png"))
    switchOff = pygame.image.load(os.path.join(application_path, "gatePics\SWITCHOFF.png"))
    lightOff = pygame.image.load(os.path.join(application_path, "gatePics\LIGHTOFF.png"))
    lightOn = pygame.image.load(os.path.join(application_path, "gatePics\LIGHTON.png"))
    clockComponent = pygame.image.load(os.path.join(application_path, "gatePics\CLOCK.png"))
    nodePic = pygame.image.load(os.path.join(application_path, "gatePics\NODE.png"))

    global gateSelect, gateSelectRect , lineButton , lineButtonRect
    global switchButton, switchButtonRect , lightButton, lightButtonRect
    global clockButton, clockButtonRect
    global timingButton, timingButtonRect, truthTableButton, truthTableButtonRect
    global saveButton, saveButtonRect, loadButton, loadButtonrect

    gateSelect = pygame.image.load(os.path.join(application_path, "gatePics\GATES.png"))
    gateSelectRect = gateSelect.get_rect()

    lineButton = pygame.image.load(os.path.join(application_path, "gatePics\LINE.png"))
    lineButtonRect = lineButton.get_rect()

    switchButton = pygame.image.load(os.path.join(application_path, "gatePics\SWITCHBUTTON.png"))
    switchButtonRect = switchButton.get_rect()

    lightButton = pygame.image.load(os.path.join(application_path, "gatePics\LIGHTBUTTON.png"))
    lightButtonRect = lightButton.get_rect()

    clockButton = pygame.image.load(os.path.join(application_path, "gatePics\CLOCKBUTTON.png"))
    clockButtonRect = clockButton.get_rect()

    truthTableButton = pygame.image.load(os.path.join(application_path, "gatePics\TRUTHTABLEBUTTON.png"))
    truthTableButtonRect = truthTableButton.get_rect()

    timingButton = pygame.image.load(os.path.join(application_path, "gatePics\TIMINGBUTTON.png"))
    timingButtonRect = timingButton.get_rect()

    saveButton = pygame.image.load(os.path.join(application_path, "gatePics\SAVEBUTTON.png"))
    saveButtonRect = saveButton.get_rect()

    loadButton = pygame.image.load(os.path.join(application_path, "gatePics\LOADBUTTON.png"))
    loadButtonrect = loadButton.get_rect()


    #Main Loop
    while True:
        width,height = size
        gateSelectRect.midtop = (width/2,0)

        saveButtonRect.midleft = (0, height/2 -260)
        loadButtonrect.midleft = (0, height/2 -200)

        lineButtonRect.midleft = (0, height/2 -120)
        switchButtonRect.midleft = (0, height/2 - 60)
        clockButtonRect.midleft = (0, height/2)
        lightButtonRect.midleft = (0, height/2 +60)

        truthTableButtonRect.midleft = (0, height/2 +140)
        timingButtonRect.midleft = (0, height/2 +200)

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
                deadClickTimestamp = datetime.utcnow()
            if event.type == pygame.MOUSEMOTION:
                mouseX,mouseY = event.pos
                mouseKey = event.buttons

        #Move component if cursor clicks & drags
        if draggingObject and not drawingLine:
            draggingObject[1].topleft = mouseX - clickOffset[0] , mouseY - clickOffset[1]
        elif mouseKey[0] == 1:
            for target in loadedGates+loadedSwitches+loadedLights+loadedClocks+loadedNodes:
                if target[1].collidepoint(mouseX,mouseY):
                    #maybe draw a line instead
                    if drawingLine and drawingLine!=3:
                        drawingLine = makeLine(mouseX,mouseY,target,drawingLine)
                    else:
                        clickOffset = mouseX-target[1].left , mouseY-target[1].top
                        draggingObject = target
                    deadClickTimestamp = datetime.min
            #Create nodes on double click if drawing a line
            if drawingLine == 2:
                if (datetime.utcnow()-deadClickTimestamp).total_seconds() < 0.2:
                    loadedNodes.append(makeNode())
                    if loadedLines[-1][0][0] is None:
                        loadedLines[-1][5] = [loadedNodes[-1]] + loadedLines[-1][5]
                    else:
                        loadedLines[-1][5].append(loadedNodes[-1])
                    deadClickTimestamp = datetime.min

        #Delete objects released over menu icons
        if mouseKey[0] == 0 and draggingObject:
            if (draggingObject and (gateSelectRect.collidepoint(draggingObject[1].center)
                or draggingObject[1].center[0] < 50)):
                Delete(draggingObject)
            draggingObject = None

        #Hold Right Click
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
                points = [line[0][2]]+[y[1].center for y in line[5]]+[line[1][2]]
                segments = [[points[x], points[x+1]] for x in range(len(points)-1)]
                for seg in segments:
                    if IsBetween(seg[0],seg[1],(mouseX,mouseY)):
                        DeleteLine(line)
            #Delete gate, light, or switch
            for object in loadedGates+loadedLights+loadedSwitches+loadedClocks:
                if object[1].collidepoint(mouseX,mouseY):
                    Delete(object)

        #Hold Left Click
        if mouseKey[0] == 1 and not draggingObject and not drawingLine:
            #Spawn new gates
            if gateSelectRect.collidepoint(mouseX,mouseY):
                select = (mouseX-gateSelectRect.left)/(gateSelectRect.width/7)
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
        screen.blit(gateSelect,gateSelectRect)
        screen.blit(lineButton,lineButtonRect)
        screen.blit(switchButton,switchButtonRect)
        screen.blit(lightButton,lightButtonRect)
        screen.blit(clockButton,clockButtonRect)
        screen.blit(truthTableButton,truthTableButtonRect)
        screen.blit(timingButton,timingButtonRect)
        screen.blit(saveButton,saveButtonRect)
        screen.blit(loadButton,loadButtonrect)
        #draw all gates, switches & Lines
        for target in loadedGates+loadedSwitches+loadedLights+loadedClocks:
            screen.blit(target[0], target[1])
        #draw and update all lines
        if draggingObject or drawingLine:
            PositionLines()
        for line in loadedLines:
            color = red if line[4] else lightRed
            start = line[0][2]
            # Draw line segments between nodes/components
            for x in range(len(line[5])):
                end = line[5][x][1].center
                pygame.draw.line(screen, color, start, end, 6)
                start = end
            end = line[1][2]
            pygame.draw.line(screen, color, start, end, 6)
            #pygame.gfxdraw.line(screen, start[0], start[1], line[1][2][0], line[1][2][1], color)
            #pygame.draw.polygon(screen, color, [start, line[1][2]], 6)
            #pygame.draw.aaline(screen, color, line[0][2], line[1][2])
        #Draw Nodes
        for node in loadedNodes:
            screen.blit(node[0], node[1])
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
        #update clocks
        if loadedClocks:
            UpdateClocks()

        for process in childProcesses:
            if not process.is_alive():
                childProcesses.remove(process)
                timingPipe = None

        #Update Screen
        previousInputsOutputs = UpdateLogic()
        pygame.display.flip()
        pygame.time.wait(1)

if __name__ == '__main__':
    Main()
