# 📁 gdsync

**gdsync** is a safe, Git-like, two-way synchronization tool for Google Drive.

It is designed for **shared academic folders**, **annotated PDFs**, and **collaborative Drive usage**, where **data safety matters more than blind automation**.

> If Git taught developers how to collaborate safely,
> **gdsync does the same for Google Drive.**

---

## ✨ Why gdsync exists

Most Drive sync tools:

* overwrite files silently
* destroy annotations
* lose shared edits
* treat conflicts as errors

**gdsync treats conflicts as decisions.**

It:

* never overwrites silently
* always shows what changed
* lets *you* decide what to keep
* logs everything for auditability

---

## 🚀 Features

* Two-way sync (local ↔ Google Drive)
* Git-like mental model (`pull`, `push`, `ask`)
* Safe conflict detection using MD5 hashes
* Interactive conflict resolution
* **Keep-both** mode (ideal for PDFs)
* Progress bars for uploads & downloads
* Dry-run mode
* Conflict audit log
* Works with shared Drive folders
* No background daemon (you stay in control)

---

## 📦 Installation

### From PyPI (users)

```bash
pip install gdsync
```

### Development install (contributors)

```bash
git clone https://github.com/abhiraj-bibhar/gdsync.git
cd gdsync
chmod +x ./scripts/dev_install.sh
./scripts/dev_install.sh
```

---

## 🔐 Authentication (required once)

gdsync uses **your own Google OAuth credentials**.
This avoids quotas, billing issues, and privacy concerns.

### Setup instructions

```bash
gdsync auth help
```

You will:

1. Create a Google Cloud project
2. Enable Google Drive API
3. Create OAuth credentials (Desktop App)
4. Authenticate locally

### Authenticate

```bash
gdsync auth
```

### Check authentication status

```bash
gdsync auth status
```

---

## 📁 Initialize a project

```bash
cd my-project
gdsync init
```

You will be asked:

* Sync **entire Google Drive**
* OR sync **a specific Drive folder**

This creates:

```
.gdsync/
├── config.json
├── state.json
└── conflicts.json
```

All of this is **git-ignored**.

---

## 🔁 Core Commands

### `gdsync run`

Run a full sync.

```bash
gdsync run
```

Options:

```bash
gdsync run --dry-run     # preview changes
gdsync run -y            # auto-confirm prompts
gdsync run --download-dir "Folder/Subfolder"
```

---

### `gdsync status`

Show project sync status.

```bash
gdsync status
```

---

### `gdsync purge`

Remove gdsync metadata from the project.

```bash
gdsync purge
```

Remove **everything** (including auth):

```bash
gdsync purge --all
```

---

## 🧠 Git-like Sync Model (IMPORTANT)

gdsync follows **Git semantics**, not Dropbox semantics.

### 🟢 No conflict

* File exists only locally → upload
* File exists only on Drive → download
* File exists on both, same hash → unchanged

### ⚠ Conflict

A conflict happens when:

* File exists locally AND on Drive
* Contents differ (MD5 mismatch)

Example:

* You annotate a PDF locally
* Your professor annotates the same PDF in Drive

---

## ⚠ Conflict Resolution Options

When a conflict is detected, gdsync offers:

### 1️⃣ Prefer Drive

* Drive overwrites local
* Use when collaborator’s version is authoritative

### 2️⃣ Prefer Local

* Local overwrites Drive
* Use when your edits are final

### 3️⃣ Keep Both (recommended for PDFs)

* No overwrite
* Both versions are preserved

Result:

```
file.pdf
file (local copy).pdf
file (drive copy).pdf
```

### 4️⃣ Skip

* Do nothing
* Revisit later

---

## 🧾 Conflict Log (Audit Trail)

All conflicts are logged to:

```
.gdsync/conflicts.json
```

Each entry contains:

* file path
* local size & timestamp
* Drive size & timestamp
* chosen resolution
* execution time

This makes gdsync **auditable and debuggable**.

---

## 🧪 Dry-Run Mode (Highly Recommended)

Preview everything without touching files:

```bash
gdsync run --dry-run
```

You will see:

* uploads
* downloads
* conflicts
* summaries

No files are modified.

---

## 📂 Directory Structure

For full-drive sync, gdsync stores Drive content in:

```
Drive/
```

This directory is **never committed to git**.

---

## 🔐 Safety Guarantees

gdsync **will never**:

* overwrite silently
* delete without confirmation
* run background processes
* auto-merge binary files
* touch credentials without consent

---

## 🧹 Cleanup

Remove project metadata:

```bash
gdsync purge
```

Remove everything (including OAuth):

```bash
gdsync purge --all
```

---

## 🧠 Design Philosophy

* Conflicts are not errors — they are decisions
* Automation must never destroy data
* Humans stay in control
* Favor safety over convenience
* Transparency over magic

---

## 📜 License

MIT License

---

## 🙌 Final Note

If you:

* read PDFs locally
* collaborate using Google Drive
* care about annotations
* hate silent overwrites

**gdsync is built for you.**
