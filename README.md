# Carta Sample Data — Kinetic Light Sculpture

Published at [carta-demo.joelstudler.ch](https://carta-demo.joelstudler.ch/)

Sample dataset for the [Carta](https://github.com/jstudler/carta) application. All content is fictional — names, institutions, places, and research findings are entirely made up.

The fictional project follows "John Doe," a sculptor at the Velderen Institute of Arts, exploring responsive light installations that react to environmental sensor data.

## Structure

Files are organized into one subdirectory per topic:

```
sample-data/
├── global/              # Abstract, conclusion, reflections
├── sensor-integration/  # Cards + media
├── projection-mapping/  # Cards + media
├── audience-interaction/# Cards + media
├── material-studies/    # Cards (markdown)
├── spatial-acoustics/   # Cards (markdown)
└── _generator/          # Media generation script
```

Within each directory:

- `<topic>_<date>.html/.md` — Content cards
- `<topic>_<date>--<suffix>.<ext>` — Sidecar media files referenced from cards

## Topics

| Topic | Cards | Description |
|---|---|---|
| `sensor-integration` | 6 | Environmental sensors and signal processing |
| `projection-mapping` | 6 | Mapping light onto sculptural forms |
| `audience-interaction` | 6 | Viewer behavior and exhibition observations |
| `material-studies` | 5 | Translucent materials for LED diffusion |
| `spatial-acoustics` | 5 | Sound-to-light mapping in gallery spaces |
| `general` | 6 | Abstract, conclusion, and reflections |

## Card Types

`abstract`, `introduction`, `normal`, `conclusion`, `reflection`, `imponderable`, `lookout`

## Categories

`research`, `experiment`, `documentation`, `studio-work`, `fabrication`, `correspondence`, `exhibition`

## Media

All media files are procedurally generated (no external assets) and can be regenerated via `_generator/`.

| Format | Count | Purpose |
|---|---|---|
| JPG | 10 | Abstract images (pictures) |
| MP4 | 2 | Short animated videos with audio |
| MP3 | 2 | Ambient audio clips |

## Regenerating Media

```sh
cd _generator
uv sync
uv run python generate.py
```

Requires [uv](https://docs.astral.sh/uv/) and [ffmpeg](https://ffmpeg.org/).

## License

See the main Carta repository for license information.
