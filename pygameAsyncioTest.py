import pygame

pygame.init()

blob_yposition=30
blob_yspeed=0
achievement=False

gravity=1

screen_size=640,480
screen=pygame.display.set_mode(screen_size)

clock=pygame.time.Clock()
running=True
flying_frames=0
best=0
color=(50,50,50)
font=pygame.font.SysFont("Helvetica Neue,Helvetica,Ubuntu Sans, Bitstream Vera Sans", 16)

while running:
    clock.tick(30)

    events=pygame.event.get()
    for e in events:
        if e.type==pygame.QUIT:
            running=False
        if e.type==pygame.KEYDOWN and e.key==pygame.K_UP:
            blob_yspeed+=10

    blob_yposition+=blob_yspeed
    blob_yspeed-=gravity

    if blob_yposition<=30:
        blob_yspeed=0
        blob_yposition=30
        flying_frames=0
    else:
        flying_frames+=1

    if flying_frames>best:
        best=flying_frames

    if not achievement and best > 300:
        pygame.time.wait(500)
        print("ACHIEVEMENT UNLOCKED")
        achievement=True
        color=(100,0,0)
    if blob_yposition>480:
        blob_yposition=480
        blob_yspeed=-1*abs(blob_yspeed)

    screen.fill((255,255,255))

    pygame.draw.rect(screen,color,
                     pygame.Rect(screen_size[0]/2,
                                 screen_size[1]-blob_yposition,
                                 18,25))
    fps=clock.get_fps()
    message= f"current:{flying_frames//30},  best:{best//30},   fps:{fps}"
    surf = font.render(message, True, (0,0,0))
    screen.blit(surf, (0,0))
    pygame.display.update()
print("Bye!")
        