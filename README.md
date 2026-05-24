# 🤖 Bot de Download de Vídeos para Telegram

Um **bot de Telegram em Python 3.14** para baixar vídeos do **YouTube, Instagram e TikTok**, com suporte a arquivos grandes (>50MB) e logging de usuários. Projeto estruturado com `venv`, `requirements.txt` e boas práticas de desenvolvimento.

---

## 🛠️ Pré-requisitos
- **Python 3.14+**
- **FFmpeg** (necessário para conversão de formatos de vídeos e áudio)
  - **Linux (Debian/Ubuntu):** `sudo apt install ffmpeg`
  - **Fedora:** `sudo dnf install -y ffmpeg-free`
  - **MacOS:** `brew install ffmpeg`
  - **Windows:** Baixe em [ffmpeg.org](https://ffmpeg.org/) e adicione ao PATH
- **GCC e Python-devel** (para compilar tgcrypto - necessário para Pyrogram)
  - **Fedora:** `sudo dnf install -y gcc python3.14-devel`
  - **Debian/Ubuntu:** `sudo apt install -y gcc python3.14-dev`
- **Conta no Telegram** (para criar o bot via [BotFather](https://t.me/BotFather))
- **API ID e Hash** do [my.telegram.org](https://my.telegram.org) (obrigatório para suporte a arquivos >50MB)

---

## 🚀 Como Usar

### 1. Configuração Inicial
1. **Clone o repositório** (ou crie uma pasta local):
   ```bash
   git clone https://github.com/seu-usuario/video-downloader-bot.git
   cd video-downloader-bot
   ```

2. **Crie e ative o ambiente virtual**:
   ```bash
   python -m venv venv
   ```
   - **Linux/MacOS:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Crie um bot no Telegram**:
   - Abra o [BotFather](https://t.me/BotFather) no Telegram.
   - Digite `/newbot` e siga as instruções.
   - Copie o **token de API** gerado.

5. **Configure o arquivo `.env`**:
   Crie um arquivo `.env` na raiz do projeto e adicione:
   ```env
   BOT_TOKEN=SEU_TOKEN_DO_BOTFATHER
   TELEGRAM_API_ID=SEU_API_ID_DO_MY_TELEGRAM
   TELEGRAM_API_HASH=SEU_API_HASH_DO_MY_TELEGRAM
   ```
   > ⚠️ **Importante**: Para obter `API_ID` e `API_HASH`, acesse [my.telegram.org](https://my.telegram.org), vá em "API development tools" e crie um aplicativo.

6. **Crie o `.gitignore`** (opcional, para versionamento):
   ```txt
   venv/
   .env
   downloads/
   __pycache__/
   *.pyc
   ```

---

### 2. Executando o Bot
```bash
python main.py
```

### 3. Testando o Bot
1. Abra o **Telegram** e procure pelo nome do seu bot.
2. Inicie uma conversa e envie um link de vídeo do **YouTube, Instagram ou TikTok**.
3. O bot baixará o vídeo e o enviará de volta para você.

---

## 📂 Estrutura do Projeto
```
video-downloader-bot/
│
├── .env                  # Tokens e API keys (NÃO INCLUA NO GIT!)
├── .gitignore            # Arquivos a serem ignorados
├── main.py               # Código principal do bot
├── requirements.txt      # Dependências do projeto
├── downloads/            # Pasta para vídeos baixados (temporária)
├── bot_session.session   # Sessão Pyrogram (gerada automaticamente)
└── README.md             # Este arquivo
```

---

## 📦 Dependências (`requirements.txt`)
```txt
python-telegram-bot==22.7
yt-dlp
python-dotenv
pyrogram==2.0.106
tgcrypto
```

> ⚠️ **Nota**: O `tgcrypto` requer GCC e Python-devel para compilação. Veja pré-requisitos.

---

## 🔧 Funcionalidades

### 🎬 Download de Vídeos
✅ **YouTube**: Download em 1080p, 720p, MP3 320kbps ou FLAC
✅ **Instagram & TikTok**: Download otimizado com codecs H.264/AAC
✅ **Validação de URLs** (apenas links suportados são processados)
✅ **Tratamento de erros** (vídeos privados, links inválidos, etc.)
✅ **Armazenamento temporário** (arquivos são excluídos após o envio)

### 📊 Logging e Monitoramento
✅ **Logging de usuários**: Todas as requisições registram @username e ID do usuário
✅ **Logging de ações**: Comandos, URLs, callbacks e erros
✅ **Nível INFO**: Logs salvos no console e podem ser redirecionados para arquivo

### 📦 Suporte a Arquivos Grandes
✅ **≤ 50MB**: Enviados via Bot HTTP API (rápido)
✅ **50MB-2GB**: Enviados via Pyrogram/MTProto (sem limite de 50MB)
❌ **> 2GB**: Rejeitados (limite absoluto do Telegram)

---

## ⚠️ Observações Importantes
- **Vídeos privados ou restritos** não podem ser baixados.
- O bot **armazena arquivos temporariamente** na pasta `downloads/` e os exclui após o envio.
- Para vídeos do **Instagram/TikTok**, o **FFmpeg é obrigatório**.
- O bot **registra logs de usuários** para auditoria (username e ID do Telegram).
- Para arquivos **>50MB**, são necessárias as variáveis `TELEGRAM_API_ID` e `TELEGRAM_API_HASH`.
- O bot **não armazena dados pessoais** além do necessário para o funcionamento (logs de requisições).

---

## 📜 Comandos Disponíveis
| Comando       | Descrição                                  |
|---------------|--------------------------------------------|
| `/start`      | Inicia o bot e exibe instruções.           |
| `/help`       | Exibe a ajuda com exemplos de uso.         |

---

## 🔄 Possíveis Melhorias
- [x] **YouTube**: Menu inline para escolher qualidade (MP4 1080p/720p, MP3, FLAC)
- [x] **Logging de usuários**: Registra quem fez cada requisição
- [x] **Suporte a arquivos >50MB**: Via Pyrogram/MTProto
- [ ] Adicionar suporte a **mais plataformas** (Twitter/X, Facebook, etc.).
- [ ] **Compressão automática**: Reduzir tamanho de vídeos >50MB para enviar via Bot API
- [ ] **Download em segundo plano** para vídeos longos.
- [ ] **Autenticação de usuários** (restringir acesso a um grupo específico).
- [ ] **Interface web** (dashboard para gerenciar downloads).
- [ ] **Estatísticas**: Contador de downloads por usuário.

---

## 🐛 Solução de Problemas
| Problema                          | Solução                                                                 |
|-----------------------------------|--------------------------------------------------------------------------|
| **FFmpeg não encontrado**         | Instale o FFmpeg (veja pré-requisitos).                                |
| **Token inválido**                | Verifique se o `BOT_TOKEN` no `.env` está correto.                     |
| **API ID/Hash não configurados**   | Obtenha em [my.telegram.org](https://my.telegram.org) e adicione ao `.env`. |
| **Vídeo não baixado**             | O vídeo pode ser privado ou restrito. Tente outro link.                 |
| **Erro de permissão**             | Dê permissão de escrita à pasta `downloads/`.                          |
| **Bot não responde**              | Verifique se o bot está online (`python main.py`).                     |
| **tgcrypto build error**          | Instale GCC e Python-devel (veja pré-requisitos).                       |
| **Arquivo > 50MB não envia**      | Verifique se `TELEGRAM_API_ID` e `TELEGRAM_API_HASH` estão configurados. |
| **RuntimeError: no event loop**   | Use lazy import do pyrogram (veja código do main.py).                   |

---

## 📄 Arquivo `main.py`

O código completo está disponível no repositório. Aqui estão os destaques das implementações atuais:

### 🔑 Configuração de Variáveis de Ambiente
```python
# .env
BOT_TOKEN=seu_token_do_bot
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
```

### 📝 Logging de Usuários (em todos os handlers)
```python
user = update.message.from_user  # ou update.callback_query.from_user
logger.info(f"Usuário:@{user.username} (ID:{user.id}) - Ação: {...}")
```

### 📦 Envio de Arquivos (com suporte a >50MB)
```python
async def send_file(chat_id, file_path, format_name, caption, context):
    if file_path.stat().st_size <= 50 * 1024 * 1024:
        # Bot HTTP API (rápido, até 50MB)
        await context.bot.send_video(...)  # ou send_audio
    else:
        # MTProto via Pyrogram (50MB-2GB)
        pyro = await get_pyrogram()
        await pyro.send_video(...)  # ou send_audio
```

### 🔄 Lazy Import do Pyrogram (evita conflito de event loop)
```python
async def get_pyrogram():
    from pyrogram import Client as PyrogramClient  # Import dentro da função!
    global _pyrogram_client
    if _pyrogram_client is None or not _pyrogram_client.is_connected:
        _pyrogram_client = PyrogramClient(
            "bot_session",
            api_id=int(os.getenv("TELEGRAM_API_ID")),
            api_hash=os.getenv("TELEGRAM_API_HASH"),
            bot_token=os.getenv("BOT_TOKEN"),
        )
        await _pyrogram_client.start()
    return _pyrogram_client
```

> 📌 **Para ver o código completo**, consulte o arquivo [`main.py`](main.py) no repositório.

---
## 📌 Notas Finais
- Este projeto é **100% funcional** para uso pessoal.
- Para **deploy em produção**, considere:
  - Usar um **servidor VPS** (ex: DigitalOcean, AWS).
  - **Containerizar** o bot com Docker.
  - Adicionar **monitoramento** (ex: Prometheus, Sentry).

---
**💡 Dica:** Atualize o `yt-dlp` regularmente para suporte a novas plataformas:
```bash
pip install --upgrade yt-dlp
```

---
**📤 Compartilhe e melhore!** Este projeto é open-source. Sinta-se à vontade para contribuir ou adaptar conforme suas necessidades.
