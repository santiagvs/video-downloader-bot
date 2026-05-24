import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
import yt_dlp
import subprocess

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

SUPPORTED_PLATFORMS = ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]


def get_yt_dlp_opts(height=1080, platform="youtube"):
    """Retorna opções do yt-dlp com a altura especificada e otimizado por plataforma."""
    if platform == "youtube":
        format_str = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
    elif platform == "instagram":
        format_str = "best[ext=mp4][vcodec^=avc1][acodec^=aac][height>=720]/best[ext=mp4][vcodec^=avc1][acodec^=aac]/best[ext=mp4]"
    elif platform == "tiktok":
        format_str = "best[ext=mp4][vcodec^=avc1][acodec^=aac][height>=720]/best[ext=mp4][vcodec^=avc1][acodec^=aac]/best[ext=mp4]"
    else:
        format_str = "best[ext=mp4][vcodec^=avc1][acodec^=aac]/best[ext=mp4]/best"
    
    return {
        "format": format_str,
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 90,
        "retries": 3,
        "cookiefile": str(Path.home() / ".yt-dlp-cookies.txt"),
        "extractor_args": {"youtube": {"player_client": ["android", "tv"]}},
    }


def convert_to_mp3(video_path: Path) -> Path:
    """Converte vídeo para MP3 usando ffmpeg."""
    try:
        mp3_path = video_path.with_suffix(".mp3")
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vn", "-c:a", "libmp3lame", "-q:a", "0",  # 320kbps VBR
            str(mp3_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
        return mp3_path
    except Exception as e:
        logger.error(f"Erro ao converter para MP3: {e}")
        return None


def convert_to_flac(video_path: Path) -> Path:
    """Converte vídeo para FLAC usando ffmpeg."""
    try:
        flac_path = video_path.with_suffix(".flac")
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vn", "-c:a", "flac",
            str(flac_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
        return flac_path
    except Exception as e:
        logger.error(f"Erro ao converter para FLAC: {e}")
        return None


async def download_youtube_video(url: str, height: int = 1080) -> Path | None:
    """Baixa vídeo do YouTube com a altura especificada."""
    try:
        ydl_opts = get_yt_dlp_opts(height, platform="youtube")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return Path(filename)
    except Exception as e:
        logger.error(f"Erro ao baixar vídeo: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /start."""
    await update.message.reply_text(
        "🎬 **Bot de Download de Vídeos**\n\n"
        "Envie um link de vídeo do **YouTube, Instagram ou TikTok** que eu baixo para você!\n\n"
        "Para **YouTube**, você poderá escolher entre: **MP4 1080p, MP4 720p, MP3 ou FLAC**\n\n"
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
        "2. Para **YouTube**, escolha o formato: MP4 1080p, MP4 720p, MP3 ou FLAC\n"
        "3. Aguarde o download e o envio do arquivo.\n\n"
        "⚠️ **Observações:**\n"
        "- Vídeos privados ou restritos não podem ser baixados.\n"
        "- O bot armazena os arquivos temporariamente e os exclui após o envio.\n"
        "- Telegram tem limite de **50MB** para envio de arquivos por bots."
    )


async def show_youtube_options(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """Mostra menu de opções para vídeos do YouTube."""
    keyboard = [
        [
            InlineKeyboardButton("🎥 MP4 1080p", callback_data=f"yt_1080p_{url}"),
            InlineKeyboardButton("🎥 MP4 720p", callback_data=f"yt_720p_{url}"),
        ],
        [
            InlineKeyboardButton("🎵 MP3 320kbps", callback_data=f"yt_mp3_{url}"),
            InlineKeyboardButton("🎵 FLAC", callback_data=f"yt_flac_{url}"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎬 **Escolha o formato para download:**",
        reply_markup=reply_markup
    )


async def handle_youtube_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para escolhas de formato do YouTube."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    url = data.split("_", 2)[2]
    
    await query.edit_message_text("⏳ **Baixando e processando...** Aguarde um momento.")
    
    if data.startswith("yt_1080p"):
        video_path = await download_youtube_video(url, height=1080)
        format_name = "MP4 1080p"
    elif data.startswith("yt_720p"):
        video_path = await download_youtube_video(url, height=720)
        format_name = "MP4 720p"
    elif data.startswith("yt_mp3"):
        video_path = await download_youtube_video(url, height=720)
        if video_path:
            converted_path = convert_to_mp3(video_path)
            if converted_path:
                video_path.unlink()
                video_path = converted_path
            else:
                video_path = None
        format_name = "MP3"
    elif data.startswith("yt_flac"):
        video_path = await download_youtube_video(url, height=720)
        if video_path:
            converted_path = convert_to_flac(video_path)
            if converted_path:
                video_path.unlink()
                video_path = converted_path
            else:
                video_path = None
        format_name = "FLAC"
    else:
        await query.edit_message_text("❌ **Opção inválida!**")
        return
    
    if not video_path or not video_path.exists():
        await query.edit_message_text(
            f"❌ **Falha ao baixar/converter o vídeo como {format_name}!**\n"
            "Verifique se o link está correto e se o vídeo é público."
        )
        return
    
    try:
        file_size = video_path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50MB
            await query.edit_message_text(
                f"❌ **Arquivo muito grande!**\n"
                f"Tamanho: {file_size / (1024*1024):.1f} MB\n"
                "O Telegram tem limite de 50MB para envio de arquivos por bots.\n"
                "Tente uma qualidade menor (720p ou áudio)."
            )
            video_path.unlink(missing_ok=True)
            return
        
        with open(video_path, "rb") as file:
            if format_name in ["MP3", "FLAC"]:
                await context.bot.send_audio(
                    chat_id=update.effective_chat.id,
                    audio=InputFile(file, filename=video_path.name),
                    caption=f"🎵 **Áudio baixado do YouTube ({format_name}):**\n{url}",
                    read_timeout=300,
                    write_timeout=300,
                )
            else:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=InputFile(file, filename=video_path.name),
                    caption=f"🎥 **Vídeo baixado do YouTube ({format_name}):**\n{url}",
                    read_timeout=300,
                    write_timeout=300,
                )
        video_path.unlink(missing_ok=True)
        await query.edit_message_text(f"✅ **Arquivo enviado com sucesso!** ({format_name})")
    except Exception as e:
        logger.error(f"Erro ao enviar arquivo: {e}")
        await query.edit_message_text(
            "❌ **Falha ao enviar o arquivo!** Tente novamente mais tarde."
        )
        if video_path.exists():
            video_path.unlink()


async def download_and_send_video(url: str, platform: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Baixa e envia vídeo para plataformas não-YouTube."""
    await update.message.reply_text("⏳ **Baixando vídeo...** Aguarde um momento.")
    
    video_path = None
    try:
        # Formato compatível com WhatsApp (H.264/AAC) preservando aspect ratio
        ydl_opts = get_yt_dlp_opts(platform=platform)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            video_path = Path(filename)
    except Exception as e:
        logger.error(f"Erro ao baixar vídeo de {platform}: {e}")
        await update.message.reply_text(
            f"❌ **Falha ao baixar o vídeo do {platform}!**\n"
            "Verifique se o link está correto e se o vídeo é público."
        )
        return
    
    if not video_path or not video_path.exists():
        await update.message.reply_text(
            f"❌ **Falha ao baixar o vídeo do {platform}!**"
        )
        return
    
    try:
        file_size = video_path.stat().st_size
        if file_size > 50 * 1024 * 1024:
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
                read_timeout=300,
                write_timeout=300,
            )
        video_path.unlink(missing_ok=True)
    except Exception as e:
        logger.error(f"Erro ao enviar vídeo: {e}")
        await update.message.reply_text(
            "❌ **Falha ao enviar o vídeo!** Tente novamente mais tarde."
        )
        if video_path.exists():
            video_path.unlink()


async def process_video_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa links de vídeos enviados pelo usuário."""
    url = update.message.text.strip()

    if not any(platform in url for platform in SUPPORTED_PLATFORMS):
        await update.message.reply_text(
            "❌ **URL inválida!**\n"
            "Envie um link válido do **YouTube, Instagram ou TikTok**."
        )
        return

    platform = (
        "YouTube" if "youtube.com" in url or "youtu.be" in url else
        "Instagram" if "instagram.com" in url else
        "TikTok"
    )
    
    if platform == "YouTube":
        await show_youtube_options(update, context, url)
    else:
        await download_and_send_video(url, platform, update, context)


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
    app.add_handler(CallbackQueryHandler(handle_youtube_choice))
    app.add_error_handler(error_handler)

    logger.info("Bot iniciado com sucesso!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
