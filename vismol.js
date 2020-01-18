// Setup to load data from rawgit
NGL.DatasourceRegistry.add(
    "data", new NGL.StaticDatasource( "//cdn.rawgit.com/arose/ngl/v2.0.0-dev.32/data/" )
);

// Create NGL Stage object
var stage = new NGL.Stage( "viewport" );

// Handle window resizing
window.addEventListener( "resize", function( event ){
    stage.handleResize();
}, false );


// Code for example: color/volume

Promise.all([
  stage.loadFile("./grid.mrc"),
  stage.loadFile("./pdbA.pdb", { voxelSize: 3.54 })
]).then(function (l) {
  var grid = l[ 0 ]
  var pdb = l[ 1 ]
  grid.addRepresentation("dot", {
  })
  grid.addRepresentation("surface", {
    contour: true
  })
  pdb.addRepresentation("spacefill", {})
  stage.autoView()
})
