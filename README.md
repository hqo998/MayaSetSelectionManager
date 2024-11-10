### **Maya Set Selection Manager**
Created by Charles von Kalm
**Installation:**
Unzip folder in scripts directory, example:

```
*\Documents\maya\2023\scripts\SaveSelectionManager\ExportationAutomation.py
*\Documents\maya\2023\scripts\SaveSelectionManager\saveSelection.py

```
Make a shelf button with python script:
```
from SaveSelectionManager import saveSelection
from importlib import reload
reload(saveSelection)

selectionsaver = saveSelection.SelectionWindow()

selectionsaver.show()
```
