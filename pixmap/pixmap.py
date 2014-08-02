
# from gimpfu import *  # for assertions

from arraymap import ArrayMap
from pixmapMask import PixmapMask
from bounds import Bounds


'''
Design note:
Pixmap subclasses ArrayMap to separate GIMP from ArrayMap's implementation of a pixmap.
ArrayMap can be doctested without GIMP.

Use of a Python array instead of GIMP is well-known for GIMP plugins.
'''



class Pixmap(ArrayMap):
  ''' 
  Adapter for gimp.PixelRgn class.
  
  Extends ArrayMap by these responsibilities:
  - buffering (initialize from and flush to a Gimp drawable)
  
  '''
  
  def __init__(self, drawable):
    ''' 
    Initialize self from a Gimp drawable. 
    
    Also initialize a PixmapMask for the drawable's selection .
    '''
    # assert isinstance(drawable, gimp.Drawable)
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
    # Retain region for later use
    
    # Get mask from GIMP first
    mask = self._getSelectionMask(drawable)
    
    super(Pixmap, self).__init__(width=drawable.width,
                                 height=drawable.height,
                                 bpp=self.region.bpp,
                                 initializer=self.region[0:drawable.width, 0:drawable.height],
                                 mask=mask
                                 )
    # superclass ArrayMap creates pixelelArray etc.
    assert self.pixelelArray is not None
    
    # One selection Pixelel (byte) per Pixel.
    assert len(self.selectionMask()) * self.bpp == len(self.pixelelArray)  
  
  
  def flush(self, bounds=None):
    '''
    Ask GIMP to display portion of self (flush buffered changes to Gimp.)
    '''
    # Write buffer back to PixelRgn. Convert from integers to string as required by gimp.PixelRgn
    self.region[0:self.width, 0:self.height] = self.pixelelArray.tostring()
    
    # Canonical steps to make GIMP display updated drawable
    ## merge_shadow only necessary if get_pixel_rgn(..., useShadow=True)
    ##self.parentDrawable.merge_shadow(True)  # Flush shadow region to region
    if bounds is None:
      # Update entire
      bounds = self.bounds()
    # else update only the passed bounds
    self.parentDrawable.update(bounds.ulx, bounds.uly, bounds.width, bounds.height)
    
    '''
    Don't gimp.displays_flush() because that depends on PyGIMP.
    Caller must call that.
    '''
  
  
  def flushAll(self):
    '''
    Flush entire drawable
    '''
    # bounds of entire drawable
    bounds = Bounds.initFromGIMPBounds(0, 0, self.parentDrawable.width, self.parentDrawable.height)
    self.flush(bounds)
    
    
  
  def _getSelectionMask(self, drawable):
    ''' 
    Drawable's selection mask as a PixmapMask. 
    
    !!! This is called before self's base class is initialized,
    so certain attributes of self are not known yet: use attributes from drawable.
    '''
    image = drawable.image
    selection = image.selection # returns a channel
    print("Selection channel, width, height", selection, selection.width, selection.height)
    assert selection.bpp == 1
    '''
    Get region for selection channel
    F, F : read only, and not need a shadow
    '''
    selectionRgn = selection.get_pixel_rgn(0, 0, selection.width, selection.height, False, False)
    print("Selection region, x, y, width, height", selectionRgn.x, selectionRgn.y, selectionRgn.w, selectionRgn.h)
    print("First pixel of selection region", str(ord(selectionRgn[0,0])))
    '''
    Note that many selections (especially grown selections) might have rounded corners
    and thus have 0 for the first pixel, which may be unexpected to casual glance.
    '''
    
    '''
    Selection channel covers entire image (?)
    Drawable may be offset within image and thus within selection channel.
    '''
    offsets = drawable.offsets
    print("Channel offsets", selection.offsets)
    print("Drawable offsets, width, height", drawable.offsets, drawable.width, drawable.height)
    '''
    Read selection mask into array, but only size of drawable, and offset.
    Thus, we can use same coords in selectionPixmapMask as we use in the drawable pixelelArray
    (but the index arithmetic different.)
    Note the selection channel is never offset from the image (has same origin.)
    The drawable is offset within the selection channel.
    '''
    width = drawable.width
    height = drawable.height
    print("Selection array w,h", width, height)
    selectionPixmapMask = PixmapMask(width=drawable.width, 
                                     initializer=selectionRgn[offsets[0]:offsets[0]+width,
                                                       offsets[1]:offsets[1]+height])                                      
    print("Size of selection channel is ", len(selectionPixmapMask))
    # selectionPixmapMask.dump()
    return selectionPixmapMask
  
  
  
"""
CRUFT
  
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

