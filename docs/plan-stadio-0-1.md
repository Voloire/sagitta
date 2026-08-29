# Sagitta — Stadio 0 e 1: fondamenta e validazione sintetica

> **Per l'agente che esegue.** Questo piano è autosufficiente: contiene ogni file, ogni riga
> di codice, ogni comando e ogni risultato atteso. **Non devi inventare niente.** Se ti trovi
> a progettare qualcosa che qui non c'è, fermati e chiedi: è un difetto del piano, non uno
> spazio lasciato alla tua iniziativa. Leggi prima l'intero **Protocollo di esecuzione** qui
> sotto, poi esegui i task nell'ordine indicato, un passo alla volta.

---

## Protocollo di esecuzione

### Dove si lavora

Radice del repository: `C:\Users\Voloirex\sagitta`, che corrisponde a
**https://github.com/Voloire/sagitta**, repository **pubblico** con licenza MIT.

**La directory di lavoro per ogni comando `Run:` è la radice del repository.** I comandi non
contengono `cd`: posizionati una volta e resta lì. Se il tuo strumento non mantiene la
directory fra un comando e l'altro, anteponi tu lo spostamento.

Il codice vive in `src/sagitta/`, i test in `tests/`, i workflow in `.github/workflows/`.
`LICENSE`, `README.md`, `SECURITY.md` e `CHANGELOG.md` stanno nella radice.

### I rami: si sviluppa su `dev`, si rilascia da `main`

Due rami, e nessun altro. La regola è breve e non ha eccezioni.

| Ramo | A cosa serve | Chi ci scrive |
|---|---|---|
| `dev` | dove nasce tutto il lavoro. Un commit per task, spinto man mano. | tu, l'agente di sviluppo |
| `main` | solo ciò che è stato verificato. Ogni commit qui è rilasciabile. | nessuno direttamente: ci arriva per merge di una pull request aperta dalla sessione Claude di revisione |

Il ciclo completo, una volta sola per capirlo:

1. **Sviluppo.** Ogni task di questo piano committa su `dev` e spinge su `dev`. La CI gira
   a ogni push e ti dice subito se hai rotto qualcosa o dimenticato un file.
2. **Test.** La suite deve essere verde su `dev`. Non è un'opinione: è il workflow `ci`
   che lo dice, in ambiente pulito, non la tua esecuzione locale.
3. **Merge.** Quando il blocco di lavoro è completo, la **sessione Claude di revisione** apre
   una pull request da `dev` a `main`, legge il diff e fa il merge. Non tu, e non perché ci
   sia una gerarchia: chi scrive il codice non può essere anche chi lo approva, altrimenti il
   controllo non vale niente.
4. **Release.** Sul `main` così ottenuto la stessa sessione di revisione crea il tag
   `vX.Y.Z`, che fa partire il workflow `release` del Task 16. Resta un solo gesto umano: la
   release nasce in bozza, e la pubblicazione è un clic del proprietario.

**Cosa fa questo per te, in concreto:** committi e spingi solo su `dev`. Non tocchi `main`,
non apri la pull request, non crei tag. I passi 3 e 4 non sono tuoi, e il Task 16 lo dice di
nuovo dove serve.

**Il tuo push è il segnale.** Non devi avvisare nessuno a fine task: una sorveglianza esterna
guarda la punta di `dev` e la CI, e apre il turno di revisione da sola. Un segnale che tu
devi ricordarti di mandare è un segnale che prima o poi non arriva.

**Il primo comando, prima di qualsiasi task.** Verifica su quale ramo ti trovi:

Run: `git rev-parse --abbrev-ref HEAD`

Expected: `dev`. Il ramo esiste già. Se rispondesse `main`, passa a `dev` con
`git switch dev` e ricontrolla: un commit finito su `main` per sbaglio è la sola cosa di
questo protocollo che è scomoda da disfare.

### Shell

Questa macchina è **Windows 11 con PowerShell 5.1**. Conseguenze che ti riguardano:

- **`&&` e `||` non esistono**: sono errori di parsing, non comandi che falliscono. Per
  questo ogni riga `Run:` di questo piano contiene **un solo comando**. Eseguili uno per
  volta e controlla l'esito di ciascuno prima del successivo.
- `2>/dev/null` non esiste: si scrive `2>$null`. Ma non serve, perché nessun comando qui lo usa.
- I percorsi si scrivono con `\` o `/` indifferentemente in PowerShell. Nel **codice Python**
  si usa sempre `pathlib`, mai separatori scritti a mano — non per PowerShell, ma perché il
  supporto a Linux è rimandato e non deve costare una riscrittura.

Se un comando di questo piano non funziona in PowerShell, è un difetto del piano: segnalalo,
non aggirarlo.

### Preparazione dell'ambiente, una volta sola

**Il virtualenv esiste già** ed è in `C:\Users\Voloirex\sagitta\.venv`, con Python 3.13.7
e `pip`, `setuptools`, `wheel` aggiornati. **Non ricrearlo.** Esiste anche il `.gitignore`
che lo esclude dal versionamento, insieme a `__pycache__`, `dist/` e le cache degli
strumenti. Esiste già anche il file `LICENSE` con il testo MIT.

Se dovessi trovarlo mancante o corrotto, si ricrea dalla radice del repository con:

Run: `python -m venv .venv`

**L'ambiente si attiva nella shell che ti lancia, non da dentro.** Se stai leggendo questo
piano dentro un agente, l'attivazione è già avvenuta prima che tu esistessi e tu ne erediti
le variabili: il tuo compito è **verificarla** a ogni task, non rifarla. Il comando qui sotto
serve a chi apre una shell a mano.

Run: `.\.venv\Scripts\Activate.ps1`

Verifica di essere nell'ambiente giusto prima di proseguire:

Run: `python -c "import sys; print(sys.prefix); print(sys.version)"`

Expected: `C:\Users\Voloirex\sagitta\.venv` e `3.13.7`. Se il percorso non termina con
`.venv`, l'ambiente non è attivo e ogni installazione successiva finirebbe nel Python di
sistema: fermati e attivalo. Se la versione fosse inferiore a 3.11, fermati comunque: il
codice usa la sintassi `X | None` nelle annotazioni, che su versioni precedenti non funziona.

Il pacchetto si installa in modalità sviluppo nel Task 1 e da quel momento resta installato:
le modifiche ai sorgenti hanno effetto immediato, senza reinstallare.

### Ordine dei task

Non è l'ordine numerico. La CI va accesa presto, così ogni task successivo è verificato in
ambiente pulito mentre lo scrivi, invece che tutto insieme alla fine:

**1 → 14 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 15 → 16**

Al Task 14 la suite contiene solo i test del Task 1, ed è normale: la CI cresce con il
codice. Prima del Task 14 leggi la sezione **La configurazione GitHub, decisa: account Free,
repository pubblico**, in fondo a questo documento: fissa cosa la piattaforma ci dà gratis e
cosa non va reintrodotto.

### Il ciclo di ogni task, e di ogni passo

**Prima riga di ogni task, sempre, prima del suo Step 1.** Sono due comandi e li esegui tu:

Run: `git rev-parse --abbrev-ref HEAD`

Expected: `dev`.

Run: `where.exe python`

Expected: la **prima** riga è `C:\Users\Voloirex\sagitta\.venv\Scripts\python.exe`. Se non
lo è, **fermati e segnala**: non provare ad attivare l'ambiente.

Il motivo è tecnico e vale la pena capirlo, perché altrimenti ci si gira intorno a vuoto.
L'ambiente virtuale non è attivo *dentro di te*: è attivo nella shell da cui sei stato
lanciato, e tu ne erediti le variabili. Un `Activate.ps1` eseguito come tuo comando gira in
un processo figlio che muore subito dopo, quindi non cambia niente per il comando successivo.
Se la verifica fallisce, il pane è stato lanciato male e va rilanciato da fuori: è l'unica
cosa di questo piano che non puoi sistemare da solo, e insistere ti farebbe solo perdere
tempo in un ciclo che non converge.

Nessuna delle due verifiche è una formalità. Sono le condizioni che, se sbagliate, fanno
finire il lavoro nel ramo sbagliato o l'installazione nel Python di sistema, e in entrambi i
casi te ne accorgi molto dopo.

Poi, ogni task è una sequenza di passi con casella di spunta. Per ciascuno:

1. Leggi il passo per intero prima di agire.
2. Fai **esattamente** ciò che dice. Il codice nei blocchi va copiato com'è, non riscritto
   con parole tue né "migliorato".
3. Esegui il comando `Run:` indicato.
4. Confronta l'esito con `Expected:`. **Se non coincide, fermati.** Non passare al passo
   successivo, non modificare il test per farlo passare, non aggiungere codice che il piano
   non prevede.
5. Spunta la casella nel documento.

I passi seguono il ciclo TDD: si scrive il test, **si verifica che fallisca**, si scrive
l'implementazione minima, si verifica che passi, si committa. Il passo "verifica che
fallisca" non è una formalità: se un test passa prima di aver scritto l'implementazione, il
test non sta misurando quello che crede, ed è un difetto da segnalare.

### Cosa non devi fare mai

Sono invarianti del progetto, non preferenze di stile. Un modello capace tende a
"sistemare" queste cose di sua iniziativa: qui sistemarle significa rompere il prodotto.

- **Non allentare mai una soglia di test per farlo passare.** Le soglie sono il contratto
  della misura. Se una non è raggiungibile, il difetto è nell'implementazione o nel piano, e
  va segnalato.
- **Non indebolire il guardrail di campionamento** e non aggirare i criteri di esclusione
  della detection. Sono la ragione per cui il programma può rifiutarsi di rispondere, che è
  una funzionalità, non un limite.
- **Non usare la parola `tilt`** per una quantità misurata da light frame, in nessun nome,
  commento, messaggio o docstring. Si dice `field_aberration`, aberrazione di campo. L'unica
  eccezione sono i parametri del generatore sintetico, dove è verità iniettata e non stima.
- **Non leggere `HFR` o `FWHM` dagli header** per usarli come misura. Vanno ignorati sempre.
- **Non toccare file che il task non dichiara.** Il blocco `**Files:**` di ogni task non è
  documentazione: è un contratto, e viene confrontato con il diff da un controllo meccanico.
  Un commit che tocca un file non dichiarato viene respinto senza che nessuno ne legga il
  merito. Se durante un task ti accorgi che serve toccarne un altro, **fermati e segnalalo**:
  o il diff è sbagliato, o è il piano a essere incompleto, e nel secondo caso si corregge il
  piano.
- **Non aggiungere dipendenze** oltre quelle elencate in `pyproject.toml`. In particolare non
  aggiungere `photutils`, `sep`, `astroquery` né alcun client HTTP.
- **Non introdurre chiamate di rete**, in nessun punto, nemmeno nei test.
- **Non modificare** i file in `docs/superpowers/`, né la spec né questo piano, se non per
  spuntare le caselle.
- **Non committare né spingere su `main`.** Si lavora su `dev` e basta. Su `main` si arriva
  solo per merge di una pull request, e la pull request la apre e la chiude la sessione
  Claude di revisione.
- **Non creare tag git** e non pubblicare release. Il tag su `main` fa partire una
  pubblicazione, e non è un tuo gesto. Tu committi e spingi su `dev`.
- **Non aprire pull request** e non usare `gh pr`. Se pensi che `dev` sia pronto, dillo e
  fermati.
- **Non usare `git commit --amend`, `git rebase`, `git push --force`.** La storia resta
  quella che è.
- **Non installare ASTAP** e non invocarlo. Serve al plate solving allo Stadio 4, che non è
  in questo piano.
- **Non rendere privato il repository** e non cambiarne la visibilità. È pubblico per
  scelta, ed è da lì che vengono i minuti illimitati, CodeQL, la push protection e le
  attestazioni.
- **Non installare Docker, Jenkins o runner self-hosted**, e non proporre CI locale. I minuti
  sono illimitati: non c'è nessun problema da risolvere.
- **Non aggiungere runner Linux o macOS alla CI dei test.** Costerebbero zero, ma
  segnalerebbero un supporto che non diamo e produrrebbero fallimenti su piattaforme che non
  promettiamo. La piattaforma supportata è una sola. L'unica eccezione già prevista è il
  workflow di sicurezza, che gira su Linux perché analizza file senza eseguire il nostro
  codice.
- **Non committare segreti.** La push protection di GitHub è attiva e bloccherà il push:
  quando succede, non aggirarla e non riscrivere la storia — rimuovi il segreto, revocalo, e
  ricommitta.

### Quando qualcosa non torna

Fermati e segnala, indicando il numero del task, il numero del passo, il comando eseguito,
l'output completo ottenuto e l'output atteso. Non tentare percorsi alternativi e non
proseguire con i task successivi: in un piano TDD ogni task poggia sui precedenti, e andare
avanti su una base rotta moltiplica il lavoro da disfare.

Sono difetti del piano da segnalare, non problemi da risolvere in autonomia: un comando che
non funziona sulla shell, un test che passa prima dell'implementazione, un import che il
piano non ha previsto, una firma di funzione che non coincide fra due task, un risultato
numerico che non rientra nelle tolleranze dichiarate.

### Quando un task è finito

Un task è finito quando tutte le sue caselle sono spuntate, il comando dell'ultimo passo di
verifica dà l'esito atteso, **l'intera suite passa** — non solo i test del task corrente — e
il commit è stato creato con il messaggio indicato. Un commit per task, nella forma scritta
nel passo di commit. Non accorpare più task in un solo commit.

**Prima del commit, i due controlli che la CI rifarà su un runner pulito.** Sono gli stessi
comandi del job `lint`, costano un secondo, e se passano qui passano anche là:

Run: `ruff check .`

Expected: `All checks passed!`

Run: `ruff format --check .`

Expected: `N files already formatted`, senza nessun `would be reformatted`. Se segnala una
riformattazione, **il file che hai scritto non è quello del piano**: torna al blocco di
codice del task e ricopialo. I blocchi di questo documento sono già nella forma che `ruff`
pretende, quindi una differenza vuol dire che hai copiato da una lettura precedente, non
che il piano e lo strumento non vadano d'accordo. Correggere con `ruff format .` fa sparire
il sintomo e lascia il tuo file diverso dal piano.

Subito dopo il commit, **spingi su `dev`**:

Run: `git push origin dev`

Il push non è una formalità di fine giornata: è ciò che fa girare la CI, ed è lì che si
scopre di aver dimenticato un file nel commit.

**E la CI si legge, non si presume.** Il task non è finito finché non hai visto l'esito:

Run: `Start-Sleep -Seconds 30`

Run: `gh run list --branch dev --limit 3`

Expected: la corsa in cima è `completed` con conclusione `success`. Se è `in_progress`,
ripeti le due righe: dura un paio di minuti. Se è `failure`, leggi il motivo con
`gh run view --log-failed` e correggilo adesso. **Un task chiuso su una CI rossa non è
finito**, e il difetto che ti porti dietro lo ritrovi a valle, dove costa di più.

**Goal:** costruire lo strato di misura di Sagitta — leggere sub da qualunque software di acquisizione, misurare la forma stellare per stella, stratificarla per posizione nel campo — e validarlo su dati sintetici con verità nota.

**Architecture:** pipeline a strati senza stato condiviso. `ingest` normalizza header eterogenei in uno schema canonico usando mappe YAML versionate; `measure` fa detection e momenti secondi per stella, senza mai fidarsi dei valori nell'header; `zones` stratifica per raggio normalizzato; `synth` genera sub artificiali con aberrazione iniettata nota, e i test verificano che la misura la restituisca. Nessuna rete, nessun LLM, nessuna diagnosi in questo blocco: solo numeri e la loro validazione.

**Tech Stack:** Python 3.11+, numpy, scipy, astropy (lettura FITS), PyYAML, pytest. Nessuna dipendenza di rete. GUI, DuckDB, parser PHD2 e classificatore diagnostico sono fuori da questo piano.

**Perché Python, decisione chiusa.** Non per la velocità: la difficoltà vera del progetto è la correttezza statistica — intervalli di confidenza, normalizzazione per covariate, modello a effetti misti con la notte come effetto casuale — e quella allo Stadio 4 è `statsmodels`. La lettura FITS con tutti i dialetti reali è `astropy`, che nessun altro ecosistema replica. Rust vincerebbe sulla distribuzione ma non ha un equivalente maturo per i modelli a effetti misti, e per il FITS tornerebbe comunque a legarsi a CFITSIO. Il costo accettato è il peso del bundle nativo, 200-300 MB, che è un problema di packaging da affrontare allo Stadio 3. Se il ciclo dei momenti risultasse troppo lento, la via d'uscita è un'estensione Rust via PyO3 **solo per quello**, non un cambio di linguaggio.

**Spec:** [docs/design.md](design.md)

## Global Constraints

- Licenza **MIT**. Ogni file sorgente nuovo non porta intestazioni di licenza per file; la licenza sta solo in `LICENSE`.
- **Piattaforma supportata: solo Windows 11.** E' dove vive il bacino di utenza: NINA e' Windows-only, ASCOM e' tecnologia COM di Windows, i driver ZWO e l'accelerazione CUDA dei tool RC-Astro stanno li'. Una sola piattaforma da impacchettare, testare e firmare.
- **Il codice resta pero' portabile per costruzione.** Sempre `pathlib`, mai separatori di percorso scritti a mano, mai API specifiche di Windows, encoding sempre esplicito. Il mondo Ekos, INDI e Alpaca e' rimandato, non escluso: quando sara' il suo turno deve costare **aggiungere un job di CI**, non riscrivere il codice. Non anticipare quel lavoro, ma non pregiudicarlo.
- **Nessuna chiamata di rete, mai**, in nessun punto del codice o dei test.
- **Mai fidarsi di `HFR` / `FWHM` scritti negli header.** Si rimisura sempre con il motore interno. Se un header li contiene, si ignorano.
- **Solo sub grezze** entrano nelle metriche di forma. Le sub calibrate o registrate hanno forma alterata dall'interpolazione.
- Terminologia obbligatoria nel codice, nei commenti, nei messaggi e nei nomi: si dice **`field_aberration`** / "aberrazione di campo", **mai `tilt`**, quando la misura proviene da light frame senza scansione di fuoco. `tilt` è ammesso solo come nome di un parametro del *generatore sintetico*, dove è verità iniettata e non stima.
- **Guardrail di campionamento**: sopra 2.5 arcsec/pixel le metriche di forma non vengono prodotte. Il codice restituisce un rifiuto esplicito, non un numero.
- Nessun numero prodotto da un modello linguistico. In questo blocco non esiste alcuna integrazione LLM.
- Ogni funzione pubblica ha type hints. Test con `pytest`.
- **Versionamento SemVer**, sorgente unica in `pyproject.toml`, letta a runtime dai metadati del package. Serie `0.x` finché il join con i log di guida non è dentro.
- **Ogni release ha una voce nel `CHANGELOG.md`, senza eccezioni.** Si scrive sotto `[Non rilasciato]` mentre si lavora, e quella sezione diventa il corpo della release quando si crea il tag. Un rilascio senza voce nel changelog non è un rilascio: è un file comparso dal nulla.
- **Account GitHub Free, repository pubblico, nessuna funzionalità a pagamento.** Essendo pubblico: minuti di Actions **illimitati**, CodeQL, secret scanning con push protection e attestazioni di provenienza sono tutti gratuiti. Se una misura richiedesse comunque un piano a pagamento, non entra.
- **Sicurezza proporzionata.** Il metro è: chi scarica deve poter verificare che l'eseguibile sia quello costruito dalla nostra CI, e che il programma non mandi i suoi dati da nessuna parte. Tutto ciò che serve a quelle due cose si fa; il resto — SBOM firmato, SLSA L3, threat model formale — no.
- **Ogni `uses:` nei workflow è pinnato al SHA completo del commit**, con il tag in commento. Un tag mobile è codice di terzi che gira nella nostra pipeline con il nostro token.
- **Due rami soli: `dev` e `main`.** Si sviluppa e si committa su `dev`; su `main` si arriva solo per merge di una pull request, e ogni commit di `main` deve essere rilasciabile. Il tag `vX.Y.Z` si crea su `main` e fa partire il rilascio. Merge e tag sono gesti del proprietario del repository, non dell'agente che esegue.

---

## File Structure

```
(radice del repository: C:\Users\Voloirex\sagitta)
├── LICENSE                          MIT
├── README.md
├── SECURITY.md                      policy e istruzioni di verifica
├── CHANGELOG.md                     Keep a Changelog
├── pyproject.toml                   metadati, dipendenze, versione (sorgente unica)
├── ruff.toml                        configurazione del linter
├── .github/
│   ├── dependabot.yml               aggiornamenti pip e github-actions, verso dev
│   └── workflows/
│       ├── ci.yml                   dev, main e PR verso main: lint, test, audit
│       ├── security.yml             settimanale e PR verso main: CodeQL
│       └── release.yml              sui tag v*: build, checksum, attestazione, bozza
├── src/sagitta/
│   ├── __init__.py
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── schema.py                FrameMeta: schema canonico
│   │   ├── dialects.py              caricamento e applicazione mappe YAML
│   │   └── fits_reader.py           lettura FITS -> FrameMeta + pixel
│   ├── dialects/                    mappe dialetto -> canonico (dati, non codice)
│   │   ├── generic.yaml
│   │   ├── nina.yaml
│   │   ├── sgp.yaml
│   │   ├── asiair.yaml
│   │   └── ekos.yaml
│   ├── measure/
│   │   ├── __init__.py
│   │   ├── sampling.py              scala in arcsec/px e guardrail
│   │   ├── cfa.py                   estrazione canale verde da matrice di Bayer
│   │   ├── detect.py                detection stellare e criteri di esclusione
│   │   ├── shape.py                 momenti secondi: FWHM, eccentricita', angolo
│   │   ├── zones.py                 stratificazione per raggio normalizzato
│   │   └── frame.py                 orchestrazione per singolo frame
│   ├── synth/
│   │   ├── __init__.py
│   │   ├── psf.py                   resa di stelle gaussiane ellittiche
│   │   └── generator.py             sub sintetiche con aberrazione nota
│   └── cli.py                       comando `sagitta measure`
└── tests/
    ├── conftest.py
    ├── test_smoke.py                end-to-end sulla CLI installata
    ├── test_no_network.py           dimostra la promessa "tutto in locale"
    ├── test_version.py              versione allineata fra package e CLI
    ├── ingest/
    │   ├── test_schema.py
    │   ├── test_dialects.py
    │   └── test_fits_reader.py
    ├── measure/
    │   ├── test_sampling.py
    │   ├── test_cfa.py
    │   ├── test_detect.py
    │   ├── test_shape.py
    │   ├── test_zones.py
    │   └── test_frame.py
    ├── synth/
    │   ├── test_psf.py
    │   └── test_generator.py
    └── test_benchmark.py            validazione: la misura recupera la verita' iniettata
```

**Responsabilità di ciascun file.** `schema.py` definisce l'unica struttura dati di metadati che attraversa il sistema. `dialects.py` non sa niente di FITS: prende un dizionario di keyword e ne restituisce uno canonico. `fits_reader.py` è l'unico punto che tocca astropy. `shape.py` non sa niente di stelle: prende un ritaglio e restituisce momenti. `detect.py` decide quali stelle esistono e quali si buttano. `zones.py` è pura geometria. `frame.py` è l'unico che conosce l'ordine delle operazioni. `synth/` non importa mai da `measure/`, così i test non sono circolari.

---

### Task 1: Scaffolding del progetto e schema canonico

**Files:**
- Create: `pyproject.toml`
- Create: `LICENSE`
- Create: `src/sagitta/__init__.py`
- Create: `src/sagitta/ingest/__init__.py`
- Create: `src/sagitta/ingest/schema.py`
- Test: `tests/ingest/test_schema.py`

**Interfaces:**
- Consumes: niente.
- Produces: `FrameMeta` dataclass con i campi elencati sotto, e `FrameMeta.is_usable_for_shape() -> bool`. Tutti i task successivi importano `from sagitta.ingest.schema import FrameMeta`.

- [ ] **Step 1: Scrivere il test che fallisce**

Creare `tests/ingest/test_schema.py`:

```python
import datetime as dt

from sagitta.ingest.schema import FrameMeta


def _minimal() -> FrameMeta:
    return FrameMeta(
        path="/tmp/light_0001.fits",
        date_obs=dt.datetime(2026, 8, 29, 21, 30, 0, tzinfo=dt.UTC),
        exposure_s=300.0,
        width=6248,
        height=4176,
    )


def test_minimal_frame_has_optional_fields_none():
    meta = _minimal()
    assert meta.filter_name is None
    assert meta.focal_length_mm is None
    assert meta.pixel_size_um is None
    assert meta.bayer_pattern is None
    assert meta.frame_kind == "unknown"


def test_date_obs_must_be_timezone_aware():
    naive = dt.datetime(2026, 8, 29, 21, 30, 0)
    try:
        FrameMeta(
            path="/tmp/a.fits",
            date_obs=naive,
            exposure_s=300.0,
            width=100,
            height=100,
        )
    except ValueError as exc:
        assert "timezone" in str(exc).lower()
    else:
        raise AssertionError("era attesa una ValueError su datetime naive")


def test_only_raw_frames_are_usable_for_shape():
    raw = _minimal()
    assert raw.is_usable_for_shape() is True

    registered = _minimal()
    registered.frame_kind = "registered"
    assert registered.is_usable_for_shape() is False

    calibrated = _minimal()
    calibrated.frame_kind = "calibrated"
    assert calibrated.is_usable_for_shape() is False
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

L'ambiente virtuale è nuovo e non contiene ancora `pytest`. Il runner arriverebbe con
`pip install -e ".[dev]"` allo Step 4, che però ha bisogno del `pyproject.toml` creato allo
Step 3: prima del rosso va quindi installato il solo runner, e nient'altro.

Run: `pip install pytest`

Run: `python -m pytest tests/ingest/test_schema.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta'`

Se leggi invece `No module named pytest`, il comando qui sopra non è stato eseguito: il
fallimento che serve è quello del package assente, non quello del runner assente.

- [ ] **Step 3: Scrivere l'implementazione minima**

Creare `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "sagitta"
version = "0.1.0"
description = "Referto forense e banco di prova per astrofotografia"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
dependencies = [
    "numpy>=1.26",
    "scipy>=1.11",
    "astropy>=6.0",
    "PyYAML>=6.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[project.scripts]
sagitta = "sagitta.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
sagitta = ["dialects/*.yaml"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`LICENSE`, `README.md` e `CHANGELOG.md` **esistono già** nella radice. Verifica che ci
siano e **non toccarli in questo task**: il README viene aggiornato nel Task 12 e il
changelog nel Task 16, con istruzioni precise su cosa sostituire.

Creare `src/sagitta/__init__.py` vuoto e `src/sagitta/ingest/__init__.py` vuoto.

Creare `src/sagitta/ingest/schema.py`:

```python
"""Schema canonico dei metadati di un frame.

Unica struttura di metadati che attraversa il sistema. Ogni dialetto di header
viene normalizzato in questa forma prima di qualunque elaborazione.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Literal

FrameKind = Literal["raw", "calibrated", "registered", "unknown"]


@dataclass
class FrameMeta:
    """Metadati canonici di un singolo frame.

    Nota: i campi HFR/FWHM eventualmente presenti nell'header originale NON
    sono rappresentati qui di proposito. Sono incomparabili tra software e
    vanno sempre rimisurati dal motore interno.
    """

    path: str
    date_obs: dt.datetime
    exposure_s: float
    width: int
    height: int

    filter_name: str | None = None
    binning: int | None = None
    gain: float | None = None
    offset: float | None = None
    sensor_temp_c: float | None = None
    ambient_temp_c: float | None = None
    pixel_size_um: float | None = None
    focal_length_mm: float | None = None
    site_latitude_deg: float | None = None
    site_longitude_deg: float | None = None
    pointing_ra_deg: float | None = None
    pointing_dec_deg: float | None = None
    rotation_deg: float | None = None
    telescope: str | None = None
    instrument: str | None = None
    software: str | None = None
    bayer_pattern: str | None = None

    frame_kind: FrameKind = "unknown"
    unknown_keywords: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.date_obs.tzinfo is None:
            raise ValueError(
                "date_obs deve avere timezone: un istante naive rende "
                "impossibile il join con i log di guida"
            )
        if self.exposure_s <= 0:
            raise ValueError("exposure_s deve essere positiva")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width e height devono essere positive")

    def is_usable_for_shape(self) -> bool:
        """Solo le sub grezze entrano nelle metriche di forma.

        Calibrazione e registrazione alterano la PSF: l'interpolazione della
        registrazione arrotonda le stelle e abbassa sistematicamente
        l'eccentricita'. Includerle avvelena l'analisi in silenzio.
        """
        return self.frame_kind in ("raw", "unknown")
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `pip install -e ".[dev]"`

Run: `python -m pytest tests/ingest/test_schema.py -v`
Expected: PASS, 3 test

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: scaffolding progetto Sagitta e schema canonico dei frame"
```

> **Prossimo task: il 14, non il 2.** Vai ora a **Task 14: Integrazione continua su
> Windows**, poi torna qui e prosegui dal Task 2. La CI va accesa adesso, così ogni task
> successivo viene verificato in ambiente pulito mentre lo scrivi, invece che tutto insieme
> alla fine. Prima di eseguire il Task 14 leggi la sezione **La configurazione GitHub,
> decisa: account Free, repository pubblico**, in fondo a questo documento.

---

### Task 2: Dialetti di header

**Files:**
- Create: `src/sagitta/dialects/generic.yaml`
- Create: `src/sagitta/dialects/nina.yaml`
- Create: `src/sagitta/dialects/sgp.yaml`
- Create: `src/sagitta/dialects/asiair.yaml`
- Create: `src/sagitta/dialects/ekos.yaml`
- Create: `src/sagitta/ingest/dialects.py`
- Test: `tests/ingest/test_dialects.py`

**Interfaces:**
- Consumes: `FrameMeta` da Task 1.
- Produces:
  - `load_dialects() -> dict[str, Dialect]`
  - `detect_dialect(header: dict) -> str` — restituisce il nome del dialetto, `"generic"` se nessuno corrisponde
  - `apply_dialect(header: dict, dialect_name: str) -> tuple[dict[str, object], dict[str, object]]` — restituisce `(campi_canonici, keyword_sconosciute)`

- [x] **Step 1: Scrivere il test che fallisce**

Creare `tests/ingest/test_dialects.py`:

```python
from sagitta.ingest.dialects import apply_dialect, detect_dialect, load_dialects


def test_generic_dialect_always_available():
    dialects = load_dialects()
    assert "generic" in dialects
    assert "nina" in dialects
    assert "asiair" in dialects


def test_detect_nina_from_software_keyword():
    header = {"SWCREATE": "N.I.N.A. 3.1.2.9001", "EXPTIME": 300.0}
    assert detect_dialect(header) == "nina"


def test_detect_asiair():
    header = {"SWCREATE": "ASIAIR V2.1", "EXPOSURE": 120.0}
    assert detect_dialect(header) == "asiair"


def test_unknown_software_falls_back_to_generic():
    header = {"SWCREATE": "SoftwareMaiVisto 1.0"}
    assert detect_dialect(header) == "generic"


def test_apply_dialect_maps_canonical_fields():
    header = {
        "DATE-OBS": "2026-08-29T21:30:00",
        "EXPTIME": 300.0,
        "NAXIS1": 6248,
        "NAXIS2": 4176,
        "FILTER": "Ha",
        "XPIXSZ": 3.76,
        "FOCALLEN": 530.0,
        "GAIN": 100,
    }
    canonical, unknown = apply_dialect(header, "generic")
    assert canonical["exposure_s"] == 300.0
    assert canonical["width"] == 6248
    assert canonical["height"] == 4176
    assert canonical["filter_name"] == "Ha"
    assert canonical["pixel_size_um"] == 3.76
    assert canonical["focal_length_mm"] == 530.0
    assert canonical["gain"] == 100
    assert unknown == {}


def test_apply_dialect_collects_unknown_keywords():
    header = {"EXPTIME": 60.0, "PIPPO": "qualcosa"}
    canonical, unknown = apply_dialect(header, "generic")
    assert canonical["exposure_s"] == 60.0
    assert unknown == {"PIPPO": "qualcosa"}


def test_header_measured_values_are_never_mapped():
    """HFR e FWHM nell'header vanno ignorati, mai promossi a campo canonico."""
    header = {"EXPTIME": 60.0, "HFR": 2.31, "FWHM": 3.9}
    canonical, unknown = apply_dialect(header, "generic")
    assert "hfr" not in canonical
    assert "fwhm" not in canonical
    assert "HFR" not in unknown
    assert "FWHM" not in unknown
```

- [x] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/ingest/test_dialects.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.ingest.dialects'`

- [x] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/dialects/generic.yaml`:

```yaml
name: generic
match:
  software_contains: []
map:
  date_obs: [DATE-OBS, DATE_OBS]
  exposure_s: [EXPTIME, EXPOSURE]
  width: [NAXIS1, IMAGEW]
  height: [NAXIS2, IMAGEH]
  filter_name: [FILTER]
  binning: [XBINNING]
  gain: [GAIN, EGAIN]
  offset: [OFFSET, BLKLEVEL]
  sensor_temp_c: [CCD-TEMP, SET-TEMP]
  ambient_temp_c: [AMBTEMP, FOCTEMP]
  pixel_size_um: [XPIXSZ, PIXSIZE1]
  focal_length_mm: [FOCALLEN]
  site_latitude_deg: [SITELAT, LAT-OBS]
  site_longitude_deg: [SITELONG, LONG-OBS]
  pointing_ra_deg: [CRVAL1]
  pointing_dec_deg: [CRVAL2]
  rotation_deg: [ROTATANG, ROTATOR]
  telescope: [TELESCOP]
  instrument: [INSTRUME]
  software: [SWCREATE, PROGRAM]
  bayer_pattern: [BAYERPAT, COLORTYP]
date_obs_is_utc: true
date_obs_at_midpoint: false
ignore:
  - HFR
  - FWHM
  - ECCENTRICITY
  - STARCOUNT
```

Creare `src/sagitta/dialects/nina.yaml`:

```yaml
name: nina
match:
  software_contains: ["N.I.N.A", "NINA"]
inherits: generic
map:
  ambient_temp_c: [FOCTEMP, AMBTEMP]
  rotation_deg: [ROTATANG]
date_obs_is_utc: true
date_obs_at_midpoint: false
```

Creare `src/sagitta/dialects/asiair.yaml`:

```yaml
name: asiair
match:
  software_contains: ["ASIAIR"]
inherits: generic
map:
  exposure_s: [EXPOSURE, EXPTIME]
date_obs_is_utc: true
date_obs_at_midpoint: false
```

Creare `src/sagitta/dialects/sgp.yaml`:

```yaml
name: sgp
match:
  software_contains: ["Sequence Generator"]
inherits: generic
date_obs_is_utc: true
date_obs_at_midpoint: false
```

Creare `src/sagitta/dialects/ekos.yaml`:

```yaml
name: ekos
match:
  software_contains: ["Ekos", "KStars"]
inherits: generic
date_obs_is_utc: true
date_obs_at_midpoint: false
```

Nessuno dei due dichiara `map`: ereditano quella di `generic` senza sovrascriverla, ed e'
il motivo per cui non hanno un blocco `map` come `nina` e `asiair`. `load_dialects()` legge
la cartella con `glob("*.yaml")`, quindi comparire nella cartella basta a esistere: non c'e'
nessun elenco di nomi da aggiornare altrove.

**Perche' ci sono, se nessun test li nomina.** I test di questo task verificano `generic`,
`nina` e `asiair`. `sgp` ed `ekos` sono dati, non codice: la loro correttezza si vede su un
header vero, che qui non abbiamo. Stanno nel piano perche' la sezione **File Structure** li
elenca e perche' il progetto dichiara di coprire quei quattro software - non perche' un
test li pretenda.

Creare `src/sagitta/ingest/dialects.py`:

```python
"""Normalizzazione dei dialetti di header FITS verso lo schema canonico.

Le mappe vivono in file YAML versionati nel repository, non sono generate a
runtime. Aggiungere il supporto a un software di acquisizione significa
aggiungere un file YAML, ed e' un contributo che la community puo' mandare
come pull request.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DIALECTS_DIR = Path(__file__).resolve().parent.parent / "dialects"


@dataclass
class Dialect:
    name: str
    software_contains: list[str] = field(default_factory=list)
    map: dict[str, list[str]] = field(default_factory=dict)
    ignore: list[str] = field(default_factory=list)
    date_obs_is_utc: bool = True
    date_obs_at_midpoint: bool = False


@functools.lru_cache(maxsize=1)
def load_dialects() -> dict[str, Dialect]:
    """Carica tutti i dialetti da disco. Il risultato e' in cache."""
    raw: dict[str, dict] = {}
    for path in sorted(DIALECTS_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        raw[data["name"]] = data

    resolved: dict[str, Dialect] = {}
    for name, data in raw.items():
        merged_map: dict[str, list[str]] = {}
        ignore: list[str] = []
        parent_name = data.get("inherits")
        if parent_name:
            parent = raw[parent_name]
            merged_map.update(parent.get("map", {}))
            ignore.extend(parent.get("ignore", []))
        merged_map.update(data.get("map", {}))
        ignore.extend(data.get("ignore", []))

        resolved[name] = Dialect(
            name=name,
            software_contains=data.get("match", {}).get("software_contains", []),
            map=merged_map,
            ignore=sorted(set(ignore)),
            date_obs_is_utc=data.get("date_obs_is_utc", True),
            date_obs_at_midpoint=data.get("date_obs_at_midpoint", False),
        )
    return resolved


def detect_dialect(header: dict) -> str:
    """Identifica il dialetto dal software di acquisizione.

    Restituisce "generic" se nessun dialetto specifico corrisponde.
    """
    software = ""
    for key in ("SWCREATE", "PROGRAM", "CREATOR"):
        value = header.get(key)
        if isinstance(value, str) and value.strip():
            software = value
            break

    for name, dialect in load_dialects().items():
        if name == "generic":
            continue
        for token in dialect.software_contains:
            if token.lower() in software.lower():
                return name
    return "generic"


def apply_dialect(header: dict, dialect_name: str) -> tuple[dict[str, object], dict[str, object]]:
    """Traduce un header grezzo in campi canonici piu' keyword sconosciute.

    Le keyword nella lista `ignore` del dialetto non finiscono ne' fra i campi
    canonici ne' fra le sconosciute: sono scartate di proposito. E' il caso di
    HFR e FWHM, che sono incomparabili tra software e vanno rimisurati.
    """
    dialect = load_dialects()[dialect_name]

    canonical: dict[str, object] = {}
    consumed: set[str] = set()

    for canonical_name, candidates in dialect.map.items():
        for keyword in candidates:
            if keyword in header:
                canonical[canonical_name] = header[keyword]
                consumed.add(keyword)
                break

    structural = {"SIMPLE", "BITPIX", "NAXIS", "EXTEND", "END", "COMMENT", "HISTORY"}
    unknown = {
        key: value
        for key, value in header.items()
        if key not in consumed and key not in dialect.ignore and key not in structural
    }
    return canonical, unknown
```

- [x] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/ingest/test_dialects.py -v`
Expected: PASS, 7 test

- [x] **Step 5: Commit**

```bash
git add .
git commit -m "feat: dialetti di header FITS come mappe YAML versionate"
```

---

### Task 3: Lettore FITS

**Files:**
- Create: `src/sagitta/ingest/fits_reader.py`
- Create: `tests/conftest.py`
- Test: `tests/ingest/test_fits_reader.py`

**Interfaces:**
- Consumes: `FrameMeta` (Task 1), `detect_dialect` e `apply_dialect` (Task 2).
- Produces: `read_frame(path: Path) -> tuple[FrameMeta, numpy.ndarray]`. L'array è sempre `float64` 2D.

- [x] **Step 1: Scrivere il test che fallisce**

Creare `tests/conftest.py`:

```python
from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits


@pytest.fixture
def write_fits(tmp_path: Path):
    """Scrive un FITS di test e ne restituisce il percorso."""

    def _write(name: str, data: np.ndarray, header_cards: dict) -> Path:
        hdu = fits.PrimaryHDU(data.astype(np.float32))
        for key, value in header_cards.items():
            hdu.header[key] = value
        path = tmp_path / name
        hdu.writeto(path, overwrite=True)
        return path

    return _write
```

Creare `tests/ingest/test_fits_reader.py`:

```python
import datetime as dt
from dataclasses import replace

import numpy as np
import pytest

from sagitta.ingest.dialects import load_dialects
from sagitta.ingest.fits_reader import read_frame


def test_reads_canonical_fields(write_fits):
    data = np.zeros((40, 60), dtype=np.float32)
    path = write_fits(
        "light.fits",
        data,
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 300.0,
            "FILTER": "Ha",
            "XPIXSZ": 3.76,
            "FOCALLEN": 530.0,
            "SWCREATE": "N.I.N.A. 3.1.2.9001",
        },
    )
    meta, pixels = read_frame(path)

    assert meta.exposure_s == 300.0
    assert meta.filter_name == "Ha"
    assert meta.pixel_size_um == 3.76
    assert meta.focal_length_mm == 530.0
    assert meta.software == "N.I.N.A. 3.1.2.9001"
    assert meta.width == 60
    assert meta.height == 40
    assert pixels.shape == (40, 60)
    assert pixels.dtype == np.float64


def test_date_obs_without_timezone_is_assumed_utc(write_fits):
    path = write_fits(
        "a.fits",
        np.zeros((10, 10), dtype=np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 60.0},
    )
    meta, _ = read_frame(path)
    assert meta.date_obs.tzinfo is dt.UTC
    assert meta.date_obs.hour == 21


def test_naive_date_obs_rejected_when_dialect_does_not_declare_timezone(write_fits, monkeypatch):
    path = write_fits(
        "naive-no-timezone.fits",
        np.zeros((10, 10), dtype=np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 60.0},
    )
    import sagitta.ingest.fits_reader as fits_reader

    dialects = load_dialects().copy()
    dialects["generic"] = replace(dialects["generic"], date_obs_is_utc=False)
    monkeypatch.setattr(fits_reader, "load_dialects", lambda: dialects)

    with pytest.raises(ValueError, match="does not declare"):
        read_frame(path)


def test_unknown_keywords_are_preserved(write_fits):
    path = write_fits(
        "b.fits",
        np.zeros((10, 10), dtype=np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 60.0, "PIPPO": "x"},
    )
    meta, _ = read_frame(path)
    assert meta.unknown_keywords["PIPPO"] == "x"


def test_header_hfr_is_discarded(write_fits):
    path = write_fits(
        "c.fits",
        np.zeros((10, 10), dtype=np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 60.0, "HFR": 2.3},
    )
    meta, _ = read_frame(path)
    assert "HFR" not in meta.unknown_keywords


def test_bayer_pattern_is_read(write_fits):
    path = write_fits(
        "osc.fits",
        np.zeros((10, 10), dtype=np.float32),
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 60.0,
            "BAYERPAT": "RGGB",
        },
    )
    meta, _ = read_frame(path)
    assert meta.bayer_pattern == "RGGB"
```

- [x] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/ingest/test_fits_reader.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.ingest.fits_reader'`

- [x] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/ingest/fits_reader.py`:

```python
"""Lettura di file FITS. Unico punto del progetto che tocca astropy."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
from astropy.io import fits

from sagitta.ingest.dialects import apply_dialect, detect_dialect, load_dialects
from sagitta.ingest.schema import FrameMeta


def _parse_date_obs(value: str, assume_utc: bool) -> dt.datetime:
    """Interpreta DATE-OBS. Senza timezone esplicita si assume UTC solo se
    il dialetto lo dichiara; altrimenti l'istante ambiguo viene rifiutato.

    L'assunzione va dichiarata all'utente: e' la sorgente di errore piu'
    comune nel join con i log di guida, specie nella notte del cambio ora.
    """
    text = value.strip().replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        if not assume_utc:
            raise ValueError(
                f"DATE-OBS {value!r} has no timezone and the dialect does not "
                "declare one: the instant is ambiguous, and guessing it would "
                "silently poison the join with the guiding logs"
            )
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed


def read_frame(path: Path) -> tuple[FrameMeta, np.ndarray]:
    """Legge un FITS e restituisce metadati canonici piu' i pixel in float64."""
    path = Path(path)
    with fits.open(path, memmap=False) as hdul:
        hdu = next(h for h in hdul if h.data is not None)
        raw_header = {key: hdu.header[key] for key in hdu.header if key}
        pixels = np.asarray(hdu.data, dtype=np.float64)

    if pixels.ndim != 2:
        raise ValueError(f"{path.name}: attesa immagine 2D, trovate {pixels.ndim} dimensioni")

    dialect_name = detect_dialect(raw_header)
    dialect = load_dialects()[dialect_name]
    canonical, unknown = apply_dialect(raw_header, dialect_name)

    date_obs_raw = canonical.get("date_obs")
    if not isinstance(date_obs_raw, str):
        raise ValueError(f"{path.name}: DATE-OBS mancante o non testuale")
    date_obs = _parse_date_obs(date_obs_raw, dialect.date_obs_is_utc)

    exposure_s = float(canonical["exposure_s"])
    if dialect.date_obs_at_midpoint:
        date_obs = date_obs - dt.timedelta(seconds=exposure_s / 2.0)

    height, width = pixels.shape

    def _opt_float(key: str) -> float | None:
        value = canonical.get(key)
        return float(value) if value is not None else None

    def _opt_str(key: str) -> str | None:
        value = canonical.get(key)
        return str(value).strip() if value is not None else None

    meta = FrameMeta(
        path=str(path),
        date_obs=date_obs,
        exposure_s=exposure_s,
        width=width,
        height=height,
        filter_name=_opt_str("filter_name"),
        binning=int(canonical["binning"]) if canonical.get("binning") else None,
        gain=_opt_float("gain"),
        offset=_opt_float("offset"),
        sensor_temp_c=_opt_float("sensor_temp_c"),
        ambient_temp_c=_opt_float("ambient_temp_c"),
        pixel_size_um=_opt_float("pixel_size_um"),
        focal_length_mm=_opt_float("focal_length_mm"),
        site_latitude_deg=_opt_float("site_latitude_deg"),
        site_longitude_deg=_opt_float("site_longitude_deg"),
        pointing_ra_deg=_opt_float("pointing_ra_deg"),
        pointing_dec_deg=_opt_float("pointing_dec_deg"),
        rotation_deg=_opt_float("rotation_deg"),
        telescope=_opt_str("telescope"),
        instrument=_opt_str("instrument"),
        software=_opt_str("software"),
        bayer_pattern=_opt_str("bayer_pattern"),
        frame_kind="unknown",
        unknown_keywords=unknown,
    )
    return meta, pixels
```

- [x] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/ingest/ -v`
Expected: PASS, tutti i test di ingest

- [x] **Step 5: Commit**

```bash
git add .
git commit -m "feat: lettura FITS con normalizzazione dei dialetti"
```

---

### Task 4: Scala di campionamento e guardrail

**Files:**
- Create: `src/sagitta/measure/__init__.py`
- Create: `src/sagitta/measure/sampling.py`
- Test: `tests/measure/test_sampling.py`

**Interfaces:**
- Consumes: `FrameMeta` (Task 1).
- Produces:
  - `pixel_scale_arcsec(pixel_size_um: float, focal_length_mm: float, binning: int = 1) -> float`
  - `SamplingVerdict` dataclass con campi `scale_arcsec: float | None`, `shape_metrics_allowed: bool`, `reason: str`
  - `evaluate_sampling(meta: FrameMeta, effective_pixel_factor: float = 1.0) -> SamplingVerdict`
  - Costante `MAX_SCALE_ARCSEC = 2.5`

- [x] **Step 1: Scrivere il test che fallisce**

Creare `tests/measure/test_sampling.py`:

```python
import datetime as dt

import pytest

from sagitta.ingest.schema import FrameMeta
from sagitta.measure.sampling import (
    MAX_SCALE_ARCSEC,
    evaluate_sampling,
    pixel_scale_arcsec,
)


def _meta(pixel_size_um=3.76, focal_length_mm=530.0, binning=1) -> FrameMeta:
    return FrameMeta(
        path="/tmp/x.fits",
        date_obs=dt.datetime(2026, 8, 29, 21, 0, tzinfo=dt.UTC),
        exposure_s=300.0,
        width=100,
        height=100,
        pixel_size_um=pixel_size_um,
        focal_length_mm=focal_length_mm,
        binning=binning,
    )


def test_pixel_scale_known_value():
    # 206.265 * 3.76 / 530 = 1.4632...
    assert pixel_scale_arcsec(3.76, 530.0) == pytest.approx(1.4633, abs=1e-3)


def test_pixel_scale_scales_with_binning():
    single = pixel_scale_arcsec(3.76, 530.0, binning=1)
    double = pixel_scale_arcsec(3.76, 530.0, binning=2)
    assert double == pytest.approx(2 * single, rel=1e-9)


def test_well_sampled_frame_allows_shape_metrics():
    verdict = evaluate_sampling(_meta())
    assert verdict.shape_metrics_allowed is True
    assert verdict.scale_arcsec == pytest.approx(1.4633, abs=1e-3)


def test_undersampled_frame_refuses_shape_metrics():
    # 3.76 um su 200 mm = 3.88 arcsec/px, ben oltre la soglia
    verdict = evaluate_sampling(_meta(focal_length_mm=200.0))
    assert verdict.shape_metrics_allowed is False
    assert "campionamento" in verdict.reason.lower()
    assert str(MAX_SCALE_ARCSEC) in verdict.reason


def test_missing_optics_data_refuses_and_says_so():
    meta = _meta()
    meta.focal_length_mm = None
    verdict = evaluate_sampling(meta)
    assert verdict.shape_metrics_allowed is False
    assert verdict.scale_arcsec is None
    assert "focale" in verdict.reason.lower()


def test_effective_pixel_factor_applies_for_osc():
    """Su OSC il sotto-reticolo verde raddoppia la scala effettiva."""
    mono = evaluate_sampling(_meta(), effective_pixel_factor=1.0)
    osc = evaluate_sampling(_meta(), effective_pixel_factor=2.0)
    assert osc.scale_arcsec == pytest.approx(2 * mono.scale_arcsec, rel=1e-9)
```

- [x] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/measure/test_sampling.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.measure'`

- [x] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/measure/__init__.py` vuoto.

Creare `src/sagitta/measure/sampling.py`:

```python
"""Scala di campionamento e guardrail sulle metriche di forma.

Sotto un campionamento sufficiente, eccentricita' e angolo di posizione sono
quantizzati a rumore: una stella larga due pixel non ha una forma misurabile.
In quel caso Sagitta si rifiuta di rispondere invece di produrre un numero.
"""

from __future__ import annotations

from dataclasses import dataclass

from sagitta.ingest.schema import FrameMeta

ARCSEC_PER_RADIAN = 206264.806

MAX_SCALE_ARCSEC = 2.5
"""Soglia oltre la quale le metriche di forma non vengono prodotte."""


def pixel_scale_arcsec(pixel_size_um: float, focal_length_mm: float, binning: int = 1) -> float:
    """Scala in arcosecondi per pixel.

    scale = 206.265 * dimensione_pixel_um / focale_mm
    """
    if focal_length_mm <= 0:
        raise ValueError("focal_length_mm deve essere positiva")
    if pixel_size_um <= 0:
        raise ValueError("pixel_size_um deve essere positiva")
    binning = max(1, int(binning))
    return (ARCSEC_PER_RADIAN * pixel_size_um * binning) / (focal_length_mm * 1000.0)


@dataclass
class SamplingVerdict:
    scale_arcsec: float | None
    shape_metrics_allowed: bool
    reason: str


def evaluate_sampling(meta: FrameMeta, effective_pixel_factor: float = 1.0) -> SamplingVerdict:
    """Decide se le metriche di forma sono ammesse per questo frame.

    `effective_pixel_factor` vale 2.0 quando si misura su un sotto-reticolo
    verde di una matrice di Bayer, perche' il passo effettivo raddoppia.
    """
    if meta.pixel_size_um is None:
        return SamplingVerdict(
            None,
            False,
            "Dimensione del pixel assente nell'header: impossibile calcolare "
            "la scala, metriche di forma non prodotte.",
        )
    if meta.focal_length_mm is None:
        return SamplingVerdict(
            None,
            False,
            "Focale assente nell'header: impossibile calcolare la scala, "
            "metriche di forma non prodotte.",
        )

    scale = (
        pixel_scale_arcsec(meta.pixel_size_um, meta.focal_length_mm, meta.binning or 1)
        * effective_pixel_factor
    )

    if scale > MAX_SCALE_ARCSEC:
        return SamplingVerdict(
            scale,
            False,
            f"Campionamento insufficiente: {scale:.2f} arcsec/px, oltre la "
            f"soglia di {MAX_SCALE_ARCSEC} arcsec/px. Eccentricita' e angolo "
            f"sarebbero rumore quantizzato, quindi non vengono prodotti.",
        )

    return SamplingVerdict(scale, True, f"Campionamento adeguato: {scale:.2f} arcsec/px.")
```

- [x] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/measure/test_sampling.py -v`
Expected: PASS, 6 test

- [x] **Step 5: Commit**

```bash
git add .
git commit -m "feat: scala di campionamento e guardrail sulle metriche di forma"
```

---

### Task 5: Estrazione del canale verde da matrice di Bayer

**Files:**
- Create: `src/sagitta/measure/cfa.py`
- Test: `tests/measure/test_cfa.py`

**Interfaces:**
- Consumes: niente da task precedenti (solo numpy).
- Produces:
  - `is_bayer(pattern: str | None) -> bool`
  - `extract_green_sublattice(pixels: np.ndarray, pattern: str) -> np.ndarray` — restituisce un array di dimensioni `(H//2, W//2)`
  - Costante `GREEN_SUBLATTICE_SCALE_FACTOR = 2.0`

- [x] **Step 1: Scrivere il test che fallisce**

Creare `tests/measure/test_cfa.py`:

```python
import numpy as np
import pytest

from sagitta.measure.cfa import (
    GREEN_SUBLATTICE_SCALE_FACTOR,
    extract_green_sublattice,
    is_bayer,
)


def test_is_bayer():
    assert is_bayer("RGGB") is True
    assert is_bayer("bggr") is True
    assert is_bayer(None) is False
    assert is_bayer("") is False
    assert is_bayer("MONO") is False


def test_green_sublattice_halves_both_dimensions():
    pixels = np.arange(8 * 6, dtype=np.float64).reshape(8, 6)
    green = extract_green_sublattice(pixels, "RGGB")
    assert green.shape == (4, 3)


def test_rggb_picks_the_green_at_row0_col1():
    # In RGGB il 2x2 e' [[R, G], [G, B]]: il verde della prima riga sta a (0, 1).
    pixels = np.zeros((4, 4), dtype=np.float64)
    pixels[0, 1] = 10.0
    pixels[0, 3] = 20.0
    pixels[2, 1] = 30.0
    pixels[2, 3] = 40.0
    green = extract_green_sublattice(pixels, "RGGB")
    assert green.tolist() == [[10.0, 20.0], [30.0, 40.0]]


def test_bggr_picks_the_same_offset_as_rggb():
    # In BGGR il 2x2 e' [[B, G], [G, R]]: il verde di riga 0 sta di nuovo a (0, 1).
    pixels = np.zeros((4, 4), dtype=np.float64)
    pixels[0, 1] = 7.0
    green = extract_green_sublattice(pixels, "BGGR")
    assert green[0, 0] == 7.0


def test_grbg_picks_the_green_at_row0_col0():
    # In GRBG il 2x2 e' [[G, R], [B, G]]: il verde di riga 0 sta a (0, 0).
    pixels = np.zeros((4, 4), dtype=np.float64)
    pixels[0, 0] = 5.0
    green = extract_green_sublattice(pixels, "GRBG")
    assert green[0, 0] == 5.0


def test_unknown_pattern_raises():
    with pytest.raises(ValueError, match="pattern"):
        extract_green_sublattice(np.zeros((4, 4)), "XXXX")


def test_scale_factor_is_two():
    assert GREEN_SUBLATTICE_SCALE_FACTOR == 2.0
```

- [x] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/measure/test_cfa.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.measure.cfa'`

- [x] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/measure/cfa.py`:

```python
"""Gestione delle sub a colori con matrice di Bayer.

Su una sub OSC grezza la forma stellare misurata e' un artefatto della
matrice: ogni canale campiona un pixel ogni due per riga e colonna, e la PSF
risulta deformata in modo dipendente dall'orientamento.

Si misura quindi su un solo sotto-reticolo verde, estratto SENZA
interpolazione. Non si usa una sub demosaicizzata: l'interpolazione del
demosaico arrotonda le stelle esattamente come fa la registrazione, e
falserebbe l'eccentricita' verso il basso.

Si prende un solo sotto-reticolo verde e non entrambi, perche' i due verdi
insieme formano un reticolo a quinconce e non una griglia regolare. Il prezzo
e' che il passo effettivo raddoppia in entrambi gli assi: da qui
GREEN_SUBLATTICE_SCALE_FACTOR, che va passato a evaluate_sampling.
"""

from __future__ import annotations

import numpy as np

GREEN_SUBLATTICE_SCALE_FACTOR = 2.0
"""Il sotto-reticolo verde ha passo doppio rispetto al pixel nativo."""

_BAYER_PATTERNS = {"RGGB", "BGGR", "GRBG", "GBRG"}

_GREEN_OFFSET = {
    "RGGB": (0, 1),
    "BGGR": (0, 1),
    "GRBG": (0, 0),
    "GBRG": (0, 0),
}


def is_bayer(pattern: str | None) -> bool:
    """Vero se la stringa e' un pattern di Bayer riconosciuto."""
    if not pattern:
        return False
    return pattern.strip().upper() in _BAYER_PATTERNS


def extract_green_sublattice(pixels: np.ndarray, pattern: str) -> np.ndarray:
    """Estrae un sotto-reticolo verde senza alcuna interpolazione.

    L'array risultante ha dimensioni (H // 2, W // 2) ed e' una griglia
    regolare, misurabile con lo stesso motore delle sub monocromatiche.
    """
    key = (pattern or "").strip().upper()
    if key not in _GREEN_OFFSET:
        raise ValueError(f"pattern di Bayer non riconosciuto: {pattern!r}")

    row_offset, col_offset = _GREEN_OFFSET[key]
    height, width = pixels.shape

    # Un campione ogni due, a partire dall'offset del verde. Il taglio a
    # (H // 2, W // 2) serve alle dimensioni dispari, dove lo slice con
    # offset 0 restituirebbe una riga o una colonna in piu' di quante ne
    # prometta la firma.
    view = pixels[row_offset::2, col_offset::2]
    return np.ascontiguousarray(view[: height // 2, : width // 2])
```

**Il conto da fare e' quanti campioni, non quanta larghezza.** Il numero di verdi su una
riga e' `width // 2`, e non dipende dall'offset: con `col_offset = 1` e `width = 6` i verdi
stanno a 1, 3, 5, e sono tre. Ragionare invece sull'intervallo utilizzabile a partire
dall'offset - `(width - col_offset) // 2 * 2`, cioe' 4 - taglia la riga a 1..4 e ne fa
uscire due. L'errore compare solo quando l'offset vale 1 e la dimensione e' pari, che e'
il caso di **ogni sensore reale** in RGGB o BGGR: su un 6248x4176 si perderebbe una colonna
su 3124, abbastanza poco da non vedersi a occhio e abbastanza da spostare le misure.

- [x] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/measure/test_cfa.py -v`
Expected: PASS, 7 test

- [x] **Step 5: Commit**

```bash
git add .
git commit -m "feat: estrazione del canale verde da matrice di Bayer senza interpolazione"
```

---

### Task 6: Momenti secondi e forma stellare

Questo task precede la detection di proposito: la misura di forma è testabile
in isolamento su ritagli costruiti a mano, e la detection la userà.

**Files:**
- Create: `src/sagitta/measure/shape.py`
- Test: `tests/measure/test_shape.py`

**Interfaces:**
- Consumes: niente (solo numpy).
- Produces:
  - `StarShape` dataclass: `x: float`, `y: float`, `flux: float`, `fwhm_px: float`, `eccentricity: float`, `position_angle_deg: float`
  - `measure_shape(cutout: np.ndarray, x0: int, y0: int) -> StarShape | None` — `x0, y0` sono le coordinate del pixel in alto a sinistra del ritaglio nell'immagine intera; restituisce `None` se i momenti non sono calcolabili.

- [x] **Step 1: Scrivere il test che fallisce**

Creare `tests/measure/test_shape.py`:

```python
import numpy as np
import pytest

from sagitta.measure.shape import measure_shape


def _gaussian(size: int, sigma_x: float, sigma_y: float, theta_deg: float = 0.0):
    """Gaussiana ellittica centrata, ruotata di theta_deg in senso antiorario."""
    c = (size - 1) / 2.0
    yy, xx = np.mgrid[0:size, 0:size]
    dx = xx - c
    dy = yy - c
    t = np.deg2rad(theta_deg)
    xr = dx * np.cos(t) + dy * np.sin(t)
    yr = -dx * np.sin(t) + dy * np.cos(t)
    return np.exp(-0.5 * ((xr / sigma_x) ** 2 + (yr / sigma_y) ** 2))


def test_circular_star_has_zero_eccentricity():
    cutout = _gaussian(21, 2.0, 2.0)
    shape = measure_shape(cutout, 0, 0)
    assert shape is not None
    assert shape.eccentricity == pytest.approx(0.0, abs=0.02)


def test_circular_star_fwhm_matches_sigma():
    sigma = 2.0
    cutout = _gaussian(31, sigma, sigma)
    shape = measure_shape(cutout, 0, 0)
    expected = 2.0 * np.sqrt(2.0 * np.log(2.0)) * sigma
    assert shape.fwhm_px == pytest.approx(expected, rel=0.05)


def test_elongated_star_has_positive_eccentricity():
    cutout = _gaussian(31, 4.0, 2.0)
    shape = measure_shape(cutout, 0, 0)
    # e = sqrt(1 - (b/a)^2) = sqrt(1 - (2/4)^2) = 0.866
    assert shape.eccentricity == pytest.approx(0.866, abs=0.05)


def test_position_angle_zero_for_horizontal_elongation():
    cutout = _gaussian(31, 4.0, 2.0, theta_deg=0.0)
    shape = measure_shape(cutout, 0, 0)
    assert shape.position_angle_deg == pytest.approx(0.0, abs=3.0)


def test_position_angle_45_degrees():
    cutout = _gaussian(31, 4.0, 2.0, theta_deg=45.0)
    shape = measure_shape(cutout, 0, 0)
    assert shape.position_angle_deg == pytest.approx(45.0, abs=3.0)


def test_position_angle_is_wrapped_into_0_180():
    cutout = _gaussian(31, 4.0, 2.0, theta_deg=170.0)
    shape = measure_shape(cutout, 0, 0)
    assert 0.0 <= shape.position_angle_deg < 180.0
    assert shape.position_angle_deg == pytest.approx(170.0, abs=3.0)


def test_offset_is_added_to_centroid():
    cutout = _gaussian(21, 2.0, 2.0)
    shape = measure_shape(cutout, x0=100, y0=200)
    assert shape.x == pytest.approx(110.0, abs=0.2)
    assert shape.y == pytest.approx(210.0, abs=0.2)


def test_empty_cutout_returns_none():
    assert measure_shape(np.zeros((11, 11)), 0, 0) is None
```

- [x] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/measure/test_shape.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.measure.shape'`

- [x] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/measure/shape.py`:

```python
"""Misura della forma stellare tramite momenti secondi pesati sul flusso.

Si usano i momenti invece di un fit di PSF perche' non richiedono di scegliere
un modello (gaussiana, Moffat, e con quale beta), sono deterministici e non
hanno problemi di convergenza. Il prezzo e' una maggiore sensibilita' al
fondo: per questo il ritaglio deve arrivare qui gia' sottratto del fondo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

FWHM_PER_SIGMA = 2.0 * math.sqrt(2.0 * math.log(2.0))
"""Fattore di conversione da sigma gaussiana a FWHM: circa 2.3548."""


@dataclass
class StarShape:
    x: float
    y: float
    flux: float
    fwhm_px: float
    eccentricity: float
    position_angle_deg: float


def measure_shape(cutout: np.ndarray, x0: int, y0: int) -> StarShape | None:
    """Momenti secondi di un ritaglio gia' sottratto del fondo.

    `x0`, `y0` sono le coordinate nell'immagine intera del pixel in alto a
    sinistra del ritaglio, e vengono sommate al centroide.

    Restituisce None se il flusso totale non e' positivo o se i momenti
    risultano degeneri.
    """
    weights = np.clip(np.asarray(cutout, dtype=np.float64), 0.0, None)
    total = float(weights.sum())
    if total <= 0.0:
        return None

    height, width = weights.shape
    yy, xx = np.mgrid[0:height, 0:width]

    x_bar = float((weights * xx).sum() / total)
    y_bar = float((weights * yy).sum() / total)

    dx = xx - x_bar
    dy = yy - y_bar
    m_xx = float((weights * dx * dx).sum() / total)
    m_yy = float((weights * dy * dy).sum() / total)
    m_xy = float((weights * dx * dy).sum() / total)

    if m_xx <= 0.0 or m_yy <= 0.0:
        return None

    half_sum = (m_xx + m_yy) / 2.0
    half_diff = (m_xx - m_yy) / 2.0
    root = math.sqrt(half_diff * half_diff + m_xy * m_xy)

    major_var = half_sum + root
    minor_var = half_sum - root
    if major_var <= 0.0:
        return None
    minor_var = max(minor_var, 0.0)

    eccentricity = math.sqrt(max(0.0, 1.0 - minor_var / major_var))

    # sigma media geometrica dei due assi -> FWHM equivalente circolare
    sigma_equiv = math.sqrt(half_sum)
    fwhm = FWHM_PER_SIGMA * sigma_equiv

    angle_rad = 0.5 * math.atan2(2.0 * m_xy, m_xx - m_yy)
    angle_deg = math.degrees(angle_rad) % 180.0

    return StarShape(
        x=x_bar + x0,
        y=y_bar + y0,
        flux=total,
        fwhm_px=fwhm,
        eccentricity=eccentricity,
        position_angle_deg=angle_deg,
    )
```

- [x] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/measure/test_shape.py -v`
Expected: PASS, 8 test

- [x] **Step 5: Commit**

```bash
git add .
git commit -m "feat: misura della forma stellare con momenti secondi"
```

---

### Task 7: Detection stellare e criteri di esclusione

**Files:**
- Create: `src/sagitta/measure/detect.py`
- Test: `tests/measure/test_detect.py`

**Interfaces:**
- Consumes: `StarShape` e `measure_shape` (Task 6).
- Produces:
  - `DetectionSettings` dataclass: `threshold_sigma: float = 5.0`, `min_pixels: int = 5`, `max_pixels: int = 2000`, `cutout_radius: int = 10`, `border_margin: int = 12`, `max_flat_top_pixels: int = 3`, `saturation_level: float | None = None`
  - `estimate_background(pixels: np.ndarray) -> tuple[float, float]` — restituisce `(mediana, sigma_robusta)`
  - `detect_stars(pixels: np.ndarray, settings: DetectionSettings | None = None) -> list[StarShape]`

- [ ] **Step 1: Scrivere il test che fallisce**

Creare `tests/measure/test_detect.py`:

```python
import numpy as np
import pytest

from sagitta.measure.detect import (
    DetectionSettings,
    detect_stars,
    estimate_background,
)


def _place_gaussian(image, cx, cy, sigma, amplitude):
    size = int(np.ceil(sigma * 6))
    yy, xx = np.mgrid[cy - size : cy + size + 1, cx - size : cx + size + 1]
    image[cy - size : cy + size + 1, cx - size : cx + size + 1] += amplitude * np.exp(
        -0.5 * (((xx - cx) / sigma) ** 2 + ((yy - cy) / sigma) ** 2)
    )
    return image


def _field(width=200, height=200, background=100.0, noise=2.0, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(background, noise, size=(height, width))


def test_estimate_background_recovers_median_and_sigma():
    image = _field(background=250.0, noise=5.0)
    median, sigma = estimate_background(image)
    assert median == pytest.approx(250.0, abs=1.0)
    assert sigma == pytest.approx(5.0, rel=0.2)


def test_detects_isolated_stars():
    image = _field(seed=1)
    for cx, cy in [(50, 50), (150, 60), (100, 140)]:
        _place_gaussian(image, cx, cy, sigma=2.0, amplitude=500.0)

    stars = detect_stars(image)
    assert len(stars) == 3

    found = sorted((round(s.x), round(s.y)) for s in stars)
    assert found == [(50, 50), (100, 140), (150, 60)]


def test_rejects_stars_touching_the_border():
    image = _field(seed=2)
    _place_gaussian(image, 5, 5, sigma=2.0, amplitude=500.0)
    _place_gaussian(image, 100, 100, sigma=2.0, amplitude=500.0)

    stars = detect_stars(image)
    assert len(stars) == 1
    assert round(stars[0].x) == 100


def test_rejects_saturated_stars():
    image = _field(seed=3)
    _place_gaussian(image, 100, 100, sigma=2.0, amplitude=500.0)
    # stella satura: cima piatta al valore massimo
    image[70:76, 70:76] = 65535.0

    stars = detect_stars(image, DetectionSettings(max_flat_top_pixels=3))
    positions = [round(s.x) for s in stars]
    assert 100 in positions
    assert 72 not in positions


def test_brightest_unsaturated_star_is_kept():
    """Il criterio di saturazione non deve scartare la stella piu' luminosa
    solo perche' e' la piu' luminosa: deve guardare la cima piatta."""
    image = _field(seed=31)
    _place_gaussian(image, 60, 60, sigma=2.0, amplitude=500.0)
    _place_gaussian(image, 140, 140, sigma=2.0, amplitude=20000.0)

    stars = detect_stars(image)
    positions = sorted(round(s.x) for s in stars)
    assert positions == [60, 140]


def test_rejects_single_hot_pixel():
    image = _field(seed=4)
    image[120, 130] = 60000.0
    _place_gaussian(image, 60, 60, sigma=2.0, amplitude=500.0)

    stars = detect_stars(image, DetectionSettings(min_pixels=5))
    positions = [round(s.x) for s in stars]
    assert 60 in positions
    assert 130 not in positions


def test_empty_field_returns_no_stars():
    assert detect_stars(_field(seed=5)) == []
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/measure/test_detect.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.measure.detect'`

- [ ] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/measure/detect.py`:

```python
"""Detection stellare e criteri di esclusione.

I criteri di esclusione contano piu' della fisica: dominano il risultato.
Una stella satura ha la cima piatta e un'eccentricita' casuale; un pixel caldo
sembra una stella perfetta; una stella tagliata dal bordo ha momenti falsati.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage

from sagitta.measure.shape import StarShape, measure_shape

MAD_TO_SIGMA = 1.4826
"""Fattore che converte la deviazione assoluta mediana in sigma gaussiana."""


@dataclass
class DetectionSettings:
    threshold_sigma: float = 5.0
    min_pixels: int = 5
    max_pixels: int = 2000
    cutout_radius: int = 10
    border_margin: int = 12
    max_flat_top_pixels: int = 3
    saturation_level: float | None = None


def estimate_background(pixels: np.ndarray) -> tuple[float, float]:
    """Fondo e rumore robusti: mediana e MAD riscalata.

    Si usano stimatori robusti perche' la media e la deviazione standard
    vengono trascinate dalle stelle stesse.
    """
    finite = pixels[np.isfinite(pixels)]
    median = float(np.median(finite))
    mad = float(np.median(np.abs(finite - median)))
    sigma = mad * MAD_TO_SIGMA
    if sigma <= 0.0:
        sigma = float(np.std(finite)) or 1.0
    return median, sigma


def detect_stars(pixels: np.ndarray, settings: DetectionSettings | None = None) -> list[StarShape]:
    """Trova le stelle usabili e ne misura la forma.

    Restituisce solo le stelle che superano tutti i criteri di esclusione.
    """
    cfg = settings or DetectionSettings()
    image = np.asarray(pixels, dtype=np.float64)
    height, width = image.shape

    median, sigma = estimate_background(image)
    threshold = median + cfg.threshold_sigma * sigma

    mask = image > threshold
    labels, count = ndimage.label(mask)
    if count == 0:
        return []

    objects = ndimage.find_objects(labels)
    stars: list[StarShape] = []

    for index, slices in enumerate(objects, start=1):
        if slices is None:
            continue
        blob = labels[slices] == index
        n_pixels = int(blob.sum())
        if n_pixels < cfg.min_pixels or n_pixels > cfg.max_pixels:
            continue

        values = image[slices][blob]
        peak = float(values.max())

        # Saturazione. Non si usa "il pixel piu' luminoso del frame per una
        # certa frazione": su un frame senza stelle sature quel criterio
        # scarta sempre la stella piu' luminosa, che e' proprio quella che
        # si vorrebbe misurare. La firma vera della saturazione e' la cima
        # piatta: molti pixel esattamente allo stesso valore massimo.
        if cfg.saturation_level is not None and peak >= cfg.saturation_level:
            continue
        flat_top = int(np.count_nonzero(values >= peak * (1.0 - 1e-6)))
        if flat_top > cfg.max_flat_top_pixels:
            continue

        y_slice, x_slice = slices
        cy = (y_slice.start + y_slice.stop - 1) / 2.0
        cx = (x_slice.start + x_slice.stop - 1) / 2.0

        if (
            cx < cfg.border_margin
            or cy < cfg.border_margin
            or cx >= width - cfg.border_margin
            or cy >= height - cfg.border_margin
        ):
            continue

        radius = cfg.cutout_radius
        x_start = int(round(cx)) - radius
        y_start = int(round(cy)) - radius
        cutout = image[
            y_start : y_start + 2 * radius + 1,
            x_start : x_start + 2 * radius + 1,
        ]
        if cutout.shape != (2 * radius + 1, 2 * radius + 1):
            continue

        shape = measure_shape(cutout - median, x_start, y_start)
        if shape is not None:
            stars.append(shape)

    return stars
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/measure/test_detect.py -v`
Expected: PASS, 7 test

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: detection stellare con criteri di esclusione"
```

---

### Task 8: Stratificazione del campo per zone

**Files:**
- Create: `src/sagitta/measure/zones.py`
- Test: `tests/measure/test_zones.py`

**Interfaces:**
- Consumes: `StarShape` (Task 6).
- Produces:
  - `normalized_radius(x: float, y: float, width: int, height: int) -> float` — vale 0 al centro e circa 1 negli angoli
  - `zone_of(x, y, width, height) -> str` — uno fra `"center"`, `"mid"`, `"corner_tl"`, `"corner_tr"`, `"corner_bl"`, `"corner_br"`
  - `ZoneStats` dataclass: `zone: str`, `n_stars: int`, `median_fwhm_px: float | None`, `median_eccentricity: float | None`, `median_position_angle_deg: float | None`
  - `summarize_zones(stars: list[StarShape], width: int, height: int, min_stars: int = 8) -> dict[str, ZoneStats]`
  - Costante `ZONE_NAMES: tuple[str, ...]`

- [ ] **Step 1: Scrivere il test che fallisce**

Creare `tests/measure/test_zones.py`:

```python
import pytest

from sagitta.measure.shape import StarShape
from sagitta.measure.zones import (
    ZONE_NAMES,
    normalized_radius,
    summarize_zones,
    zone_of,
)


def _star(x, y, fwhm=3.0, ecc=0.1, pa=0.0) -> StarShape:
    return StarShape(x=x, y=y, flux=1000.0, fwhm_px=fwhm, eccentricity=ecc, position_angle_deg=pa)


def test_radius_is_zero_at_centre():
    assert normalized_radius(50.0, 50.0, 100, 100) == pytest.approx(0.0, abs=1e-9)


def test_radius_is_one_at_corner():
    assert normalized_radius(0.0, 0.0, 100, 100) == pytest.approx(1.0, abs=0.02)
    assert normalized_radius(100.0, 100.0, 100, 100) == pytest.approx(1.0, abs=0.02)


def test_zone_names_cover_all_regions():
    assert ZONE_NAMES == (
        "center",
        "mid",
        "corner_tl",
        "corner_tr",
        "corner_bl",
        "corner_br",
    )


def test_zone_of_centre_and_corners():
    assert zone_of(500.0, 500.0, 1000, 1000) == "center"
    assert zone_of(20.0, 20.0, 1000, 1000) == "corner_tl"
    assert zone_of(980.0, 20.0, 1000, 1000) == "corner_tr"
    assert zone_of(20.0, 980.0, 1000, 1000) == "corner_bl"
    assert zone_of(980.0, 980.0, 1000, 1000) == "corner_br"


def test_zone_of_mid_ring():
    # raggio normalizzato circa 0.45, dentro l'anello intermedio
    assert zone_of(500.0, 180.0, 1000, 1000) == "mid"


def test_summarize_reports_medians_per_zone():
    stars = [_star(500 + i, 500, fwhm=3.0, ecc=0.05) for i in range(10)]
    stars += [_star(20 + i, 20, fwhm=6.0, ecc=0.40) for i in range(10)]

    stats = summarize_zones(stars, 1000, 1000, min_stars=8)

    assert stats["center"].n_stars == 10
    assert stats["center"].median_fwhm_px == pytest.approx(3.0, abs=0.01)
    assert stats["center"].median_eccentricity == pytest.approx(0.05, abs=0.01)

    assert stats["corner_tl"].n_stars == 10
    assert stats["corner_tl"].median_eccentricity == pytest.approx(0.40, abs=0.01)


def test_zone_with_too_few_stars_reports_none():
    stars = [_star(500, 500), _star(501, 500)]
    stats = summarize_zones(stars, 1000, 1000, min_stars=8)
    assert stats["center"].n_stars == 2
    assert stats["center"].median_fwhm_px is None
    assert stats["center"].median_eccentricity is None


def test_position_angle_median_is_circular():
    """Angoli a 175 e 5 gradi distano 10 gradi, non 170: la mediana deve saperlo."""
    stars = [_star(500 + i, 500, pa=175.0) for i in range(5)]
    stars += [_star(505 + i, 500, pa=5.0) for i in range(5)]
    stats = summarize_zones(stars, 1000, 1000, min_stars=8)
    angle = stats["center"].median_position_angle_deg
    assert angle is not None
    assert min(angle, 180.0 - angle) < 15.0
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/measure/test_zones.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.measure.zones'`

- [ ] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/measure/zones.py`:

```python
"""Stratificazione della misura per posizione nel campo.

Un singolo numero per frame non serve a niente: il discriminante fisico non e'
il valore medio dell'eccentricita' ma la sua dipendenza dalla posizione.
Un errore di inseguimento allunga le stelle in modo uniforme, centro compreso;
un'aberrazione del treno ottico e' nulla al centro e cresce verso i bordi.
Mediando su tutto il campo si butta via esattamente il segnale che serve.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from sagitta.measure.shape import StarShape

ZONE_NAMES = ("center", "mid", "corner_tl", "corner_tr", "corner_bl", "corner_br")

CENTER_MAX_RADIUS = 0.25
MID_MAX_RADIUS = 0.65


def normalized_radius(x: float, y: float, width: int, height: int) -> float:
    """Raggio normalizzato: 0 al centro, circa 1 negli angoli."""
    rx = (x - width / 2.0) / (width / 2.0)
    ry = (y - height / 2.0) / (height / 2.0)
    return math.hypot(rx, ry) / math.sqrt(2.0)


def zone_of(x: float, y: float, width: int, height: int) -> str:
    """Zona di appartenenza di una posizione nel campo."""
    radius = normalized_radius(x, y, width, height)
    if radius < CENTER_MAX_RADIUS:
        return "center"
    if radius < MID_MAX_RADIUS:
        return "mid"
    left = x < width / 2.0
    top = y < height / 2.0
    if top:
        return "corner_tl" if left else "corner_tr"
    return "corner_bl" if left else "corner_br"


@dataclass
class ZoneStats:
    zone: str
    n_stars: int
    median_fwhm_px: float | None
    median_eccentricity: float | None
    median_position_angle_deg: float | None


def _circular_median_angle(angles_deg: list[float]) -> float:
    """Mediana circolare per angoli definiti modulo 180 gradi.

    Un asse a 175 gradi e uno a 5 gradi distano 10 gradi, non 170. Si raddoppia
    l'angolo per portarlo su un cerchio intero, si media come vettore, si
    dimezza.
    """
    doubled = np.deg2rad(np.array(angles_deg) * 2.0)
    mean_vector = complex(np.cos(doubled).mean(), np.sin(doubled).mean())
    angle = math.degrees(math.atan2(mean_vector.imag, mean_vector.real)) / 2.0
    return angle % 180.0


def summarize_zones(
    stars: list[StarShape], width: int, height: int, min_stars: int = 8
) -> dict[str, ZoneStats]:
    """Statistiche per zona. Una zona con troppe poche stelle non conclude."""
    buckets: dict[str, list[StarShape]] = {name: [] for name in ZONE_NAMES}
    for star in stars:
        buckets[zone_of(star.x, star.y, width, height)].append(star)

    stats: dict[str, ZoneStats] = {}
    for name, members in buckets.items():
        if len(members) < min_stars:
            stats[name] = ZoneStats(name, len(members), None, None, None)
            continue
        stats[name] = ZoneStats(
            zone=name,
            n_stars=len(members),
            median_fwhm_px=float(np.median([s.fwhm_px for s in members])),
            median_eccentricity=float(np.median([s.eccentricity for s in members])),
            median_position_angle_deg=_circular_median_angle(
                [s.position_angle_deg for s in members]
            ),
        )
    return stats
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/measure/test_zones.py -v`
Expected: PASS, 8 test

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: stratificazione della misura per zone del campo"
```

---

### Task 9: Pipeline per singolo frame

**Files:**
- Create: `src/sagitta/measure/frame.py`
- Test: `tests/measure/test_frame.py`

**Interfaces:**
- Consumes: tutto dai Task 1–8.
- Produces:
  - `FrameMeasurement` dataclass: `meta: FrameMeta`, `sampling: SamplingVerdict`, `n_stars: int`, `zones: dict[str, ZoneStats]`, `stars: list[StarShape]`, `refusals: list[str]`
  - `measure_frame(path: Path, settings: DetectionSettings | None = None) -> FrameMeasurement`

- [ ] **Step 1: Scrivere il test che fallisce**

Creare `tests/measure/test_frame.py`:

```python
import numpy as np
import pytest

from sagitta.measure.frame import measure_frame


def _place_gaussian(image, cx, cy, sigma, amplitude=800.0):
    size = int(np.ceil(sigma * 6))
    yy, xx = np.mgrid[cy - size : cy + size + 1, cx - size : cx + size + 1]
    image[cy - size : cy + size + 1, cx - size : cx + size + 1] += amplitude * np.exp(
        -0.5 * (((xx - cx) / sigma) ** 2 + ((yy - cy) / sigma) ** 2)
    )


def _starfield(width=400, height=400, seed=7, sigma=2.0, step=20):
    rng = np.random.default_rng(seed)
    image = rng.normal(100.0, 2.0, size=(height, width))
    for cx in range(step, width - step, step):
        for cy in range(step, height - step, step):
            _place_gaussian(image, cx, cy, sigma)
    return image


def test_measures_stars_and_zones(write_fits):
    path = write_fits(
        "light.fits",
        _starfield().astype(np.float32),
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 300.0,
            "XPIXSZ": 3.76,
            "FOCALLEN": 530.0,
        },
    )
    result = measure_frame(path)

    assert result.sampling.shape_metrics_allowed is True
    assert result.n_stars > 30
    assert result.zones["center"].median_fwhm_px == pytest.approx(4.7, abs=1.0)
    assert result.refusals == []


def test_undersampled_frame_refuses_shape_metrics(write_fits):
    path = write_fits(
        "wide.fits",
        _starfield().astype(np.float32),
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 300.0,
            "XPIXSZ": 3.76,
            "FOCALLEN": 135.0,
        },
    )
    result = measure_frame(path)

    assert result.sampling.shape_metrics_allowed is False
    assert result.zones == {}
    assert result.stars == []
    assert any("campionamento" in r.lower() for r in result.refusals)


def test_osc_frame_is_measured_on_green_sublattice(write_fits):
    """Su OSC la misura avviene sul sotto-reticolo, quindi le dimensioni sono dimezzate."""
    image = _starfield(width=400, height=400, sigma=4.0, step=48)
    path = write_fits(
        "osc.fits",
        image.astype(np.float32),
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 120.0,
            "XPIXSZ": 1.5,
            "FOCALLEN": 530.0,
            "BAYERPAT": "RGGB",
        },
    )
    result = measure_frame(path)

    # 1.5 um su 530 mm = 0.58 arcsec/px, sul reticolo verde diventa 1.17
    assert result.sampling.scale_arcsec == pytest.approx(1.167, abs=0.02)
    assert result.sampling.shape_metrics_allowed is True
    assert all(star.x < 200 and star.y < 200 for star in result.stars)


def test_missing_focal_length_refuses_but_still_reports_metadata(write_fits):
    path = write_fits(
        "nofl.fits",
        _starfield().astype(np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 300.0, "XPIXSZ": 3.76},
    )
    result = measure_frame(path)

    assert result.sampling.shape_metrics_allowed is False
    assert result.meta.exposure_s == 300.0
    assert any("focale" in r.lower() for r in result.refusals)
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/measure/test_frame.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.measure.frame'`

- [ ] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/measure/frame.py`:

```python
"""Orchestrazione della misura di un singolo frame.

Unico modulo che conosce l'ordine delle operazioni: leggi, decidi se e' OSC,
valuta il campionamento, e solo se il campionamento lo consente misura la
forma. Il rifiuto e' un esito legittimo e viene sempre riportato.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sagitta.ingest.fits_reader import read_frame
from sagitta.ingest.schema import FrameMeta
from sagitta.measure.cfa import (
    GREEN_SUBLATTICE_SCALE_FACTOR,
    extract_green_sublattice,
    is_bayer,
)
from sagitta.measure.detect import DetectionSettings, detect_stars
from sagitta.measure.sampling import SamplingVerdict, evaluate_sampling
from sagitta.measure.shape import StarShape
from sagitta.measure.zones import ZoneStats, summarize_zones


@dataclass
class FrameMeasurement:
    meta: FrameMeta
    sampling: SamplingVerdict
    n_stars: int
    zones: dict[str, ZoneStats]
    stars: list[StarShape] = field(default_factory=list)
    refusals: list[str] = field(default_factory=list)


def measure_frame(path: Path, settings: DetectionSettings | None = None) -> FrameMeasurement:
    """Misura un frame e restituisce statistiche per zona.

    Se il frame non e' utilizzabile per le metriche di forma, restituisce un
    risultato con zone vuote e il motivo del rifiuto.
    """
    meta, pixels = read_frame(Path(path))
    refusals: list[str] = []

    if not meta.is_usable_for_shape():
        refusals.append(
            f"Frame di tipo '{meta.frame_kind}': calibrazione e registrazione "
            f"alterano la forma stellare, metriche di forma non prodotte."
        )
        return FrameMeasurement(
            meta, SamplingVerdict(None, False, refusals[-1]), 0, {}, [], refusals
        )

    pixel_factor = 1.0
    if is_bayer(meta.bayer_pattern):
        pixels = extract_green_sublattice(pixels, meta.bayer_pattern or "")
        pixel_factor = GREEN_SUBLATTICE_SCALE_FACTOR

    sampling = evaluate_sampling(meta, effective_pixel_factor=pixel_factor)
    if not sampling.shape_metrics_allowed:
        refusals.append(sampling.reason)
        return FrameMeasurement(meta, sampling, 0, {}, [], refusals)

    stars = detect_stars(pixels, settings)
    height, width = pixels.shape
    zones = summarize_zones(stars, width, height)

    for name, stats in zones.items():
        if stats.median_eccentricity is None:
            refusals.append(
                f"Zona '{name}': solo {stats.n_stars} stelle usabili, "
                f"nessuna conclusione per questa zona."
            )

    return FrameMeasurement(meta, sampling, len(stars), zones, stars, refusals)
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/measure/ -v`
Expected: PASS, tutti i test di measure

Nota: se `test_measures_stars_and_zones` fallisce sull'assenza di rifiuti, la griglia di
stelle del test potrebbe non popolare a sufficienza qualche zona d'angolo. In quel caso
ridurre ulteriormente il passo della griglia nel test, non allentare `min_stars`.

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: pipeline di misura per singolo frame"
```

---

### Task 10: Generatore di stelle sintetiche

**Files:**
- Create: `src/sagitta/synth/__init__.py`
- Create: `src/sagitta/synth/psf.py`
- Test: `tests/synth/test_psf.py`

**Interfaces:**
- Consumes: niente. **`synth` non importa mai da `measure`**, per evitare validazione circolare.
- Produces: `render_gaussian(image: np.ndarray, cx: float, cy: float, sigma_major: float, sigma_minor: float, theta_deg: float, amplitude: float) -> None` — disegna in place.

- [ ] **Step 1: Scrivere il test che fallisce**

Creare `tests/synth/test_psf.py`:

```python
import numpy as np
import pytest

from sagitta.synth.psf import render_gaussian


def test_renders_flux_at_the_requested_position():
    image = np.zeros((100, 100))
    render_gaussian(
        image, cx=30.0, cy=70.0, sigma_major=2.0, sigma_minor=2.0, theta_deg=0.0, amplitude=100.0
    )
    peak_y, peak_x = np.unravel_index(np.argmax(image), image.shape)
    assert peak_x == 30
    assert peak_y == 70


def test_circular_star_is_symmetric():
    image = np.zeros((60, 60))
    render_gaussian(image, 30.0, 30.0, 3.0, 3.0, 0.0, 100.0)
    assert image[30, 20] == pytest.approx(image[20, 30], rel=1e-6)


def test_elongated_star_is_wider_along_the_major_axis():
    image = np.zeros((60, 60))
    render_gaussian(
        image, 30.0, 30.0, sigma_major=5.0, sigma_minor=2.0, theta_deg=0.0, amplitude=100.0
    )
    # theta 0 -> asse maggiore lungo x
    assert image[30, 24] > image[24, 30]


def test_rotation_moves_the_major_axis():
    image = np.zeros((60, 60))
    render_gaussian(image, 30.0, 30.0, 5.0, 2.0, theta_deg=90.0, amplitude=100.0)
    assert image[24, 30] > image[30, 24]


def test_rendering_accumulates():
    image = np.zeros((60, 60))
    render_gaussian(image, 30.0, 30.0, 2.0, 2.0, 0.0, 100.0)
    first = image[30, 30]
    render_gaussian(image, 30.0, 30.0, 2.0, 2.0, 0.0, 100.0)
    assert image[30, 30] == pytest.approx(2 * first, rel=1e-9)
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/synth/test_psf.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.synth'`

- [ ] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/synth/__init__.py` vuoto.

Creare `src/sagitta/synth/psf.py`:

```python
"""Resa di stelle gaussiane ellittiche su un'immagine sintetica.

Questo modulo non importa nulla da `measure`: la validazione deve essere
indipendente dal codice che valida, altrimenti e' circolare.
"""

from __future__ import annotations

import math

import numpy as np


def render_gaussian(
    image: np.ndarray,
    cx: float,
    cy: float,
    sigma_major: float,
    sigma_minor: float,
    theta_deg: float,
    amplitude: float,
) -> None:
    """Somma una gaussiana ellittica all'immagine, in place.

    `theta_deg` e' l'angolo dell'asse maggiore, misurato dall'asse x verso
    l'asse y, nella stessa convenzione usata da measure_shape.
    """
    radius = int(math.ceil(max(sigma_major, sigma_minor) * 4.0))
    x_min = max(0, int(cx) - radius)
    x_max = min(image.shape[1], int(cx) + radius + 1)
    y_min = max(0, int(cy) - radius)
    y_max = min(image.shape[0], int(cy) + radius + 1)
    if x_min >= x_max or y_min >= y_max:
        return

    yy, xx = np.mgrid[y_min:y_max, x_min:x_max]
    dx = xx - cx
    dy = yy - cy

    theta = math.radians(theta_deg)
    x_rot = dx * math.cos(theta) + dy * math.sin(theta)
    y_rot = -dx * math.sin(theta) + dy * math.cos(theta)

    image[y_min:y_max, x_min:x_max] += amplitude * np.exp(
        -0.5 * ((x_rot / sigma_major) ** 2 + (y_rot / sigma_minor) ** 2)
    )
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/synth/test_psf.py -v`
Expected: PASS, 5 test

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: resa di stelle gaussiane ellittiche per dati sintetici"
```

---

### Task 11: Generatore di sub sintetiche con aberrazione nota

**Files:**
- Create: `src/sagitta/synth/generator.py`
- Test: `tests/synth/test_generator.py`

**Interfaces:**
- Consumes: `render_gaussian` (Task 10).
- Produces:
  - `Truth` dataclass: `seeing_sigma_px: float`, `spacing_error: float`, `tilt_x: float`, `tilt_y: float`, `guide_elongation: float`, `guide_angle_deg: float`, `field_rotation: float`
  - `generate_frame(width: int, height: int, truth: Truth, n_stars: int = 400, seed: int = 0) -> np.ndarray`
  - `write_synthetic_fits(path: Path, pixels: np.ndarray, pixel_size_um: float = 3.76, focal_length_mm: float = 530.0) -> Path`

**Modello di aberrazione iniettato.** Ogni causa ha una dipendenza spaziale diversa, ed è
proprio quella che la misura deve saper distinguere:

- **`guide_elongation`** — allungamento **uniforme su tutto il campo, centro compreso**,
  lungo `guide_angle_deg` fisso.
- **`spacing_error`** — allargamento **radialmente simmetrico**: nullo al centro, cresce con
  `r²`, **uguale nei quattro angoli**.
- **`tilt_x`, `tilt_y`** — allargamento **lineare** in `rx` e `ry`: crea **asimmetria fra
  angoli opposti**. È verità iniettata, quindi qui la parola `tilt` è ammessa.
- **`field_rotation`** — allungamento **tangenziale** attorno al centro immagine, di ampiezza
  proporzionale al raggio.

- [ ] **Step 1: Scrivere il test che fallisce**

Creare `tests/synth/test_generator.py`:

```python
import numpy as np
import pytest

from sagitta.synth.generator import Truth, generate_frame


def _median_in_box(image, x0, x1, y0, y1):
    return float(np.median(image[y0:y1, x0:x1]))


def test_clean_frame_has_stars_and_background():
    truth = Truth(seeing_sigma_px=2.0)
    image = generate_frame(600, 600, truth, n_stars=200, seed=1)
    assert image.shape == (600, 600)
    assert image.max() > 100.0
    assert np.median(image) == pytest.approx(100.0, abs=5.0)


def test_generation_is_reproducible_with_the_same_seed():
    truth = Truth(seeing_sigma_px=2.0)
    a = generate_frame(300, 300, truth, n_stars=50, seed=42)
    b = generate_frame(300, 300, truth, n_stars=50, seed=42)
    assert np.array_equal(a, b)


def test_different_seeds_give_different_frames():
    truth = Truth(seeing_sigma_px=2.0)
    a = generate_frame(300, 300, truth, n_stars=50, seed=1)
    b = generate_frame(300, 300, truth, n_stars=50, seed=2)
    assert not np.array_equal(a, b)


def test_spacing_error_leaves_the_centre_clean():
    """Errore di spaziatura: nullo al centro, cresce col raggio."""
    truth = Truth(seeing_sigma_px=2.0, spacing_error=3.0)
    image = generate_frame(600, 600, truth, n_stars=600, seed=3)
    centre = _median_in_box(image, 270, 330, 270, 330)
    corner = _median_in_box(image, 0, 60, 0, 60)
    # gli angoli sono piu' "sporchi" perche' le stelle sono allargate
    assert corner > centre


def test_guide_elongation_affects_the_centre_too():
    """L'errore di guida allunga anche le stelle centrali."""
    clean = Truth(seeing_sigma_px=2.0)
    guided = Truth(seeing_sigma_px=2.0, guide_elongation=2.0, guide_angle_deg=30.0)
    a = generate_frame(400, 400, clean, n_stars=300, seed=4)
    b = generate_frame(400, 400, guided, n_stars=300, seed=4)
    # stesse posizioni (stesso seed), ma le stelle centrali sono piu' larghe
    assert _median_in_box(b, 180, 220, 180, 220) > _median_in_box(a, 180, 220, 180, 220)


def test_tilt_makes_opposite_corners_differ():
    truth = Truth(seeing_sigma_px=2.0, tilt_x=3.0)
    image = generate_frame(600, 600, truth, n_stars=600, seed=5)
    left = _median_in_box(image, 0, 80, 260, 340)
    right = _median_in_box(image, 520, 600, 260, 340)
    assert abs(left - right) > 0.5
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/synth/test_generator.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'sagitta.synth.generator'`

- [ ] **Step 3: Scrivere l'implementazione minima**

Creare `src/sagitta/synth/generator.py`:

```python
"""Generazione di sub sintetiche con aberrazione iniettata nota.

E' il sostituto della verita' di riferimento che non possediamo: qui la
risposta e' scritta dentro il dato, quindi si puo' verificare che la misura la
restituisca. Ogni causa ha una dipendenza spaziale diversa, ed e' esattamente
quella che il motore di misura deve saper distinguere.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from sagitta.synth.psf import render_gaussian

BACKGROUND_LEVEL = 100.0
BACKGROUND_NOISE = 2.0


@dataclass
class Truth:
    """Verita' iniettata in un frame sintetico.

    `tilt_x` e `tilt_y` si chiamano cosi' perche' qui sono verita' nota e non
    stima: e' l'unico posto del progetto in cui la parola e' ammessa.
    """

    seeing_sigma_px: float = 2.0
    spacing_error: float = 0.0
    tilt_x: float = 0.0
    tilt_y: float = 0.0
    guide_elongation: float = 0.0
    guide_angle_deg: float = 0.0
    field_rotation: float = 0.0


def _local_shape(truth: Truth, rx: float, ry: float) -> tuple[float, float, float]:
    """Assi e orientamento della PSF in una posizione normalizzata del campo.

    rx e ry vanno da -1 a +1 rispetto al centro.
    """
    radius = math.hypot(rx, ry)

    # componente radialmente simmetrica: spaziatura errata
    radial = truth.spacing_error * radius * radius
    # componente lineare: tilt, asimmetrica fra angoli opposti
    linear = truth.tilt_x * rx + truth.tilt_y * ry

    optical = max(0.0, radial + linear)

    sigma_major = truth.seeing_sigma_px + optical
    sigma_minor = truth.seeing_sigma_px + optical
    theta = 0.0

    # Rotazione di campo: allungamento tangenziale crescente col raggio.
    # Ha la precedenza sull'orientamento perche' e' l'unica firma con un
    # angolo che dipende dalla posizione.
    if truth.field_rotation > 0.0 and radius > 1e-6:
        sigma_major += truth.field_rotation * radius
        theta = math.degrees(math.atan2(ry, rx)) + 90.0
        if truth.guide_elongation > 0.0:
            sigma_major += truth.guide_elongation
        return sigma_major, sigma_minor, theta

    # Errore di guida: uniforme su tutto il campo, centro compreso,
    # con un angolo fisso identico ovunque.
    if truth.guide_elongation > 0.0:
        sigma_major += truth.guide_elongation
        theta = truth.guide_angle_deg

    return sigma_major, sigma_minor, theta


def generate_frame(
    width: int, height: int, truth: Truth, n_stars: int = 400, seed: int = 0
) -> np.ndarray:
    """Genera un frame sintetico con l'aberrazione descritta da `truth`."""
    rng = np.random.default_rng(seed)
    image = rng.normal(BACKGROUND_LEVEL, BACKGROUND_NOISE, size=(height, width))

    margin = 20
    xs = rng.uniform(margin, width - margin, size=n_stars)
    ys = rng.uniform(margin, height - margin, size=n_stars)
    amplitudes = rng.uniform(300.0, 3000.0, size=n_stars)

    for cx, cy, amplitude in zip(xs, ys, amplitudes):
        rx = (cx - width / 2.0) / (width / 2.0)
        ry = (cy - height / 2.0) / (height / 2.0)
        sigma_major, sigma_minor, theta = _local_shape(truth, rx, ry)
        render_gaussian(image, cx, cy, sigma_major, sigma_minor, theta, amplitude)

    return image


def write_synthetic_fits(
    path: Path,
    pixels: np.ndarray,
    pixel_size_um: float = 3.76,
    focal_length_mm: float = 530.0,
) -> Path:
    """Salva un frame sintetico come FITS con header minimo ma sufficiente."""
    from astropy.io import fits

    hdu = fits.PrimaryHDU(pixels.astype(np.float32))
    hdu.header["DATE-OBS"] = "2026-08-29T21:30:00"
    hdu.header["EXPTIME"] = 300.0
    hdu.header["XPIXSZ"] = pixel_size_um
    hdu.header["FOCALLEN"] = focal_length_mm
    hdu.header["SWCREATE"] = "sagitta-synth"
    path = Path(path)
    hdu.writeto(path, overwrite=True)
    return path
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/synth/ -v`
Expected: PASS, tutti i test di synth

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: generatore di sub sintetiche con aberrazione iniettata nota"
```

---

### Task 12: Benchmark di validazione e CLI

Questo è il task che chiude lo Stadio 1. **Scoping onesto:** il benchmark di questo blocco
valida **lo strato di misura**, cioè che l'aberrazione iniettata torni fuori con la giusta
dipendenza spaziale. Il benchmark del *classificatore diagnostico* non appartiene a questo
piano, perché il classificatore è Stadio 3. Il README deve dire esattamente questo, senza
lasciare intendere di più.

**Files:**
- Create: `src/sagitta/cli.py`
- Modify: `README.md` (due sostituzioni, il file esiste già)
- Test: `tests/test_benchmark.py`

**Interfaces:**
- Consumes: `measure_frame` (Task 9), `Truth`, `generate_frame`, `write_synthetic_fits` (Task 11).
- Produces: `main(argv: list[str] | None = None) -> int`, comando `sagitta measure <path>`.

- [ ] **Step 1: Scrivere il test che fallisce**

Creare `tests/test_benchmark.py`:

```python
"""Validazione dello strato di misura contro verita' sintetica nota.

Non si valida un classificatore: qui si verifica che la dipendenza spaziale
dell'aberrazione iniettata sia quella che la misura restituisce.
"""

import numpy as np
import pytest

from sagitta.measure.detect import DetectionSettings
from sagitta.measure.frame import measure_frame
from sagitta.synth.generator import Truth, generate_frame, write_synthetic_fits


def _measure(tmp_path, truth, name, n_stars=1200, seed=11):
    pixels = generate_frame(900, 900, truth, n_stars=n_stars, seed=seed)
    path = write_synthetic_fits(tmp_path / f"{name}.fits", pixels)
    # Il ritaglio deve essere piu' largo della stella: con l'aberrazione
    # iniettata le stelle d'angolo arrivano a FWHM di circa 9 pixel, e una
    # finestra troppo stretta troncherebbe i momenti secondi, falsando
    # verso il basso sia FWHM che eccentricita'.
    settings = DetectionSettings(cutout_radius=16, border_margin=20)
    return measure_frame(path, settings)


def test_clean_frame_is_round_everywhere(tmp_path):
    result = _measure(tmp_path, Truth(seeing_sigma_px=2.5), "clean")
    assert result.zones["center"].median_eccentricity < 0.25
    assert result.zones["corner_tl"].median_eccentricity < 0.30


def test_guide_error_elongates_the_centre_as_much_as_the_corners(tmp_path):
    """Firma della guida: allungamento uniforme, centro compreso."""
    truth = Truth(seeing_sigma_px=2.0, guide_elongation=3.0, guide_angle_deg=0.0)
    result = _measure(tmp_path, truth, "guide")

    centre = result.zones["center"].median_eccentricity
    corner = result.zones["corner_br"].median_eccentricity
    assert centre > 0.6
    assert abs(centre - corner) < 0.2


def test_guide_error_position_angle_matches_the_injected_one(tmp_path):
    truth = Truth(seeing_sigma_px=2.0, guide_elongation=3.0, guide_angle_deg=30.0)
    result = _measure(tmp_path, truth, "guide30")
    measured = result.zones["center"].median_position_angle_deg
    difference = min(abs(measured - 30.0), 180.0 - abs(measured - 30.0))
    assert difference < 12.0


def test_spacing_error_leaves_the_centre_round(tmp_path):
    """Firma della spaziatura: nulla al centro, uguale nei quattro angoli."""
    truth = Truth(seeing_sigma_px=2.0, spacing_error=2.0)
    result = _measure(tmp_path, truth, "spacing")

    assert result.zones["center"].median_fwhm_px < 6.5

    corners = [
        result.zones[name].median_fwhm_px
        for name in ("corner_tl", "corner_tr", "corner_bl", "corner_br")
    ]
    assert min(corners) > result.zones["center"].median_fwhm_px
    assert max(corners) - min(corners) < 0.25 * np.mean(corners)


def test_tilt_makes_opposite_corners_asymmetric(tmp_path):
    """Firma del tilt: asimmetria fra angoli opposti, a differenza della spaziatura."""
    truth = Truth(seeing_sigma_px=2.0, tilt_x=2.0)
    result = _measure(tmp_path, truth, "tilt")

    left = np.mean(
        [
            result.zones["corner_tl"].median_fwhm_px,
            result.zones["corner_bl"].median_fwhm_px,
        ]
    )
    right = np.mean(
        [
            result.zones["corner_tr"].median_fwhm_px,
            result.zones["corner_br"].median_fwhm_px,
        ]
    )
    assert abs(right - left) > 0.25 * np.mean([left, right])


def test_spacing_and_tilt_are_distinguishable(tmp_path):
    """La differenza fra le due firme e' misurabile, e questo e' il punto."""
    spacing = _measure(tmp_path, Truth(2.0, spacing_error=2.0), "s2")
    tilt = _measure(tmp_path, Truth(2.0, tilt_x=2.0), "t2")

    def asymmetry(result):
        left = np.mean(
            [
                result.zones["corner_tl"].median_fwhm_px,
                result.zones["corner_bl"].median_fwhm_px,
            ]
        )
        right = np.mean(
            [
                result.zones["corner_tr"].median_fwhm_px,
                result.zones["corner_br"].median_fwhm_px,
            ]
        )
        return abs(right - left) / np.mean([left, right])

    assert asymmetry(spacing) < 0.15
    assert asymmetry(tilt) > 0.25
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/test_benchmark.py -v`
Expected: FAIL. Se i moduli esistono già dai task precedenti, il fallimento sarà su una
soglia numerica, non su un import.

- [ ] **Step 3: Scrivere l'implementazione minima**

Se i test falliscono su una soglia, la correzione va fatta **nel test o nei parametri della
verità iniettata, mai allentando il guardrail o i criteri di esclusione**. Le soglie del test
sono il contratto della misura: se non sono raggiungibili, è la misura ad avere un problema.

Creare `src/sagitta/cli.py`:

```python
"""Interfaccia a riga di comando di Sagitta.

In questo stadio espone solo la misura di un frame, con output JSON.
Nessuna diagnosi, nessuna attribuzione causale: solo numeri e rifiuti.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from sagitta.measure.frame import measure_frame


def _measurement_to_dict(result) -> dict:
    return {
        "path": result.meta.path,
        "date_obs": result.meta.date_obs.isoformat(),
        "exposure_s": result.meta.exposure_s,
        "filter": result.meta.filter_name,
        "sampling": asdict(result.sampling),
        "n_stars": result.n_stars,
        "zones": {name: asdict(stats) for name, stats in result.zones.items()},
        "refusals": result.refusals,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sagitta",
        description="Misura della forma stellare per zona del campo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    measure = subparsers.add_parser("measure", help="misura uno o piu' frame")
    measure.add_argument("paths", nargs="+", type=Path)

    args = parser.parse_args(argv)

    if args.command == "measure":
        output = []
        for path in args.paths:
            try:
                output.append(_measurement_to_dict(measure_frame(path)))
            except (ValueError, OSError) as exc:
                output.append({"path": str(path), "error": str(exc)})
        json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

**Il `README.md` esiste già** nella radice, ed è molto più esteso di quanto serva
riprodurre qui: contiene lo scopo del progetto, la tabella delle firme diagnostiche, i caveat
e le istruzioni di sviluppo. **Non sovrascriverlo e non riscriverlo.**

Devi solo togliere l'avvertenza che dice che non esiste ancora codice, perché a questo punto
non è più vera. Fai **due sostituzioni esatte**, e nient'altro.

**Sostituzione 1.** Trova questo titolo di sezione:

    ## ⚠️ Stato: in costruzione. Non c'è ancora niente da usare.

e sostituisci quel titolo **e tutto ciò che lo segue fino alla riga `---` esclusa** con:

```markdown
## Stato

Implementato: lettura FITS con normalizzazione dei dialetti di header, misura della
forma stellare per stella tramite momenti secondi, stratificazione per zona del campo,
guardrail di campionamento, gestione delle sub a colori su sotto-reticolo verde,
generatore di sub sintetiche e benchmark di validazione, interfaccia a riga di comando.

Non ancora implementato: join con i log di guida, classificatore diagnostico, banco di
prova statistico, interfaccia grafica.

**Non ci sono date, e non c'è una roadmap con scadenze.** È un progetto in divenire.

| | |
|---|---|
| Fase | Stadio 0 e 1 completati |
| Piattaforma | Windows 11 soltanto |

Documenti di riferimento:

- [`docs/design.md`](docs/design.md) — la specifica: cosa fa, cosa non fa, e perché
- [`docs/plan-stadio-0-1.md`](docs/plan-stadio-0-1.md) — il piano di implementazione
- [`CHANGELOG.md`](CHANGELOG.md) — cosa cambia a ogni versione
```

**Sostituzione 2.** Trova questa sezione:

    ## Come sarà usato

    **Niente di quanto segue funziona oggi**, e non c'è una data in cui funzionerà. È qui
    perché il piano lo prescrive e perché un lettore possa giudicare in anticipo se uno strumento
    del genere gli servirebbe.

    Installazione, una volta che ci sarà una release:

e sostituisci **quelle righe** con:

```markdown
## Uso

Installazione, quando ci sarà una release pubblicata:
```

Non toccare niente altro del README: né i caveat, né la sezione sullo scopo, né quella
sullo sviluppo, né quella sulle versioni.

Verifica poi che le due avvertenze siano sparite:

Run: `python -c "import io; t=io.open('README.md',encoding='utf-8').read(); assert 'in costruzione' not in t and 'Niente di quanto segue funziona oggi' not in t; print('README aggiornato')"`

Expected: `README aggiornato`

- [ ] **Step 4: Eseguire l'intera suite e verificare che passi**

Run: `python -m pytest -v`
Expected: PASS, tutti i test

Verificare anche la CLI a mano:

Run: `python -c "from pathlib import Path; from sagitta.synth.generator import Truth, generate_frame, write_synthetic_fits; write_synthetic_fits(Path('demo.fits'), generate_frame(900, 900, Truth(2.0, spacing_error=2.0), n_stars=1200, seed=1))"`

Run: `sagitta measure demo.fits`
Expected: JSON con `n_stars` maggiore di 300, `sampling.shape_metrics_allowed` a `true`, e le
statistiche delle sei zone.

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: benchmark di validazione su verita' sintetica e CLI di misura"
```

---

---

### Task 13: Suite di test e smoke test

I Task 1–12 producono test unitari. Questo task organizza la suite e aggiunge il livello che
manca: uno **smoke test end-to-end** che esercita il programma come lo esercita un utente,
cioè lanciando l'eseguibile installato, non importando moduli. È il test che si rompe quando
si rompe il packaging, l'entry point o il contratto JSON — cose che nessun test unitario vede.

**Files:**
- Modify: `pyproject.toml` (sezione `[tool.pytest.ini_options]`)
- Create: `tests/test_smoke.py`

**Interfaces:**
- Consumes: la CLI `sagitta measure` (Task 12), `Truth` / `generate_frame` /
  `write_synthetic_fits` (Task 11).
- Produces: i marker pytest `smoke` e `slow`, e il comando di gate `pytest -m smoke`.

- [ ] **Step 1: Scrivere lo smoke test**

Creare `tests/test_smoke.py`:

```python
"""Smoke test end-to-end.

Esercita il programma come lo esercita un utente: lancia l'eseguibile
installato in un sottoprocesso e legge il JSON da stdout. Non importa nulla
dal package se non per fabbricare il file di input.

Copre cio' che nessun test unitario copre: che il packaging funzioni, che
l'entry point esista, che il JSON sia valido e che i campi del contratto ci
siano davvero.
"""

import json
import subprocess
import sys

import pytest

from sagitta.synth.generator import Truth, generate_frame, write_synthetic_fits

pytestmark = pytest.mark.smoke


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sagitta.cli", *args],
        capture_output=True,
        text=True,
        timeout=180,
    )


@pytest.fixture
def synthetic_light(tmp_path):
    pixels = generate_frame(
        900, 900, Truth(seeing_sigma_px=2.0, spacing_error=2.0), n_stars=1200, seed=1
    )
    return write_synthetic_fits(tmp_path / "light_0001.fits", pixels)


def test_cli_measures_a_frame_and_emits_valid_json(synthetic_light):
    result = _run_cli("measure", str(synthetic_light))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert isinstance(payload, list)
    assert len(payload) == 1

    frame = payload[0]
    for key in ("path", "date_obs", "exposure_s", "sampling", "n_stars", "zones", "refusals"):
        assert key in frame, f"campo mancante nel contratto JSON: {key}"

    assert frame["n_stars"] > 300
    assert frame["sampling"]["shape_metrics_allowed"] is True
    assert set(frame["zones"]) == {
        "center",
        "mid",
        "corner_tl",
        "corner_tr",
        "corner_bl",
        "corner_br",
    }
    assert frame["zones"]["center"]["median_fwhm_px"] > 0


def test_cli_measures_multiple_frames(tmp_path, synthetic_light):
    second = write_synthetic_fits(
        tmp_path / "light_0002.fits",
        generate_frame(900, 900, Truth(seeing_sigma_px=2.4), n_stars=1200, seed=2),
    )
    result = _run_cli("measure", str(synthetic_light), str(second))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload) == 2


def test_cli_reports_unreadable_file_without_crashing(tmp_path):
    broken = tmp_path / "non_e_un_fits.fits"
    broken.write_text("questo non e' un FITS")

    result = _run_cli("measure", str(broken))

    # Un file illeggibile e' un esito previsto, non un crash: esce 0 e lo dice.
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "error" in payload[0]


def test_cli_without_arguments_exits_nonzero_and_explains():
    result = _run_cli()
    assert result.returncode != 0
    assert "measure" in (result.stderr + result.stdout)
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/test_smoke.py -v`
Expected: FAIL. Almeno `test_cli_without_arguments_exits_nonzero_and_explains` e
`test_cli_reports_unreadable_file_without_crashing` falliscono, perché `python -m sagitta.cli`
non è ancora un punto di ingresso eseguibile e `argparse` non è configurato per uscire con
codice diverso da zero in modo prevedibile.

- [ ] **Step 3: Rendere il modulo eseguibile e configurare i marker**

In `src/sagitta/cli.py` il blocco finale esiste già:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Questo è ciò che rende funzionante `python -m sagitta.cli`. Verificare che ci sia e non
modificarlo.

In `pyproject.toml`, sostituire la sezione `[tool.pytest.ini_options]` con:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "smoke: test end-to-end che lanciano l'eseguibile installato",
    "slow: test che superano i 10 secondi",
]
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/test_smoke.py -v`
Expected: PASS, 4 test

Run: `python -m pytest -m smoke -v`
Expected: PASS, gli stessi 4 test, nessun test unitario raccolto

Run: `python -m pytest -v`
Expected: PASS, l'intera suite

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "test: smoke test end-to-end sulla CLI e marker della suite"
```

---

### Task 14: Integrazione continua su Windows

**Che ruolo ha la CI qui.** Sagitta supporta **solo Windows 11**, e la macchina di sviluppo
**è** Windows 11. Questo cambia il mestiere della CI rispetto a un progetto multipiattaforma:
non serve a scoprire che il codice si rompe altrove, perché un "altrove" non c'è. Serve a
tre cose più ristrette ma reali. **Verificare in un ambiente pulito**, perché in locale
l'ambiente si sporca — pacchetti installati a mano, file rimasti da esperimenti, variabili
impostate e dimenticate — mentre la CI parte da zero ogni volta e scopre le dipendenze che
avevi senza dichiararle. **Verificare che tu abbia committato tutto**, che è il caso più
frequente in assoluto di "in locale passava". E **dire se `dev` è pronto per andare in
`main`**: è la CI sulla pull request a rispondere a quella domanda, non la tua parola.

**Il costo: zero.** Il repository è **pubblico**, e su repository pubblici i minuti di
GitHub Actions sono **illimitati** e non intaccano la quota dell'account. Non c'è un budget
da amministrare, e questa è metà della ragione per cui il repository è pubblico. Di
conseguenza la CI gira su **ogni push a `dev` e a `main`, e su ogni pull request verso
`main`**: il ritorno è immediato e non costa niente.

Restano comunque due versioni di Python e non tre sistemi operativi, perché la questione non
è più il prezzo ma **cosa promettiamo**: aggiungere runner Linux o macOS segnalerebbe un
supporto che non diamo e produrrebbe fallimenti su piattaforme di cui non ci occupiamo.

**Nota per il futuro, da non implementare ora.** Quando arriverà il turno di Ekos, INDI e
Alpaca — cioè del mondo Linux — riaprire quel fronte costerà **aggiungere una voce alla
matrice**, gratis e senza riscrivere niente: il codice resta portabile per costruzione, come
dice il vincolo globale sulle piattaforme.

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `ruff.toml`
- Modify: `pyproject.toml` (dipendenze di sviluppo)
- Modify: `tests/ingest/test_schema.py` (una riga, vedi Step 1-bis)

**Interfaces:**
- Consumes: la suite pytest (Task 1 in poi).
- Produces: il workflow `ci`, che gira su `dev`, su `main` e sulle pull request verso `main`.

- [x] **Step 1: Configurare il linter e le dipendenze di sviluppo**

Creare `ruff.toml`:

```toml
line-length = 100
target-version = "py311"

[lint]
select = ["E", "F", "I", "B", "UP"]
ignore = ["E501"]

[lint.per-file-ignores]
"tests/**" = ["B011"]
```

In `pyproject.toml`, sostituire la sezione delle dipendenze opzionali con:

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.6", "pip-audit>=2.7", "bandit>=1.7", "build>=1.2"]
```

- [x] **Step 1-bis: allineare il file gia' committato del Task 1**

`ruff` segnala `UP017` su `tests/ingest/test_schema.py`, scritto al Task 1 quando ruff non
c'era ancora. Il piano ora usa ovunque `dt.UTC`, che e' la forma che ruff pretende da
Python 3.11 in su. Sostituisci **una sola occorrenza**, in quel file:

    tzinfo=dt.timezone.utc   ->   tzinfo=dt.UTC

Non toccare nient'altro di quel file.

Run: `python -m pytest -q`
Expected: 3 test verdi, come prima.

Run: `ruff check .`
Expected: nessun errore.

- [x] **Step 2: Eseguire il linter e correggere ciò che segnala**

Run: `pip install -e ".[dev]"`

Run: `ruff check .`

Expected: nessun errore. Se ne segnala, correggi il codice, **non** allargare `ignore`.
L'errore più probabile è `F401`, un import non usato: rimuovilo.

Run: `ruff format --check .`

Expected: può fallire, ed è normale la prima volta. In quel caso esegui `ruff format .` e
includi la riformattazione nel commit di questo task.

- [x] **Step 3: Scrivere il workflow**

Creare `.github/workflows/ci.yml`:

```yaml
name: ci

# I due rami del progetto, piu' le pull request verso main: e' la CI
# sulla pull request a dire se dev e' pronto per il merge.
on:
  push:
    branches: [dev, main]
  pull_request:
    branches: [main]
  workflow_dispatch:

# Privilegio minimo: questa CI legge il codice e non scrive niente.
# Senza questo blocco il token eredita permessi di scrittura inutili.
permissions:
  contents: read

# Un push che ne supera un altro cancella la corsa precedente: non per
# risparmiare minuti, che sono illimitati, ma per non leggere l'esito di
# un commit gia' superato.
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - uses: actions/setup-python@42375524e23c412d93fb67b49958b491fce71c38 # v5.4.0
        with:
          python-version: "3.13"
          cache: pip

      - run: pip install -e ".[dev]"

      - run: ruff check .

      - run: ruff format --check .

      - name: Errori di sicurezza nel nostro codice
        run: bandit -r src/sagitta -ll

  test:
    strategy:
      fail-fast: false
      matrix:
        # 3.11 e' il minimo che dichiariamo in requires-python, 3.13 e'
        # quello che verra' impacchettato: si verificano entrambi gli
        # estremi di cio' che promettiamo, e niente altro.
        python-version: ["3.11", "3.13"]
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - uses: actions/setup-python@42375524e23c412d93fb67b49958b491fce71c38 # v5.4.0
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      # L'immagine del runner 3.11 porta setuptools 65.5.0, che ha
      # vulnerabilita' note ed e' sotto il setuptools>=68 che pyproject
      # dichiara. pip-audit lo vede e fa rosso, giustamente: si aggiorna,
      # non si mette in ignore. Sul 3.13 questo passo non trova niente da
      # fare, e costa qualche secondo.
      - name: Aggiornare gli strumenti di packaging
        run: python -m pip install --upgrade pip setuptools wheel

      - run: pip install -e ".[dev]"

      - name: Suite completa
        run: pytest -v --durations=10

      - name: Vulnerabilita' note nelle dipendenze
        run: pip-audit --skip-editable
```

**Perche' `--skip-editable` e non `--strict`.** `pip-audit --strict` fallisce se anche una
sola distribuzione dell'ambiente non e' auditabile, e `sagitta` installata in modalita'
sviluppo non lo e': non sta su PyPI. L'audit si chiude con
`Dependency not found on PyPI and could not be audited: sagitta (0.1.0)` e la CI resta rossa
per sempre su una riga che non parla di nessuna vulnerabilita'. `--skip-editable` salta le
distribuzioni editabili e continua ad auditare tutto il resto -- numpy, scipy, astropy,
PyYAML e le loro transitive -- che e' esattamente cio' che la tabella del Task 15 promette.

Le due opzioni **non si combinano**: `--strict --skip-editable` considera lo skip stesso un
fallimento di raccolta e fallisce ugualmente, con `sagitta: distribution marked as editable`.
Rinunciare a `--strict` costa poco qui, perche' l'unico pacchetto editabile dell'ambiente e'
il progetto stesso -- nient'altro puo' diventarlo per sbaglio -- e lo skip resta visibile
nell'output, in una tabella `Name / Skip Reason`, invece di sparire in silenzio.

**Perche' il job `test` aggiorna setuptools prima di installare.** L'immagine dei runner
GitHub per Python 3.11 include `setuptools 65.5.0`, che oggi ha sette vulnerabilita' note --
da `PYSEC-2022-43012` a `PYSEC-2026-3447`, quest'ultima corretta solo in 83.0.0. Non e' una
nostra dipendenza: e' l'ambiente su cui giriamo. Ma `pip-audit` audita l'ambiente **realmente
installato**, quindi la vede, e fa rosso il job 3.11 mentre il 3.13 passa, perche' la sua
immagine ne porta una recente.

E' la stessa cosa che la sezione **Preparazione dell'ambiente** ha gia' fatto in locale, dove
pip, setuptools e wheel sono aggiornati: il venv di sviluppo era allineato e la CI no, ed e'
per questo che lo stesso comando passava sulla macchina e falliva sul runner. Un ambiente di
verifica che non riproduce quello dichiarato non sta verificando quello che credi.

**Sul pinning delle action.** Ogni `uses:` è agganciato al **SHA completo del commit**, con
il tag in commento. Un tag come `@v4` è mobile: chi controlla quel repository può farlo
puntare altrove, e quel codice girerebbe nella nostra pipeline con il nostro token. È una
delle vie d'ingresso più usate negli attacchi alla catena di build, e chiuderla costa zero.

**I SHA di questo piano sono già stati verificati contro l'API di GitHub il 29 agosto 2026**,
e corrispondono ai tag indicati in commento — tutti e cinque, compresi quelli dei Task 15 e
16. Puoi copiarli così come sono. Questo è l'elenco completo, se dovessi ricontrollarli:

| Action | Tag | SHA del commit |
|---|---|---|
| `actions/checkout` | v4.2.2 | `11bd71901bbe5b1630ceea73d27597364c9af683` |
| `actions/setup-python` | v5.4.0 | `42375524e23c412d93fb67b49958b491fce71c38` |
| `github/codeql-action` | v3.28.9 | `9e8d0789d4a0fa9ceb6b1738f7e269594bdd67f0` |
| `actions/attest-build-provenance` | v2.2.0 | `520d128f165991a6c774bcb264f323e3d70747f4` |
| `softprops/action-gh-release` | v2.2.1 | `c95fe1489396fe8a9eb87c0abf8aa5b2ef267fda` |

Un avvertimento se li ricontrolli da solo: `github/codeql-action` usa **tag annotati**, quindi
`repos/github/codeql-action/git/ref/tags/v3.28.9` restituisce l'oggetto tag e non il commit.
Va dereferenziato con `repos/github/codeql-action/git/tags/<sha del tag>` per ottenere il SHA
qui sopra. Gli altri quattro puntano direttamente al commit.

- [x] **Step 4: Verificare prima di spingere**

GitHub Actions non si esegue in locale, ma i comandi che il workflow lancia sì — e girano
sulla stessa piattaforma del runner, che è tutto il vantaggio di essere Windows-only:

Run: `ruff check .`

Run: `ruff format --check .`

Run: `pytest -v --durations=10`

Run: `pip-audit --skip-editable`

Expected: PASS su tutti e quattro

Verifica poi che il file YAML sia sintatticamente valido:

Run: `python -c "import yaml,pathlib; yaml.safe_load(pathlib.Path('.github/workflows/ci.yml').read_text(encoding='utf-8')); print('yaml ok')"`

Expected: `yaml ok`

- [x] **Step 5: Commit e primo push**

```bash
git add .
git commit -m "ci: lint, suite e audit su Windows a ogni push su dev"
```

Run: `git push origin dev`

Questo è il push che accende la CI per la prima volta. Verifica l'esito:

La corsa non compare all'istante: fra il push e la sua registrazione passano alcuni secondi,
e in quella finestra `gh run list` stampa **zero righe**. Un output vuoto non e' un
fallimento, e' un "non ancora": aspetta e richiedi. Se dopo l'attesa la corsa risulta
`in_progress`, richiedi ancora - dura qualche minuto.

Run: `Start-Sleep -Seconds 30`

Run: `gh run list --branch dev --limit 3`

Expected: la corsa più recente in stato `completed` con conclusione `success`. Se fosse
`failure`, aprila con `gh run view --log-failed` e leggi l'errore: il caso di gran lunga
più probabile è un file che esiste in locale ma non è nel commit.

> **Prossimo task: il 2.** Torna a **Task 2: Dialetti di header** e prosegui in ordine
> numerico fino al Task 13. Il Task 15 arriva dopo il 13.

---

### Task 15: Sicurezza proporzionata

**Il modello di minaccia vero.** Sagitta è un programma che qualcuno installa e a cui dà in
pasto l'archivio di una vita di astrofotografia. Le domande di quella persona sono due:
*dove finiscono i miei dati* e *questo eseguibile è davvero quello che dicono di aver
costruito*. Tutto il resto è secondario, e la sicurezza di questo progetto consiste nel
rispondere a quelle due in modo verificabile — non nel collezionare badge.

**Repository pubblico, e questo cambia le carte in tavola.** Su repository pubblici GitHub
regala esattamente gli strumenti che su un privato con piano Free costerebbero: CodeQL,
secret scanning con push protection, e le attestazioni di provenienza sulle release. Sono la
spina dorsale di questo task e non costano niente.

C'è anche un'inversione che vale la pena notare, perché è controintuitiva: **su repository
pubblico sei più protetto dai segreti, non meno.** La push protection blocca il commit di un
token *prima* che parta. Su un repository privato con piano Free quella rete non esiste, e un
token committato per sbaglio resta lì finché non te ne accorgi.

**Cosa usiamo, e che lavoro fa ciascuno.** Nessuna sovrapposizione: ognuno vede qualcosa che
gli altri non vedono.

| Strumento | Cosa vede che gli altri non vedono | Dove gira |
|---|---|---|
| `tests/test_no_network.py` | che il programma non apra connessioni, dimostrato eseguendolo | suite, a ogni push |
| `pip-audit` | vulnerabilità note nell'ambiente **realmente installato**, transitive comprese (il progetto stesso, editabile, è saltato) | `ci`, a ogni push |
| `bandit` | errori nel **nostro** codice: subprocess, deserializzazione, tempfile | `ci`, a ogni push |
| CodeQL | analisi semantica del flusso dei dati, che né bandit né pip-audit fanno | `security`, settimanale e sulle PR verso `main` |
| Secret scanning + push protection | un segreto committato per sbaglio, **bloccato prima del push** | GitHub, sempre |
| Dependabot | apre una PR quando esce la dipendenza corretta | GitHub, settimanale |
| `SHA256SUMS` e attestazione (Task 16) | che il file scaricato sia quello pubblicato da questa CI | release |

**Il livello del controllo è a due velocità, di proposito.** `bandit` e `pip-audit` sono
istantanei e stanno nella CI di ogni push su `dev`, dove servono a non far entrare il
difetto. CodeQL è lento e sta nel workflow settimanale — più le pull request verso `main` —
dove serve a trovare quello che è già dentro prima che diventi rilasciabile.

**Cosa NON usiamo, e perché.** Va scritto, altrimenti fra sei mesi qualcuno lo riaggiunge:

| Escluso | Motivo |
|---|---|
| **Gitleaks, Trivy e altri scanner di segreti** | Ridondanti: il secret scanning con push protection di GitHub è gratuito sui repository pubblici e agisce *prima* del push, mentre uno scanner in CI si accorge del segreto quando è già online. Aggiungerli sarebbe un secondo lucchetto sulla stessa porta. |
| **Branch protection e rulesets** | La separazione fra `dev` e `main` è un protocollo, non un divieto imposto dalla piattaforma. Su un progetto a un solo autore la regola scritta basta; il lucchetto arriva se e quando ci saranno più mani. |
| **SBOM firmato, SLSA livello 3, threat model formale, penetration test** | Sproporzionati per un programma di analisi che gira in locale. Il tempo speso lì è tempo tolto alla correttezza delle misure. |
| **Qualunque strumento a pagamento** | Il progetto deve restare interamente riproducibile a costo zero. |

**Una cosa che non si risolve gratis, e va detta invece che nascosta.** Su Windows un
eseguibile non firmato con un certificato di code signing fa comparire l'avviso SmartScreen.
Il certificato costa qualche centinaio di euro l'anno. Fino ad allora la risposta onesta è
l'attestazione di provenienza più i checksum, con le istruzioni per verificarli: non fa
sparire l'avviso, ma rende verificabile ciò che l'avviso mette in dubbio. Va scritto nel
README, non taciuto.

**Files:**
- Create: `tests/test_no_network.py`
- Create: `.github/dependabot.yml`
- Create: `.github/workflows/security.yml`
- Create: `SECURITY.md`

**Interfaces:**
- Consumes: `measure_frame` (Task 9), il generatore sintetico (Task 11).
- Produces: il workflow `security` e il test che rende eseguibile la promessa "tutto in
  locale".

- [ ] **Step 1: Scrivere il test che dimostra l'assenza di rete**

È il passo più importante del task. La spec promette che i dati dell'utente non lasciano la
sua macchina: una promessa così si dimostra, non si dichiara.

Creare `tests/test_no_network.py`:

```python
"""Dimostrazione eseguibile della promessa "tutto in locale".

Sabota la creazione di socket nella libreria standard e poi esegue l'intera
pipeline di misura. Se qualcuno un giorno introdurra' una chiamata di rete,
anche indiretta attraverso una dipendenza, questo test si rompe e la build
non passa.

E' l'unico controllo di sicurezza di questo progetto che verifica una
promessa fatta all'utente, invece di cercare difetti nel codice.
"""

import socket

import pytest

from sagitta.measure.frame import measure_frame
from sagitta.synth.generator import Truth, generate_frame, write_synthetic_fits


class NetworkAccessAttempted(AssertionError):
    pass


@pytest.fixture
def no_network(monkeypatch):
    def _forbidden(*args, **kwargs):
        raise NetworkAccessAttempted(
            "Sagitta ha tentato di aprire una connessione di rete. "
            "La spec lo vieta senza eccezioni: i dati dell'utente non "
            "lasciano la sua macchina."
        )

    monkeypatch.setattr(socket, "socket", _forbidden)
    monkeypatch.setattr(socket, "create_connection", _forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", _forbidden)


def test_measurement_pipeline_works_without_network(tmp_path, no_network):
    pixels = generate_frame(
        600, 600, Truth(seeing_sigma_px=2.0, spacing_error=2.0), n_stars=600, seed=9
    )
    path = write_synthetic_fits(tmp_path / "light.fits", pixels)

    result = measure_frame(path)

    assert result.n_stars > 100
    assert result.zones["center"].median_fwhm_px is not None


def test_the_guard_itself_works(no_network):
    """Se questo test non fallisce, il guard non sta guardando niente."""
    with pytest.raises(NetworkAccessAttempted):
        socket.socket()
```

- [ ] **Step 2: Eseguire i test e verificare che passino**

Run: `python -m pytest tests/test_no_network.py -v`

Expected: PASS, 2 test

Se il primo test fallisce con `NetworkAccessAttempted`, **non aggirare il test**: significa
che una dipendenza sta aprendo una connessione, e va capito quale e perché. Il candidato
tipico è `astropy`, che in certe configurazioni scarica tabelle di dati temporali; in quel
caso si disattiva l'aggiornamento automatico via `astropy.utils.iers`, non si silenzia il
test.

- [ ] **Step 3: Scrivere il workflow di sicurezza**

Creare `.github/workflows/security.yml`:

```yaml
name: security

# Settimanale, a richiesta, e su ogni pull request verso main che tocchi
# il codice. CodeQL e' lento e serve a trovare cio' che e' gia' dentro:
# bandit e pip-audit girano invece a ogni push, nel workflow ci, dove
# servono a non far entrare il difetto.
on:
  schedule:
    - cron: "0 6 * * 1"
  workflow_dispatch:
  pull_request:
    branches: [main]
    paths:
      - "src/**"
      - "pyproject.toml"
      - ".github/workflows/**"

permissions:
  contents: read
  security-events: write

jobs:
  codeql:
    # Su Linux, non su Windows: CodeQL analizza il codice senza
    # eseguirlo, quindi il sistema operativo e' indifferente al
    # risultato, e su Linux e' piu' veloce.
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - uses: github/codeql-action/init@9e8d0789d4a0fa9ceb6b1738f7e269594bdd67f0 # v3.28.9
        with:
          languages: python
          queries: security-and-quality

      - uses: github/codeql-action/analyze@9e8d0789d4a0fa9ceb6b1738f7e269594bdd67f0 # v3.28.9
```

CodeQL è gratuito perché il repository è **pubblico**. Se un giorno diventasse privato,
questo workflow inizierebbe a fallire a ogni esecuzione: è una delle ragioni per cui il
vincolo globale vieta di cambiare la visibilità.

- [ ] **Step 4: Configurare Dependabot**

Creare `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
    # Le pull request di Dependabot nascono verso dev, non verso main:
    # un aggiornamento e' lavoro di sviluppo come un altro, e arriva in
    # main per la stessa strada di tutto il resto.
    target-branch: dev

  # Le action sono codice di terzi che gira nella nostra pipeline con il
  # nostro token, e nel Task 14 sono pinnate a SHA. Senza questo blocco
  # non verrebbero mai aggiornate, nemmeno per una correzione di
  # sicurezza: Dependabot aggiorna il SHA e mantiene il tag in commento.
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    target-branch: dev
```

- [ ] **Step 5: Scrivere la policy di sicurezza**

Creare `SECURITY.md` nella radice del repository:

```markdown
# Politica di sicurezza

## Cosa fa Sagitta con i tuoi dati

Niente che esca dalla tua macchina. Sagitta legge i file che le indichi, calcola, e
scrive il risultato dove glielo chiedi. Non ha account, non ha telemetria, non fa
upload, non apre connessioni di rete.

Non e' una promessa sulla parola. E' verificata a ogni esecuzione della suite da
`tests/test_no_network.py`, che sabota la creazione di socket nella libreria standard
e poi esegue l'intera pipeline di misura. Se una riga di codice o una dipendenza
tentasse di aprire una connessione, quel test fallirebbe e la build non passerebbe.

## Segnalare una vulnerabilita'

Usa la segnalazione privata di GitHub, nella scheda **Security** del repository
("Report a vulnerability"). Non aprire una issue pubblica.

Riceverai risposta appena possibile. Questo e' un progetto portato avanti nel tempo
libero: non ci sono tempi di risposta garantiti e non c'e' un programma di ricompense.

## Versioni supportate

Riceve correzioni solo l'ultima versione pubblicata. Finche' siamo sulla serie `0.x`
non esistono rami di manutenzione.

## Come verificare cio' che scarichi

Ogni release pubblica gli artefatti, il file `SHA256SUMS` e un'attestazione di
provenienza generata da GitHub, che lega quei file al commit e alla esecuzione del
workflow che li ha prodotti. Si verifica cosi':

    gh attestation verify <file> --repo Voloire/sagitta

Su Windows un eseguibile non firmato con un certificato di code signing fa comparire
l'avviso SmartScreen. Non abbiamo un certificato: costa qualche centinaio di euro
l'anno e questo progetto non ha entrate. L'attestazione di provenienza e' la risposta
che possiamo dare, ed e' piu' forte di una firma nel dire *chi* ha costruito *cosa*,
anche se non fa sparire l'avviso.

## Come e' controllato questo codice

- `pip-audit` a ogni push, per le vulnerabilita' note nelle dipendenze installate
- `bandit` a ogni push, per gli errori di sicurezza nel codice del progetto
- CodeQL ogni settimana e su ogni pull request verso `main`, per l'analisi semantica
  del flusso dei dati
- Secret scanning con push protection, che blocca un segreto prima che venga spinto
- Dependabot per gli aggiornamenti delle dipendenze e delle GitHub Action

Il codice arriva su `main` solo attraverso una pull request da `dev` con la CI verde,
e le release nascono da un tag su `main`.

## Cosa questo progetto deliberatamente non fa

Niente SBOM firmato, niente SLSA livello 3, niente threat model formale, niente
penetration test, nessuno scanner a pagamento. Sono sproporzionati per un programma
di analisi che gira in locale, e il tempo speso li' e' tempo tolto alla correttezza
delle misure.
```

- [ ] **Step 6: Verificare e committare**

Run: `python -m pytest tests/test_no_network.py -v`

Run: `pip-audit --skip-editable`

Run: `bandit -r src/sagitta -ll`

Expected: PASS su tutti e tre

Run: `python -c "import yaml,pathlib; [yaml.safe_load(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['.github/dependabot.yml','.github/workflows/security.yml']]; print('yaml ok')"`

Expected: `yaml ok`

```bash
git add .
git commit -m "security: test di assenza rete, CodeQL, Dependabot e policy"
```

Run: `git push origin dev`

---

### Task 16: Release versionate

**Schema di versione.** SemVer, partendo da `0.1.0`. Si resta sulla serie `0.x` finché il
join con i log di guida non è dentro, perché fino a quel momento il formato JSON di output
cambierà ancora e non vogliamo promettere una stabilità che non possiamo mantenere. La
prima `1.0.0` è la release che contiene lo Stadio 3.

**Sorgente unica della versione.** Il numero sta in `pyproject.toml` e da nessun'altra parte.
Il codice lo legge dai metadati del package installato. Un numero scritto due volte è un
numero che prima o poi diverge.

**Da dove nasce una release.** Da un tag `vX.Y.Z` **su `main`**, e da nient'altro. La catena
completa è: si sviluppa su `dev` → la CI è verde → pull request da `dev` a `main`, aperta e
chiusa dalla sessione Claude di revisione → merge → tag sul `main` così ottenuto. Il workflow che scrivi in questo task rifiuta di pubblicare se
una delle due condizioni non è vera: se il tag non coincide con la versione del package, o
se il commit taggato non sta su `main`. Sono due controlli automatici che sostituiscono la
branch protection, che su questo progetto non usiamo.

**Files:**
- Modify: `src/sagitta/__init__.py`
- Modify: `src/sagitta/cli.py` (opzione `--version`)
- Create: `tests/test_version.py`
- Modify: `CHANGELOG.md` (esiste già, si aggiunge la voce 0.1.0)
- Create: `.github/workflows/release.yml`

**Interfaces:**
- Consumes: la CLI (Task 12), il workflow `ci` (Task 14).
- Produces: `sagitta.__version__`, l'opzione `sagitta --version`, e il workflow `release` che
  scatta sui tag `v*`.

- [ ] **Step 1: Scrivere il test che fallisce**

Creare `tests/test_version.py`:

```python
import re
import subprocess
import sys
from importlib.metadata import version as metadata_version

import sagitta


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", sagitta.__version__), sagitta.__version__


def test_version_comes_from_package_metadata():
    """Un numero di versione scritto due volte e' un numero che divergera'."""
    assert sagitta.__version__ == metadata_version("sagitta")


def test_cli_reports_the_same_version():
    result = subprocess.run(
        [sys.executable, "-m", "sagitta.cli", "--version"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert sagitta.__version__ in result.stdout
```

- [ ] **Step 2: Eseguire il test e verificare che fallisca**

Run: `python -m pytest tests/test_version.py -v`
Expected: FAIL con `AttributeError: module 'sagitta' has no attribute '__version__'`

- [ ] **Step 3: Scrivere l'implementazione**

Sostituire il contenuto di `src/sagitta/__init__.py` (finora vuoto) con:

```python
"""Sagitta: referto forense e banco di prova per astrofotografia."""

from importlib.metadata import PackageNotFoundError, version as _version

try:
    __version__ = _version("sagitta")
except PackageNotFoundError:  # eseguito da sorgente, senza installazione
    __version__ = "0.0.0"

__all__ = ["__version__"]
```

In `src/sagitta/cli.py`, aggiungere l'import e l'opzione. Dopo la riga
`from sagitta.measure.frame import measure_frame` aggiungere:

```python
from sagitta import __version__
```

e subito dopo la creazione del parser, prima di `subparsers = ...`, aggiungere:

```python
parser.add_argument("--version", action="version", version=f"sagitta {__version__}")
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `pip install -e ".[dev]"`

Run: `python -m pytest tests/test_version.py -v`
Expected: PASS, 3 test

Run: `python -m pytest -v`
Expected: PASS, l'intera suite

- [ ] **Step 5: Scrivere il changelog**

**Il `CHANGELOG.md` esiste già** nella radice, con l'intestazione e una sezione
`## [Non rilasciato]`. **Non ricrearlo.** Sostituisci il contenuto della sezione
`## [Non rilasciato]` — cioè tutto ciò che sta fra quel titolo e la fine del file — con
quanto segue, lasciando l'intestazione del file intatta:

```markdown
## [Non rilasciato]

## [0.1.0]

### Aggiunto

- Lettura di file FITS con normalizzazione degli header verso uno schema canonico,
  tramite mappe dialetto in YAML versionate nel repository (NINA, SGP, ASIAIR, Ekos,
  piu' un dialetto generico).
- Misura della forma stellare per stella con momenti secondi pesati sul flusso: FWHM,
  eccentricita' e angolo di posizione dell'asse maggiore.
- Detection stellare con criteri di esclusione per stelle sature, al bordo, pixel caldi
  isolati e basso rapporto segnale-rumore.
- Stratificazione della misura per zona del campo: centro, anello intermedio e i quattro
  angoli separatamente.
- Guardrail di campionamento: sopra 2.5 arcsec/pixel le metriche di forma non vengono
  prodotte e il programma spiega perche'.
- Gestione delle sub a colori: misura su un sotto-reticolo verde estratto senza alcuna
  interpolazione, mai su un'immagine demosaicizzata.
- Generatore di sub sintetiche con aberrazione iniettata nota, e benchmark che verifica
  che la misura ne restituisca la corretta dipendenza dalla posizione nel campo.
- Interfaccia a riga di comando `sagitta measure`, con output JSON.

### Note

- I valori `HFR` e `FWHM` eventualmente presenti negli header vengono ignorati di
  proposito: sono incomparabili fra software diversi e vengono sempre rimisurati.
- Questa versione misura e basta. Non attribuisce cause, non legge i log di guida e non
  confronta configurazioni: sono gli stadi successivi.
```

- [ ] **Step 6: Scrivere il workflow di release**

Creare `.github/workflows/release.yml`:

```yaml
name: release

# Solo i tag. Il tag e' l'unico gesto che pubblica qualcosa, e per
# protocollo si crea su main.
on:
  push:
    tags: ["v*"]

permissions:
  contents: read

jobs:
  build:
    # Windows, come tutto il resto: l'artefatto deve nascere sulla
    # piattaforma che supportiamo, e allo Stadio 3 questo job costruira'
    # l'eseguibile nativo, che su Linux non si puo' proprio fare.
    runs-on: windows-latest
    permissions:
      contents: write      # creare la release
      id-token: write      # firmare l'attestazione di provenienza
      attestations: write  # depositarla
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          # Serve la storia completa: senza, il controllo "il tag sta su
          # main" non avrebbe i rami remoti con cui confrontarsi.
          fetch-depth: 0

      # Sostituisce la branch protection, che su questo progetto non
      # usiamo: se qualcuno tagga un commit rimasto su dev, o su un ramo
      # qualsiasi, il rilascio si ferma qui.
      - name: Il tag deve puntare a un commit che sta su main
        run: |
          python -c "import subprocess, sys; out = subprocess.run(['git', 'branch', '--remotes', '--contains', 'HEAD', '--list', 'origin/main'], capture_output=True, text=True).stdout.strip(); print('rami remoti che contengono questo commit: ' + (out or '(nessuno)')); sys.exit(0 if out else 1)"

      - uses: actions/setup-python@42375524e23c412d93fb67b49958b491fce71c38 # v5.4.0
        with:
          python-version: "3.13"

      - run: pip install -e ".[dev]"

      - name: La suite deve passare prima di pubblicare qualsiasi cosa
        run: pytest -v

      # Il confronto e' scritto in Python e non nella shell: su runner
      # Windows i costrutti bash come ${VAR#prefisso} non esistono, e
      # Python c'e' gia'. Il job fallisce se tag e versione divergono.
      - name: Il tag deve coincidere con la versione del package
        run: |
          python -c "import os, sys, sagitta; tag = os.environ['GITHUB_REF_NAME'].lstrip('v'); print('tag=' + tag + ' package=' + sagitta.__version__); sys.exit(0 if tag == sagitta.__version__ else 1)"

      - name: Costruire sdist e wheel
        run: python -m build

      # Anche i checksum in Python, per lo stesso motivo: sha256sum non
      # esiste su Windows, e certutil ha un formato di output diverso.
      - name: Calcolare i checksum
        run: |
          python -c "import hashlib, pathlib; d = pathlib.Path('dist'); lines = [hashlib.sha256(f.read_bytes()).hexdigest() + '  ' + f.name for f in sorted(d.iterdir()) if f.is_file()]; (d / 'SHA256SUMS').write_text('\n'.join(lines) + '\n', encoding='utf-8'); print('\n'.join(lines))"

      # Gratuita perche' il repository e' pubblico. Lega ogni artefatto al
      # commit e alla esecuzione del workflow che lo ha prodotto: e' la
      # risposta alla domanda "questo file e' davvero quello costruito
      # dalla loro CI?", e chi scarica la verifica con
      #   gh attestation verify <file> --repo Voloire/sagitta
      - uses: actions/attest-build-provenance@520d128f165991a6c774bcb264f323e3d70747f4 # v2.2.0
        with:
          subject-path: "dist/*.whl,dist/*.tar.gz"

      - uses: softprops/action-gh-release@c95fe1489396fe8a9eb87c0abf8aa5b2ef267fda # v2.2.1
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
            dist/SHA256SUMS
          body_path: ${{ github.workspace }}/CHANGELOG.md
          draft: true
```

La release nasce **bozza**: il workflow costruisce, verifica e allega, ma la pubblicazione
resta un gesto umano. È l'ultimo controllo prima che qualcosa raggiunga altre persone, e
costa un clic.

**Pubblicazione su PyPI: non ora.** Quando servirà, si fa con il *trusted publishing* via
OIDC, che è gratuito e non richiede di conservare un token API nei segreti del repository.
Va fatto solo dopo aver rivendicato il nome `sagitta` su PyPI e verificato che sia libero.
Finché l'artefatto giusto per l'utente finale è l'eseguibile nativo e non la wheel, PyPI
serve solo agli sviluppatori e può aspettare.

- [ ] **Step 7: Verificare la procedura di release in locale**

Run: `python -m build`

Run: `python -c "import pathlib; print([p.name for p in pathlib.Path('dist').iterdir()])"`
Expected: due file, `sagitta-0.1.0-py3-none-any.whl` e `sagitta-0.1.0.tar.gz`

Run: `python -c "import sagitta; assert sagitta.__version__ == '0.1.0'; print('versione allineata')"`
Expected: `versione allineata`

Run: `python -c "import yaml,pathlib; yaml.safe_load(pathlib.Path('.github/workflows/release.yml').read_text(encoding='utf-8')); print('yaml ok')"`
Expected: `yaml ok`

- [ ] **Step 8: Commit e push su `dev`**

```bash
git add .
git commit -m "release: versione da metadati del package, changelog e workflow di rilascio"
```

Run: `git push origin dev`

**Qui il tuo lavoro finisce.** Non aprire la pull request verso `main`, non fare merge, non
creare il tag `v0.1.0`. Segnala che il Task 16 è chiuso e fermati: il push su `dev` è già
il segnale, e il turno passa da solo.

- [ ] **Step 9 (sessione Claude di revisione, non l'agente di sviluppo): promuovere e taggare**

Scritto qui perché il protocollo sia completo in un solo posto, non perché l'agente di
sviluppo lo esegua.

```bash
gh pr create --base main --head dev --title "Stadio 0 e 1: motore di misura e validazione sintetica" --body-file CHANGELOG.md
```

Con la CI verde sulla pull request:

```bash
gh pr merge --merge
```

Poi, da `main` aggiornato:

```bash
git switch main
git pull
git tag -a v0.1.0 -m "Sagitta 0.1.0"
git push origin v0.1.0
```

Il push del tag fa partire il workflow `release`, che rifiuta di procedere se il tag non
coincide con la versione del package o se il commit taggato non sta su `main`. La release
resta in bozza fino alla pubblicazione manuale.

---

## La configurazione GitHub, decisa: account Free, repository pubblico

Non è una domanda aperta: è il vincolo entro cui questo piano è scritto. Va letto prima del
Task 14, perché tre task ne dipendono.

**Account GitHub Free, repository pubblico**, all'indirizzo
**https://github.com/Voloire/sagitta**. Da cui, senza spendere niente:

- **Minuti di Actions illimitati.** Sui repository pubblici non intaccano la quota di 2000
  minuti al mese dell'account, che resta interamente disponibile per gli altri progetti
  privati dello stesso proprietario. Non c'è un budget da amministrare: è metà della ragione
  per cui il repository è pubblico.
- **CodeQL gratuito**, con l'analisi semantica del flusso dei dati che bandit e pip-audit non
  fanno.
- **Secret scanning con push protection**, che blocca un segreto *prima* che il push parta.
- **Attestazioni di provenienza** sugli artefatti di release, che legano ogni file al commit
  e alla esecuzione del workflow che lo ha prodotto.
- **Dependabot**, che funziona su qualsiasi piano.

Le prime tre sono **gia' attive sul repository** — secret scanning, push protection, avvisi
di vulnerabilita' e correzioni di sicurezza automatiche di Dependabot — e sono impostazioni
del proprietario: l'agente non deve configurarle ne' verificarle, ma solo scrivere il file
`.github/dependabot.yml` del Task 15, che riguarda gli aggiornamenti di versione ed e' una
cosa diversa.

Tutto il resto della sicurezza è open source e gira come normale passo di un workflow:
`pip-audit` e `bandit`. Nessuno dei due dipende dal piano GitHub.

**Cosa cambia se il repository diventasse privato.** Non è un'ipotesi accademica, è la
ragione per cui il vincolo globale lo vieta:

| Funzionalità | Su pubblico | Su privato con piano Free |
|---|---|---|
| Minuti di Actions | illimitati | 2000/mese per account, moltiplicatore 2× su Windows |
| CodeQL | gratuito | richiede una licenza a pagamento |
| Secret scanning e push protection | gratuiti | non disponibili |
| Artifact attestations | gratuite | richiedono Team o Enterprise |

I workflow dei Task 14, 15 e 16 sono scritti su questa configurazione: cambiarla li fa
fallire a ogni esecuzione.

**I due rami, e perché non c'è la branch protection.** Si sviluppa su `dev`, si arriva su
`main` per merge di una pull request, e il tag `vX.Y.Z` su `main` fa partire il rilascio. La
branch protection imporrebbe questa regola dalla piattaforma; su un progetto a un solo autore
è attrito senza beneficio, e la stessa garanzia dove conta davvero — al momento di pubblicare
— è già ottenuta dai due controlli automatici del workflow `release`, che rifiuta un tag non
allineato alla versione o non appartenente a `main`. Se un giorno il progetto avrà più mani,
la branch protection è la prima cosa da aggiungere, e a quel punto sarà gratuita perché il
repository è pubblico.

**Nessuna infrastruttura di CI locale.** Niente Jenkins, niente Docker, niente runner
self-hosted. Un agente locale girerebbe sulla macchina di sviluppo, quindi verificherebbe
l'ambiente dello sviluppatore invece di uno pulito — che è esattamente il contrario del
motivo per cui la CI esiste in un progetto a piattaforma singola. In cambio porterebbe un
servizio da tenere aggiornato, una superficie di plugin da sorvegliare e una seconda
definizione di pipeline da mantenere allineata alla prima. Con i minuti illimitati, non c'è
proprio un problema da risolvere.

**Cosa non è pubblicato, e non va pubblicato.** La discussione preliminare da cui nasce
questo progetto contiene giudizi diretti su aziende, su loro clienti e su creator citati per
nome. Resta negli appunti di lavoro privati, fuori da questo repository. In `docs/` va solo
ciò che è argomentazione tecnica.

**Chi fa cosa, per chiudere il cerchio.** L'agente di sviluppo esegue i task, committa e
spinge su `dev`: finisce lì. Una sorveglianza esterna guarda la punta di `dev` e l'esito
della CI e apre il turno — anche quando `dev` smette di muoversi, che è il caso in cui un
esecutore bloccato e un guardiano che insiste si annullano a vicenda in silenzio. La sessione
Claude di revisione legge il diff, apre e chiude la pull request verso `main`, e crea il tag.
Resta un solo gesto umano in tutta la catena: la release nasce in bozza, e pubblicarla è un
clic del proprietario.

**Nulla delle impostazioni della piattaforma è compito dell'agente che esegue.** Visibilità
del repository, secret scanning, Dependabot e permessi sono già configurati.


## Cosa resta fuori da questo piano

Esplicitato perché nessuno lo dia per implicito:

- **Parser dei guide log PHD2**, ricostruzione del tempo assoluto, offset confermato
  dall'utente, esclusione dei settle post-dither, separazione in banda. È lo Stadio 2.
- **Classificatore diagnostico** con regole di esclusione e confidenze, e il suo benchmark
  dedicato. È lo Stadio 3.
- **Indice DuckDB**, deduplica, tracciamento della catena grezza/calibrata/registrata,
  risoluzione dei target per coordinate. È lo Stadio 4.
- **Banco di prova statistico** con covariate e intervalli di confidenza. È lo Stadio 4 ed è
  il posizionamento vero del prodotto.
- **Interfaccia grafica**, export PNG, impacchettamento in eseguibile nativo per le tre
  piattaforme.
- **Lettura XISF** e di FITS compressi.
- **Rilevamento automatico di `frame_kind`**: al momento resta `"unknown"` per ogni file
  letto, il che significa che tutte le sub sono trattate come grezze. Il rilevamento (dalla
  presenza di keyword di calibrazione, dal nome della cartella, dalla catena di HISTORY)
  appartiene allo Stadio 4, insieme all'indice.
- **Verifica di `FOCUSPOS` / `FOCPOS`** negli header reali dei vari software, che è la
  decisione aperta numero 8 della spec.

### Requisiti dello Stadio 0 che questo piano copre solo in parte

Dichiarati apertamente, perché la spec li nomina e chi esegue non deve crederli fatti.

- **Criteri di esclusione incompleti.** Sono implementati: stelle sature (cima piatta),
  stelle al bordo, pixel caldi isolati (`min_pixels`), basso SNR (soglia a 5 sigma).
  **Non** sono implementati: **stelle sovrapposte**, tracce di satellite, colonne calde,
  raggi cosmici estesi. Le stelle sovrapposte sono la lacuna che pesa di più, perché due
  stelle vicine producono un blob allungato che il motore misura come una stella
  eccentrica, e in un campo denso questo sposta la mediana di zona. Il rimedio naturale è
  un criterio di ellitticità del blob prima della misura, più il confronto fra numero di
  massimi locali e numero di blob. Va aggiunto prima dello Stadio 3, perché il
  classificatore diagnostico ne dipende direttamente.
- **Plausibilità di `XPIXSZ` e `FOCALLEN`.** La spec segnala che questi due valori sono
  spesso sbagliati negli header reali, tipicamente perché il profilo di acquisizione non
  è stato aggiornato dopo un cambio di riduttore o di camera. Qui si gestisce solo la
  loro **assenza**, non la loro **falsità**: un valore sbagliato produce una scala
  sbagliata e quindi un guardrail applicato alla soglia sbagliata. La verifica vera
  richiede un confronto con la scala risolta da plate solving, o con la moda dei valori
  su tutto l'archivio dell'utente: entrambe cose da Stadio 4.
- **`DATE-OBS` assunto UTC quando è privo di timezone.** Il lettore lo documenta nel
  codice ma non lo verifica. La verifica vera arriva allo Stadio 2, dove la
  cross-correlazione con il guide log rende l'offset misurabile e confermabile
  dall'utente. Fino ad allora nessuna funzionalità dipende dall'istante assoluto, quindi
  l'assunzione non fa danno — ma va tolta prima del join, non dopo.
