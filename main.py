import pyaudio
import wave
import threading
import sys
import os
import tempfile
import speech_recognition as sr
import requests
import re
from xpinyin import Pinyin
from cnc import convert

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def replace_numbers_with_chinese(text, language="S", bigNumber=False, forceErLian="auto"):
    """
    Replace all Arabic numbers in Chinese text with their Chinese character equivalents.

    Args:
        text (str): The input text containing Arabic numbers
        language (str): "T" for Traditional or "S" for Simplified Chinese (default: "T")
        bigNumber (bool): Whether to use capital version of characters (default: False)
        forceErLian (str): "auto", "force", or "forceNot" for Er/Lian distinction (default: "auto")

    Returns:
        str: Text with Arabic numbers replaced by Chinese characters

    Examples:
        >>> replace_numbers_with_chinese("我36岁了")
        '我三十六岁了'

        >>> replace_numbers_with_chinese("他有25个苹果和100元钱")
        '他有二十五个苹果和一百元钱'

        >>> replace_numbers_with_chinese("房间号是1205", language="S")
        '房间号是一千二百零五'
    """

    def number_replacer(match):
        number_str = match.group()
        try:
            # Convert string to integer
            number = int(number_str)
            # Convert to Chinese using the cnc library
            chinese_number = convert.number2chinese(
                number,
                language=language,
                bigNumber=bigNumber,
                forceErLian=forceErLian
            )
            return chinese_number
        except (ValueError, TypeError):
            # If conversion fails, return original number
            return number_str

    # Use regex to find all sequences of digits
    # \d+ matches one or more consecutive digits
    result = re.sub(r'\d+', number_replacer, text)

    return result

class MandarinVoiceRecorder:
    def __init__(self):
        # Audio recording parameters
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.recording = False
        self.frames = []

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()

        # Initialize pinyin converter
        self.pinyin_converter = Pinyin()

    def show_header(self):
        """Display the application header"""
        print("🎯 Mandarin Pronunciation Checker")
        print("=" * 33)

    def start_recording(self):
        """Start recording audio"""
        print("🔴 Recording started")
        print("⏹️ Press ENTER to stop recording.")

        self.recording = True
        self.frames = []

        # Open audio stream
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        # Record audio in a separate thread
        def record():
            while self.recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                except Exception as e:
                    print(f"Recording error: {e}")
                    break

        record_thread = threading.Thread(target=record)
        record_thread.daemon = True
        record_thread.start()

        # Wait for user to press Enter
        input()

        # Stop recording
        self.recording = False
        record_thread.join(timeout=1)
        stream.stop_stream()
        stream.close()

        clear_screen()
        self.show_header()
        print("☑️ Recording stopped.")
        return self.save_audio()

    def save_audio(self):
        """Save recorded audio to a temporary WAV file"""
        if not self.frames:
            print("❌ No audio data recorded.")
            return None

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_filename = temp_file.name
        temp_file.close()

        # Save audio data
        try:
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))

            print("💾 Audio saved to temporary file.")
            return temp_filename

        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return None

    def get_translation_and_pinyin(self, chinese_text):
        """Get English translation and Pinyin for Chinese text"""
        if not chinese_text or chinese_text.lower().startswith(('could not', 'service error')):
            return None, None

        # Remove punctuation and extra spaces
        cleaned_text = re.sub(r'[^\u4e00-\u9fff\s]', '', chinese_text).strip()
        if not cleaned_text:
            return None, None

        print("🔄 Getting translation and pinyin...")

        try:
            # Get pinyin using xpinyin library with tone marks
            pinyin = self.pinyin_converter.get_pinyin(cleaned_text, tone_marks='marks', splitter=' ')

            # Get English translation
            translation = self.get_translation_mymemory(cleaned_text)

            return translation, pinyin

        except Exception as e:
            print(f"⚠️ Error getting pinyin/translation: {e}")
            return None, None

    def get_translation_mymemory(self, text):
        """Get English translation using MyMemory API (free)"""
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': 'zh|en'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('responseStatus') == 200:
                translation = data['responseData']['translatedText']
                # Clean up the translation
                if translation and not translation.startswith('MYMEMORY WARNING'):
                    return translation

            return None

        except Exception as e:
            print(f"⚠️ Translation API error: {e}")
            return None

    def recognize_mandarin(self, audio_file):
        """Convert Mandarin speech to Hanzi characters"""
        if not audio_file or not os.path.exists(audio_file):
            print("❌ Audio file not found.")
            return None

        try:
            print("🔄 Processing speech recognition...")

            # Load audio file
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record audio data
                audio_data = self.recognizer.record(source)

            # Try multiple recognition services for better accuracy
            results = []

            # Method 1: Google Speech Recognition (supports Chinese)
            try:
                text = self.recognizer.recognize_google(
                    audio_data,
                    language='zh-CN'  # Simplified Chinese
                )
                formatted_text = replace_numbers_with_chinese(text)
                results.append(('Simplified: ', formatted_text))
            except sr.UnknownValueError:
                results.append(('Google', 'Could not understand audio'))
            except sr.RequestError as e:
                results.append(('Google', f'Service error: {e}'))

            # Method 2: Try Traditional Chinese as backup
            try:
                text_trad = self.recognizer.recognize_google(
                    audio_data,
                    language='zh-TW' # Traditional Chinese
                )
                results.append(('Traditional: ', text_trad))
            except sr.UnknownValueError:
                pass

            return results

        except Exception as e:
            print(f"❌ Recognition error: {e}")
            return None

        finally:
            try:
                os.unlink(audio_file)
            except OSError:
                pass

    def wait_for_continue(self):
        """Wait for user to press Enter before continuing"""
        print("=" * 33)
        print("▶️ Press ENTER to continue...")
        input()

    def run(self):
        """Main application loop"""
        try:
            while True:
                # Clear screen and show header
                clear_screen()
                self.show_header()

                print("▶️ Press ENTER to start recording")
                user_input = input().strip().lower()

                if user_input == 'q':
                    clear_screen()
                    print("👋 Goodbye!")
                    break

                # Clear screen for recording session
                clear_screen()
                self.show_header()

                # Start recording
                audio_file = self.start_recording()

                if audio_file:
                    # Recognize speech
                    results = self.recognize_mandarin(audio_file)

                    if results:
                        # print("\n📝 Recognition Results:")
                        # print("─" * 40)
                        # for service, text in results:
                        #     print(f"{service}: {text}")

                        # Get the best resultf
                        best_result = next((text for service, text in results
                                          if 'error' not in text.lower() and
                                             'could not' not in text.lower()), None)

                        if best_result:
                            print("=" * 33)
                            print(f"✨ Hanzi: {best_result}")

                            # Get translation and pinyin
                            translation, pinyin = self.get_translation_and_pinyin(best_result)

                            if pinyin:
                                print(f"🔤 Pinyin: {pinyin}")
                            else:
                                print("🔤 Pinyin: (unavailable)")

                            if translation:
                                print(f"🌍 English: {translation}")
                            else:
                                print("🌍 English: (translation unavailable)")

                        else:
                            print("\n❌ No clear recognition result obtained.")
                    else:
                        print("\n❌ Speech recognition failed.")

                # Wait for user before continuing
                self.wait_for_continue()

        except KeyboardInterrupt:
            clear_screen()
            print("👋 Application interrupted. Goodbye!")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()

def check_dependencies():
    """Check if required libraries are installed"""
    required_libs = {
        'pyaudio': 'PyAudio',
        'speech_recognition': 'SpeechRecognition',
        'requests': 'requests'
    }

    missing = []
    for lib, name in required_libs.items():
        try:
            __import__(lib)
        except ImportError:
            missing.append(name)

    if missing:
        print("❌ Missing required libraries:")
        for lib in missing:
            print(f"   - {lib}")
        print("\nInstall them with:")
        print("pip install pyaudio SpeechRecognition requests")
        print("\nNote: On some systems, you may need to install PortAudio first:")
        print("- macOS: brew install portaudio")
        print("- Ubuntu/Debian: sudo apt-get install portaudio19-dev")
        print("- Windows: Usually included with PyAudio")
        return False

    return True

def main():
    if not check_dependencies():
        sys.exit(1)

    try:
        recorder = MandarinVoiceRecorder()
        recorder.run()
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()