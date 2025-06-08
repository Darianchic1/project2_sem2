import aiohttp
import asyncio
import json
import os
from datetime import datetime, timedelta
from googletrans import Translator
import logging

logger = logging.getLogger(__name__)

class SpoonacularAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.translator = Translator()
        self.cache_dir = "cache"
        # Создаем директорию для кэша если её нет
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_file(self, url: str, params: dict) -> str:
        """Генерирует имя файла кэша"""
        cache_key = f"{url}_{str(sorted(params.items()))}"
        filename = str(hash(cache_key)).replace('-', '') + '.json'
        return os.path.join(self.cache_dir, filename)

    def _get_cached_data(self, url: str, params: dict) -> dict:
        """Получает данные из кэша"""
        try:
            cache_file = self._get_cache_file(url, params)
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Проверяем срок действия кэша (1 час)
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=1):
                os.remove(cache_file)
                return None
            
            logger.info("Cache hit")
            return cache_data['data']
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    def _save_to_cache(self, url: str, params: dict, data: dict):
        """Сохраняет данные в кэш"""
        try:
            cache_file = self._get_cache_file(url, params)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.info("Data cached")
        except Exception as e:
            logger.error(f"Cache save error: {e}")

    async def get_random_recipe(self, diet: str = ""):
        url = "https://api.spoonacular.com/recipes/random"
        params = {
            "apiKey": self.api_key,
            "diet": diet if diet != "none" else None,
            "number": 1
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        # Проверяем кэш
        cached_data = self._get_cached_data(url, params)
        if cached_data:
            return cached_data.get("recipes", [{}])[0]
        
        # Делаем запрос к API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Сохраняем в кэш
                        self._save_to_cache(url, params, data)
                        return data.get("recipes", [{}])[0]
                    else:
                        logger.error(f"API returned status {response.status}")
                        return None
        except asyncio.TimeoutError:
            logger.error("Request timeout")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {e}")
            return None
        except Exception as e:
            logger.error(f"API Error: {e}")
            return None
    
    async def search_by_ingredients(self, ingredient: str):
        # Пробуем перевести ингредиент на английский
        try:
            ingredient_en = self.translator.translate(ingredient, src='ru', dest='en').text.lower()
            logger.info(f"Переведённый ингредиент: {ingredient} → {ingredient_en}")
        except Exception as e:
            logger.warning(f"Ошибка перевода '{ingredient}': {e}")
            ingredient_en = ingredient

        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "ingredients": ingredient_en,
            "number": 5,
            "apiKey": self.api_key,
            "ignorePantry": "true",
            "ranking": 2
        }
        
        # Проверяем кэш
        cached_data = self._get_cached_data(url, params)
        if cached_data:
            return sorted(cached_data, key=lambda x: -x.get('usedIngredientCount', 0))
        
        # Делаем запрос к API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Сохраняем в кэш
                        self._save_to_cache(url, params, data)
                        return sorted(data, key=lambda x: -x.get('usedIngredientCount', 0))
                    else:
                        logger.error(f"API returned status {response.status}")
                        return []
        except asyncio.TimeoutError:
            logger.error("Request timeout")
            return []
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {e}")
            return []
        except Exception as e:
            logger.error(f"API Error: {e}")
            return []