#####################################################
# Kurssi: AT00BT78-3005 Oliot ja tietokannat        #
# Ohjelmanimi: LT-Taso-3                            #
# Tekijä: Tuomas Nissinen                           #
#                                                   #                                            
# Vakuutan, että tämä ohjelma on minun tekemä.      #
# Työhön olen käyttänyt seuraavia lähteitä, sekä    #
# saanut apua seuraavilta henkilöiltä:              #
#                                                   #
#####################################################

import sqlite3
from pathlib import Path
from enum import Enum
from abc import ABC, abstractmethod
import getpass

SQL_YHTEYS = {
    "TIETOPOLKU": Path().joinpath("./kanta.db")
}

#----------------Luokat----------------#
class Kanta(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.__sql_yhteys = sqlite3.connect(Path().joinpath("./kanta.db"))
        self.kursori = self.__sql_yhteys.cursor()
        return None

    def luoYhteysTietokantaan(self, polku: str) -> None:
        """
        :polku: tietokanta tiedostoon
        """
        try:
            self.__sql_yhteys = sqlite3.connect(polku)
            self.kursori = self.__sql_yhteys.cursor()
        except sqlite3.Error as sqliteVirhe:
            print(sqliteVirhe)
        except Exception as virhe:
            print(virhe)
        return None

    def luoKantaLista(self, tulostus: list, sarakkeiden_maara: int, oikealle_keskitetty = 0,  sarakekentan_koko = 13) -> list:
        """
        Luo listan muotoon ["| nimike       ","| arvo         |"]
        """
        try:
            lista = []
            # luo listan sisälle listoja, joissa on käyttäjien tiedot 
            for x in tulostus:
                x = ','.join(map(str, x))
                x = x.split(",")
                lista.append(x)
                # muotoilee listat oikeaan muotoon
            for rivi in range(0,len(lista)):
                for sarake in range(0,sarakkeiden_maara):
                    if (sarake == 0 and len(lista[rivi][sarake]) > 0):
                        if (sarake >= sarakkeiden_maara - oikealle_keskitetty):
                            lista[rivi][sarake] = "|" + " "*(sarakekentan_koko-len(lista[rivi][sarake])) + lista[rivi][sarake] + " |"
                        else:
                            lista[rivi][sarake] = "| " + lista[rivi][sarake] + " "*(sarakekentan_koko-len(lista[rivi][sarake])) + "|"
                    elif (sarake >= 1 and sarakkeiden_maara > 1 and len(lista[rivi][sarake]) > 0):
                        if (sarake >= sarakkeiden_maara - oikealle_keskitetty):
                            lista[rivi][sarake] = " "*(sarakekentan_koko-len(lista[rivi][sarake])) + lista[rivi][sarake] + " |"
                        else:
                            lista[rivi][sarake] = " " + (lista[rivi][sarake] + " "*(sarakekentan_koko-len(lista[rivi][sarake])) + "|")
            return lista
        except Exception as virhe:
            print("Listan luominen epäonnistui.")
            print(virhe)
            return None

    @abstractmethod
    def luoTaulukkoKanta(self):
        pass
        
class KayttajatKanta(Kanta):
    def __init__(self) -> None:
        super().__init__()
        return None

    def luoTaulukkoKanta(self) -> None:
        try:
            # Luo Käyttäjät taulukon
            sql_lause = "CREATE TABLE IF NOT EXISTS Kayttajat("
            sql_lause += "  nimi TEXT PRIMARY KEY NOT NULL,"
            sql_lause += "  salasana TEXT NOT NULL,"
            sql_lause += "  tiimi TEXT NOT NULL,"
            sql_lause += "  rooli TEXT NOT NULL,"
            sql_lause += "  UNIQUE(salasana)"
            sql_lause += ");"
            self.kursori.execute(sql_lause) # suorittaa tietokanta komennon
        except sqlite3.Error as virhe:
            print(virhe)
        return None

    def __taulukkoLaskenta(self) -> list:
        try:
            lista = [("","",""),("Käyttäjiä", "Tiimejä", "Rooleja")]
            valiLista = ()
            sql_lause = "SELECT COUNT(ALL nimi) FROM Kayttajat"
            self.kursori.execute(sql_lause)
            valiLista += self.kursori.fetchall()[0]
            sql_lause = "SELECT COUNT(DISTINCT tiimi) FROM Kayttajat"
            self.kursori.execute(sql_lause)
            valiLista += (self.kursori.fetchall()[0])
            sql_lause = "SELECT COUNT(DISTINCT rooli) FROM Kayttajat"
            self.kursori.execute(sql_lause)
            valiLista += (self.kursori.fetchall()[0])
            lista.append(valiLista)
        except sqlite3.Error as virhe:
            print(virhe)
        return lista

    def lisaaKayttaja(self, kayttajanimi: str, tiimi: str, salasana: str) -> None:
        """
        Lisää käyttäjän tietokantaan
        """
        try:
            sql_lause = "INSERT INTO Kayttajat (nimi, salasana, tiimi, rooli) VALUES (?,?,?,?);"
            sql_data = [kayttajanimi, salasana, tiimi, "Pelaaja"]
            self.kursori.execute(sql_lause, sql_data) # suorittaa tietokanta komennon
            self.__sql_yhteys.commit() # INSERT yhteydessä oltava vahvistus
        except sqlite3.Error as virhe:
            print("Käyttäjän lisääminen ei onnistunut.")
            print(virhe)
        return None
    
    def listaaKayttajat(self) -> list:
        try:
            sql_lause = "SELECT nimi,tiimi,rooli FROM Kayttajat ORDER BY nimi ASC"
            self.kursori.execute(sql_lause)
            tulostus = self.kursori.fetchall()
            tulostus += self.__taulukkoLaskenta()
            return self.luoKantaLista(tulostus, 3)
        except sqlite3.Error as virhe:
            print("Käyttäjiä ei voitu näyttää.")
            print(virhe)
        return None
    
    def etsiTiiminJasenet(self, tiimi: str) -> list:
        try:
            sql_lause = "SELECT nimi,tiimi,rooli FROM Kayttajat WHERE tiimi = ? ORDER BY nimi ASC"
            self.kursori.execute(sql_lause, (tiimi,))
            tulostus = self.kursori.fetchall()
            lista = [("","",""),("Jäseniä", "", "")]
            sql_lause = "SELECT COUNT(ALL nimi) FROM Kayttajat WHERE tiimi = ?"
            self.kursori.execute(sql_lause,(tiimi,))
            lause = self.kursori.fetchall()[0]
            valiLista = (lause[0],"","")
            lista.append(valiLista)
            tulostus += lista
            return self.luoKantaLista(tulostus, 3)# palauttaa listan, jossa on tiimin jäsenet
        except sqlite3.Error as virhe:
            print(virhe)
        return None

    def muokkaaKayttajanTiimia(self, kayttaja: str, tiimi: str) -> None:
        try:
            sql_lause = "UPDATE Kayttajat SET tiimi = ? WHERE nimi = ?"
            self.kursori.execute(sql_lause,(tiimi,kayttaja,))
            self.__sql_yhteys.commit()
        except sqlite3.Error as virhe:
            print("Käyttäjän tiimiä ei voitu muokata.")
            print(virhe)
        return None
        
    def varmistaKayttaja(self, kayttajanimi: str) -> bool:
        try:
            sql_lause =  "SELECT * FROM Kayttajat WHERE nimi = ?"
            self.kursori.execute(sql_lause, (kayttajanimi,))
            kayttaja = self.kursori.fetchall()
            if (len(kayttaja) < 1):
                return False
            return True
        except sqlite3.Error as virhe:
            print("Käyttäjän varmistaminen epäonnistui.")
            print(virhe)
            return False

    def poistaKayttaja(self, kayttajanimi: str) -> bool:
        try:
            sql_lause = "DELETE FROM Kayttajat WHERE nimi = ?"
            self.kursori.execute(sql_lause, (kayttajanimi,))
            self.__sql_yhteys.commit()
            return True
        except sqlite3.Error as virhe:
            print("Käyttäjää ei pystytty poistamaan tietokannasta.")
            print(virhe)
        return False

class TavaratKanta(Kanta):
    def __init__(self) -> None:
        super().__init__()
        return None

    def luoTaulukkoKanta(self) -> None:
        try:
            # Luo tavarat taulukon
            sql_lause = "CREATE TABLE IF NOT EXISTS Tavarat("
            sql_lause += "  nimike TEXT PRIMARY KEY NOT NULL,"
            sql_lause += "  arvo NUMERIC NOT NULL"
            sql_lause += ");"
            self.kursori.execute(sql_lause)
            #lisätään tavaroita Tavarat taulukkoon
            tavarat = [
                    ["Kahvimuki", 1],["Haarniska", 2304],
                    ["Kala", 14.45],["Vasara",19.99],
                    ["Tulitikut",0.25],["Hammasharja",0.65],
                    ["Miekka",3680],["Taideteos",1840]
            ]
            sql_lause = "INSERT INTO Tavarat (nimike, arvo) VALUES (?,?);"
            for sql_data in tavarat:
                self.kursori.execute(sql_lause, sql_data) # suorittaa tietokanta komennon
                self.__sql_yhteys.commit() # INSERT yhteydessä oltava vahvistus
        except sqlite3.Error as virhe:
            print(virhe)
        return None
    
    def naytaTavarat(self) -> list:
        try:
            sql_lause = "SELECT * FROM Tavarat"
            self.kursori.execute(sql_lause)
            tulostus = self.kursori.fetchall()
            return self.luoKantaLista(tulostus, 2, 1)
        except sqlite3.Error as virhe:
            print("Tavaroita ei voitu näyttää.")
            print(virhe)
        return None

    def haeTuotteenArvo(self,nimike:str) -> str:
        try:
            sql_lause = "SELECT * FROM Tavarat WHERE nimike = ?"
            self.kursori.execute(sql_lause, (nimike,))
            tulostus = self.kursori.fetchall()
            lista = []
            # luo listan sisälle listoja, joissa on käyttäjien tiedot 
            for x in tulostus:
                x = ','.join(map(str, x))
                x = x.split(",")
                lista.append(x)
            if (len(lista) <= 0):
                return None
            return lista[0][1]# palauttaa hinnan merkkijonona
        except sqlite3.Error as virhe:
            print(virhe)
        return None

    def vaihdaTuotteenAro(self, tuote: str, uusi_arvo: float) -> None:
        try:
            sql_lause = "UPDATE Tavarat SET arvo = ? WHERE nimike = ?"
            self.kursori.execute(sql_lause,(uusi_arvo,tuote,))
            self.__sql_yhteys.commit()
        except sqlite3.Error as virhe:
            print("Tuotteen arvoa ei pystytty vaihtamaan.")
            print(virhe)
        return None 

class KayttajaTavaraKanta(Kanta):
    def __init__(self) -> None:
        super().__init__()
        return None

    def luoTaulukkoKanta(self) -> None:
        try:
            sql_lause = "CREATE TABLE IF NOT EXISTS Kayttaja_Tavara("
            sql_lause += "  kayttaja TEXT NOT NULL,"
            sql_lause += "  tavara TEXT NOT NULL,"
            sql_lause += "  FOREIGN KEY(kayttaja) REFERENCES Kayttajat(nimi),"
            sql_lause += "  FOREIGN KEY(tavara) REFERENCES Tavarat(nimike),"
            sql_lause += "  UNIQUE(kayttaja, tavara)"
            sql_lause += ");"
            self.kursori.execute(sql_lause)
        except sqlite3.Error as virhe:
            print(virhe)
        return None

    def lisaaTavaraKayttajalle(self, kayttaja: str, tavara: str) -> None:
        try:
            sql_lause = "INSERT INTO Kayttaja_Tavara(kayttaja, tavara)"
            sql_lause += "  VALUES('" + kayttaja + "', '" + tavara +"');"
            self.kursori.execute(sql_lause)
            self.__sql_yhteys.commit()
        except sqlite3.Error as virhe:
            print(virhe)
        return None

    def listaaKayttajanienTavarat(self) -> list:
        try:
            sql_lause = "SELECT k.nimi, k.tiimi, t.nimike, t.arvo"
            sql_lause += "  FROM Kayttajat AS k"
            sql_lause += "  INNER JOIN Kayttaja_Tavara as kt"
            sql_lause += "  ON kt.kayttaja = k.nimi"
            sql_lause += "  INNER JOIN Tavarat AS t"
            sql_lause += "  ON t.nimike = kt.tavara;"
            self.kursori.execute(sql_lause)
            kantaTuple = self.kursori.fetchall()
            kantalista = self.luoKantaLista(kantaTuple, 4, 2)
            return kantalista
        except sqlite3.Error as virhe:
            print(virhe)
            return None

    def poistaTavaratKayttajalta(self, kayttaja: str) -> None:
        try:
            sql_lause = "DELETE FROM Kayttaja_Tavara WHERE kayttaja = ?;"
            self.kursori.execute(sql_lause, (kayttaja,))
            self.__sql_yhteys.commit()
        except sqlite3.Error as virhe:
            print(virhe)
        return None

    def varmistaTavara(self, tavaraNimike: str) -> bool:
        try:
            sql_lause =  "SELECT * FROM Tavarat WHERE nimike = ?"
            self.kursori.execute(sql_lause, (tavaraNimike,))
            tavara = self.kursori.fetchall()
            if (len(tavara) < 1):
                return False
            return True
        except sqlite3.Error as virhe:
            print("Tavaraa ei löytynyt.")
            print(virhe)
            return False

class Taso(Enum):
    PAATASO = 0
    ALATASO = 1
    ALINTASO = 2

class Valikko():
    def __init__(self) -> None:
        self.taso = Taso.PAATASO
        return None

    def tulostaLista(self, lista: list) -> None:
        try:
            for x in lista:
                print("".join(x))
            return None
        except Exception as virhe:
            print(virhe)
            return None
    
    def syoteKokonaisluku(self, teksti: str) -> int:
        try:
            valinta = int(input("  " * int(self.taso.value) + teksti))
        except Exception:
            return -1
        return valinta

    def syoteLiukuluku(self, teksti: str) -> float:
        try:
            valinta = float(input("  " * int(self.taso.value) + teksti))
        except Exception:
            return None
        return valinta

    def syoteMerkkijono(self, teksti: str) -> str:
        try:
            valinta = str(input("  " * int(self.taso.value) + teksti))
        except Exception:
            return None
        return valinta

    def syoteMerkkijono(self, teksti:str, piilota_syote = False, vahimmaispituus = -1, enimmaispituus = -1) -> str:
        try:
            valinta: str
            if (piilota_syote):
                valinta = getpass.getpass("  " * int(self.taso.value) + teksti)
            else:
                valinta = str(input("  " * int(self.taso.value) + teksti))
            if (len(valinta) < vahimmaispituus and vahimmaispituus > 0):
                print("  " * int(self.taso.value) +"Liian lyhyt merkkijono")
                return None
            if (len(valinta) > enimmaispituus and enimmaispituus > 0):
                print("  " * int(self.taso.value) +"Liian pitkä merkkijono")
                return None
        except Exception:
            return None
        return valinta


    def tulosta(self, teksti:str) -> None:
        print("  " * int(self.taso.value) + teksti)
        return None

    def valikko(self, teksti: list[str], aloitus_teksti = "") -> int:
        try:
            if (aloitus_teksti != ""):
                self.tulosta(aloitus_teksti)
            for i in range(1,len(teksti)):
                self.tulosta(str(i) + " - " + teksti[i])
            self.tulosta("0 - " + teksti[0])
            valinta = self.syoteKokonaisluku("Valintasi: ")
        except Exception:
            valinta = -1
        return valinta
        
class KayttajatValikko(Valikko):
    def __init__(self) -> None:
        super().__init__()
        self.__kayttajatavaraKanta = KayttajaTavaraKanta()
        self.__kayttajatKanta = KayttajatKanta()
        self.__kayttajatKanta.luoYhteysTietokantaan(SQL_YHTEYS["TIETOPOLKU"])
        self.__kayttajatKanta.luoTaulukkoKanta()
        self.__kayttajatavaraKanta.luoYhteysTietokantaan(SQL_YHTEYS["TIETOPOLKU"])
        self.__kayttajatavaraKanta.luoTaulukkoKanta()
        return None

    def kayttajatValikko(self) -> None:
        print("")
        self.taso = Taso.ALATASO
        valinta = self.valikko(["Palaa edelliseen valikkoon","Käyttäjien tiedot","Käyttäjien tavarat"], "Valikko:")
        if (valinta == 1):
            self.kayttajienTiedot()
        elif (valinta == 2):
            self.kayttajienTavarat()
        elif (valinta == 0):
            return None
        else:
            self.tulosta("Tuntematon valinta")
        self.kayttajatValikko()

    def kayttajienTiedot(self) -> None:
        print("")
        self.taso = Taso.ALINTASO
        valinta = self.valikko(["Palaa edelliseen valikkoon","Lisää käyttäjä","Listaa käyttäjät","Etsi kaikki tiimiin kuuluvat käyttäjät","Muokkaa käyttäjän tiimiä","Poista käyttäjä"], "Alavalikko:")
        if valinta == 1:
            while True:
                kayttajanimi = self.syoteMerkkijono("Anna käyttäjänimi: ", False, 3, 16)
                if (kayttajanimi == None):
                    break
                salasana = self.syoteMerkkijono("Anna salasana: ", True, 8, 32)
                if (salasana == None):
                    break
                tiimi = self.syoteMerkkijono("Anna tiimin nimi: ")
                if (len(tiimi) <= 0):
                    self.tulosta("Virheellinen tiimin nimi")
                    break
                self.__kayttajatKanta.lisaaKayttaja(kayttajanimi, tiimi, salasana)
                break
        elif valinta == 2:
            lista = self.__kayttajatKanta.listaaKayttajat()
            if (lista != None):
                self.tulostaLista(lista)
        elif valinta == 3:
            tiimi = self.syoteMerkkijono("Syötä tiimin nimi: ")
            lista = self.__kayttajatKanta.etsiTiiminJasenet(tiimi)
            if(lista != None):
                self.tulostaLista(lista)
        elif valinta == 4:
            kayttaja = self.syoteMerkkijono("Syötä käyttäjän nimi: ")
            tiimi = self.syoteMerkkijono("Syötä uuden tiimin nimi: ")
            self.__kayttajatKanta.muokkaaKayttajanTiimia(kayttaja, tiimi)
        elif valinta == 5:
            kayttajanimi = self.syoteMerkkijono("Syötä poistettavan käyttäjän nimi: ")
            if (self.__kayttajatKanta.varmistaKayttaja(kayttajanimi)):
                while True:
                    valinta = self.syoteMerkkijono("Oletko aivan varma, että haluat poistaa käyttäjän \"" + str(kayttajanimi) + "\" (K/E): ")
                    if (valinta.lower() == 'k'):
                        if (self.poistaKayttaja(kayttajanimi)):
                            self.tulosta("Käyttäjä \"" + str(kayttajanimi) + "\" poistettu.")
                        break
                    elif (valinta.lower() == 'e'):
                        break
                    else:
                        self.tulosta("Tuntematon valinta")
            else:
                self.tulosta("virheellinen syöte, käyttäjää ei löydy")
        elif valinta == 0:
            self.tulosta("Palataan edelliseen valikkoon.")
            return None
        else:
            self.tulosta("Tuntematon valinta, yritä uudelleen.")
        self.kayttajienTiedot()

    def kayttajienTavarat(self) -> None:
        print("")
        self.taso = Taso.ALINTASO
        valinta = self.valikko(["Palaa edelliseen valikkoon","Lisää käyttäjälle tavara", "Näytä käyttäjien tavarat", "Poista käyttäjän tavara"],"Alavalikko:")
        if (valinta == 1):
            while True:
                kayttaja = self.syoteMerkkijono("Anna käyttäjän nimi: ")
                kayttajaLoytyi = self.__kayttajatKanta.varmistaKayttaja(kayttaja)
                if (kayttajaLoytyi == False):
                    self.tulosta("Kayttajaa ei löytynyt")
                    break
                tavara = self.syoteMerkkijono("Anna tavaran nimi: ")
                tavaraLoytyi = self.__kayttajatavaraKanta.varmistaTavara(tavara)
                if (tavaraLoytyi == False):
                    self.tulosta("Tavaraa ei löytynyt")
                    break
                self.__kayttajatavaraKanta.lisaaTavaraKayttajalle(kayttaja, tavara)
                break
        elif (valinta == 2):
            kayttajienTavarat = self.__kayttajatavaraKanta.listaaKayttajanienTavarat()
            self.tulostaLista(kayttajienTavarat)
        elif (valinta == 3):
            while True:
                kayttaja = self.syoteMerkkijono("Anna kayttajan nimi: ")
                kayttajaLoytyi = self.__kayttajatKanta.varmistaKayttaja(kayttaja)
                if (kayttajaLoytyi == False):
                    self.tulosta("Kayttajaa ei löytynyt")
                    break
                self.__kayttajatavaraKanta.poistaTavaratKayttajalta(kayttaja)
                break
        elif (valinta == 0):
            return None
        self.kayttajienTavarat()

class TavaratValikko(Valikko):
    def __init__(self) -> None:
        super().__init__()
        self.__tavarat_Kanta = TavaratKanta()
        self.__tavarat_Kanta.luoYhteysTietokantaan(SQL_YHTEYS["TIETOPOLKU"])
        self.__tavarat_Kanta.luoTaulukkoKanta()
        return None
    
    def tavaratAlavalikko(self) -> None:
        while True:
            self.taso = Taso.ALATASO
            print("")
            valinta = self.valikko(["Palaa edelliseen valikkoon","Näytä tavarat","Hinnoittele tavara uudelleen"],"Valikko:")
            if (valinta == 1):
                tavaralista = self.__tavarat_Kanta.naytaTavarat()
                self.tulostaLista(tavaralista)
            elif (valinta == 2):
                tuote = self.syoteMerkkijono("Anna tuotteen nimi: ")
                arvo = self.__tavarat_Kanta.haeTuotteenArvo(tuote)
                if (arvo == None):
                    self.tulosta("Tuotetta ei löytynyt")
                    continue
                self.tulosta("Tuotteen \"" + tuote + "\" arvo on: " + arvo)
                uusi_arvo = self.syoteLiukuluku("Syötä uusi arvo: ")
                if (uusi_arvo == None or uusi_arvo < 0):
                    self.tulosta("Virheellinen tuotteen hinta")
                    continue
                self.__tavarat_Kanta.vaihdaTuotteenAro(tuote, uusi_arvo)
            elif (valinta == 0):
                self.tulosta("Palataan edelliseen valikkoon.")
                break
            else:
                self.tulosta("Tuntematon valinta, yritä uudelleen.")
        return None
            
class Paavalikko(Valikko):
    def __init__(self) -> None:
        super().__init__()
        print("Tervetuloa pelisysteemiin.\n")
        self.__kayttaja_valikko = KayttajatValikko()
        self.__tavarat_valikko = TavaratValikko()
        return None

    def __del__(self):
        print("Ohjelma päättyy.\n\nEnsikertaan!")
        
    def paavalikko(self) -> None:
        while True:
            print("")
            self.taso = Taso.PAATASO
            valinta = self.valikko(["Lopeta ohjelma", "Käyttäjät", "Tavarat"], "Päävalikko:")
            if valinta == 1:
                self.__kayttaja_valikko.kayttajatValikko()
            elif valinta == 2:
                self.__tavarat_valikko.tavaratAlavalikko()
            elif valinta == 0:
                break
            else:
                self.tulosta("Tuntematon valinta, yritä uudelleen.")
        return None

#----------------Pääojelma----------------#
def main() -> None:
    valikko = Paavalikko()
    valikko.paavalikko()
    return None

if __name__ == "__main__":
    main()