'''
'''
class Coord(object):
  '''
  Pair of integers supporting:
  - addition and subtraction
  - referencing by x, y attributes
  
  Similar to vectors, but with fewer operations.
  Also similar to points.
  '''
  
  def __init__(self, x, y):
    self.x = x
    self.y = y
    
  def __eq__(self, other):
    return self.x == other.x and self.y == other.y
  
  def __add__(self, other):
    return Coord( self.x + other.x, self.y + other.y )
    
  def __sub__(self, other):
    return Coord( self.x - other.x, self.y - other.y )
  
  def toTuple(self):
    return (self.x, self.y)
  
  def __repr__(self):
    ''' 
    Strict representation: as a string that will recreate self as an object when eval()'ed.
    Does NOT represent self as tuple.
    '''
    return "Coord(" + str(self.x) + "," + str(self.y) + ")"
    