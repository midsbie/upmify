# Upmify

**Upmify** is a command-line tool that converts Unity `.unitypackage` files into clean, modular [Unity Package Manager (UPM)](https://docs.unity3d.com/Manual/Packages.html)–compatible packages.

It automatically extracts asset contents, rebuilds the internal folder structure, adds assembly definitions (`.asmdef`), generates a `package.json`, and optionally initializes a Git repository for version control and reuse across projects.

## Features

- Extracts `.unitypackage` tarballs into clean folder structures
- Auto-generates `package.json` and UPM structure
- Creates optional `asmdef` files to isolate dependencies
- Initializes a Git repository (optional)
- Supports automation and CI workflows

## Installation

```bash
git clone https://github.com/midsbie/upmify.git
cd upmify
make setup
```

## Usage

### Basic CLI Usage

```bash
python -m upmify.cmd \
  /path/to/MyAsset.unitypackage \
  /path/to/output-dir \
  com.author.assetname \
  "My Asset Display Name"
```

### Supported Flags

* `-g`, `--git-init`
  Initialize a Git repository in the generated package directory and create an initial commit.

* `--lfs`
  After `--git-init`, enable Git LFS by adding a `.gitattributes` file and running `git lfs install --local`.

* `-f`, `--force`
  Overwrite the output package directory if it already exists.

* `-v`, `--verbose`
  Enable detailed logging output (debug-level messages).

* `-q`, `--quiet`
  Suppress most logging output (warnings and errors only).


## Example Use

```bash
python -m upmify.cmd \
  -g \
  "$HOME/.local/share/unity3d/Asset Store-5.x/Some Publisher/Tools/My Cool Asset.unitypackage" \
  ./WrappedPackages \
  com.author.coolasset \
  "Cool Asset"
```

Creates:

```
WrappedPackages/
└── com.mygame.coolasset/
    ├── package.json
    ├── Runtime/
    │   └── ...extracted content...
    ├── Runtime/CoolAsset.asmdef
    └── .git/
    └── .gitignore
```

Then add it to any Unity project via `manifest.json`:

```json
"com.mygame.coolasset": "file:../WrappedPackages/com.mygame.coolasset"
```

---

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. All contributions are greatly appreciated!

---

## License

Distributed under the MIT License.
See [`LICENSE`](./LICENSE) for more information.
