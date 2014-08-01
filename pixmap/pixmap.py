
from array import array

from gimpfu import *

from pixmapMask import PixmapMask
from bounds import Bounds
from coord import Coord
from pixelelID import PixelelID





class Pixmap(object):
  ''' 
  Adapter for gimp.PixelRgn class.
  
  Extends by these responsibilities:
  - buffering (initialize from and flush to a Gimp drawable)
  - subscriptable by Coord, not tuple, returning and taking an array of integer pixelels ( i.e. RGBA color )
  - known dimension attributes (width, height, bpp)
  - clipping test method
  - selection convenience methods
  - iterator protocol
  - know selection mask and get related masks
  - know bounds of selection
  - visibility test method (TODO)
  '''
  
  def __init__(self, drawable):
    ''' 
    Initialize self from a Gimp drawable. 
    
    Also initialize a PixmapMask for the drawable's selection .
    '''
    assert isinstance(drawable, gimp.Drawable)
    self.parentDrawable = drawable
    
    '''
    Responsibility: buffering.  See also self.flush()
    Create a local copy of Gimp's data (local meaning: access does not read from or write to Gimp, until flushed.)
    '''
    '''
    Note the parameters for "dirty, shadow" = True, False means that:
    in flush(), it sets the region dirty and writes directly to the image (not undoable.)
    Dirty is about undo?
    Shadow is about double buffering?
    Here we use neither.
    '''
    # TODO pass dirty, shadow
    self.region = drawable.get_pixel_rgn(0, 0, drawable.width, drawable.height, False, False)
    
    '''
    Responsibility: known dimensions.  These are exposed to public.
    '''
    self.width = drawable.width
    self.height = drawable.height
    self.bpp = self.region.bpp  # "Bytes per pixel" i.e. pixelels per pixel
    
    # If GIMP ever has more bits per pixelel, this needs to change
    '''
    Read the entire region into a 1 dimensional array of pixelels (int for each RGBA value).
    Note self.region[] returns a string, which when iterated returns chars representing pixelels
    which are stored in the array as unsigned chars i.e. ints as specified by "B" arg to array().
    See python docs for module array.
    '''
    self.pixelelArray = array("B", self.region[0:self.width, 0:self.height])
    print "Size of pixelelArray", len(self.pixelelArray)
    
    self.selectionPixmapMask = self._getSelectionMask(drawable)
  
    self.indexLimit = self.width * self.height
    
  
  def flush(self, bounds):
    '''
    Ask GIMP to display portion of self (flush buffered changes to Gimp.)
    '''
    # Write buffer back to PixelRgn. Convert from integers to string as required by gimp.PixelRgn
    self.region[0:self.width, 0:self.height] = self.pixelelArray.tostring()
    
    # Canonical steps to make GIMP display updated drawable
    ## merge_shadow only necessary if get_pixel_rgn(..., useShadow=True)
    ##self.parentDrawable.merge_shadow(True)  # Flush shadow region to region
    self.parentDrawable.update(bounds.ulx, bounds.uly, bounds.width, bounds.height)
    # Don't gimp.displays_flush() because that depends on PyGIMP
  
  
  def flushAll(self):
    '''
    Flush entire drawable
    '''
    # bounds of entire drawable
    bounds = Bounds.initFromGIMPBounds(0, 0, self.parentDrawable.width, self.parentDrawable.height)
    self.flush(bounds)
    
    
  
  def _getSelectionMask(self, drawable):
    ''' Drawable's selection mask as a PixmapMask. '''
    image = drawable.image
    selection = image.selection # returns a channel
    print "Selection channel, width, height", selection, selection.width, selection.height
    assert selection.bpp == 1
    '''
    Get region for selection channel
    F, F : read only, and not need a shadow
    '''
    selectionRgn = selection.get_pixel_rgn(0, 0, selection.width, selection.height, False, False)
    print "Selection region, x, y, width, height", selectionRgn.x, selectionRgn.y, selectionRgn.w, selectionRgn.h
    print "First pixel of selection region", str(ord(selectionRgn[0,0]))
    '''o
    Note that many selections (especially grown selections) might have rounded corners
    and thus have 0 for the first pixel, which may be unexpected to casual glance.
    '''
    
    '''
    Selection channel covers entire image (?)
    Drawable may be offset within image and thus within selection channel.
    '''
    offsets = drawable.offsets
    print "Channel offsets", selection.offsets
    print "Drawable offsets, width, height", drawable.offsets, drawable.width, drawable.height
    '''
    Read selection mask into array, but only size of drawable, and offset.
    Thus, we can use same coords in selectionPixmapMask as we use in the drawable pixelelArray
    (but the index arithmetic different.)
    Note the selection channel is never offset from the image (has same origin.)
    The drawable is offset within the selection channel.
    '''
    print "Selection array w,h", self.width, self.height
    selectionPixmapMask = PixmapMask(width=self.width, initializer=selectionRgn[offsets[0]:offsets[0]+self.width,
                                                       offsets[1]:offsets[1]+self.height])
    assert len(selectionPixmapMask) * self.bpp ==  len(self.pixelelArray)  # One selection Pixelel (byte) per Pixel.                                      
    print "Size of selection channel is ", len(selectionPixmapMask)
    # selectionPixmapMask.dump()
    return selectionPixmapMask
  
  
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
    return self.selectionMask.copy()
    
  def getNullMask(self):
    " Mask same size as self, but totally selecting ALL pixels. "
    return self.selectionMask.getNullCopy()
  
    
  def getFullMask(self):
    " Mask same size as self, but selecting NO pixels. "
    return self.selectionMask.getFullCopy()



  '''
  Responsibility: know bounds of selection.
  '''

  def selectionBounds(self):
    '''
    Bounds or None.
    
    !!! upgrading from tuple to a Bounds object.
    
    !!! Interpretation from unmasked to selected.
    '''
    if self.selectionMask.isTotalMask():
      return None
    else:
      self.selectionMask.computeUnmaskedBounds()
      return Bounds(*self.selectionMask.unmaskedBounds())


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

