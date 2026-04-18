import config

if config.VOICE_SERVICE == "elevenlabs":
    from services.elevenlabs_service import (
        extract_voice_text,
        generate_voice,
        generate_voice_from_script,
        test_voices,
        AVAILABLE_VOICES
    )

elif config.VOICE_SERVICE == "silero":
    from services.silero_service import (
        extract_voice_text,
        generate_voice,
        generate_voice_from_script,
        test_voices,
        AVAILABLE_VOICES
    )

else:  # openai (по умолчанию)
    from services.openai_voice_service import (
        extract_voice_text,
        generate_voice,
        generate_voice_from_script,
        test_voices,
        AVAILABLE_VOICES
    )

__all__ = [
    "extract_voice_text",
    "generate_voice", 
    "generate_voice_from_script",
    "test_voices",
    "AVAILABLE_VOICES"
]