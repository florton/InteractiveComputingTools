import sys, pygame
pygame.init()

size = width, height = 800, 600
screen = pygame.display.set_mode(size)

white = 255, 255, 255
black = 0,0,0

mouseX,mouseY = 0,0
mouseXR,mouseYR = 0,0
mouseKey = 0;

ball = pygame.image.load("ball.bmp")
ballrect = ball.get_rect()

draggingObject = None
gravity = .05
falling = True

#Main Loop
while True:
    #Get Input Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.MOUSEMOTION: 
            mouseX,mouseY = event.pos
            mouseXR,mouseYR = event.rel
            mouseKey = event.buttons
            
    #Move ball if cursor clicks&drags it
    if mouseKey[0] == 1 and ballrect.collidepoint(mouseX,mouseY):
        draggingObject = ballrect
    if mouseKey[0] == 0:
        draggingObject = None
    
    if draggingObject:
        draggingObject.centerx = mouseX
        draggingObject.centery = mouseY 
        gravity = .05
    else:
        if ballrect.midbottom[1] + gravity < height and falling: 
            gravity = gravity + .05
            ballrect.midbottom = (ballrect.midbottom[0],ballrect.midbottom[1] +gravity)  
        else:
            falling = False
            if gravity >0:
                gravity = gravity - .09
            else:
                falling = True
            ballrect.midbottom = (ballrect.midbottom[0],ballrect.midbottom[1] -gravity)
    screen.fill(white)
    screen.blit(ball, ballrect)
    
    
    # render text
    font=pygame.font.Font(None,30)
    info1 = font.render("MousePos: "+str(mouseX) + ", "+str(mouseY), False, black)
    info2 = font.render("MouseRel: "+str(mouseXR) + ", "+str(mouseYR), False, black)
    info3 = font.render("MouseKey:" + str(mouseKey), False, black)
    screen.blit(info1, (0, 0))
    screen.blit(info2, (0, 20))
    screen.blit(info3, (0, 40))
    
    #Update Screen
    pygame.display.flip()