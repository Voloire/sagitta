# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/it/1.1.0/).
Versionamento: [SemVer](https://semver.org/lang/it/).

**Ogni release ha una voce qui, senza eccezioni.** Si scrive sotto `[Non rilasciato]` mentre
si lavora, e quella sezione diventa il corpo della release quando si crea il tag.

Si resta sulla serie `0.x` finché il join con i log di guida non è dentro: fino ad allora il
formato JSON di output può ancora cambiare fra una minor e l'altra. È una condizione, non una
scadenza — non ci sono date su questo progetto.

## [Non rilasciato]

Nessuna release pubblicata. Il repository contiene per ora soltanto documenti: la specifica
del progetto e il piano di implementazione dei primi due stadi. Non c'è codice.

### Impostato

- Specifica del progetto in `docs/design.md`: cosa misura Sagitta, cosa non fa per scelta, e
  il ragionamento che porta a ciascuna decisione.
- Piano di implementazione degli Stadi 0 e 1 in `docs/plan-stadio-0-1.md`, eseguibile passo
  per passo.
- Rami `dev` e `main`, con il rilascio che parte da un tag su `main`.
- Integrazione continua, controlli di sicurezza e workflow di rilascio, descritti nel piano e
  da creare durante l'esecuzione.
