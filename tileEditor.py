import pygame as p
from math import floor
from copy import deepcopy
import Tkinter, tkFileDialog
root = Tkinter.Tk()
root.withdraw()
p.init()

running = True

tileWidth = 16
tileHeight = 16

mapWidth = 100
mapHeight = 100

camX = 0
camY = 0
scale = 2
uiScale = 2
hand = 1

layerStack = True

file_path = ''
file_path = tkFileDialog.askopenfilename()
if file_path[-3:] != 'png':
    exit()

layers = []
currentLayer = 1

layers.append([-1] * (mapWidth * mapHeight))
layers.append([-1] * (mapWidth * mapHeight))

prevLayers = deepcopy(layers)
prevLayerLists = []
prevLayerListsRedo = []

brush = p.image.load('brush.png')
brushHover = p.image.load('brushHover.png')
square = p.image.load('square.png')
squareHover = p.image.load('squareHover.png')
brushRect = brush.get_rect()
squareRect = square.get_rect()
brushRect.width, brushRect.height = brushRect.width * uiScale, brushRect.height * uiScale
squareRect.width, squareRect.height = squareRect.width * uiScale, squareRect.height * uiScale

(width, height) = (480, 360)
p.display.set_caption('Tile Editor')
font = p.font.Font('Minecraftia-Regular.ttf', 8)

s = p.display.set_mode((width, height), p.RESIZABLE)
clock = p.time.Clock()

middleClick = False
leftClick = False
leftClickPrev = False
rightClick = False
rightClickDown = False
rightClickPrev = False
mouseOffset = (0, 0)
mousePos = (0, 0)

buttonClick = False
buttonHover = False

sDown = False
squareT = False

sDownStart = False

startPos = (0,0)

def drawBox(width, height, filled):
    surf = p.Surface((width, height))
    if(filled):
        surf.fill((41,48,50))
    else:
        surf.fill((0,0,0,0))

    p.draw.rect(surf, (113,58,41), (0, 0, width, height), 1)

    surf.set_at((0, 0), (0,0,0,0))
    surf.set_at((width-1, 0), (0,0,0,0))
    surf.set_at((0, height-1), (0,0,0,0))
    surf.set_at((width-1, height-1), (0,0,0,0))

    p.draw.rect(surf, (10,21,27), (1, 1, width-2, height-2), 1)

    surf.set_at((1, 1), (88,41,24))
    surf.set_at((width-2, 1), (88,41,24))
    surf.set_at((1, height-2), (88,41,24))
    surf.set_at((width-2, height-2), (88,41,24))

    p.draw.lines(surf, (34,30,21), False, ((2, height-3), (2, 2), (width-3, 2)))
    p.draw.lines(surf, (86,92,86), False, ((3, height-3), (width-3, height-3), (width-3, 3)))

    #p.draw.rect(surf, (225,0,225), (3, 3, width-6, height-6))

    return(p.transform.scale(surf, (uiScale * width, uiScale * height)))

def drawButton(textt, x, y):
    global buttonClick
    buttonClick = False
    global buttonHover
    buttonHover = False
    text = font.render(textt, False, (251,175,113))
    width = text.get_width() + 5
    height = text.get_height() + 3

    if textt[-1] == str(currentLayer):
        text = font.render(textt, False, (150,179,174))
    if textt == 'Layer Stack' and layerStack:
        text = font.render(textt, False, (150,179,174))
    if p.Rect(x, y, width * uiScale, height * uiScale).collidepoint(mousePos[0], mousePos[1]):
        text = font.render(textt, False, (150,179,174))
        buttonHover = True
        if leftClick:
            y += uiScale
            if not leftClickPrev:
                buttonClick = True
    surf = p.Surface((width, height), p.SRCALPHA)
    surf.fill((41,48,50))

    surf.blit(text, (3, 1))

    p.draw.rect(surf, (113,58,41), (0, 0, width, height), 1)

    surf.set_at((0, 0), (0,0,0,0))
    surf.set_at((width-1, 0), (0,0,0,0))
    surf.set_at((0, height-1), (0,0,0,0))
    surf.set_at((width-1, height-1), (0,0,0,0))

    p.draw.rect(surf, (10,21,27), (1, 1, width-2, height-2), 1)

    surf.set_at((1, 1), (88,41,24))
    surf.set_at((width-2, 1), (88,41,24))
    surf.set_at((1, height-2), (88,41,24))
    surf.set_at((width-2, height-2), (88,41,24))

    p.draw.lines(surf, (34,30,21), False, ((2, height-3), (2, 2), (width-3, 2)))
    p.draw.lines(surf, (86,92,86), False, ((3, height-3), (width-3, height-3), (width-3, 3)))

    s.blit(p.transform.scale(surf, (uiScale * width, uiScale * height)), (x, y))


tiles = []
sheetHeight = 0
sheetWidth = 0
def load_sheet(path):
    global tiles
    global sheetHeight
    global sheetWidth
    sheet = p.image.load(path)
    if sheet.get_width() >= tileWidth and sheet.get_height() >= tileHeight:
        tiles = []
        sheetWidth = sheet.get_width()
        sheetHeight = sheet.get_height()
        for y in range(sheetHeight // tileHeight):
            for x in range(sheetWidth // tileWidth):
                image = p.Surface((tileWidth, tileHeight), p.SRCALPHA)
                image.blit(sheet, (0, 0), (x * tileWidth, y * tileHeight, tileWidth, tileHeight))
                tiles.append((image, x * tileWidth, y * tileHeight))

load_sheet(file_path)

while running:
    windowResize = False
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False
        elif event.type == p.MOUSEMOTION:
            mousePos = p.mouse.get_pos()
        elif event.type == p.MOUSEBUTTONDOWN:
            mousePos = p.mouse.get_pos()
            if event.button == 2:
                mouseOffset = (mousePos[0] - camX, mousePos[1] - camY);
                middleClick = True
            elif event.button == 1:
                leftClick = True
            elif event.button == 3:
                rightClick = True
                rightClickDown = True
        elif event.type == p.MOUSEBUTTONUP:
            if event.button == 2:
                middleClick = False
            elif event.button == 1:
                leftClick = False
            elif event.button == 3:
                rightClick = False
        elif event.type == p.MOUSEWHEEL and not middleClick:
            scale += event.y
            if(scale < 1):
                scale = 1
        elif event.type == p.VIDEORESIZE:
            width = event.w
            height = event.h
            windowResize = True
        elif event.type == p.KEYDOWN:
            if event.key == p.K_z and p.key.get_mods() & p.KMOD_CTRL:
                if len(prevLayerLists) != 0:
                    prevLayerListsRedo.append(layers)
                    layers = prevLayerLists[-1]
                    del prevLayerLists[-1]
            elif event.key == p.K_y and p.key.get_mods() & p.KMOD_CTRL:
                if len(prevLayerListsRedo) != 0:
                    prevLayerLists.append(layers)
                    layers = prevLayerListsRedo[-1]
                    del prevLayerListsRedo[-1]
            elif event.key == p.K_s:
                sDown = True

        elif event.type == p.KEYUP:
            if event.key == p.K_s:
                sDown = False

    prevLayers = deepcopy(layers)
    if middleClick:
        camX, camY = mousePos[0] - mouseOffset[0], mousePos[1] - mouseOffset[1]

    x = int(round((mousePos[0] - camX) / (tileWidth * scale)))
    y = int(round((mousePos[1] - camY) / (tileHeight * scale)))
    layers[0][(y * mapWidth) + x] = hand

    if leftClick and not sDownStart:
        if(mousePos[0] > (9 * uiScale) and mousePos[0] < (sheetWidth + 9) * uiScale and mousePos[1] > (9 * uiScale) and mousePos[1] < (sheetHeight + 9) * uiScale):
            x = int(round((mousePos[0] - (9 * uiScale)) / (tileWidth * uiScale)))
            y = int(round((mousePos[1] - (9 * uiScale)) / (tileHeight * uiScale)))
            hand = (y * (sheetWidth // (tileWidth))) + x
        else:
            if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                layers[currentLayer][(y * mapWidth) + x] = hand
    elif rightClick and not sDown:
        if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
            layers[currentLayer][(y * mapWidth) + x] = -1

    s.fill((41,48,50))
    renderList = []
    for i in range(0, len(layers)):
        if not i == 0:
            for x in range(mapWidth):
                for y in range(mapHeight):
                    if (x * tileWidth * scale) + camX > tileWidth * -scale and (x * tileWidth * scale) + camX < width and (y * tileHeight * scale) + camY > tileHeight * -scale and (y * tileHeight * scale) + camY < height:
                        tile = layers[0][y * mapWidth + x]
                        if not layerStack:
                            if i == currentLayer and tile != -1 and not [x,y] in renderList:
                                renderList.append([x,y])
                                s.blit(p.transform.scale(tiles[tile][0], (tileWidth * scale, tileHeight * scale)), ((x * tileWidth * scale) + camX, (y * tileHeight * scale) + camY))
                            else:
                                tile = layers[i][y * mapWidth + x]
                            if not [x,y] in renderList:
                                if tile == -1 and i == currentLayer:
                                    if uiScale >= scale:
                                        p.draw.rect(s, (86,92,86), p.Rect((x * tileWidth * scale) + camX, (y * tileHeight * scale) + camY, tileWidth * scale, tileHeight * scale), 1)
                                    else:
                                        p.draw.rect(s, (86,92,86), p.Rect((x * tileWidth * scale) + camX, (y * tileHeight * scale) + camY, tileWidth * scale, tileHeight * scale), uiScale)
                                elif tile != -1:
                                    renderList.append([x,y])
                                    s.blit(p.transform.scale(tiles[tile][0], (tileWidth * scale, tileHeight * scale)), ((x * tileWidth * scale) + camX, (y * tileHeight * scale) + camY))
                        else:
                            if i == currentLayer and tile != -1:
                                renderList.append([x,y,tile])
                            else:
                                tile = layers[i][y * mapWidth + x]
                            if tile == -1 and i == currentLayer:
                                if uiScale >= scale:
                                    p.draw.rect(s, (86,92,86), p.Rect((x * tileWidth * scale) + camX, (y * tileHeight * scale) + camY, tileWidth * scale, tileHeight * scale), 1)
                                else:
                                    p.draw.rect(s, (86,92,86), p.Rect((x * tileWidth * scale) + camX, (y * tileHeight * scale) + camY, tileWidth * scale, tileHeight * scale), uiScale)
                            elif tile != -1:
                                renderList.append([x,y,tile])
    if layerStack:
        for i in range(len(renderList)-1, 0, -1):
            s.blit(p.transform.scale(tiles[renderList[i][2]][0], (tileWidth * scale, tileHeight * scale)), ((renderList[i][0] * tileWidth * scale) + camX, (renderList[i][1] * tileHeight * scale) + camY))


    i = sheetHeight + int(tileHeight * 1.5 + 12)
    s.blit(drawBox(sheetWidth + 12, i, True), (3 * uiScale, 3 * uiScale))
    drawButton('New Layer', 3 * uiScale, (i + 6) * uiScale)

    if buttonClick:
        layers.append([-1] * (mapWidth * mapHeight))
        currentLayer = len(layers)-1

    for layer in range(0, len(layers)-1):
        drawButton('Layer ' + str(layer + 1), 3 * uiScale, (i + 26 * (layer + 1)) * uiScale)
        if buttonClick:
            currentLayer = layer + 1
        if buttonHover and rightClickDown and len(layers) > 2:
            prevLayerLists.append(deepcopy(layers))
            del layers[layer + 1]
            if currentLayer > len(layers) - 1:
                currentLayer -= 1
            prevLayers = layers

    for image in tiles:
        s.blit(p.transform.scale(image[0], (tileWidth * uiScale, tileHeight * uiScale)), ((image[1] + 9) * uiScale, (image[2] + 9) * uiScale))

    s.blit(p.transform.scale(tiles[hand][0], (tileWidth * uiScale, tileHeight * uiScale)), (9 * uiScale, (sheetHeight + tileHeight) * uiScale))

    drawButton('Open Tilesheet', (sheetWidth + 18) * uiScale, 3 * uiScale)
    if buttonClick:
        file_path = tkFileDialog.askopenfilename()
        if file_path[-3:] == 'png':
            load_sheet(file_path)

    drawButton('Layer Stack', (sheetWidth + 18) * uiScale, 23 * uiScale)
    if buttonClick:
        layerStack = not layerStack

    layers[0] = [-1] * (mapWidth * mapHeight)
    if not leftClick and leftClickPrev and sDownStart:
        sDownStart = False
        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) + 1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) + 1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[currentLayer][(y * mapWidth) + x] = hand

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) - 1, -1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) - 1, -1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[currentLayer][(y * mapWidth) + x] = hand

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) + 1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) - 1, -1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[currentLayer][(y * mapWidth) + x] = hand

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) - 1, -1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) + 1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[currentLayer][(y * mapWidth) + x] = hand


    elif leftClick and sDownStart:
        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) + 1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) + 1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[0][(y * mapWidth) + x] = hand

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) - 1, -1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) - 1, -1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[0][(y * mapWidth) + x] = hand

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) + 1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) - 1, -1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[0][(y * mapWidth) + x] = hand

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) - 1, -1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) + 1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[0][(y * mapWidth) + x] = hand


    if not rightClick and rightClickPrev and sDownStart:
        sDownStart = False
        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) + 1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) + 1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[currentLayer][(y * mapWidth) + x] = -1

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) - 1, -1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) - 1, -1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[currentLayer][(y * mapWidth) + x] = -1

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) + 1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) - 1, -1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[currentLayer][(y * mapWidth) + x] = -1

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) - 1, -1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) + 1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[currentLayer][(y * mapWidth) + x] = -1


    elif rightClick and sDownStart:
        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) + 1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) + 1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[0][(y * mapWidth) + x] = -2

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) - 1, -1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) - 1, -1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[0][(y * mapWidth) + x] = -2

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) + 1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) - 1, -1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[0][(y * mapWidth) + x] = -2

        for x in range(startPos[0], int(round((mousePos[0] - camX) / (tileWidth * scale))) - 1, -1):
            for y in range(startPos[1], int(round((mousePos[1] - camY) / (tileHeight * scale))) + 1):
                if(mousePos[0] > camX and mousePos[0] < camX + ((tileWidth * scale) * mapWidth) and mousePos[1] > camY and mousePos[1] < camY + ((tileHeight * scale) * mapHeight)):
                    layers[0][(y * mapWidth) + x] = -2

    if leftClick and not leftClickPrev or rightClick and not rightClickPrev:
        if sDown:
            sDownStart = True
        startPos = (int(round((mousePos[0] - camX) / (tileWidth * scale))), int(round((mousePos[1] - camY) / (tileHeight * scale))))
        if prevLayers != layers:
            prevLayerLists.append(deepcopy(prevLayers))
    leftClickPrev = leftClick
    backDown = False
    rightClickDown = False

    brushRect.x,brushRect.y = (sheetWidth + 18) * uiScale, 43 * uiScale
    if brushRect.collidepoint(mousePos[0], mousePos[1]) or not squareT:
        if leftClick and brushRect.collidepoint(mousePos[0], mousePos[1]):
            squareT = False
            sDown = False
            s.blit(p.transform.scale(brushHover, (brushRect.width, brushRect.height)), (brushRect.x, brushRect.y + uiScale))
        else:
            s.blit(p.transform.scale(brushHover, (brushRect.width, brushRect.height)), brushRect)
    else:
        s.blit(p.transform.scale(brush, (brushRect.width, brushRect.height)), brushRect)

    squareRect.x,squareRect.y = (sheetWidth + 34) * uiScale, 43 * uiScale
    if squareRect.collidepoint(mousePos[0], mousePos[1]) or squareT:
        if leftClick and squareRect.collidepoint(mousePos[0], mousePos[1]):
            squareT = True
            s.blit(p.transform.scale(squareHover, (squareRect.width, squareRect.height)), (squareRect.x, squareRect.y + uiScale))
        else:
            s.blit(p.transform.scale(squareHover, (squareRect.width, squareRect.height)), squareRect)
    else:
        s.blit(p.transform.scale(square, (squareRect.width, squareRect.height)), squareRect)
    if squareT:
        sDown = True

    rightClickPrev = rightClick
    p.display.update()
    clock.tick(60)
