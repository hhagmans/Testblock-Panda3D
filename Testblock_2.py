# -*- coding: utf-8 -*-

import direct.directbase.DirectStart
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import random, sys, os, math
from pandac.PandaModules import Texture, TextureStage
from panda3d.ai import *

SPEED = 0.5

class World(DirectObject):

    def __init__(self):

        self.switchState = True
        self.switchCam = False
        self.path_no = 1
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        base.win.setClearColor(Vec4(0,0,0,1))

        self.environ = loader.loadModel("models/world")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        self.pointer = loader.loadModel("models/arrow")
        self.pointer.setColor(1,0,0)
        self.pointer.setPos(-7.5,-1.2,0)
        self.pointer.setScale(3)
 
        self.pointer1 = loader.loadModel("models/arrow")
        self.pointer1.setColor(1,0,0)
        self.pointer1.setPos(-98.64,-20.60,0)
        self.pointer1.setScale(3)

 
        self.spieler = Actor("models/box.x")
        self.spieler.reparentTo(render)
        spielerStartPos = (-107.575, 26.6066, -0.490075)
        self.spieler.setPos(spielerStartPos)
        
        # Erstellt Gegner
        
        self.gegner = Actor("models/box.x")
        self.gegner.reparentTo(render)
        gegnerStartPos = (0, 12, 3.3)
        self.gegner.setPos(gegnerStartPos)
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Handling der Usereingaben für Bewegung

        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

        taskMgr.add(self.move,"moveTask")

        self.isMoving = False

        # Kameraeinstellungen
        
        base.disableMouse()
        base.camera.setPos(self.spieler.getX(),self.spieler.getY()+10,2)
        
        # Kollisionserkennung, um auf dem Boden zu laufen. Der Collisionray
        # erkennt die Hoehe des Gelaendes und wenn ein Objekt da ist, wird 
        # die Bewegung als illegal gewertet.

        self.cTrav = CollisionTraverser()

        self.spielerGroundRay = CollisionRay()
        self.spielerGroundRay.setOrigin(0,0,1000)
        self.spielerGroundRay.setDirection(0,0,-1)
        self.spielerGroundCol = CollisionNode('spielerRay')
        self.spielerGroundCol.addSolid(self.spielerGroundRay)
        self.spielerGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.spielerGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.spielerGroundColNp = self.spieler.attachNewNode(self.spielerGroundCol)
        self.spielerGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.spielerGroundColNp, self.spielerGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

        self.gegnerGroundRay = CollisionRay()
        self.gegnerGroundRay.setOrigin(0,0,1000)
        self.gegnerGroundRay.setDirection(0,0,-1)
        self.gegnerGroundCol = CollisionNode('gegnerRay')
        self.gegnerGroundCol.addSolid(self.gegnerGroundRay)
        self.gegnerGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.gegnerGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.gegnerGroundColNp = self.gegner.attachNewNode(self.gegnerGroundCol)
        self.gegnerGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.gegnerGroundColNp, self.gegnerGroundHandler)

        self.setAI()
        
        # Licht
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(-5, -5, -5))
        directionalLight.setColor(Vec4(1, 1, 1, 1))
        directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))
    
    # Erkennt den Status der Eingabe
    def setKey(self, key, value):
        self.keyMap[key] = value
    

    # Mit den Pfeiltasten kann der Spieler bewegt werden
    def move(self,task):

        print globalClock.getFrameTime()
        
        # cam-left Key: Kamera nach links
        # cam-right Key: Kamera nach rechts
        base.camera.lookAt(self.spieler)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        # Speichert die Startposition, damit der Spieler zurueckgesetzt
        # werden kann, sollte er irgendwo runterfallen

        startpos = self.spieler.getPos()

        # Wenn einer der Move Keys gedrueckt wird, wird der Spieler
        # in die ensprechende Richtung bewegt

        if (self.keyMap["left"]!=0):
            self.spieler.setH(self.spieler.getH() + 150 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.spieler.setH(self.spieler.getH() - 150 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.spieler.setY(self.spieler, -12 * globalClock.getDt())


        # Wenn die Kamera zu weit weg ist, zoom heran.
        # Wenn die Kamera zu nah dran ist, zoom weg.

        camvec = self.spieler.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0

        # Start der Kollisionserkennung

        self.cTrav.traverse(render)

        # Aendert die Z Koordinate des Spielers. Wenn er etwas trifft, bewegt
        # ihn entsprechend, wenn er nichts trifft, setzt die Koordinate 
        # auf den Stand des letzten Frames
        entries = []
        for i in range(self.spielerGroundHandler.getNumEntries()):
            entry = self.spielerGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.spieler.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.spieler.setPos(startpos)

        # Haelt die Kamera einen Schritt über dem Boden
        # oder zwei Schritte ueber dem Spieler, je nachdem, was groesser ist.
        
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
        if (base.camera.getZ() < self.spieler.getZ() + 2.0):
            base.camera.setZ(self.spieler.getZ() + 2.0)
            
        # Die Kamera soll in die Richtung des Spielers gucken, aber auch
        # immer horizontal bleiben.
        
        self.floater.setPos(self.spieler.getPos())
        self.floater.setZ(self.spieler.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        return Task.cont

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def gegnermove(self):
 
        # Get the time elapsed since last frame. We need this
        # for framerate-independent movement.
        elapsed = globalClock.getDt()

        startpos = self.gegner.getPos()
 
        # Adjust gegner's Z coordinate.  If gegner's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.
 
        self.cTrav.traverse(render)
 
        entries = []
        for i in range(self.gegnerGroundHandler.getNumEntries()):
            entry = self.gegnerGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.gegner.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.gegner.setPos(startpos)

 
        self.gegner.setP(0)
        return Task.cont
        
    def setAI(self):
        #Creating AI World
        self.AIworld = AIWorld(render)
 
        self.accept("space", self.setMove)
        self.AIchar = AICharacter("gegner",self.gegner, 60, 2, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
 
        self.AIbehaviors.initPathFind("models/navmesh.csv")
 
        #AI World update        
        taskMgr.add(self.AIUpdate,"AIUpdate")
 
    def setMove(self):
        self.AIbehaviors.pathFindTo(self.pointer)
 
    #to update the AIWorld    
    def AIUpdate(self,task):
        self.AIworld.update()
        self.gegnermove()
 
        if(self.path_no == 1 and self.AIbehaviors.behaviorStatus("pathfollow") == "done"):
           self.path_no = 2  
           self.AIbehaviors.pathFindTo(self.pointer1, "addPath")
           print("inside")
 
        if(self.path_no == 2 and self.AIbehaviors.behaviorStatus("pathfollow") == "done"):
           print("inside2")
           self.path_no = 1  
           self.AIbehaviors.pathFindTo(self.pointer, "addPath")
 
        return Task.cont


w = World()
run()

