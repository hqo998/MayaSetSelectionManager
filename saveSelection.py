"""
Save selection script by Charles von Kalm.
Created and tested with maya 2023

Description:
A tool for creating/managing sets of objects for ease of use with exporting and transferring to different applications included.

Requirements:
SaveSelectionManagerFolder should be placed in Documents\maya\2023\scripts
If exportationAutomation.py is missing export functions will not work.

Saving
Textfields, sets, and export fields are scene specific as fileInfo
Amount of rows is saved to maya preferences as OptionVar
Selection sets are saved to object attributes
FilInfo doesn't prompt user to save to force saving after modification with to prevent dataloss - cmds.file(force=True, save=True, options="v=0")
"""


from maya import cmds
from functools import partial
from SaveSelectionManager import ExportationAutomation
from maya import mel #used for fbx export - python version unreliable.

from importlib import reload
reload(ExportationAutomation)



class selection(object):
    """
    Class selection contains methods needed for handling selection instances.
    """
    savedSelection = []
    index = 0
    fbxexport = None
    homedir = None


    def retrieveSelection(self):
        """
        Runs on window initialisation to restore from persistent data such as optionVars and selectionset attributes on objects.

        Returns: Amount of objects with relative index to set instance.

        """
        #Check if a persistent list exists if so set it to savedSelection list
        # if cmds.optionVar(q=f'selVar_{self.index}'):
        #     self.savedSelection = cmds.optionVar(q=f'selVar_{self.index}')

        initialLength = []
        objects = cmds.ls(selection=False, dag=True, long=True)
        for object in objects:
            try:
                exist = cmds.getAttr(f"{object}.SelectionSet_{self.index}")
            except ValueError:
                exist = None
            if exist == 1:
                initialLength.append(object)

        print("about to retrieve export dir")
        if cmds.fileInfo(f"fbx_directory_{self.index}", query=True):
            print("retrieving exportdir")
            self.fbxexport = cmds.fileInfo(f"fbx_directory_{self.index}", query=True)[0]
            self.homedir = cmds.fileInfo(f"home_directory_{self.index}", query=True)[0]
            print(self.fbxexport)

        return len(initialLength)


    def makeSelection(self, *args):
        """
        Method used to add index attribute to selected objects to mark for part of a set
        Args:
            *args: Used to dispose of irrelevant args passed by button command.

        Returns: Amount of items made into new selection set

        """


        items = cmds.ls(selection=True) or []

        if not items:
            cmds.warning("Nothing selected")

        #Make sure other objects that used to be part of the selection are removed.
        objects = cmds.ls(selection=False, dag=True, long=True)
        unique_elements = list(set(objects).symmetric_difference(set(items))) #get all elements that are in selected.

        #Make sure everything that is part of selection has relative attribute removed.
        for element in unique_elements:
            try:
                exist = cmds.getAttr(f"{element}.SelectionSet_{self.index}")
            except ValueError:
                exist = None
            if exist == 1:
                cmds.deleteAttr(f"{element}.SelectionSet_{self.index}")

        #Make sure everything selected as attribute applied.
        for item in items:
            try:
                exist = cmds.getAttr(f"{item}.SelectionSet_{self.index}")
            except ValueError:
                exist = None

            if exist == -1:
                cmds.setAttr(f"{item}.SelectionSet_{self.index}", 1)
            else:
                cmds.addAttr(item, longName=f"SelectionSet_{self.index}",
                         attributeType='float',
                         defaultValue=1)

        cmds.warning(f"{len(items)} object/s added to set #{self.index}")
        return len(items)




        # self.savedSelection = cmds.ls(selection=True) or []
        #
        # #Add every item to maya persistent array.
        # cmds.optionVar(clearArray=f'selVar_{self.index}')
        # for item in self.savedSelection:
        #     cmds.optionVar(stringValueAppend=(f"selVar_{self.index}", item))
        #
        # print(len(self.savedSelection))
        # print(self.savedSelection)
        #
        # return len(self.savedSelection)



    def loadSelection(self, *args):
        """
        Load selection is a method used to select all objects with the relevant attribute to the index.
        Works by parsing all objects and adding those with the right attribute to selection.
        Args:
            *args: Used to dispose of irrelevant args passed by button command.

        Returns:
            0: True if selection is > 0
            1: Length of selection list.

        """
        cmds.select(clear=True)
        objects = cmds.ls(selection=False, dag=True, long=True)

        for object in objects:
            try:
                exist = cmds.getAttr(f"{object}.SelectionSet_{self.index}")
            except ValueError:
                exist = None
            if exist == 1:
                cmds.select(object, add=True)

        success = cmds.ls(selection=True) or []
        cmds.warning(f"{len(success)} Selected")
        return True if success else False, len(success)

        #select all items in savedselection list
        # if self.savedSelection or None:
        #     cmds.select(clear=True)
        #     print(self.savedSelection)
        #     for saved in self.savedSelection:
        #         try:
        #             cmds.select(saved, add=True)
        #         except ValueError:
        #             cmds.warning("One of more objects have been moved, deleted or renamed")
        #
        #     return True
        # else:
        #     print("No Selection Saved")
        #     return False



    def clearSelection(self, *args):
        """
        Selection method to clear all selection set relative data  including persistent data.
        Args:
            *args: ignore.

        Returns: nothing.

        """
        cmds.warning("Clearing selection")

        items  = cmds.ls(selection=False, dag=True, long=True)
        for item in items:
            try:
                cmds.deleteAttr(f"{item}.SelectionSet_{self.index}")
            except:
                pass

        #clear selection from list, persistent and viewport selected
        #cmds.select(clear=True)
        self.savedSelection = []

        #cmds.optionVar(clearArray=f'selVar_{self.index}')

        cmds.fileInfo(rm=f"fbx_directory_{self.index}")
        cmds.fileInfo(rm=f"home_directory_{self.index}")
        #cmds.file(force=True, save=True, options="v=0")


        self.fbxexport, self.homedir = None, None
        print("Cleared Selection")



    def ClearDir(self, *args):
        """
        Smaller version of the clear selection method to just remove directory data
        Args:
            *args:

        Returns:

        """
        #cmds.optionVar(clearArray=f"directory_{self.index}")
        cmds.fileInfo(rm=f"fbx_directory_{self.index}")
        cmds.fileInfo(rm=f"home_directory_{self.index}")
        #cmds.file(force=True, save=True, options="v=0")

        self.fbxexport, self.homedir = None, None


    def exportSelection(self, SetName="Mesh"):
        '''
        Prompts user to set export directory then export selection set as fbx. If directory already set uses that instead.

        Args:
            SetName: Queries text field for name of the fbx for export.

        Returns:

        '''
        restoreSelection = cmds.ls(selection=True)

        anySelelected = self.loadSelection()[1] #select everything needing to be exported

        if anySelelected:
            print("Doing Export")
            if not self.homedir:
                mesh_folder_path = cmds.fileDialog2(dialogStyle=2, fileMode=3, okCaption='Select')
                try:
                    mesh_folder_path = mesh_folder_path[0]
                except TypeError:
                    mesh_folder_path = None
            else:
                mesh_folder_path = self.homedir

            if mesh_folder_path:
                mainpath = mesh_folder_path + "/" + SetName + ".fbx"

                mel.eval( 'FBXExport -f "{0}" -s'.format(mainpath) )

                cmds.warning(f"Set {self.index} as File exported to: {mesh_folder_path} as {SetName}.fbx")  # Let user know where file is saved
                cmds.select(clear=True)

                self.fbxexport = mainpath
                self.homedir = mesh_folder_path

                # cmds.optionVar(stringValueAppend=(f"directory_{self.index}", self.fbxexport))
                # cmds.optionVar(stringValueAppend=(f"directory_{self.index}", self.homedir))

                cmds.fileInfo(f"fbx_directory_{self.index}", self.fbxexport)
                cmds.fileInfo(f"home_directory_{self.index}",self.homedir)
                cmds.file(force=True, save=True, options="v=0")

                #Restore selection from before export
                for restore in restoreSelection:
                    cmds.select(restore, add=True)

            else:
                cmds.warning(f"Export Cancelled")


    def OpenPainter(self):
        """
        References ExportationAutomation.py
        Passes exported fbx path to open substance painter using command-lines.
        Returns:

        """
        if self.fbxexport and self.homedir:
            ExportationAutomation.toPainter(self.fbxexport, self.homedir)
        else:
            cmds.warning("Mesh not Exported.")

    def OpenDir(self, *args):
        """
        References ExportationAutomation.py
        Opens Explorer at set directory.
        Args:
            *args:

        Returns:

        """
        if self.homedir:
            ExportationAutomation.openFolder(self.homedir)
        else:
            cmds.warning("No Directory Set")






class SelectionWindow(object):
    """
    UI Logic Class
    """


    def __init__(self):
        #set amount to persistent amount if it exists, if not default to 5.
        #Amount is how many selection options are available to the user.
        self.amount = cmds.optionVar(q=f'selectionAmount') if cmds.optionVar(q=f'selectionAmount') else 5
        self.windowName = ("Selection_Sets_Window")


    def show(self):
        """
        If window is opepned while opened then close and reopen. Prompts for UI build and show.
        Returns:

        """

        if cmds.window(self.windowName, query=True, exists=True): #if window by this name exists
            cmds.deleteUI(self.windowName) #delete window

        cmds.window(self.windowName) #create window with name

        self.buildUI(self.amount) #class method to set window layout and settings

        cmds.showWindow() #show window

    def buildUI(self, selamount):
            """
            UI Layout and widgets.
            Args:
                selamount: The amount of rows for the UI to build, pulls from persistent data

            Returns: no returns.

            """
            self.sel = []
            self.lengthText = []
            self.setNameFields = []
            column = cmds.columnLayout() #stack elements vertically

            cmds.text(label="Save and reuse selections")

            #Generate rows of selection UI
            for i in range(selamount):

                self.sel.append(selection()) #Creates list of selection function instances

                self.sel[i].index = i #

                length = self.sel[i].retrieveSelection() #returns the length of existing list to use as user indicator

                row = cmds.rowLayout(numberOfColumns=9)  # row have two wide.

                self.lengthText.append(cmds.text(label=length,
                                                 ann="Number of objects in selection.\nIf components selected number will be inaccurate due to index ranging.")) #make an accessible list of all the texts showing list size.

                cmds.button(label=f"Load", command=self.sel[i].loadSelection, bgc=[.4,.4,1], ann="Load selection")
                cmds.button(label="Assign", command=partial(self.domakeSelection, i), bgc=[.3,1,.3], ann="Assign selected to set.") #partial allows command to pass arg to function
                cmds.button(label="Clear", command=partial(self.doclearSelection, i), bgc=[1,.3,.3], ann="Clear selection set.")
                cmds.button(label="Export", command=partial(self.doexportSelection, i), bgc=[.2, .2, .2], ann="Export to selected folder.\nComponents will be exported as whole objects.")

                #persistent textfield
                self.setNameFields.append(cmds.textField(text=self.textfieldPersistence(i, True),
                                                         ann="Set name for export and convenience",
                                                         textChangedCommand=partial(self.textfieldPersistence, i, False)))


                #substance painter button
                cmds.button(label="Open Painter", bgc=[.2, .4, .2],
                            command=partial(self.doOpenPainter, i),
                            ann="Opens set in Substance Painter \n To Painter will open new file.\nTo update mesh please use export and the reimport function in Painter\n!Does not set up project settings!")


                #home dir
                cmds.button(label="Open Dir", bgc=[.3, .3, .3],
                            command=self.sel[i].OpenDir,
                            ann="Opens Export location")

                cmds.button(label="Clear Dir", bgc=[.3, .3, .3],
                            command=self.sel[i].ClearDir,
                            ann="Only clear directory path")

                cmds.setParent(column)

            #Bottom of UI options
            cmds.setParent(column)
            cmds.rowLayout(numberOfColumns=4)
            cmds.button(label="CLOSE", command=self.close, bgc=[.7,.3,.3])
            cmds.button(label="Clear All", command=partial(self.doclearSelection, "All"))
            cmds.button(label="Vertex Colour", command=self.doOpenVertexColour)
            cmds.button(label="Export Selection", command=self.doMayaExportSelection)

            cmds.setParent(column)
            cmds.text(label="Use Close box to close and save data")

            #range slider
            cmds.rowLayout(numberOfColumns=2)
            self.amountlabel = cmds.text(label=selamount)
            self.amountslider = cmds.intSlider(min=1, max=15, value=selamount, step=1, changeCommand=self.rebuildUI)

    def doOpenPainter(self, index, *args):
        self.sel[index].OpenPainter()

    def doOpenVertexColour(self, *args):
        mel.eval('PolygonApplyColorOptions;')

    def doclearSelection(self, index, *args):
        if index == "All":
            for i in range(len(self.sel)):
                print(i)
                self.sel[i].clearSelection()  # calls clear selection from class instance
                cmds.text(self.lengthText[i], edit=True, label=0)  # update list length text

                # Wipe textfield and remove var.
                cmds.fileInfo(rm=f"textfieldVar_{i}")
                cmds.textField(self.setNameFields[i], edit=True, text=f"Set_{i}")
        else:
            print(index)
            self.sel[index].clearSelection() #calls clear selection from class instance
            cmds.text(self.lengthText[index], edit=True, label=0) #update list length text

            #Wipe textfield and remove var.
            #cmds.optionVar(clearArray=f"textfieldVar_{index}")
            cmds.fileInfo(rm=f"textfieldVar_{index}")

            cmds.textField(self.setNameFields[index], edit=True, text=f"Set_{index}")

    def domakeSelection(self, index, *args):
        length = self.sel[index].makeSelection()
        cmds.text(self.lengthText[index], edit=True, label=length)

    def doMayaExportSelection(self, *args):
        mel.eval('ExportSelectionOptions;')

    def doexportSelection(self, index, *args):
        print("doing export")
        #query text field for name
        text = cmds.textField(self.setNameFields[index], q=True, text=True)
        self.sel[index].exportSelection(SetName=text)

    def rebuildUI(self, slidervalue):
        #closes and reopens UI with new amount of selection rows.
        cmds.deleteUI(self.windowName)
        self.amount = slidervalue
        cmds.optionVar(iv=('selectionAmount', slidervalue))
        self.show()

    def textfieldPersistence(self, index, load=False, *args):
        #makes text fields persistent
        if load:
            #print(cmds.fileInfo(f"textfieldVar_{index}", q=True)[0])
            return cmds.fileInfo(f"textfieldVar_{index}", q=True)[0] if cmds.fileInfo(f"textfieldVar_{index}", q=True) else f"Set_{index}"
        else:
            text = cmds.textField(self.setNameFields[index], q=True, text=True)
            cmds.fileInfo(f"textfieldVar_{index}", text)


            #cmds.optionVar(stringValue=(f"textfieldVar_{index}", text))

            # cmds.fileInfo(f"textfieldVar_{index}",text)
            # cmds.fileInfo(f"textfieldVar_{index}", q=True)

    def close(self, *args):
        cmds.deleteUI(self.windowName)
        cmds.file(force=True, save=True, options="v=0")
