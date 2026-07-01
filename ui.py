"""
ui.py - Tampilan output berwarna untuk ChatAI, pakai library `rich`.

Kenapa rich?
- Render Markdown balasan AI (heading, list, bold) jadi rapi di terminal.
- Syntax highlighting otomatis untuk code block (```python, ```json, dll)
  -> penting banget waktu belajar programming, biar code langsung "kebaca".
- Panel/warna beda buat: kamu, AI, notice (info), error, sukses.
- Aman di-bundle PyInstaller (murni Python, tidak butuh binary tambahan).
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.text import Text

console = Console()


# ---------------------------------------------------------------------------
# Warna dasar (mirip gaya pip: [notice] biru, error merah, sukses hijau)
# ---------------------------------------------------------------------------
def notice(message: str):
    """Info netral, gaya mirip '[notice] ...' di pip -> biru."""
    console.print(f"[bold blue][notice][/bold blue] {message}")


def success(message: str):
    console.print(f"[bold green][ok][/bold green] {message}")


def error(message: str):
    console.print(f"[bold red][error][/bold red] {message}")


def warning(message: str):
    console.print(f"[bold yellow][warning][/bold yellow] {message}")


# ---------------------------------------------------------------------------
# Prompt user (input)
# ---------------------------------------------------------------------------
def ask(username: str) -> str:
    return console.input(f"[bold cyan]{username}[/bold cyan] [dim]>[/dim] ").strip()


# ---------------------------------------------------------------------------
# Balasan AI -> di-render sebagai Markdown (code block otomatis di-highlight)
# ---------------------------------------------------------------------------
def print_ai_reply(model: str, reply: str):
    console.print()
    console.print(Rule(f"[bold magenta]AI[/bold magenta] [dim]({model})[/dim]", style="magenta"))
    console.print(Markdown(reply))
    console.print()


def print_session_header(title: str, is_new: bool):
    status = "dimulai" if is_new else "dilanjutkan"
    console.print(Panel.fit(
        f"Sesi [bold]{title}[/bold] {status}\n[dim]ketik 'exit' atau 'quit' untuk keluar[/dim]",
        border_style="cyan"
    ))


# ---------------------------------------------------------------------------
# Help & list, ditampilkan pakai table biar rapi & tidak numpuk dari atas-bawah
# ---------------------------------------------------------------------------
def print_help():
    console.print(Panel.fit("[bold]ChatAI[/bold] - CLI Chat dengan Groq API", border_style="blue"))

    usage = Table(show_header=False, box=None, padding=(0, 1))
    usage.add_row('chatai "pertanyaan"', "tanya cepat, tidak disimpan")
    usage.add_row('chatai --new <judul>', "mulai/lanjutkan chat dengan memori")
    usage.add_row('chatai --api <API_KEY>', "set API key Groq")
    usage.add_row('chatai --model <model>', "set model AI default")
    usage.add_row('chatai --user <nama>', "set nama pengguna")
    usage.add_row('chatai --list', "lihat semua judul chat tersimpan")
    console.print(Rule("Penggunaan", style="dim"))
    console.print(usage)

    args_table = Table(show_header=True, header_style="bold magenta", box=None)
    args_table.add_column("Argument")
    args_table.add_column("Keterangan")
    args_table.add_row("--help,  -h", "menampilkan bantuan")
    args_table.add_row("--user,  -u", "mengubah nama user")
    args_table.add_row("--model, -m", "mengubah model AI (default atau sekali pakai)")
    args_table.add_row("--api,   -k", "mengubah API key Groq")
    args_table.add_row("--new,   -n", "membuat/melanjutkan judul chat beserta riwayatnya")
    args_table.add_row("--list,  -l", "menampilkan daftar chat tersimpan")
    console.print(Rule("Argument", style="dim"))
    console.print(args_table)

    console.print(Rule("Contoh", style="dim"))
    console.print('  chatai "bagaimana cara membedakan oksigen dengan nitrogen"')
    console.print('  chatai --new "belajar godot"')


def print_chat_list(chats):
    if not chats:
        notice("Belum ada sesi chat tersimpan.")
        return
    table = Table(title="Sesi Chat Tersimpan", header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Judul")
    for i, title in enumerate(chats, start=1):
        table.add_row(str(i), title)
    console.print(table)