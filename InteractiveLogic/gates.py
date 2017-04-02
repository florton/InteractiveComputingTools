def And(first, second=False, *args):
    return all((first,second)+args)

def Or(first, second=False, *args):
    return any((first,second)+args)

def Nor(first, second=False, *args):
    return not Or(first, second, *args)

def Nand(first, second=False, *args):
    return not And(first, second, *args)

def Xor(first, second=False, *args):
    inputs = list(args)+[first]+[second]
    return(inputs.count(True) == 1)

def Xnor(first, second=False, *args):
    return not Xor(first, second, *args)

def CheckLoop(line,pathList,loadedLines,internalLoop):
    if internalLoop:
        return pathList.count(line[3]) > 1
    elif pathList.count(line[3]) > 1:
        result = Evaluate(line,[],loadedLines,[True,True,True])
        return False if type(result)is bool else result == line[3]

def BuildTree(component,loadedLines):
    return Evaluate(component,[],loadedLines,[True,False,True])

# Options [breakOnLoop,returnNoneOnLoop ,checkFullTree]
def Evaluate(component,pathList=[],loadedLines=[],options=[False,False,False]):
    if not component:
        return False
    name = component[2]

    if name == "LINE":
        connections = [component[0][1]]
        #Check For Loop
        if(options[2]):
            pathList.append(component[3])
            if CheckLoop(component,pathList,loadedLines,options[1]):
                if options[0]:
                    return component[3] if options[1] else None
                currentVal = next((line for line in loadedLines if line[3] == component[3]), None)[4]
                return currentVal
    else:
        connections = component[3]
    paths = []

    if(options[2]):
        for path in connections:
            result = Evaluate(path,pathList,loadedLines,options)
            if type(result) is not bool:
                return result
            paths.append(result)
    else:
        for path in connections:
            try:
                paths.append(path[4])
            except:
                break
    if not paths:
        paths = [False]

    if name == 'LINE':
        return any(paths)
    elif name == 'SWITCH':
        return component[4]
    elif name == 'LIGHT':
        return any(paths)
    elif name == 'NOT':
        return Nor(*paths)
    elif name == 'AND':
        return And(*paths)
    elif name == 'OR':
        return Or(*paths)
    elif name == 'NOR':
        return Nor(*paths)
    elif name == 'NAND':
        return Nand(*paths)
    elif name == 'XOR':
        return Xor(*paths)
    elif name == 'XNOR':
        return Xnor(*paths)
    elif name == 'CLOCK':
        return component[4]
