
from sys import maxsize   # maximal int
from array import array

from coord import Coord


class PixmapMask(object):
  '''
  A Pixmap used as a mask:
  each element value is a single int giving degree of masking,
  where the values are as defined in Gimp.
  
  Usually one-to-one with another Pixmap holding color.
  
  
  Examples:
  To test: 
  cd to the enclosing directory
  python -m doctest -v pixmapMask.py
  
  >>> from coord import Coord
  >>> from copy import copy
  
  >>> totalMask = PixmapMask(2, [0, 0, 0, 0])  # 2x2 total mask
  >>> totalMask.isTotalMask()
  True
  
  >>> totalMask.isTotallyMasked(Coord(0,0))
  True
  >>> totalMask.isTotallyUnmasked(Coord(0,0))
  False
  >>> totalMask.isSomewhatSelected(Coord(0,0))
  False
  
  >>> invertedTotalMask = copy(totalMask)
  >>> invertedTotalMask.invert()
  >>> invertedTotalMask.isTotalMask()
  False
  
  Properties of a mask
  >>> len(totalMask)
  4
  
  
  >>> invertedTotalMask.isTotallyMasked(Coord(0,0))
  False
  >>> invertedTotalMask.isTotallyUnmasked(Coord(0,0))
  True
  
  Subscripting works
  >>> invertedTotalMask[Coord(0,0)]
  255
  
  Mask value of 1 is partially masked and partially selected
  >>> partialMask = copy(invertedTotalMask)
  >>> partialMask[Coord(0,0)] = 1
  
  partialMask has one pixel (0,0) that is partially masked, all other pixels fully masked
  >>> partialMask.isTotallyMasked(Coord(0,0))
  False
  >>> partialMask.maskValueIsUnmasked(Coord(0,0))
  True
  >>> partialMask.isSomewhatSelected(Coord(0,0))
  True
  >>> partialMask.isSomewhatSelected(Coord(1,1))
  True
  
  
  Bounds
  
  >>> a = PixmapMask(3, [0, 0, 0, 0, 255, 0])
  
  unmaskedbounds are not available until call computeUnmaskedBounds() or setUnmaskedBounds()
  >>> a.unmaskedBounds()
  Traceback (most recent call last):
  ...
  AssertionError: Bounds not available until after computeUnmaskedBounds().

  # Computing unmaskedbounds returns the bounds
  >>> a.computeUnmaskedBounds()
  (1, 1, 1, 1)
  
  >>> a.unmaskedBounds()
  (1, 1, 1, 1)
  
  after inverting, must call 
  >>> a.invert()
  >>> a.computeUnmaskedBounds()
  (0, 0, 2, 1)
  >>> a.unmaskedBounds()
  (0, 0, 2, 1)
  
  >>> b = a.getUnmaskedCopy()
  >>> b.invert()
  >>> b.isTotalMask()
  True
  
  illegal to call computeUnmaskedBounds() on total mask
  >>> b.computeUnmaskedBounds()
  Traceback (most recent call last):
  ...
  RuntimeError: Illegal to computeUnmaskedBounds on a total mask.
  
  # Exception thrown when setting unmaskedbounds that don't correspond to mask values
  >>> a.setUnmaskedBounds((0, 0, 1, 1))
  Traceback (most recent call last):
  ...
  AssertionError: Passed bounds do not equal computed unmasked bounds.
  
  # After above exception thrown, unmaskedBounds are unchanged
  >>> a.unmaskedBounds()
  (0, 0, 2, 1)
  
  # Exception thrown when setting unmaskedbounds that exceed bounds of mask
  >>> a.setUnmaskedBounds((0, 0, 3, 1))
  Traceback (most recent call last):
  ...
  AssertionError: Illegal bounds.
  
  '''
  
  # Same values that Gimp uses, here as class attributes
  GIMP_TOTALLY_MASKED = 0
  GIMP_TOTALLY_UNMASKED = 255
  
  GIMP_SELECTION_TOTALLY_NOT_SELECTED = 0
  GIMP_SELECTION_TOTALLY_SELECTED = 255


  def __init__(self, width, initializer, height=None):
    ''' Initializer is iteratable. '''
    self.pixelelArray = array("B", initializer)
    self.width = width  # needed for address arithemetic
    
    # cached.  None means not computed yet.  A tuple, not a Bounds.
    # !!! Currently not updated when you change a mask value.
    self.unmaskedBoundsCache = None
    
    # Compute height.
    self.height = len(self.pixelelArray) / self.width
    
    if height is not None:
      assert height == self.height
      
    # We aren't checking that initializer len == h x w
      
  
  
  def __len__(self):
    return len(self.pixelelArray)
  
  
  ''' Subscripting '''
  def isTotallyMasked(self, coords):
    return self._maskValueFromCoords(coords) == PixmapMask.GIMP_TOTALLY_MASKED
  
  def isTotallyUnmasked(self, coords):
    return self._maskValueFromCoords(coords) == PixmapMask.GIMP_TOTALLY_UNMASKED
    
  def isSomewhatUnmasked(self, coords):
    return self.maskValueIsUnmasked(self._maskValueFromCoords(coords))
    
  def maskValueIsUnmasked(self, value):
    ''' 
    Does a pixelel value from a mask represent unmasked? 
    Returns True if the value represents partial or total unmasked.
    '''
    return value > PixmapMask.GIMP_TOTALLY_MASKED
    
    
  def _maskValueFromCoords(self, coords):
    # length of each element is one; no multiplier
    pixelIndex = coords.y * self.width + coords.x
    return self.pixelelArray[pixelIndex]
  
  
  ''' Properties '''
  def isTotalMask(self):
    ''' 
    Are any pixels fully or partially unmasked? 
    Under interpretation of selection: is there a selection? 
    '''
    for pixelel in self.pixelelArray:
      if self.maskValueIsUnmasked(pixelel):
        return False # some pixel is unmasked to some extent
    return True  # all pixels are totally masked
  
  
  def dump(self):
    print("PixmapMask:")
    for value in self.pixelelArray:
      print(value)
      
  
  def invert(self):
    '''
    Invert self.
    '''
    for pixelelIndex in range(0, len(self)):
      self.pixelelArray[pixelelIndex] = 255 - self.pixelelArray[pixelelIndex]
    # assert every pixelel still in range [0,255]
      
      
  def getUnmaskedCopy(self):
    ''' Everywhere unmasked copy of self. '''
    return self.getInitializedCopy(PixmapMask.GIMP_TOTALLY_UNMASKED)
  
  
  def getInitializedCopy(self, value):
    ''' Mask initialized to value. '''
    return PixmapMask(width=self.width, initializer=[value for _ in range(0, len(self.pixelelArray))])
  
  '''
  Assuming self is a selection mask, methods for determining selection
  '''
  def isTotallyNotSelected(self, coords):
    pixelelIndex = coords.y * self.width + coords.x   # Address arithmetic: times 1, only one mask byte
    return self.pixelelArray[pixelelIndex] == PixmapMask.GIMP_SELECTION_TOTALLY_NOT_SELECTED
  
  def isTotallySelected(self, coords):
    pixelelIndex = coords.y * self.width + coords.x   # times 1, only one mask byte
    return self.pixelelArray[pixelelIndex] == PixmapMask.GIMP_SELECTION_TOTALLY_SELECTED
    
  def isSomewhatSelected(self, coords):
    ''' Is totally or partially selected. '''
    return not self.isTotallyNotSelected(coords)
  
  
  '''
  Responsibility: subscripting.
  
  Subscripting methods returning one integer (not an array, as for Pixmap)
  Unlike Pixmaps, you CAN use this to assign individual pixelels!!!!
  See further comments at Pixmap.  
  '''
  
  def __getitem__(self, key):
    '''
    int 
    '''
    assert key is not None
    pixelIndex = ( key.y * self.width + key.x )
    assert isinstance(pixelIndex, int) and pixelIndex >= 0, str(pixelIndex)
    return self.pixelelArray[pixelIndex]
  
    
  def __setitem__(self, key, value):
    '''
    Set one pixelel from a value which is an int.
    '''
    pixelIndex = ( key.y * self.width + key.x )
    assert value >= 0 and value <= 255
    assert isinstance(pixelIndex, int) and pixelIndex >= 0, str(pixelIndex)
    self.pixelelArray[pixelIndex] = value


  
  '''
  Know bounds
  '''

  def unmaskedBounds(self):
    '''
    Return tuple of bounds of somewhat unmasked pixels.
    
    !!! This is not bounds of mask, but of mask values equal to SOMEWHAT UNMASKED
    Equivalent to Drawable.mask_bounds where Drawable is PyGIMP class.
    '''
    # For now, just return value computed at initialization, which may be None
    assert self.unmaskedBoundsCache is not None, "Bounds not available until after computeUnmaskedBounds()."
    return self.unmaskedBoundsCache
  
  
  def setUnmaskedBounds(self, bounds):
    ''' 
    Set unmasked bounds from tuple computed elsewhere.
    
    !!! These bounds should fit our notion of bounds: LR are coordinates inside the bounds.
    Which is different from GIMP.
    
    !!! This does NOT change mask values.
    Mask values should correspond to given bounds, else behaviour unpredictable.
    '''
    # Complete check, unmaskedBounds contained in bounds of mask
    assert  bounds[0] >= 0 and bounds[0] < self.width \
        and bounds[1] >= 0 and bounds[1] < self.height \
        and bounds[1] >= 0 and bounds[2] < self.width  \
        and bounds[1] >= 0 and bounds[3] < self.height , "Illegal bounds."
    '''
    Check that bounds passed equal what we would compute.
    This assertion defeats shortcut nature of this method.
    You should comment this assertion out if you really expect this method be fast.
    '''
    assert bounds == self.computeUnmaskedBounds(), "Passed bounds do not equal computed unmasked bounds."
    self.unmaskedBoundsCache = bounds
  
  
  def computeUnmaskedBounds(self):
    ''' 
    Compute and cache unmasked bounds.
    
    Standard algorithm: iterate, computing new max and min x, y
    '''
    ulx = maxsize # initially very large
    uly = maxsize
    lrx = 0
    lry = 0
    for y in range(0, self.height):
      for x in range(0, self.width):
        coords = Coord(x,y)
        if self.isSomewhatUnmasked(coords):
          if x < ulx: ulx = x # ul moves left or upper
          if y < uly: uly = y
          if x > lrx: lrx = x # lr moves lower or right
          if y > lry: lry = y
    if lrx < ulx or lry < uly:
      raise RuntimeError, "Illegal to computeUnmaskedBounds on a total mask."
    
    self.unmaskedBoundsCache = (ulx, uly, lrx, lry)
    return self.unmaskedBoundsCache





if __name__ == "__main__":
    import doctest
    doctest.testmod()
