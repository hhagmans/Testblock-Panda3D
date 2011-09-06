class Schwert():
    """ Erstellt ein Item vom Typ Schwert"""
    def __init__(self):
        self.ID = 0
        self.typ = "Waffe"
        self.name = "Schwert"
        zeile1 = [1]
        zeile2 = [1]
        self.spalte = [zeile1,zeile2]
        self.stapelbar = False
        self.angriff = 4
        
        
class Dolch():
    """ Erstellt ein Item vom Typ Dolch"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Waffe"
        self.name = "Dolch"
        zeile1 = [1]
        self.spalte = [zeile1]
        self.stapelbar = False
        self.angriff = 2
    
class Axt():
    """ Erstellt ein Item vom Typ Axt"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Waffe"
        self.name = "Axt"
        zeile1 = [1,1]
        zeile2 = [0,1]
        zeile3 = [0,1]
        self.spalte = [zeile1,zeile2,zeile3]
        self.stapelbar = False
        self.angriff = 5
    
class Ruestung():
    """ Erstellt ein Item vom Typ Ruestung"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Kleidung"
        self.name = "Ruestung"
        zeile1 = [1,1]
        zeile2 = [0,1]
        self.spalte = [zeile1,zeile2]
        self.stapelbar = False
        self.verteidigung = 5

            
class Hose():
    """ Erstellt ein Item vom Typ Hose"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Kleidung"
        self.name = "Hose"
        zeile1 = [1]
        zeile2 = [1]
        self.spalte = [zeile1,zeile2]
        self.stapelbar = False
        self.verteidigung = 3
            
class Handschuhe():
    """ Erstellt ein Item vom Typ Handschuhe"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Kleidung"
        self.name = "Handschuhe"
        zeile1 = [1]
        self.spalte = [zeile1]
        self.stapelbar = False
        self.verteidigung = 2
            
class Heiltrank():
    """ Erstellt ein Item vom Typ Heiltrank"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Energie"
        self.name = "Heiltrank"
        zeile1 = [1]
        self.spalte = [zeile1]
        self.stapelbar = True
        self.anzahl = 1
        self.maxanzahl = 20
        self.wert = 20
            
class Manatrank():
    """ Erstellt ein Item vom Typ Manatrank"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Mana"
        self.name = "Manatrank"
        zeile1 = [1]
        self.spalte = [zeile1]
        self.stapelbar = True
        self.anzahl = 1
        self.maxanzahl = 20
        self.wert = 20
            
class Schriftrolle():
    """ Erstellt ein Item vom Typ Schriftrolle"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Sonstiges"
        self.name = "Schriftrolle"
        zeile1 = [1]
        self.spalte = [zeile1]
        self.stapelbar = True
        self.anzahl = 1
        self.maxanzahl = 20

class Nichts():
    """ Erstellt ein Item vom Typ Schriftrolle"""    
    def __init__(self):
        self.ID = 0
        self.typ = "Sonstiges"
        self.name = "Nichts"
        zeile1 = [1]
        self.spalte = [zeile1]
        self.stapelbar = False
        self.wert = 0
