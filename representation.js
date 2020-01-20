isolevel = parseFloat(ctx.isolevel.value)
grid.addRepresentation("dot", {
    radius:0.1,
    pointSize: 2,
    thresholdMin:5,
    thresholdType: "value",
    color:"blue"
  })
  grid.addRepresentation("surface", {
    contour: true,
    isolevel: isolevel,
  })
  pdb.addRepresentation("spacefill", {
    opacity: 0.3
  })
