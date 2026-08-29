# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/it/1.1.0/).
Versionamento: [SemVer](https://semver.org/lang/it/).

**Ogni release ha una voce qui, senza eccezioni.** Si scrive sotto `[Non rilasciato]` mentre
si lavora, e quella sezione diventa il corpo della release quando si crea il tag.

Si resta sulla serie `0.x` finché il join con i log di guida non è dentro: fino ad allora il
formato JSON di output può ancora cambiare fra una minor e l'altra. È una condizione, non una
scadenza — non ci sono date su questo progetto.

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
