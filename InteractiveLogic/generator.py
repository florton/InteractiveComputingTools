import sys, pygame, math
import subprocess
from multiprocessing import Process
from pygame.locals import *
from gates import Evaluate

def FlipSwitches(order,switches):
    for x in range(len(switches)):
        switches[x][4] = True if order[x] == '1' else False
    return switches   
   
def TruthWindow(inputs, outputs):   
    pygame.init()
    
    white = 255, 255, 255
    black = 0,0,0

    size = width, height = len(inputs[0])*50+50, len(inputs)*50+50
    screen=pygame.display.set_mode(size)
    
    while True:
        screen.fill(white) 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
                
        #draw text
        font=pygame.font.Font(None,30)
        for x in range(len(inputs)):
            outputString = "   "
            for y in inputs[x]:
                outputString += y + " "        
            outputString+= " | "            
            for z in outputs[x]:
                outputString += str(z) + " "
                
            info = font.render(outputString, False, black)

            screen.blit(info, (0, 50*x+25))
        
        pygame.display.flip()
        pygame.time.wait(100)
        
    
def GenerateTruthTable(loadedLights,loadedSwitches,loadedLines):
    #save current switch states
    oldSwitches = []
    for switch in loadedSwitches:
        oldSwitches.append(switch[4])

    inputs = []
    outputs = []
    switchNum = len(loadedSwitches)  
    
    #try simulating all switch combinations
    for x in range(2**switchNum):
        outputs.append([])
        for light in loadedLights:
            y = str(bin(x))[2:]
            y = y.zfill(switchNum)
            loadedSwitches = FlipSwitches(y,loadedSwitches)
            
            inputs.append(list(str(y))) 
            
            outputs[x].append(Evaluate(light,loadedLines))
            
    #put switches back where they were        
    for x in range(len(loadedSwitches)):
        loadedSwitches[x][4] = oldSwitches[x]
    
    #open truth table window in a new process
    newProcess = Process(target=TruthWindow, args=(inputs,outputs))
    newProcess.start()


    
