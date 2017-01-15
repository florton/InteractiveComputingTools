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

def ListToArgs(list):
    first = list.pop(0)
    second = list.pop(0)
    args = (first,second) + tuple(list)
    return(args)

linesList = []  
  
def UpdateLine(component,state):
    print component
    for line in linesList:
        print line
        print component
        if str(component[0]) is str(line[0]) and component[1] is line[1]:
            line[3] = state
    
    
def EvaluateLight(light, lines):
    linesList = lines
    print light
    return BuildTree(light),linesList
    
def BuildTree(component):
    name = component[2]
    if name == "LINE":
        connections = [component[0][1]]
    else:
        connections = component[3]
    paths = []
    
    for path in connections:
        result = BuildTree(path)
        paths.append(result)   
        
    if not paths:
        paths = [False]  
    if name == 'LINE':
        state = Or(*paths)
        UpdateLine(component,state)
        return state
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
        
        
        
        
        
        
        
        
        