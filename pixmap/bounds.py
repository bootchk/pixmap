


class Bounds():
  '''
  2D bounds.
  
  A Bounds is a specification for a rectangular area in a Map.  IE a subrect of a rect.
  
  Compare to Rect, which is just slightly different:
  specifies the left and right sides by width and height instead of a Coord(lrx, lry)
  
  Compare to a Map, which CAN specify an irregular shape (using its mask.)
  A Map implements the Bounds API.
  
  !!! This differs from the GIMP notion of bounds, 
  which gives the coords of the pixel OUTSIDE the lower right corner as the lower right bounds.
  Here, the lower right bound is the coords of the lower right pixel INSIDE the region.
  
  Most arguments are type Coord, not tuple (x,y), but they can be named tuples with field names x, y
  
  Responsible for:
    clipping given wild Coord, i.e. isInBounds()
    knowing range of X and Y
    knowing width and height
    normalizing self to Bounds with origin at 0,0
    
  
  
  Examples:
  To test: python -m doctest -v bounds.py
  
  Test setup
  >>> from coord import Coord
  >>> a = Bounds(1,1, 3,3)
  >>> b = a.getNormalizedBounds()
  >>> c = Bounds.initFromGIMPBounds(1,1,3,3)
  
  >>> a.isInBounds(Coord(0,0))
  False
  >>> a.isInBounds(Coord(1,1))
  True
  >>> b.isInBounds(Coord(0,0))
  True
  >>> c.isInBounds(Coord(0,0))
  False
  >>> a.isInBounds(Coord(3,3))
  True
  >>> b.isInBounds(Coord(3,3))
  False
  >>> c.isInBounds(Coord(3,3))
  False
  
  >>> a.rangeX()
  [1, 2, 3]
  
  >>> b.rangeX()
  [0, 1, 2]
  
  >>> a.width
  3
  
  >>> d=Bounds(1,1, 1,1)
  >>> d=Bounds(1,1, 0,0)
  Traceback (most recent call last):
    ...
  AssertionError: LRX > ULX
  
  '''
  
  def __init__(self, ulx, uly, lrx, lry):
    ''' NOT a GIMP bounds !!! Different from GIMP notion of lower right. '''
    
    '''
    UL is less than or equal to LR, i.e. origin is northwest of UL
    '''
    assert ulx <= lrx, "LRX > ULX"
    assert uly <= lry, "LRY > ULY"
    
    self.ulx = ulx
    self.uly = uly
    self.lrx = lrx
    self.lry = lry
    self.width = lrx - ulx + 1
    self.height = lry - uly + 1
  
  @classmethod
  def initFromGIMPBounds(cls, ulx, uly, lrx, lry):
    '''
    Alternate constructor from GIMP bounds. 
    
    Converts to our notion of LR.
    '''
    return cls(ulx, uly, lrx-1, lry-1)
    
    
    
  def isInBounds(self, coord):
    return coord.x >= self.ulx and coord.x <= self.lrx \
       and coord.y >= self.uly and coord.y <= self.lry

  # Our range includes the last element.  python range(start, stop) does not include stop
  def rangeY(self):
    ''' Generator for y values in bounds. '''
    return range(self.uly, self.lry + 1)
  
  def rangeX(self):
    return range(self.ulx, self.lrx + 1)

  def getNormalizedBounds(self):
    ''' Return bounds in a new coordinate system whose origin is at the upper left of self. '''
    return Bounds(0,0,self.width-1, self.height-1)
    
  def __repr__(self):
    return "Bounds(" + str(self.ulx) + "," + str(self.uly) + "," + str(self.lrx) + "," + str(self.lry) + \
      ", w" + str(self.width) + ", h" + str(self.height) + ")"

