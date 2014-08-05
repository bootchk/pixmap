
from array import array

from bounds import Bounds
from coord import Coord
from pixelelID import PixelelID



class ArrayMap(object):
  ''' 
  Base class for Pixmap: subscriptable by coords, returning 1D array of ints.)
  
  Knows nothing about GIMP.
  
  Extends by these responsibilities:
  - subscriptable by Coord, not tuple, returning and taking an array of integer pixelels ( i.e. RGBA color )
  - known dimension attributes (width, height, bpp)
  - clipping test method
  - selection convenience methods
  - iterator protocol
  - know selection mask and get related masks
  - know bounds of selection
  - visibility test method (TODO)
  
  
  To test: 
  cd to the enclosing directory
  python -m doctest -v arraymap.py
  
  >>> from pixmapMask import PixmapMask
  
  >>> mask = PixmapMask(2, [1, 0, 0, 0])  # 2x2  mask
  >>> map = ArrayMap(2, 2, 1, [0, 0, 0, 0], mask)
  ('Size of pixelelArray', 4)
  
  >>> map.selectionMask()   #doctest: +ELLIPSIS
  <pixmapMask.PixmapMask object at 0x...>
  
  Knows bounds and bounds of selection mask
  >>> map.bounds()
  Bounds(0,0,2,2)
  
  >>> map.selectionBounds()
  Bounds(0,0,0,0)
  
  
  Clipping is by rect dimensions, regardless of mask.
  >>> map.isClipped(Coord(0,0))
  False
  >>> map.isClipped(Coord(3,30))
  True
  
  
  Generator of pixelelIDs at a coord
  >>> map.pixelelIDsAt(Coord(0,0))  #doctest: +ELLIPSIS
  <generator object pixelelIDsAt at 0x...>
  
  Test map has only one pixelel per coord
  >>> [index for index in map.pixelelIDsAt(Coord(0,0))]
  [PixelelID(Coord(0,0),0)]
  
  A map with a totalMask returns a None bounds
  >>> mask = PixmapMask(2, [0, 0, 0, 0])  # total  mask
  >>> map = ArrayMap(2, 2, 1, [0, 0, 0, 0], mask)
  ('Size of pixelelArray', 4)
  >>> map.selectionBounds()
  
  
  '''
  
  def __init__(self, width, height, bpp, initializer, mask):
    ''' 
    Initialize self from a Gimp drawable. 
    
    Also initialize a PixmapMask for the drawable's selection .
    '''
    '''
    Responsibility: known dimensions.  These are exposed to public.
    '''
    self.width = width
    self.height = height
    self.bpp = bpp  # "Bytes per pixel" i.e. pixelels per pixel
    
    # If GIMP ever has more bits per pixelel, this needs to change
    '''
    Read the entire region into a 1 dimensional array of pixelels (int for each RGBA value).
    Note self.region[] returns a string, which when iterated returns chars representing pixelels
    which are stored in the array as unsigned chars i.e. ints as specified by "B" arg to array().
    See python docs for module array.
    '''
    self.pixelelArray = array("B", initializer)
    print("Size of pixelelArray", len(self.pixelelArray))
    
    self.selectionPixmapMask = mask
  
    self.indexLimit = self.width * self.height
    
    " Ensure "
    assert self.indexLimit * self.bpp == len(self.pixelelArray), "pixelelArray is fully initialized"
  
  
  '''
  Convenience methods (so you don't need to explicitly get a copy of the selection mask.)
  '''
  def isTotallyNotSelected(self, coords):
    return self.selectionPixmapMask.isTotallyNotSelected(coords)
  
  def isTotallySelected(self, coords):
    return self.selectionPixmapMask.isTotallySelected(coords)
    
  def isSomewhatSelected(self, coords):
    ''' Is totally or partially selected. '''
    return not self.isTotallyNotSelected(coords)
  
  def invertSelection(self):
    self.selectionPixmapMask.invert()
    


  '''
  Responsibility:
  know selection mask and get related masks
  '''
  def selectionMask(self):
    '''
    Self's selection mask.
    
    !!! Not a copy and subject to side effect via invertSelection()
    '''
    return self.selectionPixmapMask
  
  def copySelectionMask(self):
    " Same as above, but a copy. "
    return self.selectionMask().copy()
    
  
  " This understands that unmasked is selected"
  def getTotalSelectMask(self):
    " Mask same size as self, but totally selecting ALL pixels. "
    return self.selectionMask().getUnmaskedCopy()
    
  def getTotalUnselectMask(self):
    " Mask same size as self, but selecting NO pixels. "
    result = self.getTotalSelectMask()
    result.invert()
    return result


  '''
  Responsibility: know bounds of self and selection.
  '''
  
  def bounds(self):
    '''
    Bounds: our notion of bounds, different from GIMP bounds.
    '''
    return Bounds(0, 0, self.width, self.height)
    
    
  def selectionBounds(self):
    '''
    Bounds or None.
    
    !!! upgrading from tuple to a Bounds object.
    
    !!! Interpretation from unmasked to selected.
    '''
    if self.selectionMask().isTotalMask():
      return None
    else:
      self.selectionMask().computeUnmaskedBounds()
      return Bounds(*self.selectionMask().unmaskedBounds())


  '''
  Responsibility: test whether coords are clipped. 
  '''
  
  def isClipped(self, coords):
    ''' 
    Are coords clipped?
    Use when you compute coords that might be out of the bounds of the region.
    Instead of preflighting by calling this, you might catch an exception.
    
    assert coords has attributes x, y
    '''
    return coords.x < 0 \
          or coords.y < 0 \
          or coords.x >= self.width \
          or coords.y >= self.height
  
  
  
  '''
  Responsibility: subscripting.
  
  Subscripting methods returning color (an array of positive integers.)
  Subscripting by Coord (not by a tuple, as in PixelRgn.)
  Implements index arithmetic from 2D (Coord) to 1D (array).
  
  On read and write: throws exception "IndexError: array index out of range" if coords are out of range.
  
  On write: throws exception "OverflowError: unsigned byte integer is greater than maximum" 
  if you pass a pixelel value greater than 255.
  
  For now, the range of values for Pixelels is [0,255] inclusive.
  You should not assume it will always be so.
  But you can assume that they will always be positive integers.
  
  See below, you can't use this to assign individual pixelels!!!!
  '''
  
  def __getitem__(self, key):
    '''
    Return an array of RGB values as ints.
    Note the returned object is type "array" which is iterable sequence.
    From the buffer (which may be stale if there exist other concurrent writers of the drawable.)
    '''
    assert key is not None
    # TODO this includes the alpha
    pixelIndex = ( key.y * self.width + key.x ) * self.bpp
    assert isinstance(pixelIndex, int) and pixelIndex >= 0, str(pixelIndex)
    return self.pixelelArray[pixelIndex:pixelIndex + self.bpp]
    
  def __setitem__(self, key, value):
    '''
    Set pixelels from a value which is a sequence of ints.
    To the buffer, but NOT write through to the underlying PixelRgn.
    '''
    # the value is a color.  Count of pixelels must equal bpp.
    assert len(value) == self.bpp
    # address arithmetic
    pixelIndex = ( key.y * self.width + key.x ) * self.bpp
    assert isinstance(pixelIndex, int) and pixelIndex >= 0, str(pixelIndex)
    self.pixelelArray[pixelIndex:pixelIndex + self.bpp] = value


  '''
  Get/set pixelel.
  
  Note that Pixmap[Coord][0] = 1 does not work, 
  since Pixmap[Coord] returns a new array foo, then foo[0] = 1 assigns to the new array, not to self.
  '''
  def setPixelel(self, pixelelID, value):
    pixel = self[pixelelID.coord]
    # pixel is an array, modify one of it's pixelels
    pixel[pixelelID.pixelelIndex] = value
    # Reassign pixel to self
    self[pixelelID.coord]=pixel


  def getPixelel(self, pixelelID):
    return self[pixelelID.coord][pixelelID.pixelelIndex]



  '''
  Python iterator protocol.   Supporting:   'for pixel in pixmap:'
  '''
  def __iter__(self):
    return self._iterator()
  
  def _iterator(self):
    '''
    Yields a Pixel (an array of ints.)
    '''
    for i in range(0, self.indexLimit):
      yield self.pixelelArray[i:i + self.bpp]
      
  
  
  def pixelelIDsAt(self, key):
    '''
    Iterator yielding PixelelID's of pixelels at key.
    (For use with getPixelel(), setPixelel() when you want to save a PixelelID.)
    
    There is no Pixelel class.
    A Pixmap is an array of Pixel is an array of pixelel values, and PixelelID identifies elements.
    '''
    assert isinstance(key, Coord)
    for i in range(0, self.bpp):
      yield PixelelID(key, i)
    
    
    
  """
  def copySelectionMask(self):
    return PixmapMask(width=self.width, initializer=self.selectionPixelelArray)
  """

    
  """
  TODO
  Creating from a subrect of a drawable:
  def fromSubrectOf(drawable, left, upper, width, height)
  """

  """
  CRUFT

  def getPixelAsIntTuple(self, coords):
    '''
    Return an array of RGB values as ints.
    Note the returned object is type "array" which is iterable sequence.
    From the buffer.
    Index arithmetic from 2D to 1D.
    Throws exception if coords are out of range.
    '''
    pixelIndex = ( coords.y * self.width + coords.x ) * self.bpp
    return self.pixelelArray[pixelIndex:pixelIndex+self.bpp]
  
  def _pixelStringToInt(self, pixelAsString):
    ''' Convert pixel string to array of ints. '''
    pixelAsInt = array("B", pixelAsString)
    return pixelAsInt
    
  def _updateCacheFromPixelString(self, coords, pixelAsString):
    pixelIndex = ( coords.y * self.width + coords.x ) * self.bpp
    self.pixelelArray[pixelIndex:pixelIndex+self.bpp] = self._pixelStringToInt(pixelAsString)
 
  
  def getPixelAsIntTuple(self, coords):
    '''
    Return a tuple of RGB values.
    Note convert from string to int.
    '''
    colorList = []
    # Subscripting a PixelRgn yields a pixel as a string of unsigned chars for RGB
    pixel = self.region[coords.x, coords.y]
    for pixelel in range(len(pixel)):
       # Convert char to int
       colorList.append(ord(pixel[pixelel]))
    return colorList
  
 
  ''' 
  Get and set pixel as strings of chars (each char a pixelel.)
  A gimp.PixelRgn stores pixels as strings.
  These are equivalent to the original (wrapped) PixelRgn subscripting methods.
  PixelelRgn (this wrapper) converts subscripting to return an array of ints.
  
  Since we are keeping a buffer, update it upon write.
  '''
  def getPixelAsString(self, coords):
    return self.region[coords.x, coords.y]
    
  def setPixelAsString(self, coords, pixelAsString):
    self.region[coords.x, coords.y] = pixelAsString
    self._updateCacheFromPixelString(coords, pixelAsString)
    
  """

