import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Caminho para a pasta de downloads
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Plataformas suportadas
SUPPORTED_PLATFORMS = ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /start."""
    await update.message.reply_text(
        "🎬 **Bot de Download de Vídeos**\n\n"
        "Envie um link de vídeo do **YouTube, Instagram ou TikTok** que eu baixo para você!\n\n"
        "Exemplo: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`"
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /help."""
    await update.message.reply_text(
        "📚 **Ajuda do Bot de Download de Vídeos**\n\n"
        "🔹 **Comandos disponíveis:**\n"
        "/start - Inicia o bot\n"
        "/help - Exibe esta ajuda\n\n"
        "🔹 **Como usar:**\n"
        "1. Envie um link de vídeo do YouTube, Instagram ou TikTok.\n"
        "2. Aguarde o download e o envio do vídeo.\n\n"
        "⚠️ **Observações:**\n"
        "- Vídeos privados ou restritos não podem ser baixados.\n"
        "- O bot armazena os vídeos temporariamente e os exclui após o envio."
    )



async def download_video(url: str, platform: str) -> Path | None:
    """Baixa um vídeo usando yt-dlp e retorna o caminho do arquivo."""
    try:
        ydl_opts = {
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 90,
            "retries": 3,
            "cookiefile": str(Path.home() / ".yt-dlp-cookies.txt"),
            "extractor_args": {"youtube": {"player_client": ["android", "tv"]}},
        }

        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return Path(filename)
    except Exception as e:
        logger.error(f"Erro ao baixar vídeo de {platform}: {e}")
        return None

async def process_video_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa links de vídeos enviados pelo usuário."""
    url = update.message.text.strip()

    if not any(platform in url for platform in SUPPORTED_PLATFORMS):
        await update.message.reply_text(
            "❌ **URL inválida!**\n"
            "Envie um link válido do **YouTube, Instagram ou TikTok**."
        )
        return

    await update.message.reply_text("⏳ **Baixando vídeo...** Aguarde um momento.")

    platform = (
        "YouTube" if "youtube.com" in url or "youtu.be" in url else
        "Instagram" if "instagram.com" in url else
        "TikTok"
    )

    video_path = await download_video(url, platform)
    if not video_path or not video_path.exists():
        await update.message.reply_text(
            f"❌ **Falha ao baixar o vídeo do {platform}!**\n"
            "Verifique se o link está correto e se o vídeo é público."
        )
        return

    try:
        # Verifica tamanho do vídeo (Telegram tem limite de 50MB para bots)
        file_size = video_path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50MB
            await update.message.reply_text(
                f"❌ **Vídeo muito grande!**\n"
                f"Tamanho: {file_size / (1024*1024):.1f} MB\n"
                "O Telegram tem limite de 50MB para envio de vídeos por bots."
            )
            video_path.unlink(missing_ok=True)
            return

        with open(video_path, "rb") as video_file:
            await update.message.reply_video(
                video=InputFile(video_file, filename=video_path.name),
                caption=f"🎥 **Vídeo baixado do {platform}:**\n{url}",
                write_timeout=300,
                read_timeout=300
            )
        video_path.unlink(missing_ok=True)
    except Exception as e:
        logger.error(f"Erro ao enviar vídeo: {e}")
        await update.message.reply_text(
            "❌ **Falha ao enviar o vídeo!** Tente novamente mais tarde."
        )
        if video_path.exists():
            video_path.unlink()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para erros gerais."""
    logger.error(f"Erro em {update}: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "⚠️ **Ocorreu um erro inesperado!** Tente novamente mais tarde."
        )

def main() -> None:
    """Função principal para iniciar o bot."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("Token do bot não encontrado no .env!")
        return

    from telegram.request import HTTPXRequest
    request = HTTPXRequest(
        read_timeout=300,
        write_timeout=300,
        connect_timeout=30,
        pool_timeout=30,
    )
    app = Application.builder().token(token).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_video_link))
    app.add_error_handler(error_handler)

    logger.info("Bot iniciado com sucesso!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
