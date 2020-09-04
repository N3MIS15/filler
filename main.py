import micropython
from pybeerfiller.filler import pyBeerFiller

micropython.alloc_emergency_exception_buf(100)
beer_filler = pyBeerFiller()

while not beer_filler.reset():
    beer_filler.readState()

machine.reset()