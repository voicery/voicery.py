"""
Python wrapper library for the Voicery text-to-speech (TTS) API.
"""
from collections import namedtuple

import requests

VOICERY_URL = "https://api.voicery.com"

Speaker = namedtuple("Speaker", "id name gender language styles default_style")
Style = namedtuple("Style", "id name")


class VoiceryError(Exception):
    """An exception raised by the Voicery API."""

    pass


class Voicery:
    """
    A handle to the Voicery API.
    """

    def __init__(self, key=None):
        """
        Create a new handle to the Voicery API.

        Arguments:
            - key:  An API key to use. By default, use no key.
                    API requests with no key will be heavily rate-limited.
        """
        self.key = key
        self.available_speakers = None

    def get_available_speakers(self):
        """
        Get a list of available speakers.
        """
        if self.available_speakers is not None:
            return self.available_speakers

        if self.key is None:
            headers = {}
        else:
            headers = {"Authorization": f"Bearer {self.key}"}

        result = requests.get(VOICERY_URL + "/speakers", headers=headers).json()

        self.available_speakers = {
            speaker["id"]: Speaker(
                id=speaker["id"],
                name=speaker["name"],
                gender=speaker["gender"],
                language=speaker["lang"],
                styles={
                    style["id"]: Style(id=style["id"], name=style["name"])
                    for style in speaker["styles"]
                },
                default_style=speaker["styles"][0]["id"],
            )
            for speaker in result
        }

        return self.available_speakers

    def stream(
        self,
        speaker,
        text,
        *,
        style=None,
        encoding="mp3",
        sample_rate=24000,
        ssml=False,
    ):
        """
        Issue a request to the Voicery API and stream the results.

        This should be used as a generator. For example:

            >>> client = voicery.Voicery(key="...")
            >>> with open("filename.wav", "wb") as handle:
            >>>     for chunk in client.stream(...):
            >>>         handle.write(chunks)
        """
        if isinstance(speaker, Speaker):
            speaker = speaker.id
        elif not isinstance(speaker, str):
            raise VoiceryError("Argument 'speaker' must be str or voicery.Speaker")

        if style is not None:
            if isinstance(style, Style):
                style = style.id
            elif not isinstance(style, str):
                raise VoiceryError("Argument 'style' must be str or voicery.Style")

        if encoding not in ["mp3", "wav", "pcm"]:
            raise VoiceryError("Argument 'encoding' must be one of 'mp3', 'wav', 'pcm'")

        if sample_rate not in [8000, 16000, 24000]:
            raise VoiceryError(
                "Argument 'sample_rate' must be one of 24000, 16000, 8000"
            )

        if self.key is None:
            headers = {}
        else:
            headers = {"Authorization": f"Bearer {self.key}"}

        data = {
            "text": text,
            "speaker": speaker,
            "encoding": encoding,
            "sampleRate": int(sample_rate),
            "ssml": bool(ssml),
        }
        if style is not None:
            data["style"] = style

        request = requests.post(
            VOICERY_URL + "/generate", stream=True, json=data, headers=headers
        )
        yield from request.iter_content(chunk_size=4 * 1024)

    def synthesize(self, speaker, text, *, output=None, **kwargs):
        """
        Issue a request to the Voicery API and collect the results.

        All parameters must be specified as keyword arguments.

        Required:
            - text: A string indicating the text of the request.
            - speaker: The speaker to use. Either a string ID or a Speaker object
                obtained via get_available_speakers().

        Optional:
            - style: What style to use for the spaker. (default varies by speaker)
            - ssml: Whether to parse request with SSML. (default: False)
            - encoding: Encoding for the output ("mp3", "wav", "pcm"). (default "mp3")
            - sample_rate: Output sample rate (8000, 16000, or default 24000).
            - output: Filename or handle to write output to.
                      If not provided, return content as a byte string.
        """
        data = b"".join(self.stream(speaker, text, **kwargs))
        if output is None:
            return data
        elif isinstance(output, str):
            with open(output, "wb") as handle:
                handle.write(data)
        else:
            output.write(data)

        return None
