import sys, pygame, math
import subprocess
from pygame.locals import *
from gates import Evaluate

def FlipSwitches(order,switches):
    for x in range(len(switches)):
        switches[x][4] = True if order[x] == '1' else False
    return switches   

   
def TruthWindow(inputs, outputs): 
    inputs = eval(inputs)
    outputs = eval(outputs)
    
    #print inputs
    #print outputs
    
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
    inputs = []
    outputs = []

    switchNum = len(loadedSwitches)  

    for x in range(2**switchNum):
        outputs.append([])
        for light in loadedLights:
            y = str(bin(x))[2:]
            y = y.zfill(switchNum)
            loadedSwitches = FlipSwitches(y,loadedSwitches)
            
            inputs.append(list(str(y))) 
            
            outputs[x].append(Evaluate(light,loadedLines))
            
    if outputs and inputs:
        subprocess.Popen(['python', 'generator.py', str(inputs), str(outputs)])

if __name__ == '__main__':
    TruthWindow(sys.argv[1],sys.argv[2])
