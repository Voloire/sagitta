# Sagitta

Referto forense e banco di prova per astrofotografia.

Sagitta misura la forma stellare delle sub **per zona del campo** e, quando i dati lo
consentono, distingue cause che hanno la stessa apparenza ma una diversa dipendenza dalla
posizione nel sensore. Stelle allungate in un angolo e stelle allungate ovunque sono due
problemi diversi con due soluzioni diverse, e la differenza sta nella geometria, non
nell'occhio di chi guarda.

---

## ⚠️ Stato: in costruzione. Non c'è ancora niente da usare.

**Questo repository al momento contiene documenti, non software.** Non c'è codice, non ci
sono release, non c'è niente da installare. Se sei arrivato qui cercando uno strumento
funzionante, oggi non c'è.

**Non ci sono date, e non c'è una roadmap con scadenze.** È un progetto in divenire, portato
avanti quando c'è tempo. Quello che segue descrive l'intenzione e il metodo, non un impegno a
consegnare qualcosa entro un momento qualsiasi. Se leggi un "sarà", leggilo come "è così che
è disegnato", non come una promessa.

| | |
|---|---|
| Codice | nessuno |
| Release | nessuna |
| Fase | Stadio 0 e 1, in partenza |
| Piattaforma | Windows 11 soltanto |

Quello che c'è, ed è tutto ciò che c'è:

- [`docs/design.md`](docs/design.md) — la specifica: cosa fa, cosa non fa, e perché
- [`docs/plan-stadio-0-1.md`](docs/plan-stadio-0-1.md) — il piano di implementazione dei
  primi due stadi, passo per passo
- [`CHANGELOG.md`](CHANGELOG.md) — cosa cambia a ogni versione, da qui in avanti

Il piano è pubblico perché il ragionamento che porta a una misura conta quanto la misura. Chi
vuole contestare un metodo deve poterlo leggere.

---

## Lo scopo, e i suoi confini

Sagitta risponde a una domanda sola: **cosa sta succedendo davvero alle mie stelle, e dove.**

Il modo in cui ci prova è misurare la forma stellare stella per stella con i momenti secondi
pesati sul flusso — FWHM, eccentricità, angolo dell'asse maggiore — e poi **stratificare** il
risultato per posizione nel campo: centro, anello intermedio, e i quattro angoli tenuti
separati. È la stratificazione a fare il lavoro, perché è lì che le cause si distinguono:

| Firma osservata | Causa compatibile |
|---|---|
| allungamento uniforme, angolo fisso, **centro compreso** | errore di guida |
| allungamento radiale, **uguale nei quattro angoli** | errore di spaziatura del correttore |
| **asimmetria fra angoli opposti** | aberrazione di campo |
| allungamento tangenziale, angolo che dipende dalla posizione | rotazione di campo |

Il valore non è nel calcolo di un numero: è nell'avere un metro **ripetibile** con cui
confrontare due configurazioni della stessa attrezzatura. Ho cambiato lo spessore
dell'anello: è migliorato, o è solo migliorato il seeing?

### Cosa NON fa, per scelta

- **Non controlla niente.** Né montatura, né camera, né focheggiatore. Legge e basta.
- **Non genera sequenze** e non pianifica sessioni.
- **Non elabora immagini** e non produce immagini migliorate. Non è un tool di
  post-processing e non ci diventerà.
- **Non si fida di `HFR` e `FWHM` scritti negli header.** Sono incomparabili fra software di
  acquisizione diversi: vengono ignorati e rimisurati sempre.
- **Non usa modelli linguistici per produrre numeri.** Nessun LLM tocca una misura.
- **Non manda niente da nessuna parte.** Vedi [SECURITY.md](SECURITY.md) quando esisterà;
  la promessa sarà verificata da un test che sabota i socket ed esegue l'intera pipeline.

---

## I caveat, che sono la parte importante

Un tool di misura che non dichiara i propri limiti è peggio di nessun tool, perché produce
numeri che sembrano risposte. Questi limiti sono **deliberati**: stanno nel disegno, non sono
mancanze in attesa di essere colmate.

### Non si chiama `tilt`, si chiama aberrazione di campo

Da light frame senza una scansione di fuoco **non si misura il tilt del sensore.** Si misura
l'**aberrazione di campo**, che è la somma di tilt, curvatura, spaziatura sbagliata,
decentramento e altro ancora. Sono cose diverse, e confonderle è il modo più comune di dare
consigli sbagliati a chi chiede aiuto. Sagitta userà la parola `field_aberration` ovunque, nel
codice come nell'output, e `tilt` mai — tranne come nome di un parametro del *generatore
sintetico*, dove è verità iniettata e non stima.

Chi vuole il tilt vero ha bisogno di una scansione di fuoco. È un'altra misura, e non è in
questo blocco di lavoro.

### Sopra 2.5 arcsec/pixel non esce nessun numero

Sotto campionamenti grossolani, eccentricità e angolo di posizione sono rumore quantizzato.
Sagitta **rifiuta di rispondere** e spiega perché, invece di restituire un numero che
sembrerebbe una misura. Il rifiuto è una funzionalità, non un limite.

### Solo sub grezze

Le sub calibrate, registrate o integrate hanno la forma alterata dall'interpolazione. Entrano
nelle metriche di forma soltanto i frame grezzi.

### Sulle sub a colori si misura un solo canale

Su sensori con matrice di Bayer la misura avviene su un **sotto-reticolo verde estratto senza
alcuna interpolazione**, mai su un'immagine demosaicizzata. La conseguenza da tenere a mente
è che la scala in arcsec per pixel **raddoppia** rispetto al sensore.

### Solo Windows 11

È dove vive il bacino di utenza: NINA è Windows-only, ASCOM è tecnologia COM di Windows, i
driver e l'accelerazione CUDA dei tool di post-processing stanno lì. Il mondo Ekos, INDI e
Alpaca è **rimandato, non escluso**: il codice è scritto per restare portabile, così quando
sarà il suo turno costerà aggiungere un job di CI e non riscrivere niente.

### Serie `0.x`: il formato di output cambierà

Fino a che il join con i log di guida non sarà dentro, il JSON prodotto può cambiare fra una
minor e l'altra. Non costruirci sopra automazioni che non puoi aggiornare.

### Nessuna firma del codice

Su Windows un eseguibile non firmato con un certificato di code signing fa comparire l'avviso
SmartScreen. Un certificato costa qualche centinaio di euro l'anno e questo progetto non ha
entrate. La risposta che possiamo dare è l'attestazione di provenienza generata da GitHub più
i checksum: non fa sparire l'avviso, ma rende verificabile ciò che l'avviso mette in dubbio.

---

## Come sarà usato

**Niente di quanto segue funziona oggi**, e non c'è una data in cui funzionerà. È qui
perché il piano lo prescrive e perché un lettore possa giudicare in anticipo se uno strumento
del genere gli servirebbe.

Installazione, una volta che ci sarà una release:

```bash
pip install sagitta
```

Misura di una singola sub, con output JSON su stdout:

```bash
sagitta measure percorso/alla/sub.fits
```

Esecuzione della validazione su dati sintetici:

```bash
pytest tests/test_benchmark.py -v
```

---

## Come si esegue il lavoro di sviluppo

Il progetto si sviluppa seguendo [`docs/plan-stadio-0-1.md`](docs/plan-stadio-0-1.md), che è
scritto per essere eseguito passo per passo senza dover inventare niente. Chi lo esegue legge
il **Protocollo di esecuzione** in testa al piano, che vale più di qualunque abitudine
personale.

L'essenziale, per chi vuole solo capire come è organizzato il lavoro:

- **Due rami.** Si sviluppa e si committa su `dev`; su `main` si arriva solo per merge di una
  pull request, e ogni commit di `main` è rilasciabile.
- **Un commit per task**, spinto su `dev` subito. La CI gira a ogni push e su ogni pull
  request verso `main`.
- **TDD, senza scorciatoie.** Si scrive il test, si verifica che fallisca, si scrive
  l'implementazione minima, si verifica che passi, si committa. Un test che passa prima
  dell'implementazione è un difetto da segnalare, non una buona notizia.
- **Le soglie dei test non si allentano.** Sono il contratto della misura: se una non è
  raggiungibile, il difetto è nell'implementazione o nel piano.
- **Ogni task dichiara i file che tocca**, e quella dichiarazione viene confrontata con il
  diff. Un commit che tocca un file non dichiarato viene respinto senza entrare nel merito.

Ambiente di sviluppo, su Windows 11 con PowerShell:

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```powershell
pip install -e ".[dev]"
```

L'ambiente virtuale si attiva **nella shell**, e i processi figli ne ereditano le variabili.

Suite di test e controlli, quando ci sarà del codice:

```powershell
pytest -v
```

```powershell
ruff check .
```

---

## Versioni e changelog

**Ogni release ha una voce nel [CHANGELOG.md](CHANGELOG.md), senza eccezioni.** Il formato è
[Keep a Changelog](https://keepachangelog.com/it/1.1.0/), il versionamento è
[SemVer](https://semver.org/lang/it/).

La regola operativa è breve: si scrive sotto `[Non rilasciato]` mentre si lavora, e quella
sezione diventa il corpo della release quando si crea il tag. Il numero di versione ha una
sorgente sola, `pyproject.toml`, e il codice lo legge dai metadati del package: un numero
scritto due volte è un numero che prima o poi diverge.

Una release nasce così, e i controlli automatici rifiutano di pubblicare se qualcosa non
torna:

1. il lavoro è su `dev` e la CI è verde
2. pull request da `dev` a `main`, con la CI che rigira
3. tag `vX.Y.Z` sul `main` ottenuto dal merge
4. il workflow di release verifica che il tag coincida con la versione del package **e** che
   il commit taggato appartenga a `main`, poi costruisce, calcola i checksum e genera
   l'attestazione di provenienza
5. la release nasce **in bozza**: pubblicarla resta un gesto umano

Si resta sulla serie `0.x` finché il join con i log di guida non è dentro — che è una
condizione, non una scadenza. Il salto a `1.0.0` avverrà quando ci sarà qualcosa che merita
quel numero, e non prima.

---

## Licenza

MIT. Vedi [LICENSE](LICENSE).
