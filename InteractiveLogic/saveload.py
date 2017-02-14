from Tkinter import Tk
import tkFileDialog
import pickle

def SaveGame(loadedGates,loadedLines,loadedSwitches,loadedLights,loadedClocks):
    #gateData =  [None, rect, gate_name_string, [(input_connection_name, id),...], on/off, id]
    gatesData = []
    for gate in loadedGates:
        gatesData.append(None)
        gatesData.append(gate[1])
        gatesData.append(gate[2])
        gatesData.append([(x[2], x[5]) if x[2] != "LINE" else (x[0][1][2], x[0][1][5]) for x in gate[3]])
        gatesData.append(gate[4])
        gatesData.append(gate[5])
    #lineData = [[start_target_anchor, (start_target_name, id) , start_coords],
    #[end_target_anchor, (end_target_name, id), end_coords],"LINE",id,on/off]
    linesData = []
    for line in loadedLines:
        linesData.append([[],[],line[2:]])
        linesData[-1][0] = [line[0][0],(line[0][1][2],line[0][1][5]),line[0][2]]
        linesData[-1][1] = [line[1][0],(line[0][1][2],line[1][1][5]),line[1][2]]
    #switchData =  [None, rect, "SWITCH" , [dummy_array],on/off, id]
    switchData = [[None]+switch[1:] for switch in loadedSwitches]
    #lightsData = [None, rect, "LIGHT", [(input_connection_name, id),...],on/off, id]
    lightsData = []
    for light in loadedLights:
        lightsData.append(None)
        lightsData.append(light[1])
        lightsData.append(light[2])
        lightsData.append([(x[2], x[5]) if x[2] != "LINE" else (x[0][1][2], x[0][1][5]) for x in light[3]])
        lightsData.append(light[4])
        lightsData.append(light[5])
    #clocksData = [None, rect, "CLOCK", [dummy_array], on/off, id, freq, timestamp]
    clocksData = [[None]+clock[1:] for clock in loadedClocks]

    saveData = []
    saveData.append(gatesData)
    saveData.append(linesData)
    saveData.append(switchData)
    saveData.append(lightsData)
    saveData.append(clocksData)

    Tk().withdraw()
    filename = tkFileDialog.asksaveasfilename(**{'defaultextension':'.logic'})
    if filename != '':
        with open(filename, "wb") as f:
            pickle.dump(saveData, f)

def LoadGame():
    #global loadedGates,loadedLines,loadedSwitches,loadedLights,loadedClocks
    #global totalInputOutputCount

    Tk().withdraw()
    filename = tkFileDialog.askopenfilename()
    loadData = []

    if filename != '':
        with open(filename, "rb") as f:
            loadData = pickle.load(f)

        loadedGates = loadData[0]
        loadedLines = loadData[1]
        loadedSwitches = loadData[2]
        loadedLights = loadData[3]
        loadedClocks = loadData[4]
        totalInputOutputCount = loadData[5]
