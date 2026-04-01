# Background Remover Studio

> **[English](#english) | [Português BR](#português-br)**

---

## English

A free, local, and privacy-first background remover. Everything runs on your machine — no internet required after the first model download, no account, no upload limits.

### Features

- Modern dark desktop UI with English / Portuguese toggle
- Batch background removal (process multiple images at once)
- Drag and drop image import
- Adaptive processing — different logic for photos vs. artwork/logos
- Edge refinement tools (smoothing, erosion, hair protection)
- Export to PNG, WebP, TIFF, JPG, and BMP
- Copy processed output directly to the clipboard
- Guided setup assistant (install, repair, and cleanup — all in a GUI)
- Web UI coming soon

### What Gets Installed

The setup assistant installs the following Python packages into your current Python environment:

| Package | Version | Purpose |
|---|---|---|
| `rembg[cpu]` | latest | AI background removal engine |
| `pillow` | latest | Image processing |
| `numpy` | latest | Numerical computing |
| `tkinterdnd2` | latest | Drag and drop support for the desktop UI |

> **First run note:** On the first time you remove a background, `rembg` will automatically download the **u2net AI model (~170 MB)** from the internet and save it to `%USERPROFILE%\.u2net\`. This only happens once. After that the app works fully offline.

The following packages are installed only for the Web UI (coming soon):

| Package | Purpose |
|---|---|
| `fastapi` | Local web server framework |
| `uvicorn` | ASGI server |
| `python-multipart` | File upload handling |

### Requirements

- Windows 10 or 11
- Python 3.10 or higher — [python.org](https://www.python.org/downloads/)

### Quick Start

1. Double-click **`start.bat`**
2. The setup assistant opens — click **"Install / Repair Dependencies"** on the first run
3. After installation, click **"Open App"** → **"Desktop App"**
4. A shortcut called **"Background Remover Studio"** with the app icon is automatically created in this folder — use it for all future launches (no CMD window)

### Manual Start (advanced)

```bash
pip install -r requirements.txt
python src/main.py
```

### Uninstall / Cleanup

Double-click **`src/uninstall.bat`** or use the **"Uninstall / Cleanup"** button inside the setup assistant.

The cleanup assistant lets you choose what to remove:

- `__pycache__` and local generated files
- Python packages installed by this app (`rembg`, `pillow`, `numpy`, `tkinterdnd2`)
- Downloaded AI model cache (`~/.u2net/`)

It always shows a summary before doing anything and **never touches your source images or exported files**.

For a full removal, delete this project folder manually after cleanup.

### Project Structure

```
background-remover-studio/
├── start.bat              # Windows launcher — always works, no setup required
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT
├── README.md
└── src/
    ├── main.py                # Desktop app entry point
    ├── background_remover.py  # Desktop UI + shared AI pipeline
    ├── api_server.py          # Local FastAPI server (Web UI — coming soon)
    ├── setup_assistant.pyw    # Setup / repair / cleanup GUI
    ├── uninstall.bat          # Uninstall entry point
    ├── icon.ico               # App icon
    └── webui/                 # Web interface (HTML / CSS / JS)
        ├── index.html
        ├── app.js
        └── styles.css
```

> **Note:** A shortcut `Background Remover Studio.lnk` is automatically created in the root on the first launch. It points directly to `pythonw.exe` with the custom icon — no CMD window. It is listed in `.gitignore` and not committed to the repository.

### Export Formats

| Format | Transparency | Notes |
|---|---|---|
| PNG | ✅ | Lossless, recommended |
| WebP | ✅ | Smaller file size |
| TIFF | ✅ | Lossless, for print workflows |
| JPG | ❌ | White background fill |
| BMP | ❌ | White background fill |

### License

MIT — see [LICENSE](LICENSE)

### Author

**Henrique Fernandes**
LinkedIn: [linkedin.com/in/henriquehsf](https://pt.linkedin.com/in/henriquehsf)
Instagram / Company: [@oportunipt](https://instagram.com/oportunipt)

---

## Português BR

Removedor de fundo gratuito, local e com privacidade total. Tudo roda na sua máquina — sem internet depois do primeiro download do modelo, sem conta, sem limite de uploads.

### Funcionalidades

- Interface desktop dark moderna com botão English / Português
- Remoção em lote (processa várias imagens de uma vez)
- Importação por arrasto (drag and drop)
- Processamento adaptativo — lógica diferente para fotos vs. arte/logos
- Ferramentas de refinamento de borda (suavização, erosão, proteção de cabelo)
- Exportação em PNG, WebP, TIFF, JPG e BMP
- Copiar resultado direto para a área de transferência
- Assistente de setup guiado (instalar, reparar e limpar — tudo em GUI)
- Interface Web em breve

### O que é Instalado

O assistente de setup instala os seguintes pacotes Python no seu ambiente Python atual:

| Pacote | Versão | Função |
|---|---|---|
| `rembg[cpu]` | mais recente | Motor de IA para remoção de fundo |
| `pillow` | mais recente | Processamento de imagens |
| `numpy` | mais recente | Computação numérica |
| `tkinterdnd2` | mais recente | Suporte a arrastar e soltar no app desktop |

> **Nota sobre o primeiro uso:** Na primeira vez que você remover um fundo, o `rembg` vai baixar automaticamente o **modelo de IA u2net (~170 MB)** da internet e salvar em `%USERPROFILE%\.u2net\`. Isso acontece uma única vez. Depois disso o app funciona completamente offline.

Os seguintes pacotes são instalados apenas para a Interface Web (em breve):

| Pacote | Função |
|---|---|
| `fastapi` | Framework para servidor web local |
| `uvicorn` | Servidor ASGI |
| `python-multipart` | Upload de arquivos |

### Requisitos

- Windows 10 ou 11
- Python 3.10 ou superior — [python.org](https://www.python.org/downloads/)

### Início Rápido

1. Dê dois cliques em **`start.bat`**
2. O assistente de setup abre — clique em **"Instalar / Reparar Dependências"** na primeira vez
3. Após a instalação, clique em **"Abrir App"** → **"App Desktop"**
4. Um atalho chamado **"Background Remover Studio"** com o ícone do app é criado automaticamente nesta pasta — use-o para abrir o app nas próximas vezes (sem janela de CMD)

### Início Manual (avançado)

```bash
pip install -r requirements.txt
python src/main.py
```

### Desinstalar / Limpar

Dê dois cliques em **`src/uninstall.bat`** ou use o botão **"Desinstalar / Limpar"** dentro do assistente.

O assistente de limpeza permite escolher o que remover:

- `__pycache__` e arquivos locais gerados
- Pacotes Python instalados por este app (`rembg`, `pillow`, `numpy`, `tkinterdnd2`)
- Cache do modelo de IA (`~/.u2net/`)

Ele sempre mostra um resumo antes de fazer qualquer coisa e **nunca toca nas suas imagens originais nem nos arquivos exportados**.

Para remover completamente, apague esta pasta manualmente após a limpeza.

### Estrutura do Projeto

```
background-remover-studio/
├── start.bat              # Launcher Windows — sempre funciona, sem configuração
├── requirements.txt       # Dependências Python
├── LICENSE                # MIT
├── README.md
└── src/
    ├── main.py                # Ponto de entrada do app desktop
    ├── background_remover.py  # Interface desktop + pipeline de IA
    ├── api_server.py          # Servidor FastAPI local (Interface Web — em breve)
    ├── setup_assistant.pyw    # GUI de setup / reparo / limpeza
    ├── uninstall.bat          # Ponto de entrada para desinstalação
    ├── icon.ico               # Ícone do app
    └── webui/                 # Interface Web (HTML / CSS / JS)
        ├── index.html
        ├── app.js
        └── styles.css
```

> **Nota:** Um atalho `Background Remover Studio.lnk` é criado automaticamente na raiz na primeira inicialização. Ele aponta diretamente para `pythonw.exe` com o ícone personalizado — sem janela de CMD. Está listado no `.gitignore` e não é enviado para o repositório.

### Formatos de Exportação

| Formato | Transparência | Notas |
|---|---|---|
| PNG | ✅ | Sem perda de qualidade, recomendado |
| WebP | ✅ | Arquivo menor |
| TIFF | ✅ | Sem perda, para impressão |
| JPG | ❌ | Fundo branco |
| BMP | ❌ | Fundo branco |

### Licença

MIT — veja [LICENSE](LICENSE)

### Autor

**Henrique Fernandes**
LinkedIn: [linkedin.com/in/henriquehsf](https://pt.linkedin.com/in/henriquehsf)
Instagram / Empresa: [@oportunipt](https://instagram.com/oportunipt)
