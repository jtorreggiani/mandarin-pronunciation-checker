# Mandarin Pronunciation Checker

This tool helps check the accuracy of the pronunciation of Mandarin Chinese. It is build using Google's TTS (Text-to-Speech) API to generate Hanzi characters, the `xpinyin` Python library to show the pinyi annotations, and the public MyMemory API to return the English translation.

## Requirements & Dependencies
- Python 3.x
- uv
- pyaudio
- requests
- speechrecognition
- xpinyin
- [MyMemory API](https://mymemory.translated.net/doc/)

Note this has only been tested on MacOS.

## Environment Setup

1. Create a virtual environment using uv

```bash
uv venv python-env
```

2. Activate the virtual environment

```bash
source venv/bin/activate
```

3. Install the required packages

```bash
uv sync
```

4.  Install `pyaudio` if not already installed. You can use Homebrew on MacOS:

```bash
brew install portaudio
```

5. Start the program

```bash
./start
```
