# Article Generator MCP Server

MCP server untuk mencari referensi web terbaru, membuat, dan menerbitkan artikel blog Bukansarjanakomputer.

Endpoint publik yang diharapkan di Traefik:

```text
https://YOUR_DOMAIN/mcp-article-generator
```

Di backend container, endpoint MCP dijalankan pada `/`, lalu Traefik melakukan `StripPrefix(/mcp-article-generator)`.

## Tools

1. `get_last_article`
   Mengambil artikel terakhir dari API blog.

2. `generate_next_article`
   Mengambil kategori artikel terakhir, mencari referensi web terbaru untuk kategori berikutnya, membuat artikel, lalu langsung menerbitkannya ke API blog.

3. `generate_article_by_topic`
   Membuat artikel berdasarkan topik yang diminta, otomatis memilih kategori dari `Web Development`, `SEO`, `IoT`, `DevOps`, atau `Automation`, mencari referensi web terbaru untuk topik tersebut, lalu langsung menerbitkannya ke API blog.

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
- `WEB_RESEARCH_ENABLED`: aktif/nonaktifkan pencarian referensi web sebelum generate artikel.
- `WEB_RESEARCH_REQUIRED`: jika `true`, proses generate gagal ketika pencarian referensi gagal. Jika `false`, generate tetap berjalan tanpa referensi.
- `WEB_RESEARCH_PROVIDER`: provider search. Saat ini mendukung `tavily`.
- `WEB_RESEARCH_MAX_RESULTS`: jumlah maksimal referensi web yang dikirim ke prompt.
- `WEB_RESEARCH_TIME_RANGE`: rentang waktu referensi Tavily, misalnya `day`, `week`, `month`, atau `year`.
- `WEB_RESEARCH_SEARCH_DEPTH`: kedalaman search Tavily, misalnya `basic`, `fast`, `advanced`, atau `ultra-fast`.
- `WEB_RESEARCH_COUNTRY`: opsional, boost hasil dari negara tertentu sesuai daftar Tavily, misalnya `indonesia`. Kosongkan untuk hasil global.
- `WEB_RESEARCH_EXCLUDE_DOMAINS`: daftar domain yang dikecualikan dari referensi, dipisahkan koma.
- `TAVILY_API_KEY`: API key Tavily untuk produksi. Jika kosong, server mencoba mode keyless Tavily yang rate limited.
- `PORT`: port internal container, default `3000`.
- `MCP_ENDPOINT`: endpoint MCP internal container, default `/`.
- `HEALTH_PATH`: endpoint health, default `/healthz`.
- `MAIN_DOMAIN`: domain Traefik.

Jika Gemini mengembalikan `429`, semua key yang terbaca sedang terkena rate limit atau quota habis. Tambahkan key yang masih memiliki quota, tunggu quota reset, atau ganti `GEMINI_BASE_URL` ke model yang tersedia untuk akun/API key tersebut.

## Riset Web Sebelum Generate

Sebelum artikel dibuat, tool generate akan mencari referensi web terbaru memakai Tavily. Referensi ini hanya dipakai sebagai konteks prompt Gemini dan dikembalikan di response MCP pada field `web_research`. Payload artikel yang dikirim ke API blog tetap berisi data artikel utama, sehingga endpoint blog tidak perlu menerima field sumber tambahan.

Jika ingin mematikan riset web:

```env
WEB_RESEARCH_ENABLED=false
```

Jika ingin proses generate berhenti ketika riset web gagal:

```env
WEB_RESEARCH_REQUIRED=true
```

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

## Cron Generate Harian

Cron tidak perlu memanggil protokol MCP. Gunakan script CLI yang memakai logic yang sama dengan tool `generate_next_article`, yaitu generate artikel lalu langsung publish.

Tes manual di server Docker:

```bash
cd /path/to/article-generator
docker compose exec -T mcp-article-generator python scripts/generate_next_article.py
```

Crontab host Linux untuk menjalankan setiap hari jam 06:00:

```cron
0 6 * * * cd /path/to/article-generator && docker compose exec -T mcp-article-generator python scripts/generate_next_article.py >> logs/cron.log 2>&1
```

Jika menjalankan tanpa Docker:

```cron
0 6 * * * cd /path/to/article-generator && /path/to/venv/bin/python scripts/generate_next_article.py >> logs/cron.log 2>&1
```

Pastikan timezone server sudah sesuai. Jika memakai Docker Compose, container `mcp-article-generator` harus sedang berjalan saat cron dieksekusi.

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
