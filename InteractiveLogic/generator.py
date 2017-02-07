import sys, pygame, math
import subprocess
from multiprocessing import Process
from pygame.locals import *
from gates import Evaluate

def FlipSwitches(order,switches):
    for x in range(len(switches)):
        switches[x][4] = True if order[x] == '1' else False
    return switches   
   
def TruthWindow(inputs, outputs, ids):   
    pygame.init()
    
    white = 255, 255, 255
    black = 0,0,0

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
            outputs[x].append(int(Evaluate(light,loadedLines)))
            
    #put switches back where they were        
    for x in range(len(loadedSwitches)):
        loadedSwitches[x][4] = oldSwitches[x]
    
    #print inputs
    #print outputs
    
    #open truth table window in a new process
    newProcess = Process(target=TruthWindow, args=(inputs,outputs,ids))
    newProcess.start()
    return newProcess


    
