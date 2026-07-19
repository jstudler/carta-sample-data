---
title: Frequency-Band Light Mapping
date: 2025-07-10
topic: spatial-acoustics
category: experiment
type: normal
width: 2
---

Developed a new mapping approach that splits the microphone input into four frequency bands and assigns each to a different aspect of the light behavior:

| Frequency Band | Range | Light Parameter |
|---|---|---|
| Sub-bass | 20–100 Hz | Overall brightness pulsation |
| Low-mid | 100–500 Hz | Color temperature (warm ↔ cool) |
| Mid | 500–2000 Hz | Spatial spread of the glow |
| High | 2000–10000 Hz | Shimmer / rapid micro-variations |

This creates a much richer sound-to-light relationship than the previous single-channel approach. Low rumbles (HVAC, traffic) produce slow, warm pulses. Voices activate the color temperature and spatial spread. High-frequency sounds (keys jangling, heels on hardwood) create a delicate shimmer.

The mapping feels surprisingly intuitive — several test viewers described the correspondence as "natural" without being told how it works. This aligns with research on [crossmodal correspondences](https://en.wikipedia.org/wiki/Crossmodal_correspondence) suggesting that low frequencies are perceptually associated with warmth and large spatial extent, while high frequencies map to brightness and small spatial detail.

## Technical Implementation

The frequency splitting is done with four second-order bandpass filters running on the Crestboard. CPU load is minimal (~3%). Each band feeds into the existing exponential moving average pipeline with independently tuned time constants.
