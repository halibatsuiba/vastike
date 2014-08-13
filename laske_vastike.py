from __future__ import division
import json
import datetime
import time
import sys
from hae_postit import hae_postit


class vastikelaskelma():

    def __init__(self):
        with open('data.txt') as data_file:    
            self.vastike = json.load(data_file)
            mailObj = hae_postit()
            self.timeframe, self.kausiStr, self.prevKausiStr = mailObj.get_current_timeframe()
            print "Aikavali %s, kausi %s" % (self.timeframe, self.kausiStr)

    '''
    Tama funktio laskee taloyhtion asukasmaaran
    '''
    def talon_asukasluku(self, vuosi, kuukausi, talo):
        try:
            #kausi = '{0:0{width}}'.format(kuukausi, width=2)+str(vuosi)
            return self.vastike["talotiedot"][talo]["asukasluku"]
        except:
            return -1

  
    def lammin_vesi_jyvitys(self, vuosi, kuukausi):
        print "Jyvitetaan lammin vesi..."
        asukkaita_yhteensa = 0
        for talo in "ABCDEFG":
            asukkaita_talossa = int(self.talon_asukasluku(vuosi, kuukausi, talo))
            asukkaita_yhteensa += asukkaita_talossa

        print "Asukkaita yhteensa:", asukkaita_yhteensa

        jyvitys = {}
        for talo in "ABCDEFG":
            asukkaita_talossa = int(self.talon_asukasluku(vuosi, kuukausi, talo))
            talon_lamminvesi_jyvitys = asukkaita_talossa / round(asukkaita_yhteensa,2)
            jyvitys[talo] = round(talon_lamminvesi_jyvitys,3)
            
        return jyvitys

    def yhtion_lampiman_veden_kulutus(self, vuosi, kuukausi):
        taloyhtion_mittarilukema_nyt = self.vastike["yhtionmittarit"][self.kausiStr]["vesimittari"]
        taloyhtion_mittarilukema_viimekuussa = self.vastike["yhtionmittarit"][self.prevKausiStr]["vesimittari"]

        taloyhtion_vedenkulutus = taloyhtion_mittarilukema_nyt - taloyhtion_mittarilukema_viimekuussa
        print "Yhtion vedenkulutus: ", taloyhtion_vedenkulutus
    
        kylman_veden_kulutus = 0
        for talo in "ABCDEFG":
            kylma_vesi_nyt = self.vastike["talot"][talo][self.kausiStr]["KylmaVesi"]
            kylma_vesi_viimekuussa = self.vastike["talot"][talo][self.prevKausiStr]["KylmaVesi"]
            kylman_veden_kulutus += (kylma_vesi_nyt - kylma_vesi_viimekuussa)
      
        lampiman_veden_kulutus = taloyhtion_vedenkulutus - kylman_veden_kulutus
        #print "Yhtion kylman veden kulutus: ", kylman_veden_kulutus
        #print "Yhtion lampiman veden kulutus: ", lampiman_veden_kulutus
        return lampiman_veden_kulutus

    def lampiman_veden_kulutus_per_talo(self, vuosi, kuukausi):
        print "Lasketaan lampiman veden kulutus..."
        lamminta_vetta_kulunut = self.yhtion_lampiman_veden_kulutus(vuosi, kuukausi)
        lampiman_veden_jyvitys = self.lammin_vesi_jyvitys(vuosi, kuukausi)
        lampiman_veden_laskennallinen_kulutus_per_talo = {}

        lampiman_veden_tarkistussumma = 0
        for talo in "ABCDEFG":
            lampiman_veden_laskennallinen_kulutus_per_talo[talo] = lamminta_vetta_kulunut * lampiman_veden_jyvitys[talo]
            lampiman_veden_tarkistussumma += lampiman_veden_laskennallinen_kulutus_per_talo[talo]
  
        tarkistussumma = lampiman_veden_tarkistussumma - lamminta_vetta_kulunut
        if tarkistussumma:
            print "   VIRHE!"
            print "   Tarkistussumma: %s" % (tarkistussumma)

        return lampiman_veden_laskennallinen_kulutus_per_talo

    def kylman_veden_kulutus_per_talo(self, vuosi, kuukausi):
        print "Lasketaan kylman veden kulutus..."
        kylman_veden_kulutus = {}
        for talo in "ABCDEFG":
            kylma_vesi_nyt = self.vastike["talot"][talo][self.kausiStr]["KylmaVesi"]
            kylma_vesi_viimekuussa = self.vastike["talot"][talo][self.prevKausiStr]["KylmaVesi"]
            kylman_veden_kulutus[talo] = kylma_vesi_nyt - kylma_vesi_viimekuussa
            print "%s : %s %s %s" % (talo, kylman_veden_kulutus[talo],kylma_vesi_nyt,kylma_vesi_viimekuussa)
        return kylman_veden_kulutus

    def lammityksen_kulutus_per_talo(self, vuosi, kuukausi):
        print "Lasketaan lammityksen kulutus..."
        lammityksen_kulutus = {}
        totaali_kulutus = 0
        for talo in "ABCDEFG":
            lammitys_nyt = self.vastike["talot"][talo][self.kausiStr]["Lammitys"]
            lammitys_viimekuussa = self.vastike["talot"][talo][self.prevKausiStr]["Lammitys"]
            lammityksen_kulutus[talo] = (lammitys_nyt - lammitys_viimekuussa) / 1000
            totaali_kulutus += lammityksen_kulutus[talo]
        return lammityksen_kulutus, totaali_kulutus

    def kierto_per_talo(self, vuosi, kuukausi):
        print "Lasketaan kierron kulutus..."
        kiertovesi = {}
        kiertovesiTotal = 0
        for talo in "ABCDEFG":
            kiertovesi_nyt = self.vastike["talot"][talo][self.kausiStr]["KiertoVesi"]
            kiertovesi_viimekuussa = self.vastike["talot"][talo][self.prevKausiStr]["KiertoVesi"]
            kiertovesi[talo] = kiertovesi_nyt - kiertovesi_viimekuussa
            if kiertovesi[talo] < 30:
                kiertovesi[talo] = 30
                kiertovesiTotal += kiertovesi[talo]
        return kiertovesi, kiertovesiTotal

    def laske_autopaikat(self, vuosi, kuukausi):
        print "Lasketaan autopaikat..."
        autopaikat = {}
        for talo in "ABCDEFG":
            autopaikat[talo] = self.vastike["talotiedot"][talo]["autopaikat"]
        return autopaikat



    def hae_uusimmat_hinnat(self):
        print "Haetaan hinnat..."
        uusin_hinta = ""
        uusin_timestamp = 0
        hinnat = self.vastike["hinnat"]
        for hinta in hinnat:
            vuosi = hinta[4:8]
            kuukausi = hinta[2:4]
            paiva = hinta[0:2]
            d = datetime.datetime (int(vuosi),int(kuukausi),int(paiva))
            timestamp = time.mktime(d.timetuple())

            if timestamp > uusin_timestamp:
                uusin_timestamp = timestamp
                uusin_hinta = hinta

        hintataulukko = self.vastike["hinnat"][uusin_hinta]
        return hintataulukko

    def kaukolammon_kokonaiskulutus(self, vuosi, kuukausi):
        taloyhtion_mittarilukema_nyt = self.vastike["yhtionmittarit"][self.kausiStr]["kaukolampo"]
        print "Kaukolampi nyt",taloyhtion_mittarilukema_nyt
        taloyhtion_mittarilukema_viimekuussa = self.vastike["yhtionmittarit"][self.prevKausiStr]["kaukolampo"]
        print "Kaukolampi edellinen",taloyhtion_mittarilukema_viimekuussa
        kaukolampo_kokonaiskulutus = (taloyhtion_mittarilukema_nyt - taloyhtion_mittarilukema_viimekuussa)
        return kaukolampo_kokonaiskulutus
    

    def hae_muut_yhtion_menot(self, vuosi, kuukausi):
        muut_kulut = self.vastike["yhtionmenot"][self.kausiStr]
        summa = 0
        for kulu in muut_kulut:
            summa += muut_kulut[kulu]
        muutKulutPerTalo = round(summa/7,2)
        return muut_kulut, muutKulutPerTalo, summa

    def check_if_all_data_available(self):
        kaikkiDatatSaatu = True
        for talo in "ABCDEFG":
            if self.kausiStr not in self.vastike["talot"][talo]:
                print "Ei oo: ",talo
                kaikkiDatatSaatu = False
            else:
                print "On: ",talo

        return kaikkiDatatSaatu
    
if __name__ == "__main__":
    print "\n**** Aloitetaan laskelma ****"
    laskelma = vastikelaskelma()
  
    if not laskelma.check_if_all_data_available():
        exit()
  
    now = datetime.datetime.now()

    hinnat = laskelma.hae_uusimmat_hinnat()

    #Lasketaan kulutukset
    kylmavesi_per_talo = laskelma.kylman_veden_kulutus_per_talo(now.year,now.month-1)
    print kylmavesi_per_talo

    lamminvesi_jyvitys = laskelma.lammin_vesi_jyvitys(now.year,now.month-1)

    autopaikat = laskelma.laske_autopaikat(now.year,now.month-1)

    kierto_per_talo, kokonaiskierto = laskelma.kierto_per_talo(now.year,now.month-1)
    print "Kierron kokonaiskulutus:", kokonaiskierto
  
    yhtion_menot, muutKulutPerTalo, muutKulutSumma = laskelma.hae_muut_yhtion_menot(now.year,now.month-1)
    print "Muut kulut:%s per talo:%s" %(muutKulutSumma,muutKulutPerTalo)

    lammityksen_kulutus_per_talo, lammitys_kokonaiskulutus = laskelma.lammityksen_kulutus_per_talo(now.year,now.month-1)
    print "Taloyhtion lammityksen kokonaiskulutus:", lammitys_kokonaiskulutus
  
    yhtion_lampiman_veden_kulutus = laskelma.yhtion_lampiman_veden_kulutus(now.year,now.month-1)
    print "Yhtion lampiman veden kulutus:",yhtion_lampiman_veden_kulutus

    kaukolammon_kokonaiskulutus = laskelma.kaukolammon_kokonaiskulutus(now.year,now.month-1)
    print "Kaukolammon kokonaiskulutus:", kaukolammon_kokonaiskulutus

    print "*** HINNAT ***"
    kaukolammon_perusmaksu = hinnat["kaukolampo_perusmaksu"]
    kaukolammon_perusmaksu_per_talo = kaukolammon_perusmaksu / 7
    print "Kaukolammon perusmaksu: %s per talo: %s " % (kaukolammon_perusmaksu,kaukolammon_perusmaksu_per_talo)
  
    kaukolammon_yksikkohinta = hinnat["kaukolampo_yksikkohinta"]
    kaukolammon_hinta_mwh = kaukolammon_yksikkohinta * 1000
    print "Kaukolammon yksikkohinta: %s/kWh %s/mWh" % ( kaukolammon_yksikkohinta,kaukolammon_hinta_mwh)
  
    kylmavesi_hinta = hinnat["vesi"]
    print "Kylma vesi hinta:", kylmavesi_hinta
  
    kuution_lammitysenergia = hinnat["kuution_Lammitys"]
    print "Veden lammitysenergia %skWh per kuutio." %(kuution_lammitysenergia)
  
    lamminvesi_hinta = kylmavesi_hinta + ( kuution_lammitysenergia * kaukolammon_yksikkohinta)
    print "Lampiman veden kuutiohinta:", lamminvesi_hinta
  
    kaukolammon_kokonaishinta = round(kaukolammon_perusmaksu + kaukolammon_kokonaiskulutus * kaukolammon_yksikkohinta,2)
    print "Kaukolammon kokonaishinta:", kaukolammon_kokonaishinta

    lampiman_veden_lammitysenergia = (yhtion_lampiman_veden_kulutus * 53) / 1000
    print "Lampiman veden lammitysenergia:",lampiman_veden_lammitysenergia

    kierron_kerroin = hinnat["kierron_kerroin"]

    #Lasketaan hukka
    print "*** HUKKALASKU ***"
    kaukolammon_kokonaishinta = kaukolammon_kokonaiskulutus * kaukolammon_hinta_mwh
    print "Kaukolammon kokonaishinta:",kaukolammon_kokonaishinta
  
    lammityksen_kokonaishinta = lammitys_kokonaiskulutus * kaukolammon_hinta_mwh
    print "Lammityksen kokonaishinta:",lammityksen_kokonaishinta
  
    kierron_kokonaishinta = kokonaiskierto * kierron_kerroin
    print "Kierron kokonaishinta:",kierron_kokonaishinta
  
    veden_lammityksen_kokonaishinta = lampiman_veden_lammitysenergia * kaukolammon_hinta_mwh
    print "Veden lammityksen kokonaishinta:",veden_lammityksen_kokonaishinta
  
    hukka_hinta_per_talo = round((kaukolammon_kokonaishinta - (lammityksen_kokonaishinta + kierron_kokonaishinta + veden_lammityksen_kokonaishinta)) / 7,2)
    print "Hukan hinta per talo:",hukka_hinta_per_talo
  
    lasku = {"A":{},"B":{},"C":{},"D":{},"E":{},"F":{},"G":{}}

    #Lasketaan hinnat
    for talo in "ABCDEFG":
        lasku[talo]["Lammitys"] = round(lammityksen_kulutus_per_talo[talo] * kaukolammon_hinta_mwh + kaukolammon_perusmaksu_per_talo,2)
    
        lasku[talo]["KylmaVesi"] = round(kylmavesi_per_talo[talo] * kylmavesi_hinta,2)
    
        lasku[talo]["LamminVesi"] = round(lamminvesi_jyvitys[talo] * lamminvesi_hinta * yhtion_lampiman_veden_kulutus,2)
    
        lasku[talo]["KiertoVesi"] = round(kierto_per_talo[talo] * kierron_kerroin,2)
    
        lasku[talo]["hukka"] = hukka_hinta_per_talo
    
        lasku[talo]["autopaikka"] = round(autopaikat[talo]*hinnat["autopaikka"],2)
    
        lasku[talo]["muut"] = round(muutKulutPerTalo,2)
    #lasku[talo]["sahko"] = round(yhtion_menot["sahko"]/7,2)
    #lasku[talo]["ytv"] = round(yhtion_menot["ytv"]/7,2)
    #lasku[talo]["pankki"] = round(yhtion_menot["pankki"]/7,2)
    #lasku[talo]["hsy"] = round(yhtion_menot["hsy"]/7,2)
    #lasku[talo]["lisamaksu"] = round(yhtion_menot["lisamaksu"]/7,2)
    #lasku[talo]["tilintarkastus"] = round(yhtion_menot["tilijavero"]/7,2)
    #lasku[talo]["kirjanpito"] = round(yhtion_menot["kirjanpito"]/7,2)

    print "MUUT TALOYHTION MENOT"
    for item in yhtion_menot:
        print item, yhtion_menot[item], round(yhtion_menot[item]/7,2)

    print "\n\nTALOKOHTAISET LASKELMAT"
    taloyhtion_totaali = 0
    for talo in "ABCDEFG":
        #print lasku[talo]
        talon_totaali = 0
        laskuRivi = ""
        for item in lasku[talo]:
            laskuRivi += item + ":"+str(lasku[talo][item]) + " "
            talon_totaali += lasku[talo][item]
        print talo, laskuRivi, talon_totaali,"\n"
        taloyhtion_totaali += talon_totaali
            
    print "Total:",taloyhtion_totaali





#  with open('data.txt', 'w') as outfile:
#    json.dump(laskelma.vastike, outfile)



  
