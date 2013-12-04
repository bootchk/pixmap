'''
'''

from array import array




class PixmapMask(object):
  '''
  A Pixmap used as a mask:
  each element value is a single int giving degree of masking,
  where the values are as defined in Gimp.
  
  Usually one-to-one with another Pixmap holding color.
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
  def isMasked(self, coords):
    return self._maskValueFromCoords(coords) == PixmapMask.GIMP_TOTALLY_MASKED
    
  def isUnmasked(self, coords):
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
    ''' Are any pixels unmasked? EG is there a selection? '''
    for pixelel in self.pixelelArray:
      if self.maskValueIsUnmasked(pixelel):
        return True # some pixel is unmasked to some extent
    return False  # all pixels are totally masked
  
  
  def dump(self):
    print "PixmapMask:"
    for value in self.pixelelArray:
      print value 
      
  
  def invert(self):
    '''
    Invert self.
    '''
    for pixelelIndex in range(0, len(self)):
      # TODO is this the right arithmetic?
      self.pixelelArray[pixelelIndex] = 255 - self.pixelelArray[pixelelIndex]
      
      
  def getNulledCopy(self):
    ''' Null mask (everywhere unmasked) same size as self. '''
    return PixmapMask(width=self.width, initializer=[PixmapMask.GIMP_TOTALLY_UNMASKED for i in range(0, len(self.self.pixelelArray))])
  
  
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
      