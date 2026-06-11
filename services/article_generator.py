from google import genai
from datetime import date
import json
from config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_article(category: str):
    prompt = f'''
Buat artikel blog teknologi profesional.
Kategori: {category}
Persyaratan:
- Bahasa Indonesia
- Minimal 700 kata
- SEO Friendly
- HTML Full
- Gunakan tag h2 dan h3
- Jangan gunakan markdown

Output HARUS JSON valid:
{{
  "title": "",
  "category": "{category}",
  "excerpt": "",
  "content": ""
}}
'''
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt
    )

    text = response.text.replace("```json", "").replace("```", "").strip()
    article = json.loads(text)
    article["published_at"] = str(date.today())
    return article
