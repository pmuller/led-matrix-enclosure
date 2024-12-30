# LED Matrix Enclosure Generator

A Python tool to generate 3D printable enclosures for LED matrix panels.
Built with [build123d](https://github.com/gumyr/build123d).

## Disclaimer

This project is a work in progress.
While it satisfies my own requirements,
it might not be suitable for your specific needs.
Feel free to fork and modify it to your needs.

## Features

- Supports multiple [LED matrix panel](https://www.aliexpress.com/item/4001296811800.html)
  sizes (8x8, 16x16, 32x8)
- Modular design allowing multiple panels to be connected together
- Customizable grid and diffuser for even light distribution
- Wire management slots for clean cable routing
- Robust mounting system with support pillars and borders
- Configurable parameters for fine-tuning the design

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- VSCode and the
  [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer/tree/main)
  extension

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/pmuller/led-matrix-enclosure.git
# 2. First cd into the cloned directory
cd led-matrix-enclosure
# 3. Then sync dependencies
uv pip sync
# 4. Source the virtual environment
. .venv/bin/activate
```

## Usage

The tool provides a CLI to generate enclosure models:

```bash
led-matrix-enclosure 16x16,16x16 32x8 --enclosure-layout 2x1
```

This will generate an enclosure for two 16x16 LED matrices arranged horizontally on the 1st row,
and a 32x8 LED matrix on the 2nd row.

### Key Parameters

- LED Matrix Layout: Specify panel sizes and arrangement (e.g. "16x16,16x16" for two 16x16 panels)
- Enclosure Layout: Define how to split the enclosure into modules (e.g. "2x1" for 2 horizontal modules)
- Border Options: Customize border thickness, radius, and support ledge size
- Grid Options: Configure grid line heights and spacing
- Diffuser Options: Set diffuser thickness and margins
- Pillar Options: Adjust support pillar dimensions and spacing

Run with `--help` to see all available options.

## Output

The tool generates assets in the `build/` directory:

- STL files for the chassis components
- STEP files for the lid components (grid + diffuser)

The output files can be directly used with a 3D printer slicer.

## Splitting the enclosure as separate parts

In case you want to print an enclosure that is bigger than your printer bed,
you can split the enclosure into multiple parts using the `--enclosure-layout` option.

For example, to split the enclosure into 2 horizontal parts, you can run:

```bash
led-matrix-enclosure 16x16,16x16 32x8 --enclosure-layout 2x1
```

This will generate 2 STL files in the `build/` directory:

- `module:x=0,y=0.chassis.stl`
- `module:x=0,y=0.lid.step`
- `module:x=160,y=0.chassis.stl`
- `module:x=160,y=0.lid.step`

You can then print each part separately and assemble them together using M3 screws and nuts.

## Development

1. Follow the [Installation](#installation) section to set up the development environment.
2. Run tests:

    ```bash
    pytest -vvv
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with [build123d](https://github.com/gumyr/build123d) - An awesome Python CAD library.
