class Goblin():
    """ Erstellt Gegner vom Typ Goblin mit seinen Standardattributen"""
    def __init__(self,Actor):
        self.name = "Goblin"
        self.energie = 20
        self.maxenergie = 20
        self.angriff = 2
        self.verteidigung = 2
        self.geschicklichkeit = 3
        self.tempo = 2
        self.actor = Actor
        
class Ork():
    """ Erstellt Gegner vom Typ Ork mit seinen Standardattributen"""
    def __init__(self,Actor):
        self.name = "Ork"
        self.energie = 25
        self.maxenergie = 25
        self.angriff = 4
        self.verteidigung = 2
        self.geschicklichkeit = 2
        self.tempo = 2
        self.actor = Actor
        
class Troll():
    """ Erstellt Gegner vom Typ Troll mit seinen Standardattributen"""
    def __init__(self,Actor):
        self.name = "Troll"
        self.energie = 30
        self.maxenergie = 30
        self.angriff = 5
        self.verteidigung = 3
        self.geschicklichkeit = 1
        self.tempo = 1
        self.actor = Actor
