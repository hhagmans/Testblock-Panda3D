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
import random, sys, os, math, Battle, Monster, Players, Bag, Items
from pandac.PandaModules import Texture, TextureStage
from panda3d.ai import *
from direct.gui.DirectGui import *

SPEED = 0.5

class World(DirectObject):

    def __init__(self):
        self.itemID = 0
        self.switchState = True
        self.iAktion = "E"
        self.altIPos = [0,0]
        self.switchCam = False
        self.kampf = Battle.Kampf()
        self.itemDa = False
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        base.win.setClearColor(Vec4(0,0,0,1))

        self.environ = loader.loadModel("models/world")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)

 
        self.spieler = Players.Player(Actor("models/box.x"))
        self.spieler.actor.reparentTo(render)
        spielerStartPos = (-107.575, 26.6066, -0.490075)
        self.spieler.actor.setPos(spielerStartPos)
        self.textObjectSpieler = OnscreenText(text = self.spieler.name+":  "+str(self.spieler.energie)+"/"+str(self.spieler.maxenergie)+" HP", pos = (-0.90, -0.98), scale = 0.07, fg = (1,0,0,1))        

        # Erstellt Gegner
        
        self.gegnerStartPos = ([(-39.1143569946,25.1781406403,-0.136657714844),
                                (-102.375793457,-30.6321983337,0.0),
                                (-56.927986145, -34.6329650879, -0.16748046875),
                                (-79.6673126221,30.8231620789,2.89721679688),
                                (-4.37648868561,30.5158863068,2.18450927734),
                                (22.6527004242,4.99837779999,3.11364746094),
                                (-23.8257598877,-7.87773084641,1.36920166016),
                                (-80.6140823364,19.5769443512,4.70764160156),
                                (-75.0773696899,-15.2991075516,6.24676513672)
                                ])
        
        gegnerPos = random.choice(self.gegnerStartPos)
        self.gegnerErstellen(gegnerPos)
        self.textObjectGegner = OnscreenText(text = str(self.gegner.name)+": "+str(self.gegner.energie)+"/"+str(self.gegner.maxenergie)+" HP", pos = (0.90, -0.98), scale = 0.07, fg = (1,0,0,1))
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        self.item = None
        
        # Handling der Usereingaben für Bewegung

        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("i", self.setKey, ["inventar",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

        self.accept("e", self.iAktionsHandler,["e"])
        self.accept("v", self.iAktionsHandler,["v"])
        self.accept("w", self.iAktionsHandler,["w"])
        
        taskMgr.add(self.move,"moveTask")
        taskMgr.add(self.erkenneKampf,"Kampferkennung")
        taskMgr.add(self.screentexts,"Screentexte")


        # Menü erstellen

        self.createMenu()
        
        # Kameraeinstellungen
        
        base.disableMouse()
        base.camera.setPos(self.spieler.actor.getX(),self.spieler.actor.getY()+10,2)
        
        self.collisionInit();
        
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

        # Hintergrund (Himmel)

        self.setupSkySphere()

    def iAktionsHandler(self,key):
        if key == "e":
            self.iAktion = "E"
        elif key == "w":
            self.iAktion = "W"
        elif key == "v":
            self.iAktion = "V"
            

    def collisionInit(self):
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


    def setupSkySphere(self):
        self.skysphere = loader.loadModel("models/LinearPinkSkySphere.bam")
        # Textur für den Himmel laden
        self.sky_tex = loader.loadTexture("Images/Sterne.jpg")
        # Himmel Textur konfigurieren
        self.skysphere.setTexture(self.sky_tex, 1)
	self.skysphere.setBin('background', 1) 
        self.skysphere.setDepthWrite(0) 
        self.skysphere.reparentTo(render)
        self.skysphere.setScale(40)
        taskMgr.add(self.skysphereTask, "SkySphere Task") 

    def skysphereTask(self, task): 
        self.skysphere.setPos(base.camera, 0, 0, 0) 
        return task.cont

    def createMenu(self):
        self.createFrame()
        itemListe = self.spieler.inventar.anzeigen(1)
        standardpos = [0.18, 0.98, 0.83]
        self.buttonListe = []
        beutelLabel = DirectLabel(text = itemListe[0][0], pos = (0.18, 0.98, 0.95), scale = 0.07, text_fg = (1,0,0,1), text_bg = (0, 50, 50, 1), textMayChange = 1)
        del itemListe [0][0]
        for zeile in range(4):
            for i in range(0,5):
                Button = DirectButton(text = itemListe [zeile] [i], pos = standardpos, scale = 0.07, text_fg = (1,0,0,1), text_bg = (0, 50, 50, 1), textMayChange = 1, extraArgs = [zeile,i], command = self.inventarAktion)
                self.buttonListe.append (Button)
                standardpos[0] += 0.25
            standardpos[0] = 0.18    
            standardpos[2] -= 0.15
            
    def createFrame(self):
        self.myFrame = DirectFrame(frameColor=(0, 50, 50, 0.5),
                      frameSize=(-1, 1, -.7, 1),
                      pos=(1, -1, 1))

    def inventarAktion(self,zeile,spalte):
        if self.iAktion == "E":
            self.spieler.inventar.entfernen(1,[zeile,spalte])
            self.myFrame.destroy()
            i = 0
            for item in self.buttonListe:
                    self.buttonListe [i].destroy()
                    i += 1
            del self.buttonListe[:]
            self.createMenu()  
        elif self.iAktion == "W":
            self.altIPos = [zeile,spalte]
        elif self.iAktion == "V":
            self.spieler.inventar.verschieben(1,1,self.altIPos,[zeile,spalte])
            self.myFrame.destroy()
            i = 0
            for item in self.buttonListe:
                    self.buttonListe [i].destroy()
                    i += 1
            del self.buttonListe[:]
            self.createMenu()        
        
        
    # Erkennt den Status der Eingabe
    def setKey(self, key, value):
        self.keyMap[key] = value

    def screentexts(self,task):
        self.textObjectSpieler.destroy()
        self.textObjectSpieler = OnscreenText(text = self.spieler.name+":  "+str(self.spieler.energie)+"/"+str(self.spieler.maxenergie)+" HP", pos = (-0.90, -0.98), scale = 0.07, fg = (1,0,0,1))
        self.textObjectGegner.destroy()
        if self.kampf.active == True:
            self.textObjectGegner = OnscreenText(text = str(self.gegner.name)+": "+str(self.gegner.energie)+"/"+str(self.gegner.maxenergie)+" HP", pos = (0.90, -0.98), scale = 0.07, fg = (1,0,0,1))
        else:
            self.textObjectGegner = OnscreenText(text = "Kein Gegner vorhanden", pos = (0.90, -0.98), scale = 0.07, fg = (1,0,0,1))
        return Task.cont

    def camera(self):
         # cam-left Key: Kamera nach links
        # cam-right Key: Kamera nach rechts
        base.camera.lookAt(self.spieler.actor)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

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

    def collisions(self,startpos):
        
        # Überprüfen auf Itemkollision
        
        if self.item <> None:
            if (self.item.actor.getX() - self.spieler.actor.getX() < 1
            and self.item.actor.getY() - self.spieler.actor.getY() < 1
            and self.item.actor.getZ() - self.spieler.actor.getZ() <1
            and self.itemDa == True):
                self.itemDa = False
                self.item.actor.detachNode()
                self.spieler.inventar.einfuegen(self.item)
                self.myFrame.destroy()
                del self.buttonListe[:]
                self.createMenu()

         # Start der Kollisionserkennung

        self.cTrav.traverse(render)


        # Aendert die Z Koordinate des Spielers. Wenn er etwas trifft, bewegt
        # ihn entsprechend, wenn er nichts trifft, setzt die Koordinate 
        # auf den Stand des letzten Frames
        self.dummyMethode(self.spielerGroundHandler, self.spieler.actor,startpos)

    
    def move(self,task):

        self.camera();
        
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

        self.collisions(startpos);

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
        self.dummyMethode(self.gegnerGroundHandler, self.gegner.actor,startpos)
 
        self.gegner.actor.setP(0)
        if self.gegner.energie == 0:
            return Task.done
        else:
            return Task.cont

    def dummyMethode(self, handler, actor,startpos):
        entries = []
        for i in range(handler.getNumEntries()):
            entry = handler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            actor.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            actor.setPos(startpos)
	
	
	
    def setAI(self):
        # Erstellt die AI World
        self.AIworld = AIWorld(render)
 
        self.AIchar = AICharacter("gegner",self.gegner.actor, 100, 0.02, 1)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
 
        self.AIbehaviors.wander(360, 0, 15, 1.0)
 
        #AI World update zum Tasknamager hinzufügen       
        taskMgr.add(self.AIUpdate,"AIUpdate")
 
 
    # Update der AI World   
    def AIUpdate(self,task):
        if self.kampf.active == False:
            self.AIworld.update()
            self.gegnermove()
 
        return Task.cont

    # Startet bei einem Abstand von 4 zwischen Spieler und Gegner einen Kampf
    def erkenneKampf(self,task):
        if (self.spieler.actor.getX() - self.gegner.actor.getX() < 4
        and self.spieler.actor.getX() - self.gegner.actor.getX() > -4
        and self.kampf.active == False):
            self.kampf.active = True
            self.startzeit = globalClock.getLongTime()
        if self.kampf.active == True:
            self.Kampf(self)
        if self.gegner.energie == 0:
            return Task.done
        else:
            return Task.cont

    def gegnerErstellen(self,pos):
        self.gegner = Monster.Goblin(Actor("models/box.x"))
        self.gegner.actor.reparentTo(render)
        self.gegner.actor.setPos(pos)
        self.gegnerAltPos = pos
        self.setAI()

    def gegnerTod(self):
        self.kampf.active = False
        itemPos = self.gegner.actor.getPos()
        self.gegner.actor.detachNode()
        self.item = Items.Axt()
        self.item.ID = self.itemID
        self.itemID += 1
        self.itemDa = True
        self.item.actor.setScale(0.3)
        self.item.actor.reparentTo(render)
        self.item.actor.setPos(itemPos)
        gegnerNeuPos = random.choice(self.gegnerStartPos)
        while gegnerNeuPos == self.gegnerAltPos:
            gegnerNeuPos = random.choice(self.gegnerStartPos)
        self.gegnerErstellen(gegnerNeuPos)

    # Lässt Spieler und Gegner nach bestimmter Zeit Aktionen ausführen. Bei Tod des
    # Gegners wird ein neuer Gegner sowie ein Item generiert
    def Kampf(self,task):
        if ((int(globalClock.getLongTime()) - int(self.startzeit)) % 5 == 0
        and self.kampf.active == True):
            erg = self.kampf.Kampf(self.spieler,self.gegner)
            self.spieler = erg[0]
            self.gegner = erg[1]
            self.startzeit -= 1
            if self.spieler.energie == 0:
                sys.exit
            elif self.gegner.energie == 0:
                self.gegnerTod();
        if self.startzeit <= 0:
            self.startzeit = globalClock.getLongTime()
            
        
w = World()
run()

