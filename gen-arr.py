import numpy as np
import scipy.signal
from scipy.spatial import cKDTree as KDTree
import itertools

half_sqrt_three = np.sqrt(3) / 2

coor_tree = KDTree(coor)

mins = coor.min(axis=0)
maxes = coor.max(axis=0)
bounds=np.max([-mins, maxes],axis=0)
bounds += clash_threshold
bounds += extrusion
bounds -= 0.5 * voxelsize

superdivision_level = 0
while 1:
    voxsize = 2**superdivision_level * voxelsize
    if clash_threshold - voxsize * half_sqrt_three < 0:
        break
    superdivision_level += 1

superdivision_level = 1
#print("SUPER!", superdivision_level)

center = (bounds/voxelsize+0.999).astype(int)
dims = center * 2
first_voxel = -(center - 0.5) * voxelsize
arr = np.zeros(shape=dims, dtype=bool)

supervoxelsize = 2**superdivision_level * voxelsize
supercenter = ((bounds+voxelsize)/supervoxelsize+0.999).astype(int)
superdims = supercenter * 2
first_supervoxel = -(supercenter - 0.5) * supervoxelsize

def cartesian_coord(*arrays):
    # https://stackoverflow.com/a/25463061
    grid = np.meshgrid(*arrays)        
    coord_list = [entry.ravel() for entry in grid]
    points = np.vstack(coord_list).T
    return points

points0 = cartesian_coord(
    np.arange(superdims[0]),
    np.arange(superdims[1]),
    np.arange(superdims[2]),
)
points0 = points0[points0[:,0].argsort(kind='mergesort')]

points = points0 * supervoxelsize + first_supervoxel
result = []

sub = np.array(list(itertools.product(
    [-0.25, 0.25],
    [-0.25, 0.25],
    [-0.25, 0.25]
)))

def subdivide(points, old_voxelsize):
    sub2 = sub * old_voxelsize
    newpoints = points[:, None, :] + sub2[None, :, :] 
    return newpoints.reshape(-1, 3)  

def classify(points, curr_voxelsize):
    matches = coor_tree.query_ball_point(
        points, 
        clash_threshold, 
        return_length=True
    )    

    match_mask = matches.astype(bool)
    delta = curr_voxelsize * half_sqrt_three
    possible_points = points[match_mask]
    if delta > clash_threshold:
        return possible_points, None
    new_matches = coor_tree.query_ball_point(
        possible_points, 
        clash_threshold - delta, 
        return_length=True
    )
    new_match_mask = new_matches.astype(bool)
    definite_points = possible_points[new_match_mask]
    ambiguous_points = possible_points[~new_match_mask]
    return ambiguous_points, definite_points

def set_grid_blocks(blocks, block_superdivision):
    #print("SET GRID BLOCKS", blocks.shape, block_superdivision)
    points = blocks
    for n in range(block_superdivision, 0, -1):
        curr_voxelsize = voxelsize * 2**n
        points = subdivide(points, curr_voxelsize)
    indices = np.round(
        (points - first_voxel) / voxelsize
    ).astype(int)
    indices = indices[indices[:, 0] < dims[0]]
    indices = indices[indices[:, 0] >= 0]
    indices = indices[indices[:, 1] < dims[1]]
    indices = indices[indices[:, 1] >= 0]
    indices = indices[indices[:, 2] < dims[2]]
    indices = indices[indices[:, 2] >= 0]
    arr[indices[:,0], indices[:,1], indices[:,2]] = 1

#set_grid_blocks(points, superdivision_level) 

match_points = []
curr_points = points
for n in range(superdivision_level, -1, -1):
    curr_voxelsize = 2**n * voxelsize
    if not len(curr_points):
        ambiguous_points = []
        continue
    ambiguous_points, definite_points = classify(
        curr_points, curr_voxelsize
    )
    ldef = None if definite_points is None else len(definite_points)
    #print("SUPERDIV", n, curr_voxelsize, len(curr_points), len(ambiguous_points), ldef)
    if definite_points is not None and len(definite_points):
        set_grid_blocks(definite_points, n)
    if n > 0:
        curr_points = subdivide(ambiguous_points, curr_voxelsize)



subdivision_level = 0
ambiguous_subpoints = ambiguous_points
ambiguous_subpoint_index = np.arange(len(ambiguous_points))
while len(ambiguous_subpoints):
    subdivision_level += 1
    curr_voxelsize = 0.5**subdivision_level * voxelsize
    curr_subpoints = subdivide(ambiguous_subpoints, curr_voxelsize)
    curr_subpoint_index = np.repeat(ambiguous_subpoint_index, 8)
    #print("SUBDIV", subdivision_level,curr_voxelsize, len(curr_subpoints), len(np.unique(curr_subpoint_index)))
    matches = coor_tree.query_ball_point(
        curr_subpoints, 
        clash_threshold, 
        return_length=True
    )
    match_mask = matches.astype(bool)
    impossible_index = np.unique(curr_subpoint_index[~match_mask])
    #print("ELIMINATE", len(impossible_index))
    subpoint_mask = np.isin(curr_subpoint_index, impossible_index, invert=True)
    #print("FILTER", subpoint_mask.sum(), len(curr_subpoints))
    keep_mask = subpoint_mask & match_mask
    assert keep_mask.sum() == subpoint_mask.sum()

    curr_subpoints2 = curr_subpoints[keep_mask]
    curr_subpoint_index2 = curr_subpoint_index[keep_mask]
    if not len(curr_subpoints2):
        break

    delta = curr_voxelsize * half_sqrt_three
    #print("DELTA", delta)
    if delta > clash_threshold:
        ambiguous_subpoints = curr_subpoints2
        ambiguous_subpoint_index = curr_subpoint_index2
        continue

    matches2 = coor_tree.query_ball_point(
        curr_subpoints2, 
        clash_threshold-delta, 
        return_length=True
    )
    match_mask2 = matches2.astype(bool)   
    nondefinite_index = np.unique(curr_subpoint_index2[~match_mask2])
    ambiguous_mask = np.isin(curr_subpoint_index2, nondefinite_index)
    definite_index = np.unique(curr_subpoint_index2[~ambiguous_mask])
    definite_points = ambiguous_points[definite_index]    
    if definite_points is not None and len(definite_points):        
        set_grid_blocks(definite_points, 0)
    keep_mask = ambiguous_mask & ~match_mask2
    
    ambiguous_subpoints = curr_subpoints2[keep_mask]
    ambiguous_subpoint_index = curr_subpoint_index2[keep_mask]
    #print("SELECT", len(definite_points), len(ambiguous_subpoints), len(curr_subpoints2))
    #print()

kdim0 = np.ceil(extrusion/voxelsize)
krange = np.arange(-kdim0,kdim0+1)
kdim = len(krange)
kernel = cartesian_coord(krange, krange, krange) * voxelsize
kernel = (kernel*kernel).sum(axis=1).reshape(kdim, kdim, kdim)
kernel = (kernel<(extrusion**2))

def fill_outer_shell(a):
    a[[0,-1],:,:] = 1
    a[:, [0,-1], :] = 1
    a[:, :, [0,-1]] = 1


small = 0.01
arr_extrude = scipy.signal.convolve(arr.astype(np.float32), kernel, "same")
arr_extrude = (arr_extrude > small)
solvent = np.zeros(arr.shape, bool)
fill_outer_shell(solvent)
inv_arr_extrude = (~arr_extrude) | solvent
solvent_size = solvent.sum()
neighbor_kernel = np.ones((3,3,3), np.float32)
print("conv")
while 1:
    solvent = solvent.astype(np.float32)
    solvent = scipy.signal.convolve(solvent, neighbor_kernel, "same")
    solvent = (solvent > small)
    solvent = (solvent & inv_arr_extrude)
    new_solvent_size = solvent.sum()
    print(solvent_size, new_solvent_size)
    if new_solvent_size == solvent_size:
        break
    solvent_size = new_solvent_size
solvent_extrude = scipy.signal.convolve(solvent.astype(np.float32), kernel, "same")
solvent_extrude = scipy.signal.convolve(solvent_extrude, neighbor_kernel, "same")
solvent_extrude = (solvent_extrude > small)
#result = (arr | (~solvent_extrude)).astype(np.float32)
result = (((~solvent_extrude) & arr_extrude) | arr)
print(result.shape)

while 1:
    shell = np.zeros(result.shape, bool)
    fill_outer_shell(shell)
    if (result & shell).sum():
        break
    result = result[1:-1,1:-1,1:-1]

print(result.shape)
result = result.astype(np.float32)
