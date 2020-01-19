isolevel = parseFloat(ctx.isolevel.value)
grid.addRepresentation("dot", {
    radius:5,
    color:"blue"
  })
  grid.addRepresentation("surface", {
    contour: true,
    isolevel: isolevel
  })
  pdb.addRepresentation("spacefill", {
    opacity: 0.5
  })
