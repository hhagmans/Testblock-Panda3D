import Items,Bag

class Player():
    """ Erstellt den Spieler mit seinen Standardattributen, nur fuer den Spielstart vorgesehen"""
    def __init__(self,Actor):
        self.name = "Spieler 1"
        self.energie = 100
        self.maxenergie = 100
        self.mana = 50
        self.maxmana = 50
        self.angriff = 5
        self.verteidigung = 5
        self.geschicklichkeit = 5
        self.tempo = 5
        self.inventar = Bag.Tasche(4,4,4,4)
        self.waffe = Items.Nichts()
        self.ruestung = Items.Nichts()
        self.hose = Items.Nichts()
        self.schuhe = Items.Nichts()
        self.helm = Items.Nichts()
        self.actor = Actor
