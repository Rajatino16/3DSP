import JupyterNotebooksLib as slicernb
slicernb.showSliceViewAnnotations(False)
slicer.mrmlScene.Clear(False)

# specify the absolute file path of CT.nrrd
volume = slicer.util.loadVolume('C:/Users/baxir/OneDrive/Desktop/Assignment/Python/CT.nrrd')

slicernb.AppWindow.setWindowSize(scale=1)
slicernb.showSliceViewAnnotations(False)
# for viewing initial set up
slicernb.ViewDisplay("FourUp")

segmentationNode = slicer.vtkMRMLSegmentationNode()
slicer.mrmlScene.AddNode(segmentationNode)
segmentationNode.CreateDefaultDisplayNodes()
segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(volume)
# Creating segment editor to get access to effects
segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
# To show segment editor widget : segmentEditorWidget.show()
segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
slicer.mrmlScene.AddNode(segmentEditorNode)
segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
segmentEditorWidget.setSegmentationNode(segmentationNode)
segmentEditorWidget.setMasterVolumeNode(volume)

# for manually adding the Bone segment --> select Add then rename the segment as 'bone'
segmentEditorWidget.show()

####################################(1)####################################

# for selecting the segment and getting its ID for future use
segmentEditorNode.SetSelectedSegmentID('bone')
segmentId = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName('bone')

segmentId

# for Thresholding
segmentEditorNode.SetSelectedSegmentID(segmentId)
segmentEditorWidget.setActiveEffectByName('Threshold')
effect = segmentEditorWidget.activeEffect()
effect.setParameter('MinimumThreshold',203.83)
effect.setParameter('MaximumThreshold',1492)
effect.self().onApply()

# for Islands Selection
segmentEditorWidget.setActiveEffectByName('Islands')
effect.setParameter('Operation','KEEP_SELECTED_ISLAND')

# with mouse select the part of the bone that is needed
# once done with selection run below statement
####################################(2)####################################

segmentEditorWidget.setActiveEffectByName('None')

segmentEditorNode.SetSelectedSegmentID(segmentId)

# for segmenting Region of Interest
live3dSeg = slicernb.ViewInteractiveWidget('1')
live3dSeg.trackMouseMove = True
live3dSeg
segmentEditorWidget.setActiveEffectByName("Scissors")
effect = segmentEditorWidget.activeEffect()
effect.setParameter('Operation','EraseOutside')
effect.setParameter('Shape','FreeForm')

####################################(3)####################################

segmentEditorWidget.setActiveEffectByName('None')

segmentEditorWidget.setActiveEffectByName('Smoothing')
effect = segmentEditorWidget.activeEffect()
effect.setParameter('SmoothingMethod', 'Closing')
effect.setParameter("KernelSizeMm", 3)
effect.self().onApply()

# ROI after applying Closing
slicernb.ViewDisplay("FourUp")

# applying various filters for enhanced model
effect.setParameter('SmoothingMethod', 'MEDIAN')
effect.setParameter("KernelSizeMm", 4)
effect.self().onApply()

effect.setParameter('SmoothingMethod', 'Gaussian')
effect.setParameter("KernelSizeMm", 3)
effect.self().onApply()

segmentEditorWidget.setActiveEffectByName('Scissors')
effect = segmentEditorWidget.activeEffect()
effect.setParameter('Operation','EraseInside')
effect.setParameter('Shape','FreeForm')

segmentEditorWidget.show()
# to see the segmented region in 3D --> select Show 3D button below Master Volume Field in segment Editor segmentEditorWidget

####################################(4)####################################

# After modifying the 3D Model as needed through Scissors and filters
segmentEditorWidget.setActiveEffectByName('None')

slicernb.ViewDisplay("OneUp3D")

# for 3D view
slicernb.AppWindow.setWindowSize(scale=1)
live3d = slicernb.ViewInteractiveWidget('1')
live3d.trackMouseMove = True
live3d
