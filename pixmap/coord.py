

class Coord(object):
  '''
  Pair of integers supporting:
  - addition and subtraction
  - referencing by x, y attributes
  
  Similar to vectors, but with fewer operations.
  Also similar to points.
  
  Not typesafe.
  Below, we don't check that other is Coord or int.
  
  All math ops return a new object.
  '''
  
  def __init__(self, x, y):
    assert isinstance(x, int)
    assert isinstance(y, int)
    self.x = x
    self.y = y
    
  def __eq__(self, other):
    return self.x == other.x and self.y == other.y
  
  def __add__(self, other):
    return Coord( self.x + other.x, self.y + other.y )
    
  def __sub__(self, other):
    return Coord( self.x - other.x, self.y - other.y )
  
  def addScalar(self, scalar):
    assert isinstance(scalar, int)
    # Safer would be: return Coord( int(self.x + scalar), int(self.y + scalar) )
    return Coord( self.x + scalar, self.y + scalar )
    
  def toTuple(self):
    return (self.x, self.y)
  
  def __repr__(self):
    ''' 
    Strict representation: as a string that will recreate self as an object when eval()'ed.
    Does NOT represent self as tuple.
    '''
    return "Coord(" + str(self.x) + "," + str(self.y) + ")"
    