import asyncio
import importlib
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.handlers.handler import Handler
from pyrogram.raw.functions.messages.save_draft import SaveDraft

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

raw_api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")

# Validasi kredensial dasar
if not raw_api_id or not api_hash:
    print("❌ [ERROR] API_ID atau API_HASH belum disetel!")
    print("👉 Salin file '.env.example' menjadi '.env' lalu isi kredensial Telegram kamu:")
    print("   API_ID=12345678")
    print("   API_HASH=abcdef0123456789abcdef0123456789")
    print("   SESSION_STRING= (opsional jika jalan di lokal, Pyrogram akan buat sesi .session otomatis)")
    sys.exit(1)

try:
    api_id = int(raw_api_id)
except ValueError:
    print(f"❌ [ERROR] API_ID harus berupa angka integer, bukan: '{raw_api_id}'")
    sys.exit(1)

# Inisialisasi client
client_kwargs = {
    "name": "mori_ubot",
    "api_id": api_id,
    "api_hash": api_hash,
}
if session_string and session_string.strip():
    client_kwargs["session_string"] = session_string.strip()

app = Client(**client_kwargs)

# Registry plugin aktif: {plugin_name: [(handler, group), ...]}
LOADED_PLUGINS: dict[str, list[tuple[Handler, int]]] = {}
RESTART_FILE = Path("restart.tmp")
PLUGIN_MTIMES: dict[str, float] = {}


# --- PLUGIN MANAGER ENGINE ---
def load_plugin(client: Client, plugin_name: str) -> int:
    """Load atau reload sebuah modul plugin dan daftarkan semua handler miliknya."""
    module_name = f"plugins.{plugin_name}"
    
    if module_name in sys.modules:
        module = importlib.reload(sys.modules[module_name])
    else:
        module = importlib.import_module(module_name)

    handlers = []
    for attr in dir(module):
        obj = getattr(module, attr)
        for h, g in getattr(obj, "handlers", []):
            if isinstance(h, Handler) and isinstance(g, int):
                client.add_handler(h, g)
                handlers.append((h, g))

    LOADED_PLUGINS[plugin_name] = handlers
    return len(handlers)


def unload_plugin(client: Client, plugin_name: str) -> bool:
    """Hapus semua handler plugin dan lepaskan modul dari memory."""
    if plugin_name not in LOADED_PLUGINS:
        return False

    for h, g in LOADED_PLUGINS[plugin_name]:
        client.remove_handler(h, g)

    del LOADED_PLUGINS[plugin_name]

    module_name = f"plugins.{plugin_name}"
    if module_name in sys.modules:
        del sys.modules[module_name]

    return True


def reload_plugin(client: Client, plugin_name: str) -> int:
    """Hot-reload satu plugin tertentu."""
    unload_plugin(client, plugin_name)
    return load_plugin(client, plugin_name)


def load_all_plugins(client: Client) -> dict[str, int]:
    """Muat semua file python di direktori plugins/."""
    results = {}
    plugins_dir = Path("plugins")
    if not plugins_dir.exists():
        plugins_dir.mkdir(parents=True, exist_ok=True)
        return results

    for py_file in sorted(plugins_dir.glob("*.py")):
        if py_file.stem.startswith("__"):
            continue
        try:
            count = load_plugin(client, py_file.stem)
            results[py_file.stem] = count
            PLUGIN_MTIMES[py_file.stem] = py_file.stat().st_mtime
            print(f"📦 [PLUGIN LOADED] {py_file.stem} ({count} handlers)")
        except Exception as e:
            print(f"❌ [PLUGIN ERROR] Gagal memuat {py_file.stem}: {e}")
    return results


# --- MANAJEMEN SISTEM: RESTART & HOT-RELOAD ---

@app.on_message(filters.command("restart", prefixes=".") & filters.me)  # type: ignore
async def restart_command(client: Client, message):
    """Restart proses bot sepenuhnya via execl."""
    await message.edit("🔄 **Sedang merestart Mori-UBOT...**")
    try:
        RESTART_FILE.write_text(f"{message.chat.id}:{message.id}")
    except Exception as e:
        print(f"Gagal menulis restart file: {e}")
    
    await asyncio.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)


@app.on_message(filters.command("reload", prefixes=".") & filters.me)  # type: ignore
async def reload_command(client: Client, message):
    """Hot-reload plugin tanpa mematikan bot atau koneksi Telegram."""
    args = message.command
    if len(args) > 1:
        target = args[1].lower().replace(".py", "")
        plugin_file = Path(f"plugins/{target}.py")
        if not plugin_file.exists():
            return await message.edit(f"❌ **Plugin `{target}` tidak ditemukan di folder `plugins/`!**")

        await message.edit(f"🔄 **Mereload plugin `{target}`...**")
        try:
            cnt = reload_plugin(client, target)
            await message.edit(f"✅ **Plugin `{target}` berhasil di-reload!** ({cnt} handler aktif)")
        except Exception as e:
            await message.edit(f"❌ **Gagal reload plugin `{target}`:** `{e}`")
    else:
        await message.edit("🔄 **Sedang mereload semua plugin...**")
        plugins_to_reload = [p.stem for p in sorted(Path("plugins").glob("*.py")) if not p.stem.startswith("__")]
        
        success = []
        errors = []
        for name in plugins_to_reload:
            try:
                cnt = reload_plugin(client, name)
                success.append(f"`{name}` ({cnt})")
            except Exception as e:
                errors.append(f"`{name}`: {e}")

        res = f"✅ **Semua Plugin Berhasil Di-reload!**\n\n📦 **Aktif ({len(success)}):**\n" + ", ".join(success)
        if errors:
            res += f"\n\n⚠️ **Error ({len(errors)}):**\n" + "\n".join(errors)
        
        # Sinkronkan mtimes agar tidak memicu notifikasi watcher berulang
        PLUGIN_MTIMES.clear()
        for p in Path("plugins").glob("*.py"):
            if not p.stem.startswith("__"):
                PLUGIN_MTIMES[p.stem] = p.stat().st_mtime

        await message.edit(res)


@app.on_message(filters.command("plugins", prefixes=".") & filters.me)  # type: ignore
async def list_plugins_command(_, message):
    """Menampilkan daftar plugin yang aktif dalam memori."""
    if not LOADED_PLUGINS:
        return await message.edit("📦 **Tidak ada plugin yang aktif saat ini.**")

    text = "📦 **DAFTAR PLUGIN AKTIF MORI-UBOT**\n━━━━━━━━━━━━━━━━━━━━\n"
    for name, handlers in LOADED_PLUGINS.items():
        text += f"• `{name}` — {len(handlers)} handler(s)\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\nTotal: `{len(LOADED_PLUGINS)}` plugin aktif."
    await message.edit(text)


@app.on_message(filters.command("load", prefixes=".") & filters.me)  # type: ignore
async def load_cmd(client: Client, message):
    """Memuat plugin baru dari folder plugins/."""
    if len(message.command) < 2:
        return await message.edit("❌ **Format salah!** Gunakan: `.load <nama_plugin>`")

    target = message.command[1].lower().replace(".py", "")
    plugin_file = Path(f"plugins/{target}.py")
    if not plugin_file.exists():
        return await message.edit(f"❌ **File `plugins/{target}.py` tidak ditemukan!**")

    try:
        cnt = load_plugin(client, target)
        await message.edit(f"✅ **Plugin `{target}` berhasil dimuat!** ({cnt} handler aktif)")
    except Exception as e:
        await message.edit(f"❌ **Gagal memuat `{target}`:** `{e}`")


@app.on_message(filters.command("unload", prefixes=".") & filters.me)  # type: ignore
async def unload_cmd(client: Client, message):
    """Mematikan plugin dari memori."""
    if len(message.command) < 2:
        return await message.edit("❌ **Format salah!** Gunakan: `.unload <nama_plugin>`")

    target = message.command[1].lower().replace(".py", "")
    if target not in LOADED_PLUGINS:
        return await message.edit(f"❌ **Plugin `{target}` tidak sedang aktif!**")

    unload_plugin(client, target)
    await message.edit(f"🛑 **Plugin `{target}` berhasil dinonaktifkan!**")


# --- BACKGROUND WATCHER: AUTO DRAFT NOTIFIER ---
async def plugin_watcher(client: Client):
    """Memantau folder plugins/ dan memasang draf .reload otomatis di Saved Messages jika ada file baru/update."""
    await asyncio.sleep(5)  # Beri jeda awal agar inisialisasi awal selesai
    while True:
        try:
            await asyncio.sleep(4)
            plugins_dir = Path("plugins")
            if not plugins_dir.exists():
                continue

            current_files = {
                p.stem: p.stat().st_mtime
                for p in plugins_dir.glob("*.py")
                if not p.stem.startswith("__")
            }

            changes = []
            for name, mtime in current_files.items():
                if name not in PLUGIN_MTIMES:
                    changes.append(f"Plugin baru: `{name}`")
                elif mtime > PLUGIN_MTIMES[name]:
                    changes.append(f"Pembaruan plugin: `{name}`")

            for name in list(PLUGIN_MTIMES.keys()):
                if name not in current_files:
                    changes.append(f"Plugin dihapus: `{name}`")

            if changes:
                # Update mtimes agar tidak berulang
                PLUGIN_MTIMES.clear()
                PLUGIN_MTIMES.update(current_files)

                change_desc = "\n".join(f"• {c}" for c in changes)
                notify_text = (
                    f"📢 **Pembaruan Fitur Terdeteksi!**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{change_desc}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👉 *Draf pesan* `.reload` *telah disiapkan di kolom ketik di bawah. Cukup tekan **Kirim** untuk menerapkan!*"
                )

                # Kirim pesan notifikasi ke Saved Messages ("me")
                await client.send_message("me", notify_text)

                # Pasang draf .reload otomatis di kolom ketik Saved Messages
                peer = await client.resolve_peer("me")
                await client.invoke(SaveDraft(peer=peer, message=".reload"))  # type: ignore
                print(f"🔔 [WATCHER] Perubahan terdeteksi: {changes}. Draf .reload disiapkan di Saved Messages.")

        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"⚠️ [WATCHER ERROR] {e}")


# --- STARTUP RUNNER ---
async def startup():
    print("🚀 Menginisialisasi Mori-UBOT...")
    await app.start()
    
    # Muat semua plugin
    load_all_plugins(app)

    # Jalankan background watcher untuk auto-draft update
    asyncio.create_task(plugin_watcher(app))
    
    # Cek apakah bot baru saja direstart via .restart
    if RESTART_FILE.exists():
        try:
            content = RESTART_FILE.read_text().strip()
            RESTART_FILE.unlink(missing_ok=True)
            if ":" in content:
                chat_id_str, msg_id_str = content.split(":", 1)
                await app.edit_message_text(
                    chat_id=int(chat_id_str),
                    message_id=int(msg_id_str),
                    text="🔥 **Mori-UBOT Berhasil Direstart & Menyala Kembali!** 🔥\nSemua plugin siap digunakan."
                )
        except Exception as e:
            print(f"Gagal mengedit pesan restart: {e}")

    me = await app.get_me()
    name = f"{me.first_name} {me.last_name or ''}".strip()
    print(f"✅ Mori-UBOT aktif sebagai: {name} (@{me.username or me.id})")
    print("🔥 Siap tempur! Tekan Ctrl+C untuk berhenti.")

    # Notifikasi startup otomatis dengan logo ke Saved Messages
    logo_file = Path("assets/logo.png")
    startup_msg = (
        f"🤖 **Mori-UBOT Menyala!** 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Pengguna:** {name}\n"
        f"🆔 **ID:** `{me.id}`\n"
        f"⚡ **Status:** Online & Siap Tempur!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Ketik* `.help` *untuk melihat daftar perintah bantuan.*"
    )
    try:
        if logo_file.exists():
            await app.send_photo("me", photo=str(logo_file), caption=startup_msg)
        else:
            await app.send_message("me", startup_msg)
    except Exception as e:
        print(f"Gagal mengirim notifikasi startup ke Saved Messages: {e}")


async def main():
    await startup()
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        app.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Mori-UBOT dimatikan dengan aman.")
