# 📕 code-style-cpp-guide

这是一份笔者自用的 Code Style C++ Guide

也是一份 Agent SKILL

## 🌏 Website

[C++ Code Style Guide](https://mico845.github.io/code-style-cpp-guide/) 👈 


## ▶️ Run

执行：

```bash
python scripts/generate_site.py
```

该脚本将

- 更新 `references/` 里的 `*.md` MarkDown 源文本到 `SKILL.md`

- 把 `references/html` 里的网页复制到 `docs/references/html`，并加载到 `docs/index.html`

## 📁 Project Structure

```
.
├─ docs/
├─ references/
│  ├─ html/
│  │  └─ *.html
│  └─ *.md
├─ scripts/
│  └─ generate_site.py
└─ SKILL.md
```

## 📄 License

MIT License