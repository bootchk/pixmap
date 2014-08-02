
from array import array


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
  '''
  
  # Same values that Gimp uses, here as class attributes
  GIMP_TOTALLY_MASKED = 0
  GIMP_TOTALLY_UNMASKED = 255
  
  GIMP_SELECTION_TOTALLY_NOT_SELECTED = 0
  GIMP_SELECTION_TOTALLY_SELECTED = 255


  def __init__(self, width, initializer):
    ''' Initializer is iteratable. '''
    self.pixelelArray = array("B", initializer)
    self.width = width  # needed for address arithemetic
  
  
  def __len__(self):
    return len(self.pixelelArray)
  
  
  ''' Subscripting '''
  def isTotallyMasked(self, coords):
    return self._maskValueFromCoords(coords) == PixmapMask.GIMP_TOTALLY_MASKED
  
  def isTotallyUnmasked(self, coords):
    return self._maskValueFromCoords(coords) == PixmapMask.GIMP_TOTALLY_UNMASKED
    
  def isPartiallyUnmasked(self, coords):
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
