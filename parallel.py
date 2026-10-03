import numpy as np
import scipy.io.wavfile as wave

import sys

# Textbeschreibungen der Stimmregister.
registers = [
    "Bass", "Tenor", "Alto", "Soprano"
]

# Töne des vorangegangenen Klangereignisses. Ist zu Beginn ungültig, da es noch kein vorangegangenes Ereignis gab.
prev_voices = []

# Aktuelle Stimmlagen
voices = []

# Gleichstufige Temperierung in Hz. Orientiert sich grob am üblichen Ambitus von Chorälen.
notes = {
    "F": 87.31,
    "F#": 92.50,
    "G": 98.00,
    "G#": 103.83,
    "A": 110.00,
    "A#": 116.54,
    "H": 123.47,

    "c": 130.81,
    "c#": 138.59,
    "d": 146.83,
    "d#": 155.56,
    "e": 164.81,
    "f": 174.61,
    "f#": 185.00,
    "g": 196.00,
    "g#": 207.65,
    "a": 220.00,
    "a#": 233.08,
    "h": 246.94,

    "c1": 261.63,
    "c#1": 277.18,
    "d1": 293.66,
    "d#1": 311.13,
    "e1": 329.63,
    "f1": 349.23,
    "f#1": 369.99,
    "g1": 392.00,
    "g#1": 415.30,
    "a1": 440.00,
    "a#1": 466.16,
    "h1": 493.88,

    "c2": 523.25,
    "c#2": 554.37,
    "d2": 587.33,
    "d#2": 622.25,
    "e2": 659.25,
    "f2": 698.46,
    "f#2": 739.99,
    "g2": 783.99,
    "g#2": 830.61,
    "a2": 880.00
}

# Zu analysierende Audiodatei
if len(sys.argv) < 2:
    print("Usage: python test.py filename [-v]")
    sys.exit()
filename = sys.argv[1]

# Debug-Output
verbose = True if len(sys.argv) >= 3 and sys.argv[2] == "-v" else False


#============================================
# HILFSFUNKTIONEN
#============================================

# Extrahiere unterschiedliche Stimmen aus einem Frame. Ermittle auch die zugehörigen Notennamen
# aus der gleichstufigen Frequenztabelle.
#
# Eingabe: Ein Ausschnitt aus der Audiodatei ("Frame"), deren Sample-Rate sowie ein Schwellwert, ab welchem eine Frequenz als Teil des Akkords gewertet wird
# Ausgabe: Eine Liste, welche die Notennamen des Akkords im Frame enthält.
def get_frame_voices(frame, sample_rate, threshold=1):
    fft_data = np.fft.fft(frame, sample_rate)
    fft_frequencies = np.abs(fft_data)
    x_freq = np.fft.fftfreq(sample_rate, 1/sample_rate)

    frame_voices = []
    for f in range(len(fft_frequencies[:880])):
        f_scaled = round(fft_frequencies[ f ] / 1e7, 2)
        if f_scaled >= threshold:

            note_name = "?"
            for n in notes:
                if round(notes[ n ]) == x_freq[ f ]:
                    note_name = n

            #print("Spike at: {0} with {1}, note: {2}".format(f, f_scaled, note_name))
            if note_name != "?":
                frame_voices.append(note_name)

    return frame_voices

# Gebe die vorherigen und die aktuellen Stimmen auf der Konsole aus
def print_voices():
    for v in reversed(range( len(voices) )):
            try:
                print((registers[ v ] + ":").rjust(8), prev_voices[ v ].ljust(3), "->", voices[ v ])
            except:
                print((registers[ v ] + ":").rjust(8), voices[ v ])
    print()

# Ermittelt Quint- und Oktavabstände in einem einzelnen vierstimmigen Akkord.
#
# Eingabe: Eine Liste aus mehreren (typischerweise 4) unabhängigen Stimmen
# Ausgabe: Zwei Listen, welche jeweils Stimmen im Quint- bzw. Oktavabstand in Tupeln zusammenfassen
def calc_parallels(voices):

    quints = []
    octaves = []

    notes_list = list(notes)

    # Wir kombinieren jede Stimme untereinander und ermitteln jeweils den tonalen Abstand.
    for i in range( len(voices) ):
        for j in range( i, len(voices) ):
            if i == j:
                continue
            v1 = voices[ i ]
            v2 = voices[ j ]
            dist = abs(notes_list.index( v1 ) - notes_list.index( v2 ))

            # Quinten
            if dist == 7 or dist == 19 or dist == 31: # 7 Halbtonschritte ergeben eine reine Quinte, aber wir wollen auch Quinten über mehrere Oktaven erfassen!
                quints.append( (i,j) )

            if dist == 12 or dist == 24 or dist == 36:
                octaves.append( (i,j) )

    return quints,octaves

# Analysiere zwei aufeinanderfolgende Klangereignisse (d.h. die vorherigen Stimmen und die aktuellen Stimmen).
# Hier werden Quint- und Oktavparallelen ermittelt.
# Zur genaueren zeitlichen Lagebestimmung der Parallelen werden der Funktion Framenummer und -länge übergeben
def analyze_progression(frame_length, frame_idx):

    parallels_found = False

    prev_quints,prev_octaves = calc_parallels(prev_voices)
    quints,octaves = calc_parallels(voices)

    for pair in prev_quints:
        if pair in quints:
            print("Parallel quints found between {0} and {1}. At: {2}s".format(registers[ pair[0] ], registers[ pair[1] ], frame_idx * frame_length))
            parallels_found = True

    for pair in prev_octaves:
        if pair in octaves:
            print("Parallel octaves found between {0} and {1}. At: {2}s".format(registers[ pair[0] ], registers[ pair[1] ], frame_idx * frame_length))
            parallels_found = True

    return parallels_found



#============================================
# PROGRAMM
#============================================

RATE, wavedata = wave.read(filename)
wavedata = np.array(wavedata)

found = False

# Framelänge in Sekunden
FRAME_LENGTH = 0.5
# ... und in Samples
FRAME_SIZE = int(FRAME_LENGTH * RATE)

print("Analyzing {0}s sample \"{1}\" at {2} Hz".format(round(len(wavedata) / RATE, 1), filename, RATE))

step = 0
frame_idx = 0
while step < len(wavedata):
    # Nächster Frame aus der Datei
    if step+FRAME_SIZE > len(wavedata):
        frame = wavedata[step:]
    else:
        frame = wavedata[step:step+FRAME_SIZE]

    frame_voices = get_frame_voices(frame, RATE, 5.5)

    if not frame_voices:
        if verbose:
            print("* silence *\n")
    else:
        if voices != frame_voices:
            voices = frame_voices

            if analyze_progression(FRAME_LENGTH, frame_idx):
                found = True

            if verbose:
                print_voices()

            prev_voices = voices

    frame_idx = frame_idx + 1
    step += FRAME_SIZE

if not found:
    print("No parallels found in file.")
