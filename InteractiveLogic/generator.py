import sys, pygame, math
import subprocess
from multiprocessing import Process, Pipe
from pygame.locals import *
from gates import Evaluate
from datetime import datetime

global white,black, green, red
white = 255, 255, 255
black = 0,0,0
red = 255,0,0
green = 0,255,0

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
        pygame.time.wait(100)

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
        pygame.time.wait(100)


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
    size = width, height = 400,300
    screen=pygame.display.set_mode(size,HWSURFACE|DOUBLEBUF)

    dataPoints = []
    windowSize = 1

    startIndex = 0
    timeOnScreen = 20

    while True:
        size = width,height

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        font=pygame.font.Font(None,30)

        if(mainProgram.poll()):
            #response = [loadedSwitches,loadedClocks,loadedLights]
            response = mainProgram.recv()

            inputs = [(switch[5],switch[4]) for switch in response[0]]
            clocks = [(clock[5],clock[4]) for clock in response[1]]
            outputs = [(light[5],light[4]) for light in response[2]]

            #Each datapoint = [timestamp, [(componentId,True/False),...]]
            data = [datetime.utcnow(),inputs+outputs+clocks]
            dataPoints.append(data)
            windowSize = len(dataPoints[-1][1])*60

        #print height
        #print windowSize
        if(height != windowSize):
            height = windowSize
            screen=pygame.display.set_mode((width,height),HWSURFACE|DOUBLEBUF)
            #dataPoints = [dataPoints[-1]]
            
        screen.fill(white)

        tempDataPoints = dataPoints + [[datetime.utcnow(),dataPoints[-1][1]]]
        for x in range(len(dataPoints)):
            #print tempDataPoints
            #print startIndex
            timeStampDelta = (datetime.utcnow()-tempDataPoints[x][0]).total_seconds()
            nextTimestampDelta = (datetime.utcnow()-tempDataPoints[x+1][0]).total_seconds()
            if (timeStampDelta > timeOnScreen and startIndex < len(tempDataPoints)-1):
                startIndex+=1
                continue
            else:
                itemPosition = 1
                for i in range(len(tempDataPoints[x][1])):
                    value = tempDataPoints[x][1][i][1]
                    color = green if value else red
                    height = 50*itemPosition if color is red else 50*itemPosition-20
                    startPoint = timeStampDelta*(width/timeOnScreen), height
                    endPoint = nextTimestampDelta*(width/timeOnScreen), height
                    #print startPoint
                    #print endPoint
                    pygame.draw.line(screen, color , startPoint, endPoint ,5)
                    itemPosition+=1


        pygame.time.wait(100)
        pygame.display.flip()
