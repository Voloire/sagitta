# Sagitta — design

Banco di prova e referto forense per astrofotografia.

Data: 2026-08-29
Nome: **Sagitta**
Licenza: **MIT**
Piattaforme: **Windows, macOS, Linux**
Stato: design approvato, in attesa di piano di implementazione
Discussione preliminare: appunti di lavoro privati, non pubblicati.

---

## 1. Il problema

L'astrofotografia ha due popolazioni con lo stesso identico problema, e nessuna delle due
ha uno strumento per risolverlo.

**Il praticante** guarda le proprie sub, vede stelle allungate negli angoli, e chiede aiuto
su un forum. Riceve sei diagnosi diverse da sei persone: "guidi male", "è tilt", "è
backfocus", "è flessione differenziale". Nessuna delle sei è una misura. La liturgia si
ripete migliaia di volte l'anno ed è il thread più frequente di CloudyNights e di
r/AskAstrophotography.

**Il recensore** — chi produce contenuti di settore su YouTube — fa video del tipo "ho
provato X per tre mesi". Confronta notti diverse, con seeing diverso, altezze diverse,
temperature diverse, e conclude "sì, migliora". Quei video sono metodologicamente
indifendibili e chi li fa lo sa: non esiste uno strumento che dica *se* la differenza sia
reale e *quanto* valga, al netto delle condizioni.

Sono lo stesso problema visto a due distanze: **attribuire una differenza osservata alla
causa giusta, invece che al confondente di turno.**

## 2. Cosa costruiamo

Un'applicazione desktop, locale, gratuita e open source, con **due schermate**.

### Schermata 1 — Il referto

Trascini una cartella di sub. In meno di due minuti hai:

- la mappa dell'aberrazione sul sensore (eccentricità e FWHM per zona, con i vettori)
- la timeline per-sub delle metriche
- il join opzionale con il guide log di PHD2
- un referto che **esclude** cause invece di proclamarne una, con confidenza e prove

È la porta d'ingresso: si dimostra in quarantacinque secondi, e il referto esportato in
PNG è condivisibile su forum e Discord.

### Schermata 2 — Il banco di prova

Dai due gruppi di sub — prima e dopo un cambio di attrezzatura — e il tool normalizza per
massa d'aria, seeing, temperatura, RMS di guida e campionamento, poi risponde con un
**effetto stimato e il suo intervallo di confidenza**:

```
FWHM:                     -0.31" (IC 95%: -0.39 / -0.23)   significativa
Eccentricità angoli:      -0.14  (IC 95%: -0.19 / -0.09)   significativa
Eccentricità centro:      invariata (IC 95% include zero)

-> compatibile con correzione di aberrazione ai bordi,
   non con un miglioramento del seeing
```

Con i grafici già pronti da mettere in un video, e **"dati insufficienti" come risposta
legittima e frequente**.

Questa è la schermata che fa restare gli utenti, e che rende chi la usa un recensore
migliore invece che un recensore in più.

## 3. Utenti bersaglio e strategia di adozione

**Utente primario: il creator di contenuti di settore.** Non è il pubblico, è l'utente. Ha
un bisogno acuto, ricorrente e professionale che nessuno serve, ha un archivio enorme su cui
il tool produce valore immediato, e quando lo usa lo cita per necessità metodologica, non
per cortesia. Ogni video che mostra un confronto normalizzato è distribuzione.

**Utente secondario: il praticante in crisi.** Chi ha appena cambiato treno ottico, montato
un OAG, ricevuto un tubo nuovo. Uso a raffica per due settimane, poi più niente fino al
prossimo cambio. È un tool da crisi, non da routine — e i tool da crisi si condividono nei
thread, che è esattamente il canale che ci interessa.

**Utente terziario: la community dev.** Interessata al problema di validazione: come si
dimostra che un classificatore diagnostico funziona quando non si possiede la verità di
riferimento. La risposta è la sezione 9, e vale un contributo a sé.

### Vincoli di adozione, non negoziabili

Derivano da cosa ha funzionato (Siril, ASTAP, GraXpert, StarNet, i plugin NINA, SharpCap) e
da cosa è rimasto a quattromila download.

| Vincolo | Motivo |
|---|---|
| Installer a doppio clic su tutte e tre le piattaforme | "Richiede Python 3.11 e conda" è un abbandono immediato. Windows è il grosso del bacino, ma Mac e Linux sono scoperti dai concorrenti ed è lì che si entra senza competere. |
| Drag & drop di una cartella, zero configurazione | Ogni campo da compilare prima del primo risultato dimezza gli utenti. Si legge tutto dagli header, si chiede solo ciò che manca. |
| Sotto i 2 minuti su 200 sub, su un portatile normale | Se non sta in una clip, non sta in un video. |
| Funziona degradato | Senza log di guida deve comunque dare aberrazione di campo e andamento del fuoco, e dire chiaramente cosa non può concludere. |
| Legge il mondo reale | NINA, SGP, APT, ASIAIR (header ridotti, ma guide log in formato PHD2), Ekos/KStars, MaximDL, Voyager. Se si rompe sui file del 2022 di qualcuno, non esiste. |
| Ogni verdetto mostra prove e confidenza, e sa dire "non lo so" | È la feature che dà credibilità. Un verdetto sicuro e sbagliato distrugge il progetto in un thread. |
| Report esportabile in PNG con il nome sopra | Motore di crescita: ogni volta che qualcuno lo posta per chiedere aiuto, è pubblicità. GraXpert è cresciuto così. |
| Tutto locale, nessun account, nessuna telemetria, nessun "Pro in arrivo" | Sospetto immediato altrimenti. |
| Nessun upload dei dati altrove | Idem, e non negoziabile. |

## 3bis. Delimitazione competitiva

Ricerca svolta il 2026-08-29. Serve a evitare di costruire un clone peggiore di ciò che
esiste già.

### Cosa fa Hocus Focus (plugin NINA di George Hilios, MPL-2.0)

È lo standard de facto per tilt e backfocus **dentro NINA**, in sviluppo attivissimo.

| Copre già, e bene | Non copre |
|---|---|
| HFR robusto, PSF gaussiana e Moffat con gate su R² | Uso fuori da NINA: niente CLI, niente libreria, niente standalone |
| FWHM ed eccentricità per stella | **macOS e Linux** (NINA è .NET/WPF, solo Windows) |
| Griglia 3x3, contour FWHM, campo vettoriale di eccentricità | Lettura di FITS/XISF arbitrari da SGP, APT, ASIAIR, Ekos, Voyager |
| Tilt via piano sui quattro angoli, in passi e micrometri | Analisi di light frame già su disco: carica **solo run di autofocus salvati da NINA** |
| Modello a paraboloide inclinato per stella, reiezione MAD | **Qualsiasi integrazione con PHD2 o dati di guida** |
| Separazione tilt / curvatura / backfocus per forma funzionale | Correlazione forma stellare con la qualità di inseguimento |
| Traduzione in giri di vite, comando adattatori motorizzati | **Statistica prima/dopo su cambio attrezzatura** |
| Curve di autofocus per regione con diagnostica di fit | **Normalizzazione per massa d'aria, seeing, temperatura** |
| | Andamenti multi-notte, funzionamento senza hardware connesso |

**Il vincolo strutturale che ne deriva**: per i numeri veri di tilt, Hocus Focus richiede una
**scansione attraverso il fuoco**. Su singola posa produce solo mappa FWHM e campo vettoriale.
E fuori da NINA i dati di sweep **non esistono in forma riutilizzabile**: la posizione del
focheggiatore non è in un header FITS standardizzato. Quindi Sagitta è confinata all'analisi
di popolazioni di light frame — che è esattamente il terreno da presidiare, purché non si
finga di fare altro.

### Precedente diretto sul join con la guida

**N.I.N.A. Session Analysis** legge FITS, log NINA, **log PHD2** e session metadata, e correla
guida e qualità delle sub. Ma è **solo macOS**, closed source, e orientato a NINA. Dimostra
due cose: che l'idea funziona, e che **Windows e Linux, dove sta la stragrande maggioranza
degli astrofotografi, sono scoperti**.

### Sul terreno della singola sub siamo in affollamento

ASTAP (aberration inspector, multipiattaforma, gratis), Siril (`tilt` e `seqtilt`,
multipiattaforma, gratis), PixInsight (FWHMEccentricity, AberrationInspector,
SubframeSelector), CCD Inspector (commerciale, Windows). Su quel terreno non si compete.

### Regola di onestà, non negoziabile

La critica tecnica che divide il settore, formulata da freestar8n su CloudyNights, è che **da
una singola posa non si può misurare il tilt del sensore**: si può solo misurare
un'indicazione di aberrazione sul campo, che può non avere niente a che fare col tilt.

Sagitta la accetta e la adotta: **si chiama "aberrazione di campo", mai "tilt"**, quando la
misura viene da light frame senza scansione di fuoco. È l'unico modo di stare dalla parte
giusta di quella critica invece che dalla parte sbagliata.

### Posizionamento

**Hocus Focus risponde a "quale vite giro stanotte"**: è attuazione correttiva, in tempo
reale, con l'hardware in mano e il focheggiatore sotto controllo.

**Sagitta risponde a "il cambio ha davvero funzionato, ed era l'ottica o la montatura"**: è
uno strumento **forense e probatorio, a posteriori**, la cui unità di analisi è la
**popolazione di light frame** con le sue covariate.

Sono due mestieri diversi, non due implementazioni dello stesso. Da cui:

- **si interopera, non si compete**: i report di autofocus di NINA e i run salvati sono
  *sorgenti dati* per Sagitta, dichiaratamente;
- **niente layout a mosaico 3x3**, niente la parola "inspector" nel nome o nella UI. Un
  referto statistico con intervalli di confidenza deve avere l'aspetto di un referto, non di
  un pannello di collimazione.

### Ordine di priorità che ne deriva

**Banco di prova > join con la guida > lettura di sub arbitrarie > mappe di aberrazione.**

Se si inverte quest'ordine e si parte dalle mappe, si costruisce un clone peggiore: noi non
controlliamo il focheggiatore, non possiamo fare uno sweep e non possiamo chiudere il ciclo
dicendo di che frazione di giro girare la vite. Su quel terreno si perde per costruzione.

## 4. Scope negativo — cosa NON facciamo

Elencato esplicitamente perché ognuna di queste è stata considerata e scartata per un
motivo preciso.

- **Nessuna generazione di sequenze eseguibili** (NINA, Ekos, altro). Una sequenza sbagliata
  manda un tubo contro una gamba del treppiede o punta il Sole all'alba. È una responsabilità
  che non ci prendiamo e che squalifica il progetto agli occhi di chi conta.
- **Nessun controllo del rig, in nessuna forma.** Read-only, sempre.
- **Nessuna pianificazione di sessione.** NINA Target Scheduler ed Ekos Scheduler lo fanno,
  gratis, dentro il software che la gente ha già aperto.
- **Nessun text-to-SQL libero sull'archivio.** Fallisce in silenzio producendo numeri
  plausibili e sbagliati, che l'utente non può verificare.
- **Nessun numero prodotto da un LLM.** Mai, in nessun punto della pipeline.
- **Nessuna elaborazione delle immagini.** Non tocchiamo pixel, non produciamo immagini
  migliorate. Misuriamo e basta.
- **Nessuna previsione di seeing o di condizioni future.**
- **Nessun confronto tra rig diversi** senza che l'utente lo forzi esplicitamente, con
  avviso.

## 5. Architettura

Cinque componenti con confini netti.

```
    cartelle di sub                guide log PHD2 / log NINA
          |                                    |
          v                                    v
   +---------------+                  +------------------+
   |    INGEST     |                  |   TELEMETRIA     |
   | header ->     |                  | parse, tempo     |
   | schema canon. |                  | assoluto, eventi |
   +---------------+                  +------------------+
          |                                    |
          v                                    |
   +---------------+                           |
   |    MISURA     |                           |
   | detection per |                           |
   | stella e sub  |                           |
   +---------------+                           |
          |                                    |
          +----------------+-------------------+
                           v
                    +--------------+
                    |    INDICE    |   DuckDB locale
                    | per-stella   |   incrementale
                    | per-sub      |
                    | per-sessione |
                    +--------------+
                       |          |
            +----------+          +-----------+
            v                                 v
    +---------------+              +------------------+
    |  DIAGNOSTICA  |              | BANCO DI PROVA   |
    | firme, regole |              | modello con      |
    | di esclusione |              | covariate, IC    |
    +---------------+              +------------------+
            |                               |
            +---------------+---------------+
                            v
                     +--------------+
                     |   REFERTO    |  UI + export PNG/JSON
                     +--------------+
```

### 5.1 Ingest

Legge FITS e XISF. Normalizza gli header eterogenei in uno **schema canonico**.

Campi canonici minimi: istante di inizio posa (UTC), durata, filtro, binning, guadagno,
offset, temperatura sensore, temperatura ambiente se presente, dimensione pixel, focale,
coordinate del sito, coordinate puntate, coordinate risolte se presenti, angolo di rotazione
risolto, telescopio, camera, software di acquisizione.

Il problema vero è che ogni software scrive keyword diverse e con convenzioni diverse. La
mappa dialetto → canonico vive in **`dialects/*.yaml` versionati nel repository**, non
generati a runtime. Vedi sezione 8 per il ruolo dell'AI qui.

Regole dure:

- `DATE-OBS` si assume UTC a inizio posa, ma **si verifica**: se il software è noto per
  scrivere ora locale o centro posa, si applica la correzione del dialetto e la si dichiara
  nel referto.
- **Non ci si fida mai di HFR/FWHM scritti nell'header.** Sono incomparabili tra software
  perché dipendono da soglia di detection, campionamento e fondo. Si rimisura sempre con un
  motore unico.
- `XPIXSZ` e `FOCALLEN` sono spesso assenti o riportano la focale nominale invece di quella
  reale con riduttore. Se il campionamento risultante è incoerente con la dimensione
  stellare misurata, si segnala e si chiede conferma.

### 5.2 Misura

Un solo motore per tutto il progetto. Per ogni sub, detection stellare e, per ogni stella
accettata: posizione, flusso, FWHM, eccentricità, **angolo di posizione dell'asse maggiore
nel sistema del sensore**.

Criteri di esclusione, che contano più della fisica perché dominano il risultato:

- stelle **sature** o vicine alla saturazione (cima piatta, eccentricità casuale)
- stelle **blended** e ammassi densi
- stelle troppo vicine al bordo per essere misurate interamente
- raggi cosmici, colonne calde, pixel caldi residui
- tracce di satelliti
- stelle sotto una soglia di SNR

**Guardrail di campionamento**: sotto una soglia (indicativamente peggio di 2.5–3 arcsec per
pixel) eccentricità e angolo sono quantizzati a rumore. Il tool **si rifiuta di rispondere**
sulle metriche di forma e lo dichiara. Questo evita la figuraccia sistematica con chi usa un
RASA o una focale corta.

**Sub a colori (OSC) e matrice di Bayer.** Metà del bacino riprende con camera a colori, e
su una sub grezza la matrice di Bayer altera la forma misurata: campionando un canale ogni
due pixel per riga e colonna, la PSF risulta deformata in modo dipendente dall'orientamento
e la misura di eccentricità diventa un artefatto. Regola: sulle OSC si misura **su un solo
canale estratto senza interpolazione** (il verde, che ha doppia densità nella matrice), con
la scala corretta di conseguenza — mai su una sub demosaicizzata, perché l'interpolazione
del demosaico arrotonda le stelle esattamente come fa la registrazione. Il campionamento
effettivo che ne risulta va confrontato con il guardrail: molte OSC a focale corta finiranno
sotto soglia, e il tool deve dirlo invece di rispondere.

*Da decidere con benchmark*: motore proprio (photutils/sep) o ASTAP da riga di comando come
acceleratore. ASTAP è velocissimo e già presente in molte installazioni; un motore proprio è
più controllabile e non aggiunge dipendenze esterne. Da valutare con un benchmark, tenendo
conto anche di come ciascuno gestisce le CFA.

### 5.3 Stratificazione del campo — il punto centrale

**Un singolo numero per sub non serve a niente.** Il discriminante fisico non è il valore
medio dell'eccentricità, è la sua **dipendenza dalla posizione nel campo**.

Il sensore viene diviso in:

- **zona centrale**: raggio normalizzato < 0.25
- **anello intermedio**: 0.25 – 0.65
- **anello esterno**: > 0.65
- **quattro angoli**, identificati come settori dell'anello esterno

Per ogni zona: mediana e dispersione di FWHM, eccentricità, angolo di posizione, conteggio
stelle usabili. Una zona con troppe poche stelle non produce conclusioni per quella zona.

### 5.4 Le firme diagnostiche

Questa è la parte dove il ragionamento intuitivo sbaglia, quindi le firme sono definite
esplicitamente.

| Causa | Firma | Note |
|---|---|---|
| **Errore di guida / inseguimento** | Allungamento **uniforme su tutto il fotogramma, centro compreso**. Angolo coerente e allineato all'asse RA proiettato sul sensore. | Se il centro è pulito, non è la guida. È l'esclusione più utile del tool. |
| **Backfocus / spaziatura errata** | Degrado **radialmente simmetrico**: nullo al centro, cresce col raggio, **uguale nei quattro angoli**. Pattern sagittale o tangenziale a seconda del segno dell'errore. | Non si separa dal tilt guardando l'angolo. Si separa guardando la **simmetria**. |
| **Tilt del sensore o del focheggiatore** | **Asimmetria tra angoli opposti**: un angolo a fuoco, quello diagonalmente opposto no. | Tilt del sensore, tilt del focheggiatore e decentraggio ottico danno la **stessa firma su un singolo frame**. Non sono separabili senza una scansione attraverso il fuoco. Il tool lo dichiara invece di scegliere. |
| **Rotazione di campo** (errore di stazionamento, o alt-az) | Allungamento **tangenziale attorno al centro di rotazione**, che è la **stella di guida**, non il centro del sensore. Cresce col raggio da quel punto. | Firma nettamente distinguibile. |
| **Flessione differenziale** | Direzione **fissa rispetto alla geometria tubo/montatura**, che varia lentamente col **carico gravitazionale** (altezza e azimut), non col tempo in sé. | **Impossibile per costruzione se si guida con OAG.** Se l'utente dichiara OAG, l'ipotesi è esclusa a priori. |
| **Deriva di fuoco** | FWHM che cresce in modo monotono, **simmetrica e uniforme sul campo**. | La temperatura utile spesso non esiste nei dati: vedi 5.6. |
| **Velatura / cirri sottili** | Conteggio stelle che crolla, fondo cielo che cambia, FWHM apparente che può **calare** perché restano solo le brillanti. | Firma facilmente scambiata per deriva di fuoco. Conteggio stelle e fondo sono i discriminanti. |
| **Rugiada sull'ottica** | FWHM che sale gradualmente, conteggio stelle che scende, **fondo che sale**, gonfiamento simmetrico. | Idem. |

### 5.5 I due test guidati — la funzione distintiva

Nessuno automatizza questi due test, e sono i due che chiudono davvero la questione. Il tool
li propone quando i dati da soli non bastano, e poi confronta le due acquisizioni.

**Test di rotazione della camera.** Scatti una posa, ruoti la camera di 90 gradi, riscatti.
Se il pattern di aberrazione **ruota con la camera**, la causa è nella camera o nel sensore.
Se **resta ancorato al tubo**, la causa è nell'ottica o nel treno. Il tool calcola la
differenza tra le due mappe e dà il verdetto.

**Test del flip al meridiano.** Il flip **ribalta il vettore gravità rispetto all'OTA**. Se
la firma si inverte al flip è meccanica (flessione); se resta identica è ottica. Questo test
è gratis: la maggior parte delle sessioni lunghe contiene già un flip, quindi il tool può
spesso eseguirlo **retroattivamente sui dati esistenti**, senza chiedere niente all'utente.

### 5.6 Telemetria e join temporale

Il join con il guide log di PHD2 è la parte che nessun tool esistente fa, ed è anche un
campo minato. Va trattato con paranoia.

**Ricostruzione del tempo assoluto.** L'header del guide log PHD2 contiene data e ora
**locale** di inizio; le righe contengono secondi trascorsi. Va ricostruito l'istante
assoluto, applicando fuso e ora legale. La notte del cambio ora è il caso in cui un tool
ingenuo sbaglia di un'ora e giura che la guida era pessima durante pose perfette.

**Offset esplicito e confermato.** Gli orologi non sono sincronizzati: ASIAIR e portatile
divergono, i mini PC hanno la RTC morta e datano i file al 2001. Il tool:

1. stima l'offset per cross-correlazione tra eventi (inizio pose e dither)
2. **mostra graficamente la sovrapposizione e chiede conferma all'utente**
3. non procede mai su un offset indovinato in silenzio

**Esclusione dei settle post-dither.** Dopo ogni dither c'è una coda di assestamento che può
valere il 5–10% della posa e domina l'RMS. Va parsata dagli eventi del log ed esclusa dalla
finestra, altrimenti ogni sub post-dither appare guidata male.

**Separazione in banda — evitare la tautologia.** L'RMS di PHD2 è misurato su una stella e
**contiene già il seeing**, esattamente come la FWHM della sub. Correlarli grezzi e dire "la
guida ha peggiorato la FWHM" è in gran parte una tautologia, non una causa. Solo le
componenti dell'errore di guida **più lente del tempo di posa** producono smearing
sistematico aggiuntivo; quelle più veloci sono già dentro il termine di seeing. Il join
calcola quindi, per ogni sub: RMS totale, RMS in banda lenta (filtrato sotto 1/T_posa),
picco, deriva, numero di star lost — e usa **la banda lenta** per l'attribuzione.

**Temperatura.** `CCD-TEMP` è la temperatura del sensore, che con il set point è **costante
per definizione** e non dice nulla sulla deriva di fuoco. Serve la temperatura del tubo, che
esiste solo se l'utente ha una sonda sul focheggiatore. Per chi non ce l'ha, la deriva di
fuoco **non è calcolabile** e il tool lo dichiara invece di stimarla.

**ASIAIR: il join funziona.** Verificato: l'ASIAIR usa PHD2 internamente e scrive guide log
in **formato PHD2 standard** (`PHD2_GuideLog*.txt`, nella cartella `log` sul supporto di
archiviazione). Non perdiamo quella fetta di utenza, che è la più numerosa. Resta da
confermare su un file reale in fase di implementazione, e da verificare se il formato sia
identico o solo simile.

**Casi in cui il join non è disponibile**: chi non guida affatto, chi usa un guider diverso
da PHD2, chi ha cancellato i log. Il tool deve funzionare degradato e dirlo.

**Vincoli sul backlash e sulla guida in DEC**: se il log mostra guida DEC unidirezionale
(north-only o south-only) non ci sono inversioni e non si conclude nulla sul backlash. E
l'algoritmo di default Resist Switch **rifiuta per progetto** di invertire finché non vede N
errori consecutivi nello stesso verso: il ritardo osservato all'inversione è dominato da
un'impostazione software, non dal treno di ingranaggi. Non lo chiamiamo backlash meccanico.

### 5.7 Indice

DuckDB locale, tre tabelle: per-stella (campionata), per-sub, per-sessione.

Requisiti derivati dai volumi reali — un archivio serio è 50–200 mila file, 2–10 TB, metà su
dischi scollegati:

- **scansione incrementale e ripartibile**
- **chiave sul UUID del volume**, non sul percorso, per gestire i dischi offline
- lettura di FITS compressi (`.fits.fz`, archivi) e di **XISF**
- **deduplica su chiave logica** (istante di posa + camera + esposizione), non su hash: la
  stessa sub esiste in copia grezza, calibrata e registrata, con pixel e hash diversi. Se si
  contano tutte, il totale ore è tre volte sbagliato e **plausibile**, quindi nessuno se ne
  accorge.
- **tracciamento della catena** grezza → calibrata → registrata. Le registrate hanno la forma
  stellare alterata dall'interpolazione, con eccentricità sistematicamente più bassa: se
  finiscono nelle metriche, l'analisi è avvelenata in silenzio. **Solo le grezze entrano
  nelle metriche di forma.**
- **risoluzione dei target per coordinate** con cone search, mai per stringa: `M31`, `M 31`,
  `NGC224`, `Andromeda`, `m31_Ha_300s` sono lo stesso oggetto.
- **chiave di confronto obbligatoria** (telescopio, camera, binning, campionamento): il tool
  si rifiuta di mettere rig diversi nello stesso grafico senza conferma esplicita.

L'indice non è un prodotto e non si comunica come tale. È l'infrastruttura che rende
possibile il banco di prova, ed è il fossato difendibile del progetto perché nessuno lo ha.

## 6. Il banco di prova

Input: due gruppi di sub, "prima" e "dopo" un cambio.

**Metriche target**, ognuna analizzata separatamente: FWHM al centro, FWHM agli angoli,
eccentricità al centro, eccentricità agli angoli, asimmetria fra angoli opposti, conteggio
stelle a soglia fissa.

**Covariate di normalizzazione**: massa d'aria (da altezza), temperatura, RMS di guida in
banda lenta, filtro, campionamento, densità stellare del campo, fase e altezza lunare, fondo
cielo.

**Modello**: regressione sulle metriche target con termine di gruppo e covariate, con la
**notte come effetto casuale** — le sub della stessa notte non sono osservazioni
indipendenti. Output: effetto stimato con intervallo di confidenza al 95%.

**Il problema del seeing, dichiarato apertamente.** Il seeing è la covariata più importante e
non è misurabile indipendentemente dalle sub stesse. Quando la metrica target è
l'eccentricità agli angoli, la FWHM al centro è un proxy di seeing accettabile. Quando la
metrica target è la FWHM, quel proxy non è utilizzabile e l'incertezza cresce. Il tool **lo
dichiara nel referto** invece di nasconderlo dentro un intervallo troppo stretto.

**La raccomandazione che cambia il mestiere del recensore.** Il gold standard è il confronto
**interlacciato nella stessa notte**: A/B/A/B, alternando i due setup. Elimina in un colpo
seeing, trasparenza, temperatura e massa d'aria come confondenti. Il tool lo raccomanda
attivamente **prima** che la persona faccia l'acquisizione, e riconosce quando i dati sono
interlacciati per stringere l'intervallo di conseguenza.

**Rifiuti espliciti.** Il banco di prova risponde "dati insufficienti" quando:

- i gruppi sono troppo piccoli
- c'è confondimento totale (tutte le sub "prima" a bassa quota, tutte le "dopo" allo zenit)
- i due gruppi hanno rig, campionamento o filtro diversi
- il seeing è l'unica spiegazione compatibile

Questo è un requisito funzionale, non una nota a piè di pagina: **un tool che risponde sempre
non è credibile.**

## 7. Forma dell'output: esclusione, non diagnosi

Il referto non dice "hai il tilt". Dice, in quest'ordine:

1. **Cosa è escluso, con la misura.**
   `NON è la guida: eccentricità al centro 0.06, agli angoli 0.34.`
2. **Cosa resta compatibile, con confidenza.**
   `Compatibile con aberrazione del treno ottico. Asimmetria fra angoli opposti 0.31 → più
   compatibile con tilt che con spaziatura.`
3. **Cosa non è distinguibile con questi dati, e il test che lo distinguerebbe.**
   `Non posso separare tilt del sensore da decentraggio ottico. Esegui il test di rotazione
   camera: [istruzioni].`
4. **Le prove**, sempre visibili: numeri per zona, conteggi, grafici.

Ogni affermazione è ancorata a un numero mostrato. Nessuna frase conclusiva senza la sua
misura accanto.

## 8. Dove sta l'AI — e dove non sta

Due punti soli, entrambi difendibili davanti a una community che ha passato tre anni a
litigare su cosa sia dato reale.

**1. Normalizzazione dei dialetti di header.** Ogni software scrive keyword diverse. Mappare
dialetti arbitrari a uno schema canonico è una cosa che un modello fa bene. Ma si esegue
**una volta**, in fase di sviluppo o su keyword sconosciute, e il risultato viene scritto in
**`dialects/*.yaml` versionato nel repository, su cui la community manda pull request**. Non
è un costo per file, non è un risultato irriproducibile, ed è un bene comune. È anche la
parte che parla al pubblico dev.

**2. Scrittura del referto in linguaggio naturale a partire da numeri già calcolati** e da
regole di esclusione già applicate. Il modello formula, non conclude.

**Divieti assoluti:**

- mai un numero prodotto da un LLM
- mai un'attribuzione causale che non derivi da una regola esplicita e ispezionabile
- mai una sequenza eseguibile
- mai il caricamento dei dati dell'utente da qualche parte
- mai la parola "AI" come argomento di vendita nel titolo o nella prima riga

## 9. Validazione — il pezzo che sostituisce le credenziali

L'autore non ha un rig né anni di immagini pubblicate. Nella community astrofotografica
questo è un problema di credibilità reale: le immagini sono le credenziali. La risposta non è
nasconderlo, è **sostituirlo con qualcosa di più forte**.

### 9.1 Verità sintetica

Generatore di sub artificiali con la risposta scritta dentro:

- tilt noto, espresso in millimetri di inclinazione del piano focale
- errore di spaziatura noto, in millimetri
- deriva di guida iniettata, con ampiezza e direzione note
- rotazione di campo nota
- seeing variabile, PSF che varia nel campo
- rumore, fondo cielo e saturazione realistici

Il discriminatore viene validato su questi dati, dove la verità è controllata. È la mossa più
credibile possibile per chi non ha un rig, ed è anche quella che parla al pubblico dev, che
di astrofotografia non capisce niente ma di validazione sì.

### 9.2 Corpus etichettato reale

I thread "what's wrong with my stars" contengono spesso sub allegate **e la diagnosi
confermata a posteriori** nei commenti successivi: "era tilt, risolto con gli shim", "era
backfocus, 1.5 mm in meno". Raccolta, **con permesso esplicito degli autori**, curata e
pubblicata con licenza chiara.

Attenzione, e non è un dettaglio: chi risponde in quei thread è spesso lo sviluppatore stesso
di PHD2 o di altri strumenti community. Usare il loro lavoro volontario senza chiedere è la
mina sociale più grossa del progetto. **Si chiede sempre, e si accredita.**

Il dataset di benchmark è **di per sé un contributo alla community che nessuno ha**, e va
pubblicato **prima** del tool.

### 9.3 Metrica dichiarata

Il README riporta il risultato sul benchmark: "classifica correttamente 41 casi su 47, con 6
casi dichiarati indeterminati". Non "secondo me è tilt".

## 10. Requisiti non funzionali

| Requisito | Target |
|---|---|
| Piattaforme | Windows, macOS, Linux, tutte e tre di prima classe, GUI compresa |
| Distribuzione | eseguibile o installer nativo per ciascuna, nessun prerequisito |
| Tempo di analisi | < 2 min su 200 sub da 20 MP, portatile medio |
| Tempo al primo risultato visibile | < 45 s dal drag & drop |
| Memoria | deve girare su 8 GB |
| Rete | nessuna, mai |
| Formati input | FITS, FITS compresso, XISF |
| Export | PNG (referto), JSON (dati), CSV (tabella per-sub) |
| Licenza | **MIT** |

**Stack proposto**, da confermare in fase di piano: core in Python per misura e statistica,
impacchettato in eseguibile singolo; GUI desktop leggera; DuckDB come indice; ASTAP da CLI
come acceleratore opzionale per la detection. Il vincolo "niente Python per l'utente" è
soddisfatto dall'impacchettamento, non dalla scelta del linguaggio.

## 11. Rischi

| Rischio | Gravità | Mitigazione |
|---|---|---|
| Un verdetto sicuro e sbagliato in un thread pubblico | Alta — può chiudere il progetto | Output per esclusione, confidenza sempre visibile, "non lo so" come risposta di prima classe, guardrail di campionamento |
| Sovrapposizione con Hocus Focus, plugin NINA che già stima tilt e backfocus | Alta | Il terreno unico è il **join con la guida**, i **test guidati** e il **banco di prova**. Non competiamo sulla mappa di aberrazione da sola, e lo diciamo apertamente |
| Join temporale sbagliato in silenzio | Alta | Offset confermato dall'utente, mai indovinato |
| Doppio conteggio del seeing nell'attribuzione | Media | Separazione in banda, uso della sola banda lenta |
| Archivio con rig diversi mischiati | Media | Chiave di confronto obbligatoria, rifiuto esplicito |
| Metriche avvelenate dalle sub registrate | Media | Tracciamento della catena, solo grezze nelle metriche di forma |
| Percezione "ennesimo wrapper LLM" | Media | AI confinata ai due usi dichiarati, mai in prima riga, validazione in evidenza |
| Assenza di credenziali dell'autore | Media | Validazione sintetica e benchmark pubblico prima del tool |
| Uso non autorizzato di materiale dei forum | Alta, reputazionale | Permesso esplicito e accreditamento, sempre |

## 12. Roadmap

Ogni stadio è utile e pubblicabile da solo.

**Stadio 0 — Fondamenta.** Ingest e schema canonico, dialetti in YAML, motore di misura
unico, stratificazione del campo, guardrail di campionamento. Nessuna AI, nessuna UI: solo
CLI e JSON.

**Stadio 1 — Validazione.** Generatore sintetico, benchmark, metrica dichiarata. Pubblicato
**prima** del tool.

**Stadio 2 — Il join con la guida.** Parser PHD2 (incluso il formato ASIAIR), tempo assoluto,
offset confermato, esclusione settle, separazione in banda. Più il **test del flip
retroattivo**, che gira sui dati già esistenti.

**Stadio 3 — Il referto.** Firme diagnostiche, regole di esclusione, confidenze, GUI con drag
& drop, mappa del campo, export PNG. **Prima release visibile, e nasce già con il join
dentro**: senza il join il referto è la mappa di aberrazione di tutti gli altri, e saremmo un
clone. Con il join risponde alla domanda che nessun altro su Windows e Linux sa oggi
affrontare, cioè "è il tubo o è la montatura?", ed è quello il titolo.

**Stadio 4 — Il banco di prova.** Indice, modello con covariate, intervalli di confidenza,
rifiuti espliciti, grafici pronti per il montaggio, raccomandazione dell'interlacciamento. È
la release che serve l'utente primario, ed è il posizionamento più difendibile del progetto.

**Stadio 5 — Corpus reale.** Raccolta con permesso, curatela, pubblicazione, ri-misura del
benchmark.

## 13. Decisioni

**Chiuse:**

1. **Nome: Sagitta.** Freccia, e richiamo all'aberrazione sagittale. Corto, pronunciabile,
   senza "AI" dentro, e non contiene "inspector".
2. **Licenza: MIT.**
3. **Piattaforme: Windows, macOS e Linux**, tutte e tre di prima classe. È anche una scelta
   di posizionamento: Hocus Focus è Windows-only e Session Analysis è macOS-only.
4. **ASIAIR: supportato.** Scrive guide log in formato PHD2 standard (verificato su fonti
   community, da riconfermare su file reale).
5. **Hocus Focus: delimitato**, vedi sezione 3bis. Si interopera, non si compete.
6. **Motore di detection e di misura: proprio. ASTAP serve al plate solving, non alla
   misura.** Chiusa senza benchmark, perché non c'era niente da confrontare: il CSV per
   stella che ASTAP esporta dalla riga di comando contiene **X, Y, flusso e HFD**, e basta.
   Niente eccentricità, niente angolo di posizione — cioè esattamente le due quantità su cui
   poggia l'intera tabella delle firme diagnostiche della sezione 5.4. Senza di quelle non si
   separa la guida dall'ottica, e senza quella separazione non abbiamo un prodotto.

   Si aggiunge che HFD non è FWHM: importarlo violerebbe la nostra stessa regola di non
   fidarsi mai del numero di forma prodotto da un altro software. E l'aberration inspector
   di ASTAP, cioè la parte che più assomiglia a noi, è una funzione della GUI e non è
   scriptabile.

   **ASTAP resta però la scelta giusta per il plate solving**, come dipendenza **opzionale**
   dallo Stadio 4: gratuito, su tutte e tre le piattaforme, e sotto licenza **MPL-2.0**,
   quindi ridistribuibile accanto a un programma MIT senza contaminazione. Serve a due cose
   che oggi non sappiamo fare: verificare la **plausibilità di `XPIXSZ` e `FOCALLEN`**
   confrontando la scala dichiarata con quella risolta (un valore sbagliato applica il
   guardrail alla soglia sbagliata) e **risolvere i target per coordinate**. È accettabile
   come dipendenza esterna proprio perché è una funzione degradabile, non il nucleo: se
   ASTAP non c'è, quelle due verifiche non si fanno e il resto continua a funzionare.

**Aperte, da chiudere con un benchmark in fase di implementazione:**

7. **Framework GUI**: da scegliere in funzione del vincolo "eseguibile nativo su tutte e tre
   le piattaforme, nessun prerequisito".
8. **Presenza di `FOCUSPOS` / `FOCPOS` negli header reali** dei vari software di
   acquisizione. Da verificare su un campione: determina se una modalità con scansione di
   fuoco sia mai possibile fuori da NINA, o se restiamo definitivamente sulla popolazione di
   light frame.
