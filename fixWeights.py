'''
Copyright (c) 2013 Gary Fixler
          gfixler@gmail.com
'''

try:
    import maya.cmds as cmds
except ImportError:
    print 'WARNING (%s): failed to load maya.cmds module.' % __file__

try:
    import maya.mel as mel
except ImportError:
    print 'WARNING (%s): failed to load maya.mel module.' % __file__

import math


# POLY TOOLS (pulled from poly.py in gmaya library, copyright (c) 2013 Gary Fixler)

def getMeshShapeFromVert (vert):
    obj = vert.split('.')[0]
    if cmds.objectType(obj) == 'mesh':
        return obj
    shape = cmds.listRelatives(obj, shapes=True)[0]
    return shape

def getMeshFromMeshShape (meshShape):
    return cmds.listRelatives(meshShape, parent=True, fullPath=True)[0]

def convertVertsToEdges (verts):
    if not verts:
        return []
    edges = cmds.polyListComponentConversion(verts,
            fromVertex=True, toEdge=True)
    return cmds.ls(edges, flatten=True)

def convertEdgesToVerts (edges):
    if not edges:
        return []
    verts = cmds.polyListComponentConversion(edges,
            fromEdge=True, toVertex=True)
    return cmds.ls(verts, flatten=True)

def convertFacesToVerts (faces):
    if not faces:
        return []
    verts = cmds.polyListComponentConversion(faces,
            fromFace=True, toVertex=True)
    return cmds.ls(verts, flatten=True)

def getSelectedVerts ():
    return cmds.filterExpand(selectionMask=31,
            expand=True, fullPath=True) or []

def getSelectedEdges ():
    return cmds.filterExpand(selectionMask=32,
            expand=True, fullPath=True) or []

def getSelectedFaces ():
    return cmds.filterExpand(selectionMask=34,
            expand=True, fullPath=True) or []

def getPolySelectionInVerts ():
    verts = getSelectedVerts()
    edges = getSelectedEdges()
    faces = getSelectedFaces()
    edgeVerts = convertEdgesToVerts(edges)
    faceVerts = convertFacesToVerts(faces)
    return list(set(verts) | set(edgeVerts) | set(faceVerts))

def getVertsConnectedToVerts (vert):
    edges = convertVertsToEdges(vert)
    verts = convertEdgesToVerts(edges)
    return sorted(list(set(verts) - set(cmds.ls(vert))))

def getVertPosition (vert):
    return cmds.xform(vert, query=True, worldSpace=True, translation=True)

def getVertDistance (vertA, vertB):
    posA = getVertPosition(vertA)
    posB = getVertPosition(vertB)
    ax, ay, az = posA
    bx, by, bz = posB
    return math.sqrt((ax-bx)**2 + (ay-by)**2 + (az-bz)**2)


# SKIN TOOLS (pulled from skin.py in gmaya library, copyright (c) 2013 Gary Fixler)

def getSkinFromMesh (mesh):
    return mel.eval('findRelatedSkinCluster %s;' % mesh)

def getSkinFromVert (vert):
    meshShape = getMeshShapeFromVert(vert)
    mesh = getMeshFromMeshShape(meshShape)
    skin = getSkinFromMesh(mesh)
    return skin

def getVertWeights (vert):
    skinCluster = getSkinFromVert(vert)
    infs = cmds.skinCluster(vert, query=True, influence=True)
    values = cmds.skinPercent(skinCluster, vert, query=True, value=True)
    weights = dict(zip(infs, values))
    return weights

def getVertInfluencesFromVerts (targetVert, verts):
    distances = [getVertDistance(targetVert, vert) for vert in verts]
    totalDistance = sum(distances)
    scaleFactor = (len(distances) - 1) * totalDistance
    return [(totalDistance - distance) / scaleFactor for distance in distances]

def getAverageVertWeights (targetVert, maxInfs=4):
    verts = getVertsConnectedToVerts(targetVert)
    effects = getVertInfluencesFromVerts(targetVert, verts)
    weights = {}
    for vert, effect in zip(verts, effects):
        for inf, weight in getVertWeights(vert).items():
            currentWeight = weights.get(inf, 0)
            weights[inf] = currentWeight + weight * effect
    weights = weights.items()
    if len(weights) > maxInfs:
        weights.sort(key=lambda x:x[1])
        weights = weights[maxInfs:]
    return weights

def averageVertWeights (targetVerts, *args, **kwargs):
    targetVerts = cmds.ls(targetVerts, flatten=True)
    allWeights = {}
    for targetVert in targetVerts:
        skinCluster = getSkinFromVert(targetVert)
        if not skinCluster in allWeights:
            allWeights[skinCluster] = {}
        averageWeights = getAverageVertWeights(targetVert, *args, **kwargs)
        allWeights[skinCluster][targetVert] = averageWeights
    for skinCluster, allWeights in allWeights.items():
        for targetVert, weights in allWeights.items():
            cmds.skinPercent(skinCluster, targetVert, normalize=False,
                    zeroRemainingInfluences=False, transformValue=weights)

def averageVertWeightsOnSelection (*args, **kwargs):
    selectedVerts = getPolySelectionInVerts()
    averageVertWeights(list(selectedVerts))

