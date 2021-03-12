import numpy as np
import os
import copy
import glob
from math import *
import matplotlib.pyplot as plt
from functools import reduce
# reading in dicom files
import pydicom
# skimage image processing packages
from skimage import measure, morphology
from skimage.morphology import ball, binary_closing, area_closing
from skimage.measure import label, regionprops
from scipy.linalg import norm
import scipy.ndimage
from ipywidgets.widgets import *
import ipywidgets as widgets
# plotly 3D interactive graphs
import plotly
from plotly.graph_objs import *
from plotly.figure_factory import create_trisurf
from scipy.spatial import Delaunay
import chart_studio
from chart_studio.plotly import plot, iplot
from mpl_toolkits import mplot3d

data_path = "3DSPData/series-000001"
output_path = working_path = "Out/"
g = glob.glob(data_path + '/*.dcm')
data_path = "3DSPData/series-000002"
g += glob.glob(data_path + '/*.dcm')
# Printing out the first 5 file names for verification
print ("Total of %d DICOM images.\nFirst 5 filenames:" % len(g))
print ('\n'.join(g[:5]))

def load_scan(path):
    slices = [pydicom.dcmread(os.path.join(path, s)) for s in os.listdir(path)]
    slices.sort(key = lambda x: int(x.InstanceNumber))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

    for s in slices:
        s.SliceThickness = slice_thickness

    return slices

def get_pixels_hu(scans):
    image = np.stack([s.pixel_array for s in scans])
    image = image.astype(np.int16)
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope

    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)

    image += np.int16(intercept)

    return np.array(image, dtype=np.int16)

id=0
patient = load_scan(data_path)
imgs = get_pixels_hu(patient)


np.save(output_path + "fullimages_%d.npy" % (id), imgs)

file_used=output_path+"fullimages_%d.npy" % id
imgs_to_process = np.load(file_used).astype(np.float64)

plt.hist(imgs_to_process.flatten(), bins=50, color='c')
plt.xlabel("Hounsfield Units (HU)")
plt.ylabel("Frequency")
plt.show()


id = 0
imgs_to_process = np.load(output_path+'fullimages_{}.npy'.format(id))
# showing every 3rd Slice
def sample_stack(stack, rows=5, cols=5, start_with=0, show_every=3):
    fig,ax = plt.subplots(rows,cols,figsize=[12,12])
    for i in range(rows*cols):
        ind = start_with + i*show_every
        ax[int(i/rows),int(i % rows)].set_title('slice %d' % ind)
        ax[int(i/rows),int(i % rows)].imshow(stack[ind],cmap='gray')
        ax[int(i/rows),int(i % rows)].axis('off')
    plt.show()


sample_stack(imgs_to_process)


print ("Slice Thickness: %f" % patient[0].SliceThickness)
print ("Pixel Spacing (row, col): (%f, %f) " % (patient[0].PixelSpacing[0], patient[0].PixelSpacing[1]))

id = 0
imgs_to_process = np.load(output_path+'fullimages_{}.npy'.format(id))
def resample(image, scan, new_spacing=[1,1,1]):
    # Determining current pixel spacing
    spacing = map(float, ([scan[0].SliceThickness] + list(scan[0].PixelSpacing)))
    spacing = np.array(list(spacing))

    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor

    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)

    return image, new_spacing

print ("Shape before resampling\t", imgs_to_process.shape)
imgs_after_resamp, spacing = resample(imgs_to_process, patient, [1,1,1])
print ("Shape after resampling\t", imgs_after_resamp.shape)

# Applying various filters on a single image before applying on all the images in the DataSet
img = imgs_after_resamp[19]

from scipy import ndimage, misc

result = ndimage.median_filter(img, size=4)
fig = plt.figure()
plt.gray()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
ax1.imshow(img)
ax2.imshow(result)
plt.show()


result = ndimage.sobel(img)
fig = plt.figure()
plt.gray()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
ax1.imshow(img)
ax2.imshow(result)
plt.show()


fig = plt.figure()
plt.gray()
result = ndimage.gaussian_filter(img,1)
ax1 = fig.add_subplot(121)
ax1.imshow(result)
plt.show()


fig = plt.figure()
plt.gray()
result = ndimage.grey_closing(img,3)
ax1 = fig.add_subplot(121)
ax1.imshow(result)
plt.show()


def make_mask(img, display = False):
    # for noise removal
    eroded = morphology.erosion(img,np.ones([3,3]))
    dilation = morphology.dilation(eroded,np.ones([3,3]))
    # Filters for further enhancement
    result = ndimage.grey_closing(dilation,2)
    result = ndimage.median_filter(result, size=3)
    result = ndimage.gaussian_filter(result,2)
    result = ndimage.grey_closing(img,5)
    return result


masked = []
# applying to all the images
for img in imgs_after_resamp:
    masked.append(make_mask(img))

sample_stack(masked, show_every=5)

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# The threshold of -300 HU is fine for visualizing chest CT scans but change it if you going to use MRI (check your intensity values distribution) or binary volumes (threshold =0).
def make_mesh(image, threshold=0, step_size=1):
    print ("Transposing surface")
    p = image.transpose(2,1,0)

    print ("Calculating surface")
    verts, faces, norm, val = measure.marching_cubes_lewiner(p, threshold, step_size=step_size, allow_degenerate=True)
    return verts, faces

def plotly_3d(verts, faces):
    x,y,z = zip(*verts)

    print ("Drawing")

    colormap=['rgb(236, 236, 212)','rgb(236, 236, 212)']

    fig = create_trisurf(x=x,
                        y=y,
                        z=z,
                        plot_edges=False,
                        colormap=colormap,
                        simplices=faces,
                        backgroundcolor='rgb(64, 64, 64)',
                        title="Interactive Visualization")
    iplot(fig)

def plt_3d(verts, faces):
    print ("Drawing")
    x,y,z = zip(*verts)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces], linewidths=0.05, alpha=1)
    face_color = '#5b5348'
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)

    ax.set_xlim(0, max(x))
    ax.set_ylim(0, max(y))
    ax.set_zlim(0, max(z))
    ax.set_fc((0.7, 0.7, 0.7))
    plt.show()


np.save(output_path + "Mask1_%d.npy" % (id), imgs)
file_used2 = output_path+"Mask1_%d.npy" % id
maskedI = np.load(file_used2).astype(np.float64)
maskedImgs, spacing2 = resample(maskedI, patient, [1,1,1])


v, f = make_mesh(maskedImgs, 300)
plt_3d(v, f)
# for Interactive 3D visualization
# v, f = make_mesh(imgs_after_resamp, 300, 6)
# plotly_3d(v, f)

# Creation of the Model in STL format
from stl import mesh
shape = mesh.Mesh(np.zeros(f.shape[0], dtype=mesh.Mesh.dtype))
for i, a in enumerate(f):
    for j in range(3):
        shape.vectors[i][j] = v[a[j], :]

shape.save('Bone.stl')

# Creating a new plot
figure = plt.figure()
axes = mplot3d.Axes3D(figure)

# Loading the STL files and adding the vectors to the plot
BoneMesh = mesh.Mesh.from_file('Bone.stl')
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(BoneMesh.vectors))
scale = BoneMesh.points.flatten()
axes.auto_scale_xyz(scale, scale, scale)

plt.show()
