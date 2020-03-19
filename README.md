# Python Voicery API

Voicery provides a text-to-speech engine accessible via an easy-to-use REST API in the
cloud. This repository provides some starter Python code that you can include in your
project to quickly and easily synthesize speech using the Voicery speech synthesis
engine, without worrying about the details of HTTP requests and encodings.

## Example Usage
The following example code can be used to query the Voicery API: 
```
# Import this library.
import voicery

# Create a new client.
#
# If you have a Voicery account and have created an API key, provide it.
# Otherwise, you can remove the 'key=...' argument, and you will still be able to make
# requests, but they will be heavily rate-limited.
client = voicery.Voicery(key="ASDF-QWERTY-12345")

# Get a list of available speakers.
for speaker, description in client.get_available_speakers().items():
    print("Speaker:", speaker)
    print("\tGender:", description.gender)
    print("\tStyles:", ", ".join(description.styles))
    print()

# Choose one of the available speakers.
speaker, style = "steven", "narration"

# Synthesize a WAV file and write it to disk immediately.
client.synthesize(speaker, "Hello!", style=style, output="test.wav", encoding="wav")

# Synthesize an MP3 file and write it to disk immediately via a handle.
with open("test.mp3", "wb") as handle:
    client.synthesize(speaker, "Hello!", style=style, output=handle, encoding="mp3")

# Synthesize an MP3 file and stream it to disk.
with open("streamed.mp3", "wb") as handle:
    for chunk in client.stream(speaker, "Hello!", style=style):
        handle.write(chunk)
```

More information can be found on the [Voicery API documentation](https://www.voicery.com/docs).

Most notably, `stream` and `synthesize` accept the following arguments:

```
Required:
    - text: A string indicating the text of the request.
    - speaker: The speaker to use. Either a string ID or a Speaker object
        obtained via get_available_speakers().

Optional:
    - style: What style to use for the spaker. (default varies by speaker)
    - ssml: Whether to parse request with SSML. (default: False)
    - encoding: Encoding for the output ("mp3", "wav", "pcm"). (default "mp3")
    - sample_rate: Output sample rate (8000, 16000, or default 24000).

Only for synthesize(), not stream():
    - output: Filename or handle to write output to.
              If not provided, return content as a byte string.
```

## Including this in your project

1. Ensure that your `requirements.txt` includes all of the packages in [requirements.txt](https://github.com/voicery/voicery.py/blob/master/requirements.txt). If you don't have a `requirements.txt`, make sure all the requirements are installed by running `pip install -r requirements.txt` to install them.
2. Copy the Python files from this repository into a place you can import them.
