isolevel = parseFloat(ctx.isolevel.value)
grid.addRepresentation("dot", {
  radius:0.1,
  pointSize: voxelsize,
  thresholdMin:0.01,
  thresholdType: "value",
  color:"blue"
})
grid.addRepresentation("surface", {
  contour: true,
  isolevel: isolevel,
})
pdb.addRepresentation("spacefill", {
  opacity: 0.2
})
