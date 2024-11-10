"""
Save selection script by Charles von Kalm.
Created and tested with maya 2023

Description:
A tool for creating/managing sets of objects for ease of use with exporting and transferring to different applications included.

installation:

Create folder named SaveSelectionManagerFolder it should be placed in Documents\maya\2023\scripts

Place saveselection.py and exportationautomation.py inside folder




Add to Python Maya Shelf:

from SaveSelectionManager import saveSelection

from importlib import reload

reload(saveSelection)

selectionsaver = saveSelection.SelectionWindow()

selectionsaver.show()
