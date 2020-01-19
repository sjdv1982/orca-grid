isolevel = parseFloat(ctx.isolevel.value)
grid.addRepresentation("dot", {
    radius:0.1,
    pointSize: 0.2,
    thresholdMin:90,
    thresholdType: "value",
    color:"blue"
  })
  grid.addRepresentation("surface", {
    contour: true,
    isolevel: isolevel
  })
  pdb.addRepresentation("cartoon", {
    opacity: 0.5
  })
