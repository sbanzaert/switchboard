import math

def rToL(a: int,b: int ):
    return list(range(a,b))


######
### MIDI track parameters
######
jackStart = 0
jackEnd = 30
switchStart = 30
switchEnd = 38
crankPitch = 38
leadInSkip = 40
leadOutSkip = 80
testPointPitch = 127

jackRange = range(jackStart,jackEnd)
switchRange = range(switchStart, switchEnd)
jackInRange = range(jackStart+leadInSkip, jackEnd+leadInSkip)
jackOutRange = range(jackStart+leadOutSkip, jackEnd+leadOutSkip)
switchInRange = range(switchStart + leadInSkip, switchEnd + leadInSkip)
switchOutRange = range(switchStart + leadOutSkip, switchEnd + leadOutSkip)

bellPitch = 127
alarmPitch = 20
hornPitch = 40

#GPIO readings for inputs
jackPlugged = True
switchUp = False
switchDown = True

### pixel addresses indicating wired switches
### same ordering as pinState via orderMcpN
activePanel1 = ( 0, 2, 5, 8, 9,94,92,89,87,86) ## pinState0
activePanel2 = (18,20,22,25,26,77,74,73,71,69)
activePanel3 = (34,36,37,41,43,60,57,56,53,52)
activePanels = (activePanel1, activePanel2, activePanel3)

activeSwitch1top=(104,105,109,112)
activeSwitch1bot=(158,157,153,150)
activeSwitch2top=(120,122,123,124)
activeSwitch2bot=(144,142,141,136)
activeSwitchTops = (activeSwitch1top, activeSwitch2top)
activeSwitchBots = (activeSwitch1bot, activeSwitch2bot)
activeSwitches = (activeSwitchTops, activeSwitchBots)

allJack1 = rToL(0,10) + rToL(86,95)[::-1]
allJack2 = rToL(17,27) + rToL(68,78)[::-1]
allJack3 = rToL(34,44) + rToL(51,61)[::-1]
allSwitch1top = rToL(103,113)
allSwitch2top = rToL(120,130)
allSwitch1bot = rToL(150,160)[::-1]
allSwitch2bot = rToL(135,145)[::-1]
allSwitchTops = allSwitch1top + allSwitch2top
allSwitchBots = allSwitch1bot + allSwitch2bot

color = {'red': (255,0,0), 'green': (0,255,0), 'off': (0,0,0), 'amber': (255,120,0)}
##########
#### i2c GPIO parameters
##########

orderMcp0 = [0,1,2,3,4,8,9,10,11,12,5,6,13,14] # {jacks 0-9} {switches 0-3} - 7 & 15 not used, 14 reserved for hand crank
orderMcp1 = [0,1,2,3,4,8,9,10,11,12,5,6,13,14] # {jacks 0-9} {switches 0-3}
orderMcp2 = [0,1,2,3,4,8,9,10,11,12,5,6,13,14] # {jacks 0-9} {switches 0-3} {hand crank}
mcpOrders = (orderMcp0, orderMcp1, orderMcp2)


def returnFirstElement(a):
    return a[0]
        
def getOrderedPinState(pinArray, pinOrderArray):
    pinState=[]
    for p in range(15):
        # print("p: {} ps0: {}".format(p, pinState0[p])) # get pins in order 0-15 {PORTA}{PORTB}
        if p in range(0,5) or p in range(0+8, 5+8):
            pinState.append(pinArray[p].value) # True = plugged in, need to check switches
        elif p in range(5,7) or p in range(5+8, 7+8):
            pinState.append(pinArray[p].value == False) # switches are active FALSE
    pinState = [pinState[i] for i in pinOrderArray]
    return pinState

def getStructuredGPIO(GPIOarray):
    out = []
    for s in range(len(GPIOarray)):
        out.append(getOrderedPinState(GPIOarray[s],mcpOrders[s]))
    return out

def jackLEDFromNote(pitch: int):    # can only access LEDs attached to wired switches
    if pitch in jackRange:
        bank = math.floor((pitch-jackStart)/10)
        return activePanels[bank][pitch % 10]
    else:
        return 0

def switchLEDFromNote(pitch: int, dir: str):
    dirs = {'up': 0, 'down': 1}
    if pitch in switchRange:
        bank = math.floor((pitch-switchStart)/4)
        return activeSwitches[dirs[dir]][bank][(pitch-switchStart) % 4]
    else:
        return 0



def updateScore(score, data, targets): # 
    if (len(data) != len(targets)):
        print("data {} and target {} length mismatch!".format(len(data), len(targets)))
        return
    for i in range(len(data)):
        if (len(data[i]) != len(targets[i])):
            print("data {} and target {} inner length mismatch on index {}!".format(len(data[i]), len(targets[i]),i))
            return
        for j in range(len(data[i])):
            if (data[i][j] == True and targets[i][j] == True):
                score = score + correct
            if (data[i][j] == True and targets[i][j] == False):
                score = score + incorrect
            if (data[i][j] == False and targets[i][j] == True):
                score = score + incorrect
    return score




#########################################
## DEFUNCT table descriptions - accurate but not needed
#########################################

# n0 = rToL(0,10) + rToL(85,95)[::-1] #segments 1 and 6, left jack panel
# n1 = rToL(17,27) + rToL(68,78)[::-1] #segments 2 and 5, center jack panel
# n2 = rToL(34,44) + rToL(51,61)[::-1] #segments 3 and 4, right jack panel
# n3 = rToL(103,113) # segments 7 & 10, left switch panel, seg 10 currently not built
# n4 = rToL(120,130) + rToL(135,145)[::-1] # segments 8 & 9, right switch panel
# # actually-wired switches:
# panel0 = (0,0,1,1,0,
#           1,0,0,1,1)
# panel1 = (0,0,1,1,0,
#           1,0,0,1,1)
# panel2 = (0,0,1,1,0,
#           1,0,0,1,1)
# panel3 = (0,0,1,1,0,
#           1,0,0,1,1) # panels 3 and 4 need to be in format 0a0b0a0b or 0ab00ab0 etc
# panel4 = (0,0,1,1,0,
#           1,0,0,1,1)

# switchPanelLEDskip = 4 # 4 switches per panel, skip ahead 4 spots to get to lower LED

# panel0Active = [panel0[i] * n0[i] for i in len(n0)]
# panel0Active = [i for i in panel0Active if i != 0]
# panel1Active = [panel1[i] * n1[i] for i in len(n1)]
# panel1Active = [i for i in panel1Active if i != 0]
# panel2Active = [panel2[i] * n2[i] for i in len(n2)]
# panel2Active = [i for i in panel2Active if i != 0]
# panel3Active = [panel3[i] * n3[i] for i in len(n3)]
# panel3Active = [i for i in panel3Active if i != 0]
# panel4Active = [panel4[i] * n4[i] for i in len(n4)]
# panel4Active = [i for i in panel4Active if i != 0]
# panelsActive = (panel0Active, panel1Active, panel2Active, panel3Active, panel4Active)

# panels = (nA, nB, nC, nD, nE)

# allLights = rToL(0,10) + rToL(17,27) + rToL(34,44) + rToL(51,61) + rToL(68,78) + rToL(85,95) + rToL(103,113) + rToL(120,130) + rToL(135,145)
# skips = list(range(10,17)) + list(range(27,34)) + list(range(44,51)) + list(range(61,68)) + list(range(78,85))+list(range(95,103))+list(range(113,120))+list(range(130,135))

# def ledFromPanel(panelNo: int, pos: int): # this can access all LEDs on the board
#     if (panelNo > 4):return 0
#     if (panelNo == 3 and pos > 9): return 0
#     if (pos > 19): return 0
#     return panels[panelNo][pos]

# def targetFromNote(pitch: int):
#     if (pitch in range(jackStart,jackEnd)):
#         bank = math.floor((pitch-leadInSkip)/10)
#         return bank, pitch % 10
#     if (pitch in range(switchStart, switchEnd)):
#         bank = math.floor((pitch-leadInSkip)/10)-3
#         return bank, 10+ pitch % 10
#     return 0,0