'''
'''

class PixelelID(object):
  '''
  PixelelID is a 3D coord for a pixelel,
  i.e. 2D coord of pixel within pixmap and 1D index of pixelel within pixel.
  
  A named tuple
  '''
  
  def __init__(self, coord, pixelelIndex):
    self.coord = coord
    self.pixelelIndex = pixelelIndex

  def __eq__(self, other):
    return self.coord == other.coord and self.pixelelIndex == other.pixelelIndex