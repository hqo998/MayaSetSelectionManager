### **Maya Set Selection Manager**
Created by Charles von Kalm

**Features**

Assign Set, Load Set, Clear Set, Export Set, Name Set, Open Set in S3D Painter, Open Export Directory, Clear Export Directory.


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
![image](https://github.com/user-attachments/assets/dcdde05d-377e-48dd-af8e-55d8d6a0f273)
![image](https://github.com/user-attachments/assets/0281b9cf-1315-45e7-b567-2ae861385a25)
