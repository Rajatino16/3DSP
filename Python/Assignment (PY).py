import JupyterNotebooksLib as slicernb
slicernb.AppWindow.setWindowSize(scale=0.5)
slicernb.showSliceViewAnnotations(False)
slicer.mrmlScene.Clear(False)

volume = slicer.util.loadVolume('CT.nrrd')

slicernb.AppWindow.setWindowSize(scale=0.5)
slicernb.showSliceViewAnnotations(False)
# for viewing initial set up
display(slicernb.ViewDisplay("FourUp"))

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

# for manually adding the Bone segment
segmentEditorWidget.show()

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
segmentEditorWidget.show()

segmentEditorNode.SetSelectedSegmentID(segmentId)
app = slicernb.AppWindow(contents="viewers", windowScale=1)
slicernb.setViewLayout("FourUp")
app.setWindowSize(scale=1)
app.setContents("viewers")

# for segmenting Region of Interest
live3dSeg = slicernb.ViewInteractiveWidget('1')
live3dSeg.trackMouseMove = True
display(live3dSeg)
segmentEditorWidget.setActiveEffectByName("Scissors")
effect = segmentEditorWidget.activeEffect()
effect.setParameter('Operation','EraseOutside')
effect.setParameter('Shape','FreeForm')

segmentEditorWidget.show()

segmentEditorWidget.setActiveEffectByName('Smoothing')
effect = segmentEditorWidget.activeEffect()
effect.setParameter('SmoothingMethod', 'Closing')
effect.setParameter("KernelSizeMm", 3)
effect.self().onApply()

# ROI after applying Closing
display(slicernb.ViewDisplay("FourUp"))

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


# after modifying through Scissors and applying filters
display(slicernb.ViewDisplay("OneUp3D"))

slicer.modules.jupyterkernel.setPollIntervalSec(0.001)

# for 3D view
slicernb.AppWindow.setWindowSize(scale=0.5)
live3d = slicernb.ViewInteractiveWidget('1')
live3d.trackMouseMove = True
display(live3d)
