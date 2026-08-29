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
