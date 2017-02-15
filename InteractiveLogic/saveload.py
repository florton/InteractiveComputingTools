from Tkinter import Tk
import tkFileDialog
import pickle

def SaveGame(loadedGates,loadedLines,loadedSwitches,loadedLights,loadedClocks):
    #gateData =  [None, rect, gate_name_string, [(input_connection_name, id),...], on/off, id]
    gatesData = []
    for gate in loadedGates:
        gatesData.append( [None,gate[1],gate[2],[],gate[4],gate[5]])
        #gatesData.append([(x[2], x[5]) if x[2] != "LINE" else (x[0][1][2], x[0][1][5]) for x in gate[3]])

    #lineData = [[start_target_anchor, (start_target_name, id) , start_coords],
    #[end_target_anchor, (end_target_name, id), end_coords],"LINE",id,on/off]
    linesData = []
    for line in loadedLines:
        linesData.append([[],[],line[2],line[3],line[4]])
        linesData[-1][0] = [line[0][0],(line[0][1][2],line[0][1][5]),line[0][2]]
        linesData[-1][1] = [line[1][0],(line[1][1][2],line[1][1][5]),line[1][2]]

    #switchData =  [None, rect, "SWITCH" , [dummy_array],on/off, id]
    switchData = [[None]+switch[1:] for switch in loadedSwitches]

    #lightsData = [None, rect, "LIGHT", [(input_connection_name, id),...],on/off, id]
    lightsData = []
    for light in loadedLights:
        lightsData.append([None,light[1],light[2],[],light[4],light[5]])
        #lightsData.append([(x[2], x[5]) if x[2] != "LINE" else (x[0][1][2], x[0][1][5]) for x in light[3]])

    #clocksData = [None, rect, "CLOCK", [dummy_array], on/off, id, freq, timestamp]
    clocksData = [[None]+clock[1:] for clock in loadedClocks]

    saveData = [gatesData,linesData,switchData,lightsData,clocksData]

    Tk().withdraw()
    filename = tkFileDialog.asksaveasfilename(**{'defaultextension':'.logic'})
    if filename != '':
        with open(filename, "wb") as f:
            pickle.dump(saveData, f)

def lookupComponent(name, componentId,switchData,clocksData,gatesData,lightsData):
    if name == 'SWITCH':
        for switch in switchData:
            if switch[5] == componentId:
                return switch
    elif name == 'LIGHT':
        for light in lightsData:
            if light[5] == componentId:
                return light
    elif name == 'CLOCK':
        for clock in clocksData:
            if clock[5] == componentId:
                return clock
    elif name =='LINE':
        print "Line"
    else:
        for gate in gatesData:
            if gate[2] == name and gate[5] == componentId:
                return gate

    print name, componentId

def LoadGame(switchOn,switchOff,lightOn,lightOff,clockComponent,gatePics):
    gateNames = ['AND','OR','NOT','NOR','NAND','XOR','XNOR']

    Tk().withdraw()
    filename = tkFileDialog.askopenfilename(**{'defaultextension':'.logic'})

    loadData = []
    if filename != '':
        with open(filename, "rb") as f:
            loadData = pickle.load(f)

        #switches
        switchData = [[switchOn if switch[4] else switchOff]+switch[1:] for switch in loadData[2]]
        #clock
        clocksData = [[clockComponent]+clock[1:] for clock in loadData[4]]
        #gates
        print loadData

        gatesData = [[gatePics[gateNames.index(gate[2])]] +gate[1:] for gate in loadData[0]]
        #lights
        lightsData = [[lightOn if light[4] else lightOff]+light[1:] for light in loadData[3]]
        #lines
        linesData = []
        for line in loadData[1]:
            #startTarget
            name1 = line[0][1][0]
            id1 = line[0][1][1]
            startComponent = lookupComponent(name1,id1,switchData,clocksData,gatesData,lightsData)
            #endTarget
            name2 = line[1][1][0]
            id2 = line[1][1][1]
            endComponent = lookupComponent(name2,id2,switchData,clocksData,gatesData,lightsData)

            line[0][1] = startComponent
            line[1][1] = endComponent
            linesData.append(line)
            endComponent[3].append(linesData[-1])

        return [gatesData,linesData,switchData,lightsData,clocksData]
    else:
        return None
