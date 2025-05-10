# Upmify

Upmify is a command-line tool that converts Unity `.unitypackage` files into clean, modular [Unity Package Manager (UPM)](https://docs.unity3d.com/Manual/Packages.html)–compatible packages.

It extracts asset contents, rebuilds the internal folder structure, adds assembly definitions (.asmdef), generates a package.json (including any declared dependencies), and optionally initializes a Git repository for version control and reuse across projects.

## Features

* Extracts `.unitypackage` tarballs into clean folder structures
* Auto-generates `package.json` and UPM structure, integrating any declared dependencies in the
  package's manifest.json file
* Creates `.asmdef` files to isolate assets in Unity
* Initializes a Git repository (optional)
* Supports Git LFS (optional)

## Installation

```bash
git clone https://github.com/midsbie/upmify.git
cd upmify
make setup
```

## Usage

### Basic CLI Example

```bash
python -m upmify.cmd \
  /path/to/MyAsset.unitypackage \
  --output-dir ./WrappedPackages \
  --package-name com.author.assetname \
  --display-name "My Asset Display Name" \
  --assembly-name Author.AssetName
```

### Additional Options

| Flag                  | Description                                                      |
|-----------------------|------------------------------------------------------------------|
| `-o, --output-dir`    | Directory where the UPM-style package will be created (required) |
| `-p, --package-name`  | UPM package name, e.g., `com.company.assetname` (required)       |
| `-d, --display-name`  | Human-readable display name shown in Unity (required)            |
| `-a, --assembly-name` | C# assembly name for the generated `.asmdef` file (required)     |
| `--package-version`   | Set the package version                                          |
| `--unity-version`     | Minimum Unity version required                                   |
| `-g, --git-init`      | Initialize a Git repo in the package folder                      |
| `--lfs`               | Enable Git LFS and add `.gitattributes` (requires `--git-init`)  |
| `-f, --force`         | Overwrite existing output directory                              |
| `-v, --verbose`       | Enable debug logging                                             |
| `-q, --quiet`         | Suppress most output                                             |

## Example: Full Command

```bash
python -m upmify.cmd \
  "$HOME/.local/share/unity3d/Asset Store-5.x/Some Publisher/Tools/Cool Asset.unitypackage" \
  --output-dir ./WrappedPackages \
  --package-name com.author.coolasset \
  --display-name "Cool Asset" \
  --assembly-name Author.CoolAsset \
  --package-version 2.1.0 \
  --unity-version 2022.3 \
  --git-init \
  --lfs \
  --force
```

### Resulting Structure

```
WrappedPackages/
└── com.author.coolasset/
    ├── package.json
    ├── Runtime/
    │   ├── ...extracted asset files...
    │   └── Author.CoolAsset.asmdef
    ├── .git/
    └── .gitignore
```

### Adding to `manifest.json` in a Unity project:

```json
"com.author.coolasset": "file:../WrappedPackages/com.author.coolasset"
```

## Contributing

Pull requests, issues, and feature suggestions are welcome!

## License

Distributed under the MIT License.
See [`LICENSE`](./LICENSE) for more details.
