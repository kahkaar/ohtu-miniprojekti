# Ryhmä 17: Loppuraportti

- Aaron Kähkönen — @kahkaar
- Veeti Martinmäki — @veetimar
- Nooa Kosteila — @knoooa
- Veeti Kurpari — @VeetiKu

## Sprinttien meno
### Sprint 1
Huomasimme myöhässä, että tämä sprintti oli jo alkanut, jonka takia emme ehtineet toteuttaa sprintin käyttäjätarinat kunnolla.

### Sprint 2
Valmistimme sprint 1 aikana olleet käyttäjätarinat. Tämän takia, emme ehtineet tehdä enempää käyttäjätarinoita kuin kirja -tyypin sitaatteiden muokkaus ja poisto.

### Sprint 3
Sprint 1 mokan takia, meidän täytyi suunnitella tietokannan struktuuri uudelleen, sillä edellisillä sprintillä oli vain `book` -taulu tietokannassa.

Uuden tietokannan struktuurin suunnittelu ja totetuts valmistui tämän sprintin aikana. Huomasimme, että on hankala tehdä dynaamisempia sivua pelkällä `Python` + `Flask` kombinaatiolla.

Teimme mahdollisuuden hakea siteerauksia haun perusteella.

Lopuksi kehitettiin mahdollisuus viedä siteerauksen tiedot (`.bib`) leikepöydälle.

Aloimme käyttämään GitHub:in PR ominaisuutta enemmän


### Sprint 4
Lisäsimme tietokantaan mahdollisuus luokitella siteeraukset tageilla ja/tai kategoreilla. Tämän toteutuksessa piti muokata aikaisempia `citations` -taulun tietokanta kyselyitä.

Lisäksi teimme mahdollisuuden viedä siteeraukset pois .bib tiedostona.

Lopuksi lisäsimme mahdollisuuden luoda uusia siteerauksia tuomalla sen DOI -linkin. Tässäkin oli ankara käyttää pelkkää `Python` + `Flask` kombinaatiota.

## Mikä sujui projektissa hyvin, mitä pitäisi parantaa seuraavaa kertaa varten
Projektityön lopullinen toteutus meni hyvin, mutta voisi parantaa ajan hallintaa.

## Mitä opimme?
- Testien teko on hyvä tapa estää bugien tekemistä.

- Olisi hyvä oppia mahdollisuus tehdä enemmän dynaamisia verkkosovelluksia (esim. lomakkeiden automaattinen täyttö ilman n.s. sivunvaihtoa (käyttöliittymä ei päivity (F5 tyylimäisesti), kun näin tekee) -pyyntöä, tai ilman JavaScriptiä).

- Myöskin testien teko eri toiminnallisuuksille, jotka mahdollisesti poistuvat käytöstä myöhemmin on epämielyttävää, sillä kirjoittaa koodia kahteen kertaan yhen toiminnallisuuden suhteen.
