#!/usr/bin/env python3

SYSTEM_CLOCK = 27_000_000

A4_FREQ = 440
RANGE = (-44, 83)

BPMS = [20, 40, 60, 80, 120, 140]


from sys import stderr
from typing import NamedTuple

assert len(range(*RANGE)) == 127

NOTE_NAMES = ['A', 'As', 'B', 'C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs']
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 1, 4, 5, 7, 8, 10] #?

class Note(NamedTuple):
	name: str
	octave: int
	freq: float
	divider: int
	div12: bool

notes: list[Note] = []

for nn in range(*RANGE):
	name = NOTE_NAMES[nn % len(NOTE_NAMES)]
	octave = 4 + (nn - 3) // len(NOTE_NAMES)
	freq = A4_FREQ * (2.0 ** (nn / len(NOTE_NAMES)))

	print(f"{name}[{octave}] = {freq}Hz", file=stderr)
	divider = SYSTEM_CLOCK / freq
	div12 = False

	if divider > (2**16 - 1):
		div12 = True
		divider /= 12

	divider = round(divider)
	assert divider < 2**16, f'Too low frequency for {name}[{octave}] = {freq}, requires divider of {divider}'

	print(f"  ~= {SYSTEM_CLOCK}{' / 12' if div12 else ''} / {divider} = {SYSTEM_CLOCK / (12 if div12 else 1) / divider}", file=stderr)

	notes.append(Note(name=name, octave=octave, freq=freq, divider=divider, div12=div12))



print('; Note tables')
print('; 1) T2H for each note')
print('notes_table_t2h:')
print('    .db 0x00        ; Mute')

for note in notes:
	print(f'    .db {hex((2**16 - note.divider) >> 8)}'.ljust(20), f'; {note.name}{note.octave}', sep='')

print('; 2) T2L for each note')
print('notes_table_t2l:')
print('    .db 0x00        ; Mute')

for note in notes:
	print(f'    .db {hex((2**16 - note.divider) & 0xFF)}'.ljust(20), f'; {note.name}{note.octave}', sep='')

print('; 3) AUXR for each note')
print('notes_table_auxr:')
print('    .db 0x00      ; Mute')

for note in notes:
	print(f'    .db {hex((1 << 4) | (0 if note.div12 else (1 << 2)))}'.ljust(20), f'; {note.name}{note.octave}', sep='')


print('; Tempo tables')

def calc_tempo_dividers(bpm) -> (int, int):
	total_div = (60 / (16 * bpm)) * (SYSTEM_CLOCK / 12)

	divider_1, divider_2 = None, None

	for i in range(1, 256):
		if total_div / i <= 65535:
			divider_1 = i
			divider_2 = int(total_div / i)
			break

	assert divider_1 is not None, f'Too big divider {total_div} for tempo of {bpm} bpm'

	resulting_div = divider_1 * divider_2

	print(f"BPM = {bpm}, divider = {total_div} ~= {resulting_div} = {divider_1} * {divider_2} (delta={total_div - float(resulting_div)})")

	return divider_1, divider_2

TEMPO_DIVIDERS = [calc_tempo_dividers(bpm) for bpm in BPMS]

print('; 1) TH per tempo')
print('tempo_table_th:')
for ((sd, hd), bpm) in zip(TEMPO_DIVIDERS, BPMS):
	print(f'    .db {hex((2**16 - hd) >> 8)}'.ljust(20), f'; {bpm} bpm', sep='')

print('; 2) TL per tempo')
print('tempo_table_tl:')
for ((sd, hd), bpm) in zip(TEMPO_DIVIDERS, BPMS):
	print(f'    .db {hex((2**16 - hd) & 0xFF)}'.ljust(20), f'; {bpm} bpm', sep='')

print('; 3) Software divider per tempo')
print('tempo_table_sd:')
for ((sd, hd), bpm) in zip(TEMPO_DIVIDERS, BPMS):
	print(f'    .db {hex(sd)}'.ljust(20), f'; {bpm} bpm', sep='')

