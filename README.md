# 📦 flake8-no-emoji

![PyPI version](https://img.shields.io/pypi/v/flake8-no-emoji.svg)
![Downloads](https://pepy.tech/badge/flake8-no-emoji)
![License](https://img.shields.io/pypi/l/flake8-no-emoji.svg)

**Flake8 plugin that detects and reports any emoji characters in Python source code.**
Helps keep your codebase clean, consistent, and free from unwanted Unicode emojis.

---

## ✨ Features

**Note:** Do not set the same category in both `--ignore-emoji-types` and `--only-emoji-types`, as `only` takes precedence.

* Scans Python files for **all Unicode emoji characters** (including multi-codepoint clusters).
* Raises a linting error (`EMO001`) when emojis are found.
* Supports filtering by **emoji categories**:

    * `--ignore-emoji-types=PEOPLE,FOOD`
    * `--only-emoji-types=FLAGS`
* Works seamlessly with **Flake8** and **pre-commit hooks**.
* Lightweight and dependency-minimal (`regex` and `emoji` required).

---

## 📥 Installation

```bash
pip install flake8-no-emoji
```

---

## 🚀 Usage

Run normally via `flake8`:

```bash
flake8 your_code/
```

Example output:

```
your_code/example.py:3:10: EMO001 Emoji detected in code
```

---

## ⚙️ Configuration

You can configure categories to **ignore** or **allow exclusively**.

### Ignore certain categories

```bash
flake8 --ignore-emoji-types=PEOPLE,FOOD
```

This ignores emojis in the `PEOPLE` and `FOOD` categories, but still reports others.

### Allow only specific categories

```bash
flake8 --only-emoji-types=FLAGS
```

This only reports `FLAGS` emojis, ignoring everything else.
(**Note:** `only` takes precedence over `ignore`.)

---

## 🧩 Example (with pre-commit)

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/AlgorithmAlchemy/flake8-no-emoji
    rev: v0.2.2
    hooks:
      - id: flake8
        additional_dependencies: [flake8-no-emoji]
```

Run:

```bash
pre-commit run --all-files
```

---

## 📂 Categories Supported

* **PEOPLE** 👩 👨 😀
* **NATURE** 🌳 🐶 🌸
* **FOOD** 🍕 🍔 🍎
* **ACTIVITY** ⚽ 🎮 🎭
* **TRAVEL** ✈️ 🚗 🚀
* **OBJECTS** 💻 📱 📚
* **SYMBOLS** ❤️ ☮️ ✔️
* **FLAGS** 🇺🇸 🇯🇵 🏳️‍🌈
* **OTHER** (fallback if no match)

---

## 📝 Error Codes

* **EMO001** — Emoji detected in code.

---

## 🔧 Development

Clone and install in editable mode:

```bash
git clone https://github.com/AlgorithmAlchemy/flake8-no-emoji
cd flake8-no-emoji
pip install -e .[dev]
pytest
```

---

## 📜 License

MIT License © 2025 [AlgorithmAlchemy](https://github.com/AlgorithmAlchemy)
