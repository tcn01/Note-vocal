import logging
import os
import uuid
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# =============================================
# Dịch vụ Text-to-Speech
# Dùng gTTS (Google Text-to-Speech free) để tạo
# file audio, lưu vào static/audio/.
# Fallback: nếu lỗi thì trả về None.
# =============================================

TTS_LANG_MAP = {
    "en": "en",
    "vi": "vi",
    "zh": "zh-CN",
    "ja": "ja",
    "ko": "ko",
}


class TTSService:
    """Tạo file audio phát âm từ vựng"""

    def __init__(self):
        self.settings = get_settings()
        self.audio_dir = Path(self.settings.AUDIO_DIR)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    async def generate_pronunciation(self, text: str, language: str) -> str | None:
        """Tạo file audio .mp3 cho từ/text, trả về URL path.
        
        Args:
            text: Nội dung cần đọc (từ vựng)
            language: Mã ngôn ngữ (vi/en/zh/ja/ko)
            
        Returns:
            URL path dạng /static/audio/{uuid}.mp3, hoặc None nếu lỗi
        """
        tts_lang = TTS_LANG_MAP.get(language, "en")
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = self.audio_dir / filename

        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            tts.save(str(filepath))
            logger.info("TTS generated: text=%s lang=%s path=%s", text, language, filename)
            return f"/static/audio/{filename}"
        except Exception as e:
            logger.warning("TTS failed for '%s' (%s): %s", text, language, e)
            return None


tts_service = TTSService()
