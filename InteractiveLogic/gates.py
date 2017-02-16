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
        return pathList.count(line[3]) > 2
    elif pathList.count(line[3]) > 2:
        result = BuildTree(line,[],loadedLines,[True,True])
        return False if type(result)is bool else result == line[3]

def Evaluate(component,loadedLines,breakOnLoop = False):
    pathList = []
    return BuildTree(component,pathList,loadedLines,[breakOnLoop,False])

def BuildTree(component,pathList,loadedLines,options):
    if not component:
        return False
    name = component[2]
    if name == "LINE":
        connections = [component[0][1]]
        pathList.append(component[3])
        if CheckLoop(component,pathList,loadedLines,options[1]):
            if options[0]:
                return component[3] if options[1] else None
            currentVal = next((line for line in loadedLines if line[3] == component[3]), None)[4]
            return currentVal
    else:
        connections = component[3]
    paths = []

    for path in connections:
        result = BuildTree(path,pathList,loadedLines,options)
        if type(result) is not bool:
            return result
        paths.append(result)
    if not paths:
        paths = [False]
    if name == 'LINE':
        return Or(*paths)
    elif name == 'SWITCH':
        return component[4]
    elif name == 'LIGHT':
        return Or(*paths)
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
