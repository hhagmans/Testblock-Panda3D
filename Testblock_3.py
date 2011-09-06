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
import random, sys, os, math, Battle, Monster, Players, Bag
from pandac.PandaModules import Texture, TextureStage
from panda3d.ai import *

SPEED = 0.5

class World(DirectObject):

    def __init__(self):

        self.switchState = True
        self.switchCam = False
        self.kampf = False
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        base.win.setClearColor(Vec4(0,0,0,1))

        self.environ = loader.loadModel("models/world")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)

 
        self.spieler = Players.Player(Actor("models/box.x"))
        self.spieler.actor.reparentTo(render)
        spielerStartPos = (-107.575, 26.6066, -0.490075)
        self.spieler.actor.setPos(spielerStartPos)
        
        # Erstellt Gegner
        
        self.gegner = Monster.Goblin(Actor("models/box.x"))
        self.gegner.actor.reparentTo(render)
        gegnerStartPos = (-45, 15, 3.3)
        self.gegner.actor.setPos(gegnerStartPos)
        
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
        self.accept("k", self.setKey, ["kampfAus",1])
        self.accept("k-up", self.setKey, ["kampfAus",0])

        taskMgr.add(self.move,"moveTask")
        taskMgr.add(self.erkenneKampf,"Kampferkennung")

        self.isMoving = False

        # Kameraeinstellungen
        
        base.disableMouse()
        base.camera.setPos(self.spieler.actor.getX(),self.spieler.actor.getY()+10,2)
        
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
        self.spielerGroundColNp = self.spieler.actor.attachNewNode(self.spielerGroundCol)
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
        self.gegnerGroundColNp = self.gegner.actor.attachNewNode(self.gegnerGroundCol)
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

        # cam-left Key: Kamera nach links
        # cam-right Key: Kamera nach rechts
        base.camera.lookAt(self.spieler.actor)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())


        # Speichert die Startposition, damit der Spieler zurueckgesetzt
        # werden kann, sollte er irgendwo runterfallen

        startpos = self.spieler.actor.getPos()

        # Wenn einer der Move Keys gedrueckt wird, wird der Spieler
        # in die ensprechende Richtung bewegt

        if (self.keyMap["left"]!=0):
            self.spieler.actor.setH(self.spieler.actor.getH() + 150 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.spieler.actor.setH(self.spieler.actor.getH() - 150 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.spieler.actor.setY(self.spieler.actor, -12 * globalClock.getDt())


        # Wenn die Kamera zu weit weg ist, zoom heran.
        # Wenn die Kamera zu nah dran ist, zoom weg.

        camvec = self.spieler.actor.getPos() - base.camera.getPos()
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
            self.spieler.actor.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.spieler.actor.setPos(startpos)

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
        if (base.camera.getZ() < self.spieler.actor.getZ() + 2.0):
            base.camera.setZ(self.spieler.actor.getZ() + 2.0)
            
        # Die Kamera soll in die Richtung des Spielers gucken, aber auch
        # immer horizontal bleiben.
        
        self.floater.setPos(self.spieler.actor.getPos())
        self.floater.setZ(self.spieler.actor.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        return Task.cont


    def gegnermove(self):
 
        # Zeit seit dem letzten Frame. Benötigt fuer
        # framerateunabhaengige Bewegung.
        elapsed = globalClock.getDt()

        startpos = self.gegner.actor.getPos()
 
        # Aendert die Z Koordinate des Gegners. Wenn er etwas trifft, bewegt
        # ihn entsprechend, wenn er nichts trifft, setzt die Koordinate 
        # auf den Stand des letzten Frames
 
        self.cTrav.traverse(render)
 
        entries = []
        for i in range(self.gegnerGroundHandler.getNumEntries()):
            entry = self.gegnerGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.gegner.actor.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.gegner.actor.setPos(startpos)

 
        self.gegner.actor.setP(0)
        if self.gegner.energie == 0:
            return Task.done
        else:
            return Task.cont
        
    def setAI(self):
        # Erstellt die AI World
        self.AIworld = AIWorld(render)
 
        self.AIchar = AICharacter("gegner",self.gegner.actor, 60, 2, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
 
        self.AIbehaviors.wander(5, 0, 10, 1.0)
 
        #AI World update zum Tasknamager hinzufügen       
        taskMgr.add(self.AIUpdate,"AIUpdate")
 
 
    # Update der AI World   
    def AIUpdate(self,task):
        if self.kampf == False:
            self.AIworld.update()
            self.gegnermove()
 
        return Task.cont

    def erkenneKampf(self,task):
        if (self.spieler.actor.getX() - self.gegner.actor.getX() < 4
        and self.spieler.actor.getX() - self.gegner.actor.getX() > -4
        and self.kampf == False):
            self.kampf = True
            self.startzeit = globalClock.getLongTime()
        if self.kampf == True:
            self.Kampf(self)
        if self.gegner.energie == 0:
            return Task.done
        else:
            return Task.cont

    def Kampf(self,task):
        if ((int(globalClock.getLongTime()) - int(self.startzeit)) % 5 == 0
        and self.kampf == True):
            erg = Battle.Kampf(self.spieler,self.gegner)
            self.spieler = erg[0]
            self.gegner = erg[1]
            self.kampf = erg[2]
            self.startzeit -= 1
            if self.spieler.energie == 0:
                sys.exit
            elif self.gegner.energie == 0:
                self.kampf = False
                self.gegner.actor.detachNode()
            
        
w = World()
run()

