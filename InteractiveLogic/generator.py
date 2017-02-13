import sys, pygame, math
import subprocess
from multiprocessing import Process, Pipe
from pygame.locals import *
from gates import Evaluate
from datetime import datetime

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

    size = width, height = len(error*10) , 50
    screen=pygame.display.set_mode(size)

    while True:
        screen.fill(white)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        font=pygame.font.Font(None,30)
        errorLine = font.render(error, True, black)
        screen.blit(errorLine, (0, 10))

        pygame.display.flip()
        #pygame.time.wait(100)

def LoadTruthWindow(inputs, outputs, ids):
    pygame.init()
    pygame.display.set_caption("Truth Table")
    size = width, height = len(inputs[0])*28+len(outputs[0])*28 +55, len(inputs)*50+50
    screen=pygame.display.set_mode(size)

    while True:
        screen.fill(white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        font=pygame.font.Font(None,30)

        #Draw I/O Labels
        firstLine = "  "
        for input in ids[0]:
            firstLine += "S"+str(input)+" "
        firstLine += " | "
        for output in ids[1]:
            firstLine += "L"+str(output)+ " "

        first = font.render(firstLine, True, black)
        screen.blit(first, (0, 20))

        second = font.render("".ljust(len(firstLine),'_'), True, black)
        screen.blit(second, (0, 30))
        #Draw each I/O line

        for x in range(len(inputs)):
            outputString = "   "
            for y in inputs[x]:
                outputString += y + "   "
            outputString+= "|  "
            for z in outputs[x]:
                outputString += str(z) + "   "

            line = font.render(outputString, True, black)

            screen.blit(line, (0, 50*x+60))

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
            result = Evaluate(light,loadedLines,True)
            if result is None:
                return TruthTableError("Loop detected, cannot generate truth table");
            outputs[x].append(int(result))

    #put switches back where they were
    for x in range(len(loadedSwitches)):
        loadedSwitches[x][4] = oldSwitches[x]

    #print inputs
    #print outputs

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

    playButton = pygame.image.load("gatePics\Timing\PLAY.png")
    playPauseButtonRect = playButton.get_rect()

    pauseButton = pygame.image.load("gatePics\Timing\PAUSE.png")

    while True:
        size = width,height

        playPauseButtonRect.midtop = width/2,0

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
                if playPauseButtonRect.collidepoint(event.pos) and not hasClicked:
                    isPaused = not isPaused
                hasClicked = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                hasClicked = False

        font=pygame.font.Font(None,30)

        #Get pipe info from main program
        if(mainProgram.poll()):
            #response = [loadedSwitches,loadedClocks,loadedLights,parentTimestamp]
            response = mainProgram.recv()
            timeSinceResponse = (nowTime - response[3]).total_seconds()
            #print timeSinceResponse

            if abs(timeSinceResponse) < 0.03 or not dataPoints:
                inputs = [("S"+str(switch[5]),switch[4]) for switch in response[0]]
                clocks = [("C"+str(clock[5]),clock[4]) for clock in response[1]]
                outputs = [("L"+str(light[5]),light[4]) for light in response[2]]

                #Each datapoint = [timestamp, [(componentId,True/False),...]]
                data = [datetime.utcnow(),inputs+outputs+clocks]
                dataPoints.append(data)
                #print data
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

        tempDataPoints = dataPoints + [[datetime.utcnow(),dataPoints[-1][1]]]
        for x in range(len(dataPoints[-1][1])):
            label = font.render(dataPoints[-1][1][x][0], True, black)
            screen.blit(label, (10, (80*x)+20 ))

        previousRects = [None for x in range(len(dataPoints[-1][1]))]

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

                    #Draw Blue Transition Lines
                    if previousRects[i]:
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
                            pygame.draw.line(screen, lineColor, lineStart, lineEnd, 1)

                    previousRects[i] = lineRect


        #pygame.time.wait(10)
        pygame.display.flip()
