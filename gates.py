def And(first, second, *args):
    return all((first,second)+args)
    
def Or(first, second, *args):
    return any((first,second)+args)
    
def Not(bool):
    return not bool
   
def Nor(first, second, *args):
    return not Or(first, second, *args)
    
def Nand(first, second, *args):
    return not And(first, second, *args)
    
def Xor(first, second):
    return((first and not second)or(second and not first))
    
def Xnor(first, second):
    return not Xor(first, second)
    
print Not(Or(And(True,False),And(False,True)))

print Nor(False,False,False)

print Nand(True,True,False)

print Xor(False,True)

print Xnor(False,False)