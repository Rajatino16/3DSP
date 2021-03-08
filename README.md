# 3DSP

In the "Python" folder there exist 3 files, the jupyter Notebook (IPYNB file), Python Script (PY file), and CT.nrrd.

To Run the Python Script:
There are 4 locations in the script where interaction with Slicer is needed. These 4 locations are marked by a series of # in the script. 
ex; ######(1)###### indicates first location.

These 4 locations require the user:
1) To add a Segment using the Segment Editor widget and rename this segment as 'bone', close the Segment Editor Widget.
2) For Islands Selection, just click on the region needed.
3) For Segmenting the region of interest, select the region in any view with the help of scissors (which has already been enabled and parameters are set through code).
4) To see the model in 3D view, click on the "Show 3D" button (located below the Master volume field in Segment Editor). Moreover, further Enhancement of the model can be done manually through scissors and filters after this line.

The code located between these lines can be directly pasted in the python interactor present inside Slicer to run these lines.
Commenting has been done for better understanding.

The jupyter notebook can be directly run locally if SlicerJupyter Extension is installed in Slicer.

NOTE: The absolute path of the CT.nrrd file location needs to be specified according to the user.
