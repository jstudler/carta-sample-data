---
title: Feedback Loop Risk
date: 2025-08-05
topic: spatial-acoustics
category: research
type: lookout
width: 2
---

A potential issue emerged during the frequency-band mapping tests that warrants attention in future work.

If a light sculpture is exhibited alongside any sound-producing element — another artwork, a loudspeaker playing ambient music, or even the hum of its own power supply — there is a risk of acoustic feedback loops. The sculpture responds to sound with light, but if the sound source responds to the visual environment (as in some interactive audiovisual installations), a runaway oscillation could occur.

Even without a closed feedback loop, the sculpture's own electronics produce faint sounds:

- The LED driver [PWM](https://en.wikipedia.org/wiki/Pulse-width_modulation) frequency is nominally above the audible range (20kHz) but harmonics can descend into the high-frequency band
- The Crestboard's fan (when present) contributes a steady noise at ~4kHz
- The power supply emits a faint 50Hz hum

In a very quiet gallery, these self-generated sounds can be picked up by the MEMS microphone and create a subtle self-referential loop where the sculpture responds to its own electronic noise. In testing, this manifested as a very slow drift in the high-frequency shimmer parameter.

## Mitigation Strategies

- Use a fanless Crestboard configuration (with a passive heatsink case)
- Add a notch filter at the PWM frequency and its harmonics
- Implement a [noise gate](https://en.wikipedia.org/wiki/Noise_gate) that suppresses input below a calibrated noise floor
- For multi-artwork exhibitions, coordinate with other artists about acoustic interactions

This is not an urgent problem but could become significant in specific exhibition contexts.
