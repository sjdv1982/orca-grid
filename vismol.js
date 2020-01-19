
// Create NGL Stage object
var stage = new NGL.Stage("viewport");

// Handle window resizing
window.addEventListener("resize", function (event) {
  stage.handleResize();
}, false);


grid = null
pdb = null

ctx = connect_seamless("ws://localhost:5138", "http://localhost:5813", "ctx");
ctx.self.onsharelist = function(sharelist) {
  ctx.isolevel.onchange = function() {
    loadNGL()
  }
}

function loadNGL() {
  Promise.all([
    stage.removeAllComponents(),
    stage.loadFile("./grid.mrc"),  
    stage.loadFile("./pdbA.pdb")
  ]).then(function (l) {
    grid = l[0]
    c = grid.getCenter()
    grid.setTransform( grid.transform.makeTranslation(-c.x, -c.y, -c.z) )
    pdb = l[1]
    eval(ctx["representation.js"])
    stage.autoView()
  })
}
loadNGL()
