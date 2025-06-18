# Mandarin Pronunciation Checker

This tool helps check the accuracy of the pronunciation of Mandarin Chinese. It is built using Google's TTS (Text-to-Speech) API to generate Hanzi characters, the `xpinyin` Python library to show the pinyi annotations, and the public MyMemory API to return the English translation. The checker is currently implemented as a basic command line interface and using your device microphone for recording audio.

⚠️ This project is experimental and its performance dependends heavily on the underlying libraries.

## Requirements & Dependencies
- Python 3.x
- `uv`
- `pyaudio`
- `requests`
- `speechrecognition`
- `xpinyin`
- `chinesenumberutils`
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

## How to use

Once the program is running, you will be prompted to press enter to start recording your first pronunciation. You can then say the Mandarin phrase you want to check. The program will listen for your audio input until you press enter again to stop recording. After stopping the recording, the program will process your audio and return the Hanzi characters, pinyin annotations, and English translation of the phrase you pronounced.

https://github.com/user-attachments/assets/178036db-9667-481a-9547-eede54d755d6

### Use with flashcard applications

This tool is helpful when used alongside flashcard applications like Anki. Run program side by side with your flashcard app of choice.

<img width="1280" alt="anki" src="https://github.com/user-attachments/assets/17a7c464-94d4-44f6-a91c-3982aec29c9b" />


