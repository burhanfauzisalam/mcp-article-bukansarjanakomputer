# Article Generator MCP Server

MCP server untuk membuat dan menerbitkan artikel blog Bukansarjanakomputer.

Endpoint publik yang diharapkan di Traefik:

```text
https://YOUR_DOMAIN/mcp-article-generator
```

Di backend container, endpoint MCP dijalankan pada `/`, lalu Traefik melakukan `StripPrefix(/mcp-article-generator)`.

## Tools

1. `get_last_article`
   Mengambil artikel terakhir dari API blog.

2. `generate_next_article`
   Membuat artikel berikutnya berdasarkan kategori artikel terakhir, lalu langsung menerbitkannya ke API blog.

3. `generate_article_by_topic`
   Membuat artikel berdasarkan topik yang diminta, otomatis memilih kategori dari `Web Development`, `SEO`, `IoT`, `DevOps`, atau `Automation`, lalu langsung menerbitkannya ke API blog.

4. `publish_next_article`
   Tool kompatibilitas lama untuk membuat artikel berikutnya lalu menerbitkannya ke API blog.

## Environment Variable

Lihat `.env.example`.

Variabel penting:

- `BASE_URL`: URL website/API blog.
- `API_KEY`: API key untuk endpoint blog.
- `GEMINI_API_KEY` atau `GEMINI_API_KEY1..4`: API key Gemini.
- `GEMINI_BASE_URL`: endpoint Gemini REST. Default contoh memakai `gemini-2.5-flash-lite`.
- `GEMINI_MAX_ATTEMPTS_PER_KEY`: jumlah retry per API key untuk status sementara seperti `429`.
- `GEMINI_RETRY_DELAY_SECONDS`: jeda awal retry Gemini dalam detik.
- `PORT`: port internal container, default `3000`.
- `MCP_ENDPOINT`: endpoint MCP internal container, default `/`.
- `HEALTH_PATH`: endpoint health, default `/healthz`.
- `MAIN_DOMAIN`: domain Traefik.

Jika Gemini mengembalikan `429`, semua key yang terbaca sedang terkena rate limit atau quota habis. Tambahkan key yang masih memiliki quota, tunggu quota reset, atau ganti `GEMINI_BASE_URL` ke model yang tersedia untuk akun/API key tersebut.

## Menjalankan Lokal

```powershell
copy .env.example .env
# edit .env sesuai environment

.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe server.py
```

URL lokal:

```text
http://127.0.0.1:3000/
```

Health check:

```text
http://127.0.0.1:3000/healthz
```

## Menjalankan Dengan Docker

```bash
cp .env.example .env
# edit .env sesuai environment

docker compose up -d --build
```

## Contoh Konfigurasi MCP Client

### Lokal

```toml
[mcp_servers.article_generator]
url = "http://127.0.0.1:3000/"
```

### Traefik

```toml
[mcp_servers.article_generator]
url = "https://YOUR_DOMAIN/mcp-article-generator"
```

## Contoh Tool Input

Generate dan publish artikel dengan topik tertentu:

```json
{
  "topic": "Cara deploy aplikasi Laravel dengan Docker dan Traefik"
}
```
