# Homework Zero: Environment Setup

## Welcome to Hawkeye Spirits

Before diving into tools, let's understand the project you'll be building across all five activities.

Read the [Hawkeye Spirits brief](../hawkeye_spirits_brief.md) and the [data dictionary](../dataset/data_dictionary.md) now. They provide the business context and data documentation you'll need throughout the course.

---

## Purpose

Get your development environment ready **before** Activity 1 is released. This homework is not graded, but completing it now will save you hours of frustration later. Every activity in this course depends on three tools: Python (managed by `uv`), Docker, and Git. If any of these are missing or misconfigured when you start Activity 1, you will spend your lab time debugging installation issues instead of learning MLOps.

Budget 30-60 minutes for this setup. Most of the time goes to Docker, especially on Windows.

**No cloud accounts are required.** Everything in this course runs on your local machine.

---

## 1. Python + uv

We use **uv** as our Python package and environment manager. It replaces `pip`, `venv`, `virtualenv`, `pyenv`, and `pipenv` with a single fast tool. Every activity uses `uv` to create isolated environments and install dependencies.

### Install uv

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your terminal (or run `source ~/.bashrc` / `source ~/.zshrc`) so the `uv` command is available.

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, restart your terminal.

### Verify uv

```bash
uv --version
```

You should see a version number (e.g., `uv 0.6.x`). If you get "command not found," the installation did not add `uv` to your PATH. Try opening a new terminal window.

### Test uv with a throw-away project

Run the following commands to confirm `uv` can create a project, install a package, and run Python code:

```bash
uv init test-project
cd test-project
uv add pandas
uv run python -c "import pandas; print('pandas', pandas.__version__)"
```

You should see output like:

```
pandas 2.2.x
```

If this works, delete the test project:

```bash
cd ..
rm -rf test-project
```

On Windows, use `rmdir /s /q test-project` instead.

---

## 2. Docker

Docker lets you package applications into containers that run identically on any machine. Activities 2, 5, and the final project use Docker extensively.

### Linux (Ubuntu / Debian)

```bash
sudo apt-get update
sudo apt-get install -y docker.io
```

On Fedora / RHEL:

```bash
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

Add your user to the `docker` group so you do not need `sudo` for every Docker command:

```bash
sudo usermod -aG docker $USER
```

**Important:** You must log out and log back in (or restart your machine) for the group change to take effect. After logging back in, verify:

```bash
docker run hello-world
```

You should see "Hello from Docker!" in the output.

### macOS

1. Download **Docker Desktop** from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. Open the downloaded `.dmg` file and drag Docker to Applications
3. Launch Docker Desktop from Applications
4. Wait for the Docker icon in the menu bar to show "Docker Desktop is running"
5. Open a terminal and verify:

```bash
docker run hello-world
```

**Apple Silicon users (M1/M2/M3/M4):** Open Docker Desktop, go to **Settings** (gear icon) -> **General**, and enable **Use Rosetta for x86_64/amd64 emulation on Apple Silicon**. This ensures compatibility with x86 container images used in the course.

### Windows

Windows requires WSL2 (Windows Subsystem for Linux 2) as the backend for Docker. Follow these steps carefully:

**Step 1: Enable WSL2**

Open **PowerShell as Administrator** (right-click PowerShell -> "Run as administrator") and run:

```powershell
wsl --install
```

This installs WSL2 with Ubuntu as the default Linux distribution. **Restart your computer** when prompted.

**Step 2: Verify WSL2**

After restarting, open a terminal and run:

```powershell
wsl --list --verbose
```

You should see Ubuntu listed with VERSION 2. If it shows VERSION 1, upgrade it:

```powershell
wsl --set-version Ubuntu 2
```

**Step 3: Install Docker Desktop**

1. Download **Docker Desktop** from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. Run the installer
3. During installation, ensure the checkbox **"Use WSL 2 instead of Hyper-V"** is checked
4. Complete the installation and restart your computer if prompted

**Step 4: Start Docker Desktop**

Launch Docker Desktop. Wait for it to fully initialize (the icon in the system tray will stop animating). This can take 1-2 minutes on the first launch.

**Step 5: Verify**

Open a terminal (PowerShell, CMD, or WSL2 Ubuntu terminal) and run:

```bash
docker run hello-world
```

You should see "Hello from Docker!" in the output.

### Windows Troubleshooting

| Problem | Solution |
|---------|----------|
| "WSL 2 installation is incomplete" error | Download and install the WSL2 Linux kernel update package from Microsoft: [https://aka.ms/wsl2kernel](https://aka.ms/wsl2kernel). Then restart Docker Desktop. |
| Docker Desktop will not start | Restart your computer and try again. If it still fails, check the next row. |
| "Hardware assisted virtualization and data execution protection must be enabled in the BIOS" | Restart your computer, enter BIOS/UEFI settings (usually by pressing F2, F10, F12, or Del during boot), find the virtualization setting (called **VT-x** on Intel or **AMD-V** / **SVM** on AMD), enable it, save, and reboot. |
| Docker commands hang or timeout | Make sure Docker Desktop is fully started (check the system tray icon). If using WSL2, run `wsl --shutdown` then reopen Docker Desktop. |
| "permission denied" when running docker commands | On Linux: make sure you added your user to the docker group and logged out/in. On Windows: make sure Docker Desktop is running. |

---

## 3. Git

Git is our version control system. You will use it to manage your project code across all activities and to access checkpoint branches.

### Verify Git

```bash
git --version
```

You should see a version number (e.g., `git version 2.43.x`). If Git is already installed, you are done with this section.

### Install Git (if not already installed)

**Linux (Ubuntu / Debian):**

```bash
sudo apt-get install -y git
```

**Linux (Fedora / RHEL):**

```bash
sudo dnf install -y git
```

**macOS:**

```bash
xcode-select --install
```

This installs the Xcode Command Line Tools, which include Git. Follow the prompts in the dialog that appears.

**Windows:**

If you installed WSL2 (Step 1 of Docker setup), Git is already available inside your WSL2 Ubuntu terminal. Verify with `git --version` inside WSL2.

If you also need Git in native Windows (PowerShell/CMD), download and install **Git for Windows** from [https://git-scm.com/download/win](https://git-scm.com/download/win). Use the default installation settings.

### Configure Git (first-time setup)

If you have never used Git on this machine, set your name and email:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

These are attached to your commits. Use the name and email associated with your student account.

---

## 4. Verification Checklist

Run each command below and confirm it produces the expected output. Check off each item:

- [ ] **`uv --version`** prints a version number (e.g., `uv 0.6.x`)
- [ ] **`docker run hello-world`** prints "Hello from Docker!" (Docker daemon must be running)
- [ ] **`git --version`** prints a version number (e.g., `git version 2.43.x`)
- [ ] **`make --version`** prints a version number (needed for Activity 3)

If all three commands succeed, your environment is ready for Activity 1.

---

## 5. Timeline

Complete this homework **before Activity 1 is released**. Do not wait until the first lab session -- if you hit an installation issue (especially Docker on Windows), you will need time to troubleshoot.

| Estimated time | Component |
|----------------|-----------|
| 5 minutes | uv installation and verification |
| 15-45 minutes | Docker installation (longest on Windows due to WSL2 + restarts) |
| 5 minutes | Git verification / installation |
| **Total** | **30-60 minutes** |

---

## Common Issues

1. **Corporate or university firewall blocks downloads**: Try connecting to a different network (e.g., your home WiFi or a mobile hotspot) to download Docker Desktop and uv.
2. **Antivirus software blocks Docker**: Some antivirus programs interfere with Docker's network setup. Temporarily disable your antivirus during installation, then re-enable it. Add Docker Desktop to your antivirus exceptions list.
3. **Low disk space**: Docker Desktop requires approximately 2-3 GB of disk space. Docker images for this course will use an additional 2-5 GB. Ensure you have at least 10 GB free.
4. **Older Windows versions**: WSL2 requires Windows 10 version 2004 or later, or Windows 11. Run `winver` to check your version. If you are on an older version, update Windows first.
