# fixlerWeightHammer
A simple, solid, weight hammer, for smoothing skin weights in Autodesk Maya.

There are a number of useful commands in this tiny library, but they're mostly
there to serve the weight averager. The weight averager works on object, face,
edge, and vert selections, and any combination thereof.

## Usage
1. Put this library somewhere on your Maya/Python path.
2. Import the library
3. Select verts, edges, and/or faces you want to hammer¹
4. Call `averageVertWeightsOnSelection()`

It's helpful to make it a shelf button, or link it to a hotkey.

For low-res rigs, I like to set weights in key locations with the component
editor, then use the weight hammer to blend both those locations (where it
makes sense to), and the areas between them.

¹ hammer = here, smoothing out the skin weights on selected/contained verts
