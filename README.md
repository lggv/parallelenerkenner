# parallelenerkenner

## Einleitung

Im vierstimmigen Choral (genau genommen in allen klassischen Musikgattungen) gelten einige Satzregeln,
die die klangliche Unabhängigkeit der einzelnen Stimmen sicherstellen sollen.
Eine wichtige Satzregel ist das Verbot von [Quint- und Oktavparallelen](https://www.lehrklaenge.de/PHP/Harmonielehre1/Satzregeln1.php) zwischen einzelnen Stimmen
bei einem Akkordwechsel.

Die Fragestellung dieser Anwendung ist, inwieweit solche Parallelen in einer eingegebenen Audiodatei automatisch ermittelt werden können.

## Choräle

Im Gegensatz zu hochpolyphonen Chorwerken weisen sich Choralsätze (bei weiterhin bestehender Unabhängigkeit der vier Stimmen voneinander) durch eine einfachere, homophonere Gestaltung aus.
Dies erleichtert die harmonische Analyse und erlaubt die Betrachtung des Satzes als zeitliche Abfolge wechselnder Klangereignisse (Akkorde).

Das zeigt beispielhaft der Choral "So wandelt froh auf Gottes Wegen" von Johann Sebastian Bach, bei dem nicht nur eine "horizontale" Leseweise pro Stimme, sondern auch eine "vertikale",
welche alle Stimmen zu einem Zeitpunkt erfasst, möglich ist:

![Choral als Notentext](https://www.bachfestleipzig.de/sites/default/files/article-text/Wer_nur_BWV%20197_10_oben.gif)

## Funktionsweise

Die Anwendung ermittelt sequenziell Parallelen aus einer WAV-Eingabedatei. Zwei Aufgabenbereiche sind dabei wesentlich:

1) Einlesen der Audiodatei, Unterteilung in Abschnitte, Identifikation einzelner Akkorde und Extraktion der jeweiligen Stimmen.
2) Parallelenermittlung auf Basis der "aktuellen" und der vorangegangenen Stimmdisposition.

## 1) Analyse der Audiodatei

Für die weitere Analyse wird die eingegebene Audiodatei in mehrere aufeinanderfolgende Abschnitte ("Frames") unterteilt. Diese "Frames" werden dann nacheinander analysiert.
Auf die Sampledaten jedes Frames wird eine FFT-Funktion angewendet, um die einzelnen Stimmen zu extrahieren. Das Ergebnis dieser Funktion ist eine Frequenzverteilung,
deren "Peaks" die im Akkord enthaltenen Töne angeben. Da uns nur die Grundtöne der Akkorde interessieren und die höchsten Frauenstimmen in der klassischen Musik
selten über das hohe a2 (= 880Hz) hinausgehen, wird zudem nur der Bereich von 0-880Hz betrachtet. Etwaige Obertöne fallen deswegen nicht ins Gewicht.

Zwei Variablen haben einen Einfluss auf die Genauigkeit der Akkordanalyse: Sample-Rate und zeitliche Länge des Frames. Für genauere Ergebnisse ist eine höhere Sample-Rate
von Vorteil, weswegen im Laufe der Entwicklung vorwiegend Testdateien mit 88,2kHz verwendet wurden.
Die zeitliche Länge des Frames wurde auf ~0,5s festgelegt, da Choralmusik in vorwiegend langsameren Tempi erklingt.

Damit die Akkordanalyse auf Basis einer FFT reibungslos möglich ist, muss die eingegebene Audiodatei derzeit noch aus reinen Sinuskurven bestehen.

## 2) Parallelenermittlung

Die Anwendung verwaltet zwei verschiedene Stimmdispositionen: Zum einen die Stimmen des vorangegangenen Klangereignisses, zum anderen diejenigen des "aktuellen" Klangereignisses. Ändert sich irgendeine
Stimme in einem Frame, so wird die komplette aktuelle Stimmdisposition aktualisiert und die vorangegangene Disposition nimmt die alten Werte der aktuellen an. So lässt sich jede Akkordveränderung einzeln
untersuchen, was für die Ermittlung von Parallelen essentiell ist.

Die Anwendung arbeitet in der heute üblichen [gleichstufigen Stimmung](https://de.wikipedia.org/wiki/Gleichstufige_Stimmung). Diese liegt in chromatischer Sortierung vor. Ist ein Ton (und dessen Index in der Liste) bekannt, lässt sich somit
durch Abstandsberechnung sehr leicht die zugehörige Quinte (Oktave / Quinte über der Oktave etc.) bestimmen. Gibt es in der vorangegangenen Stimmdisposition solche Intervalle, werden dieselben Stimmen in der aktuellen Disposition untersucht.
Weisen auch sie dasselbe Intervall auf, ist eine Parallele gefunden. Mithilfe der Länge des Frames in Sekunden und der Framenummer lässt sich zudem die ungefähre Position der Parallele in der Audiodatei ermitteln.

## Limitierungen

### Stimmklänge

Die "größte Baustelle" der Anwendung bildet zweifellos das zugegebenermaßen etwas künstliche Erfordernis, die Eingabedatei aus einer Kombination von Sinuskurven zu konstruieren. Idealerweise besteht die Eingabe direkt aus einem Export aus einem Notensetzprogramm,
wodurch die einzelnen Stimmen in einem etwas organischeren MIDI-Klang vorliegen würden. Dies stellt jedoch weitaus höhere Anforderungen an die Akkorderkennung als eine FFT, weswegen hierauf fürs erste verzichtet wurde. Immerhin ist die Anwendung modular genug gehalten,
sodass die Funktionalität zur Ermittlung von Parallelen lediglich "fertige" Akkorde als Eingabe benötigt und der erste Block der Akkorderkennung theoretisch komplett umgebaut werden könnte, solange die Schnittstelle unverändert bleibt.

### Stimmführung

Nach den Satzregeln ist z.B. die vereinzelte Dopplung von Stimmen (d.h. Erklingen zweier Stimmen auf dem gleichen Ton) gültig und üblich. Rein klanglich gesehen "verschwindet" dabei jedoch eine Stimme aus dem Klanggeschehen,
wenn alle Stimmen "gleich klingen". In der Folge ist es nicht trivial, den Stimmverlauf allein auf Basis des Gehörten zu rekonstruieren. Dies ist außerdem der Grund, weshalb die ebenfalls verbotenen Primparallelen in der Analyse zunächst ausgeklammert wurden.

Die beiden folgenden zweistimmigen Notentexte sollen dieses Problem verdeutlichen. Beide Takte klingen gleich, jedoch unterscheiden sie sich maßgeblich in der Stimmführung.

<img width="500" alt="grafik" src="https://github.com/user-attachments/assets/e05018ec-bee6-4653-a7be-a7e129ea6825" />
<img width="500" alt="grafik" src="https://github.com/user-attachments/assets/4f5ac704-5208-40aa-8637-3d9f751418db" />

Die zweite Grafik zeigt zudem die Gültigkeit von Stimmkreuzungen: Es ist durchaus erlaubt, eine eigentlich höhere Stimmlage unter eine tiefere Stimmlage zu setzen; insbesondere in der frühbarocken Choralmusik von Michael Praetorius kommt dies durchaus häufig und großflächig vor.
Auch das lässt sich in seiner Gänze außer der Analyse von Audioinformationen nur durch das Studium der zugehörigen Notentexte erkennen.
Die vorliegende Anwendung nimmt daher auf Stimmkreuzungen und -dopplungen keine Rücksicht und analysiert lediglich die unabhängig erklingenden Stimmen.



