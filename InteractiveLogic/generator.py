import sys, pygame, math, os
import subprocess
from multiprocessing import Process, Pipe
from pygame.locals import *
from gates import Evaluate, BuildTree
from datetime import datetime

#Extra code for PyInstaller building
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

global white,black, green, red, blue
white = 255, 255, 255
black = 0,0,0
red = 255,0,0
green = 0,255,0
blue = 0,0,255

def FlipSwitches(order,switches):
    for x in range(len(switches)):
        switches[x][4] = True if order[x] == '1' else False
    return switches

def TruthTableError(error):
    newProcess = Process(target=LoadErrorWindow, args=([error]))
    newProcess.start()
    return newProcess

def LoadErrorWindow(error):
    pygame.init()
    pygame.display.set_caption("Error")

    size = width, height = len(error*10)+20 , 50
    screen=pygame.display.set_mode(size)

    while True:
        screen.fill(white)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        font=pygame.font.Font("freesansbold.ttf", 20)
        errorLine = font.render(error, True, black)
        screen.blit(errorLine, (0, 10))

        pygame.display.flip()
        pygame.time.wait(100)

def LoadTruthWindow(inputs, outputs, ids):
    pygame.init()
    pygame.display.set_caption("Truth Table")

    halfWidth = len(inputs[0])*28
    width = halfWidth+len(outputs[0])*28 +65
    height = len(inputs)*30+40 if len(inputs)<9 else 520
    screen=pygame.display.set_mode((width,height))
    font=pygame.font.Font(None,30)

    scrollHeight = 0
    mouseDown = False
    mouseX,mouseY = 0,0

    scrollBarRect = Rect(width-20, 0, 20, height/(len(inputs)/9 if len(inputs)/9 != 0 else 1))

    while True:
        screen.fill(white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and scrollBarRect.collidepoint(mouseX,mouseY):
                mouseDown = True
            if event.type == pygame.MOUSEBUTTONUP:
                mouseDown = False
            if event.type == pygame.MOUSEMOTION:
                mouseX,mouseY = event.pos

        #Draw each I/O line
        for x in range(len(inputs)):
            currentHeight = 30*x+45 - scrollHeight
            # Alternating background bars
            backgroundColor = (200, 200, 200) if x % 2 == 0 else white
            pygame.draw.rect(screen, backgroundColor, (0,currentHeight-5,width,30))

            outputString = "   "
            for y in inputs[x]:
                outputString += y + "   "
            outputString+= "   "
            for z in outputs[x]:
                outputString += str(z) + "   "

            line = font.render(outputString, True, black)
            screen.blit(line, (0, currentHeight))

        #Draw I/O Labels
        screen.fill(white, Rect(0, 0, width, 40) )
        firstLine = "  "
        for input in ids[0]:
            firstLine += "S"+str(input)+" "
        firstLine += "   "
        for output in ids[1]:
            firstLine += "L"+str(output)+ " "

        first = font.render(firstLine, True, black)
        screen.blit(first, (0, 10))
        #second = font.render("".ljust(len(firstLine),'_'), True, black)
        #screen.blit(second, (0, 30))

        #Draw lines & scroll bar
        pygame.draw.line(screen, black, (0, 40), (width,40), 4)
        pygame.draw.line(screen, black, (halfWidth+28, 0) ,(halfWidth+28, height) ,4)

        pygame.draw.rect(screen, (100, 100, 100), Rect(width-20, 0, 20, height))

        pygame.draw.rect(screen, (60, 60, 60), scrollBarRect)

        if mouseDown and mouseY-(scrollBarRect.height/2)>-5 and mouseY+(scrollBarRect.height/2)<height+10:
            scrollBarRect.centery = mouseY
            scrollHeight = (float(scrollBarRect.top)/float(height)) * (len(inputs)*30)
        pygame.display.flip()
        #pygame.time.wait(100)


def GenerateTruthTable(loadedLights,loadedSwitches,loadedLines):
    #save current switch states
    oldSwitches = []
    for switch in loadedSwitches:
        oldSwitches.append(switch[4])

    inputs = []
    outputs = []
    ids = [[input[5] for input in loadedSwitches],[output[5] for output in loadedLights]]
    switchNum = len(loadedSwitches)

    #try simulating all switch combinations
    for x in range(2**switchNum):
        outputs.append([])
        y = str(bin(x))[2:]
        y = y.zfill(switchNum)
        loadedSwitches = FlipSwitches(y,loadedSwitches)
        inputs.append(list(str(y)))
        for light in loadedLights:
            result = BuildTree(light,loadedLines)
            if result is None:
                return TruthTableError("Loop detected, cannot generate truth table");
            outputs[x].append(int(result))

    #put switches back where they were
    for x in range(len(loadedSwitches)):
        loadedSwitches[x][4] = oldSwitches[x]
    #open truth table window in a new process
    newProcess = Process(target=LoadTruthWindow, args=(inputs,outputs,ids))
    newProcess.start()
    return newProcess

def GenerateTimingDiagram():
    #open timing window in a new process
    parentConnection, childConnection = Pipe()
    newProcess = Process(target=LoadTimingWindow, args=(childConnection,))
    newProcess.start()
    return newProcess,parentConnection

def LoadTimingWindow(mainProgram):
    pygame.init()
    pygame.display.set_caption("Timing Diagram")
    size = width, height = 600,300
    screen=pygame.display.set_mode(size,HWSURFACE|DOUBLEBUF|RESIZABLE)
    defaultWidth = 600
    dataPoints = []
    componentCount = [1,1]

    startIndex = 0
    timeOnScreen = 20
    nowTime = datetime.utcnow()

    isPaused = False
    hasClicked = False

    playButton = pygame.image.load(os.path.join(application_path, "gatePics\PLAY.png"))
    pauseButton = pygame.image.load(os.path.join(application_path, "gatePics\PAUSE.png"))
    playPauseButtonRect = playButton.get_rect()

    clearButton = pygame.image.load(os.path.join(application_path, "gatePics\CLEAR.png"))
    clearButtonRect = clearButton.get_rect()

    while True:
        size = width,height

        playPauseButtonRect.midtop = width/2 - 15, 0
        clearButtonRect.midtop = width/2 + 15, 0

        #Pause if window is dragging
        if (datetime.utcnow()-nowTime).total_seconds() > 0.1:
            for dataPoint in dataPoints:
                dataPoint[0] += (datetime.utcnow()-nowTime)
            nowTime = datetime.utcnow()

        nowTime = datetime.utcnow() if not isPaused else nowTime

        #Handle window close & window resize events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainProgram.close()
                sys.exit()
        if event.type == pygame.VIDEORESIZE:
            size = width,height = event.size
            screen=pygame.display.set_mode(size,HWSURFACE|DOUBLEBUF|RESIZABLE)
        if event.type == pygame.MOUSEBUTTONDOWN:
            #Left click
            if event.button == 1:
                if not hasClicked:
                    if playPauseButtonRect.collidepoint(event.pos):
                        isPaused = not isPaused
                    if clearButtonRect.collidepoint(event.pos):
                        dataPoints = [dataPoints[-1]]
                        dataPoints[0][0] = datetime.utcnow()
                hasClicked = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                hasClicked = False

        font=pygame.font.Font(None,30)

        #Get pipe info from main program
        if(mainProgram.poll()):
            #The response  is a list = [loadedSwitches,loadedClocks,loadedLights,parentTimestamp]
            response = mainProgram.recv()
            timeSinceResponse = (nowTime - response[3]).total_seconds()

            if abs(timeSinceResponse) < 0.1 or not dataPoints:
                inputs = [("S"+str(switch[5]),switch[4]) for switch in response[0]]
                clocks = [("C"+str(clock[5]),clock[4]) for clock in response[1]]
                outputs = [("L"+str(light[5]),light[4]) for light in response[2]]

                #Each datapoint is a list = [timestamp, [(componentId,True/False),...]]
                data = [datetime.utcnow(),inputs+outputs+clocks, [len(inputs),len(outputs),len(clocks)]]
                dataPoints.append(data)
                componentCount[1] = len(dataPoints[-1][1])

        #Reset window if number of combonents is changed
        if(componentCount[0] != componentCount[1]):
            height = componentCount[1]*80+30
            componentCount[0] = componentCount[1]
            screen=pygame.display.set_mode((width,height),HWSURFACE|DOUBLEBUF|RESIZABLE)
            dataPoints = [dataPoints[-1]]

        #Draw lines & labels
        screen.fill(white)

        if isPaused:
            screen.blit(playButton,playPauseButtonRect)
        else:
            screen.blit(pauseButton,playPauseButtonRect)

        screen.blit(clearButton, clearButtonRect)

        tempDataPoints = dataPoints + [[datetime.utcnow(),dataPoints[-1][1]]]
        for x in range(len(dataPoints[-1][1])):
            label = font.render(dataPoints[-1][1][x][0], True, black)
            screen.blit(label, (10, (80*x)+20 ))
            if x is data[2][0] or x is data[2][0]+data[2][1]:
                pygame.draw.line(screen, (100, 100, 100), (0,(80*x)+13), (width,(80*x)+13), 4)

        previousRects = {}

        #For each dataPoint recieved from the main program
        for x in range(len(dataPoints)):
            timeStampDelta = (nowTime-tempDataPoints[x][0]).total_seconds()
            nextTimestampDelta = (nowTime-tempDataPoints[x+1][0]).total_seconds()
            if (timeStampDelta > timeOnScreen and startIndex < len(tempDataPoints)-1):
                startIndex+=1
                continue
            else:
                #For each input,clock, or output
                for i in range(len(tempDataPoints[x][1])):
                    value = tempDataPoints[x][1][i][1]
                    color = green if value else red
                    linePos = 80*(i+1) if color is red else 80*(i+1)-30

                    #Draw Green/Red Bars
                    lineThickness = 10
                    startPoint = timeStampDelta*(defaultWidth/timeOnScreen), linePos-(lineThickness/2)
                    endPoint = nextTimestampDelta*(defaultWidth/timeOnScreen), linePos-(lineThickness/2)
                    lineRect = Rect((startPoint[0]+2,startPoint[1]),(endPoint[0]-startPoint[0],lineThickness))
                    pygame.draw.rect(screen, color, lineRect)

                    #Draw Red/Green Transition Lines
                    if i in previousRects.keys():
                        #if transition is from low to high
                        if value:
                            lineColor = red
                            lineStart = lineRect.bottomleft
                            lineEnd = lineStart[0], previousRects[i].topright[1]
                        else:
                            lineColor = green
                            lineStart = previousRects[i].bottomright[0]-1,previousRects[i].bottomright[1]
                            lineEnd = lineStart[0] , lineRect.topleft[1]-0.5
                        if abs(lineStart[1] - lineEnd[1]) >15:
                            pygame.draw.line(screen, lineColor, lineStart, lineEnd, 2)

                    previousRects[i] = lineRect


        #pygame.time.wait(1)
        pygame.display.flip()
