# Pixel Play Boy

An alternative firmware for STC15F2K60S2-based game kit that turns it into a musical instrument.

Because just soldering few parts together and playing Tetris for few minutes is not fun enough.

## Hardware modifications

This firmware requires some changes in original kit schematic:

1) Reconnect resistor from `P5.5` (pin 19 of MCU) to `P3.5` (pin 26 of MCU). This connects audio amplifier input to hardware output of timer T0, so no (interrupt) code is required to output the signal, MCU hardware does it automatically. This change is necessary for the device to play any sound.

2) Connect `P1.5` (pin 14 of MCU) to pin 3 of 5631AS seven-segment indicator. Pin 6 of the indicator is missing. This connection enables displaying dots on the seven-segment indicator, so it's not really critical for device function.

## Programming the MCU

The STC15F2K60S2 MCU can be programmed using a USB to TTL serial converter, connected as follows:

```
MCU pins                     Converter pins
[22] -------/\/\/\/--------- [RxD]
            300R (330R)
[21] ----------|>|---------- [TxD]
            (diode)
```

Most likely, any converter will work. I used a CH340-based one.

Be sure to select the right MCU type and system clock frequency in the programming application.

## How to build

This project uses MCS-51 assembler (`as31`) created by Paul Stoffregen.

The firmware is assembled by the following command:

```sh
as31 -l pixel_play_boy.a31
```

If you want to have different tone range, tempo options or use a different MCU frequency, you can change constants in [generate_freq_tables.py](generate_freq_tables.py), run it

```sh
python3 ./generate_freq_tables.py > ./freq_tables.a31
```

and replace the tables in `pixel_play_boy.a31` by new contents of `freq_tables.a31`.

## Why "Pixel Play Boy"?

One of names present on the kit I've got was "Pixel Game Boy".
With this firmware this thing still plays, but not games, so...

## Useful links

[Another attempt to rewrite firmware of similar device](https://github.com/mogoreanu/8x16),
[1](https://github.com/mogoreanu/8x16_blink),
[2](https://github.com/mogoreanu/8x16_draw),
[3](https://github.com/mogoreanu/8x16_snake)

[Full sources of original firmware](https://github.com/mogoreanu/8x16/issues/1),
[direct](https://drive.google.com/file/d/1PPoQzjSBBf56hC0j88NpE-BPuN4MxSsc/view?usp=sharing)

[Paul Stoffregen's 8051 assembler](https://www.pjrc.com/tech/8051/tools/index.html),
[sources mirror](https://github.com/Susmit-A/as31)

[Official programming software for Windows](https://www.stcmicro.com/rjxz.html)
