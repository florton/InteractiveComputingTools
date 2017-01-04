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

    
def EvaluateLight(light):
    return BuildTree(light)
    
def BuildTree(component):
    name = component[2]
    connections = component[3]
    paths = []
    
    for path in connections:
        result = BuildTree(path)
        paths.append(result)        
    
    if not paths:
        paths = [False]
    
    if type(name) == type(True):
        return name
    elif paths:
        if type(name) == type(1):
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
        
        
        
        
        
        
        
        
        