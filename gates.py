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
        
def CheckLoop(pathList,id):
    if pathList.count(id) > 1:
        return True
    return False
        
def Evaluate(component):
    pathList = []
    return BuildTree(component,pathList)

def BuildTree(component,pathList):
    name = component[2]
    if name == "LINE":
        connections = [component[0][1]]
        pathList.append(component[3])
        if CheckLoop(pathList, component[3]):
            return False
    else:
        connections = component[3]
    paths = []

    for path in connections:
        result = BuildTree(path,pathList)
        paths.append(result) 
    print name        
    print paths        
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
        
        
        
        
        
        
        
        
        