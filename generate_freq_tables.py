#!/usr/bin/env python3

SYSTEM_CLOCK = 27_000_000

A4_FREQ = 440
RANGE = (-44, 84)

BPMS = [20, 33.3, 40, 60, 80, 120, 140]
BPM_INITIAL = 80


from sys import stderr
from typing import NamedTuple

assert len(range(*RANGE)) == 128

assert BPM_INITIAL in BPMS

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

first_x12_note_id = next(i for (i, note) in enumerate(notes) if not note.div12)


print('; Note tables')
print('; 1) T2H for each note')
print('notes_table_th:')

for note in notes:
	print(f'    .db {hex((2**16 - note.divider) >> 8)}'.ljust(20), f'; {note.name}{note.octave}', sep='')

print('; 2) T2L for each note')
print('notes_table_tl:')

for note in notes:
	print(f'    .db {hex((2**16 - note.divider) & 0xFF)}'.ljust(20), f'; {note.name}{note.octave}', sep='')

print("; Index of first note that does need full system frequency")
print(f'.equ    FIRST_X12_NOTE_ID, {first_x12_note_id}')


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

	print(f"BPM = {bpm}, divider = {total_div} ~= {resulting_div} = {divider_1} * {divider_2} (delta={total_div - float(resulting_div)})", file=stderr)

	return divider_1, divider_2

_CHR_TO_SS = {' ': '0', **{ str(x): f'SS_CHR_{x}' for x in range(10)}}

def bpm_to_ss(bpm) -> (str, str, str):
	bpm_str = str(bpm).rjust(3)
	chr_lst = []

	for c in bpm_str:
		if c in _CHR_TO_SS:
			chr_lst.append(_CHR_TO_SS[c])
		elif c == '.':
			chr_lst[-1] += ' | SS_SEGB_DP'
		else:
			assert False

	assert len(chr_lst) == 3, f'Too long text ({chr_lst}) for bpm {bpm}'
	print(f"BPM = {bpm} -> {chr_lst}", file=stderr)
	return tuple(chr_lst)

TEMPO_DIVIDERS = [calc_tempo_dividers(bpm) for bpm in BPMS]

TEMPO_SS_TEXTS = [bpm_to_ss(bpm) for bpm in BPMS]

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

print(f'.equ tempo_initial_index, {BPMS.index(BPM_INITIAL)}')
print(f'.equ tempo_max_index, {len(BPMS) - 1}')

print('; 4.1) Seven-segment first character per tempo')
print('tempo_table_ss_0:')
print(f'    .db {", ".join(s[0] for s in TEMPO_SS_TEXTS)}')

print('; 4.2) Seven-segment second character per tempo')
print('tempo_table_ss_1:')
print(f'    .db {", ".join(s[1] for s in TEMPO_SS_TEXTS)}')

print('; 4.3) Seven-segment third character per tempo')
print('tempo_table_ss_2:')
print(f'    .db {", ".join(s[2] for s in TEMPO_SS_TEXTS)}')
