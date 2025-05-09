# Upmify

**Upmify** is a command-line tool that converts Unity `.unitypackage` files into clean, modular [Unity Package Manager (UPM)](https://docs.unity3d.com/Manual/Packages.html)–compatible packages.

It automatically extracts asset contents, rebuilds the internal folder structure, adds assembly definitions (`.asmdef`), generates a `package.json`, and optionally initializes a Git repository for version control and reuse across projects.

---

## Features

- Extracts `.unitypackage` tarballs into clean folder structures
- Auto-generates `package.json` and UPM structure
- Creates optional `asmdef` files to isolate dependencies
- Initializes a Git repository (optional)
- Supports automation and CI workflows

---

## Installation

```bash
git clone https://github.com/midsbie/upmify.git
cd upmify
````

## Usage

### Basic CLI Usage

```bash
python upmify.py \
  /path/to/MyAsset.unitypackage \
  /path/to/output-dir \
  com.author.assetname \
  "My Asset Display Name"
```

### Optional Flags (coming soon)

* `--remote <git-url>`: Automatically adds a Git remote and pushes initial tag

---

## Example Use

```bash
python upmify.py \
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
    └── .git/  (optional Git repo initialized)
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
