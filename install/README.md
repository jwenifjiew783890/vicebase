# Installing Vision

Vision is a personal AI assistant that runs on your own machine. Your
conversations, your memory and your notes stay on your computer.

---

## Windows

1. Download or clone this folder.
2. **Double-click `Install-Vision.bat`.**
3. Wait. It takes 10–20 minutes, mostly downloading the model.
4. Launch Vision from the **Desktop shortcut**.
5. Your browser opens at `http://127.0.0.1:8765`. Talk to it.

If Windows warns about running a script, that is expected — the installer
is a PowerShell file. Choose *Run anyway*, or right-click
`Install-Vision.ps1` → *Run with PowerShell*.

**You need Python 3.10 or newer first.** The installer checks, and stops
with instructions if it is missing. It will not install a language runtime
on your PATH without asking, because an installer should not do that
quietly. Get it from [python.org](https://www.python.org/downloads/) and
tick **"Add python.exe to PATH"**.

### With an NVIDIA GPU

```powershell
powershell -ExecutionPolicy Bypass -File install\Install-Vision.ps1 -Gpu
```

Needs the CUDA Toolkit and Visual Studio Build Tools. Without them Vision
runs on the CPU, which works — just slower.

---

## macOS and Linux

```bash
bash install/install.sh
```

Then launch it:

```bash
~/.local/share/vision/bin/vision      # or just: vision
```

---

## What the installer does

- Creates a private Python environment — nothing is installed system-wide
- Installs Vision and its dependencies
- Downloads Chromium for the browser agent (~150 MB)
- Downloads the models (~2.9 GB): the conversational model, two speech
  voices, and the speech recogniser
- Creates a launcher and a shortcut
- Runs a preflight check and shows you the result

**Everything lands in one place** — `%LOCALAPPDATA%\Vision` on Windows,
`~/.local/share/vision` elsewhere — and your data in `~/.vision`. To
uninstall, delete those two folders.

### If a download fails

Re-run it. Downloads resume, and nothing is re-fetched:

```
# Windows
%LOCALAPPDATA%\Vision\.venv\Scripts\python -m vision.setup_models
# macOS / Linux
~/.local/share/vision/.venv/bin/python -m vision.setup_models
```

---

## First run

### Connect your Obsidian vault

Open Vision → **System** tab → paste your vault path → **Connect vault**.
It indexes every `.md` file and starts using your notes to answer.

Or set it permanently:

```
VISION_VAULT=C:\Users\you\Documents\MyVault
```

### Talk to it

Click **🎙 Talk** and hold while you speak, or just type. English, हिन्दी
and Hinglish all work, including switching mid-sentence.

Your browser will ask for microphone permission the first time. That is the
microphone working — Vision captures audio in the browser, on your machine,
and only sends it to the local server for transcription.

### Add plugins

**Plugins** tab → give it a name and a command. Any MCP server works:

```
name:    filesystem
command: npx -y @modelcontextprotocol/server-filesystem C:\Users\you\Documents
```

Its tools become available immediately. Ask *"what tools do you have"*.

### Optional integrations

Set these as environment variables before launching:

| For | Set |
|---|---|
| WhatsApp | `VISION_WHATSAPP_TOKEN`, `VISION_WHATSAPP_PHONE_ID` from a Meta Cloud API app |
| Email | `VISION_SMTP_HOST`, `VISION_SMTP_USER`, `VISION_SMTP_PASSWORD`, `VISION_SMTP_FROM` |
| A different model | `VISION_LLM=C:\path\to\model.gguf` |
| GPU offload | `VISION_LLM_GPU_LAYERS=20` |

Without them, those agents say they are not connected. They never pretend.

---

## Is it working?

```
python -m vision --check
```

Every line says OK or explains what is missing.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Python 3.10+ is required" | Install Python, tick *Add to PATH*, re-run |
| Mic button does nothing | Browsers only allow microphone access on `localhost` or HTTPS. Use the shortcut, which opens `127.0.0.1`. |
| "no model" | The download did not finish. Re-run `setup_models` above. |
| Very slow replies | That is the CPU. Set `VISION_LLM_GPU_LAYERS=20` if you have an NVIDIA GPU. |
| Web searches find nothing | Often correct — a restricted network blocks the search provider, and Vision says so rather than inventing results. |
| Browser agent unavailable | Run `.venv/bin/python -m playwright install chromium` |

More detail, including how to add your own agents: [`../VISION.md`](../VISION.md).
