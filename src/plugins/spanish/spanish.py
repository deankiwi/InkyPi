import logging
import random
import os
from datetime import datetime, date
from typing import Dict, Any, List, Tuple
from PIL import Image
from plugins.base_plugin.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class Spanish(BasePlugin):
    def __init__(self, config: Dict[str, Any], **dependencies):
        super().__init__(config, **dependencies)
        self.words_file = os.path.join(self.get_plugin_dir(), "words.txt")
        self.words: List[Tuple[str, str, str]] = self._load_words()

    def _load_words(self) -> List[Tuple[str, str, str]]:
        words = []
        if not os.path.exists(self.words_file):
            logger.error(f"Words file not found at {self.words_file}")
            return []
        
        try:
            with open(self.words_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('" "')
                    if len(parts) == 3:
                        # Clean up quotes
                        word = parts[0].strip('"')
                        meaning = parts[1].strip('"')
                        pronunciation = parts[2].strip('"')
                        words.append((word, meaning, pronunciation))
        except Exception as e:
            logger.error(f"Error loading words from {self.words_file}: {e}")
        
        return words

    def generate_image(self, settings: Dict[str, Any], device_config: Dict[str, Any]) -> Image.Image:
        logger.info(f"Spanish plugin settings: {settings}")
        
        # Determine available words based on progression settings
        available_word_count = len(self.words)
        base_limit = int(settings.get("wordLimit", 10))
        increment_daily = settings.get("incrementDaily") == "true"
        start_date_str = settings.get("startDate")
        
        effective_limit = base_limit
        
        if increment_daily and start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                days_passed = (date.today() - start_date).days
                if days_passed > 0:
                    effective_limit += days_passed
            except ValueError:
                logger.error(f"Invalid start date format: {start_date_str}")
                
        # Clamp effective limit
        effective_limit = max(1, min(effective_limit, available_word_count))
        
        # Select words to show
        num_words_to_show = int(settings.get("numWordsToShow", 1))
        # Ensure we don't try to show more words than available in the effective pool
        num_words_to_show = min(num_words_to_show, effective_limit)
        
        # Select random words from the *first* effective_limit words
        # This ensures we only show words "unlocked" by the day/limit
        available_pool = self.words[:effective_limit]
        selected_words = random.sample(available_pool, num_words_to_show)
        
        # Render
        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
            
        template_params = {
            "words": selected_words,
            "font_size": settings.get("fontSize", "medium"),
            "word_count_class": f"count-{num_words_to_show}"
        }
        
        return self.render_image(
            dimensions, 
            "index.html", 
            "style.css", 
            template_params
        )
