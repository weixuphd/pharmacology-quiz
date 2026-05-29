# 抗病毒药题库 — 部署指南

## 文件清单

```
pnas/
├── app.py                 # Flask 后端（API + 安全控制）
├── antiviral.csv          # 题库文件（100题）—— 只在服务器端，绝不暴露给学生
├── templates/
│   └── index.html         # 前端页面
├── requirements.txt       # Python 依赖
├── Procfile               # 云平台部署配置
└── README.md              # 本文件
```

## 安全设计

- **题库 CSV 文件只存在于服务器端**，学生无法下载
- API 每次只返回**一道题**，且**不含正确答案**
- 学生提交答案后，服务器才返回该题的正误和解析
- **限速控制**：每 IP 每小时 300 请求、每分钟 30 请求，阻止脚本批量抓取
- 无任何批量导出接口

---

## 方式一：课堂 WiFi 局域网（最简单，无需注册任何平台）

教师在教室电脑上启动服务，学生在同一 WiFi 下用浏览器访问教师 IP 即可。

```bash
# 1. 安装依赖
pip3 install Flask Flask-Limiter

# 2. 启动服务器
cd ~/Downloads/pnas
python3 app.py

# 3. 查看本机 IP 地址（macOS）
ipconfig getifaddr en0
# 例如输出: 192.168.1.105

# 4. 学生在浏览器访问
# http://192.168.1.105:5000
```

> **注意**: macOS 上端口 5000 可能被 AirPlay 占用，使用其他端口：
> ```bash
> PORT=8080 python3 app.py
> # 学生访问 http://192.168.1.105:8080
> ```

---

## 方式二：Render.com 免费部署（推荐，永久在线）

免费将应用部署到互联网，学生随时随地可访问。

### 步骤

**1.** 注册 [render.com](https://render.com)（用 GitHub 账号即可）

**2.** 将项目推送到 GitHub：
```bash
cd ~/Downloads/pnas
git init
git add app.py antiviral.csv templates/ requirements.txt Procfile
git commit -m "Antiviral drug quiz app"
# 在 GitHub 上创建新仓库，然后：
git remote add origin https://github.com/你的用户名/antiviral-quiz.git
git push -u origin main
```

**3.** 在 Render Dashboard 中：
- 点击 "New +" → "Web Service"
- 连接你的 GitHub 仓库
- 设置：
  - **Name**: `antiviral-quiz`
  - **Runtime**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
  - **Free Instance Type**: 选择 Free
- 点击 "Create Web Service"

**4.** 部署完成后，Render 会提供一个 URL（如 `https://antiviral-quiz.onrender.com`），分享给学生即可。

> **注意**: 免费实例在 15 分钟无访问后会休眠，首次唤醒需约 30-60 秒。

---

## 方式三：PythonAnywhere 免费部署

1. 注册 [pythonanywhere.com](https://www.pythonanywhere.com)
2. 上传 `app.py`、`antiviral.csv`、`templates/index.html`
3. 在 Web 选项卡中创建 Flask 应用，指向 `app.py`
4. PythonAnywhere 限制免费账户只能访问特定白名单站点，不适合学生自由访问。

---

## 方式四：Gunicorn 生产模式（本地/服务器）

```bash
pip3 install gunicorn
cd ~/Downloads/pnas
gunicorn app:app --bind 0.0.0.0:8080 --workers 2
```

---

## 教师使用说明

1. 打开网页 → 自动加载第一道题
2. 点击选项或按键盘 A-E / 1-5 作答
3. 作答后立即显示正误和解析
4. 左右箭头键切换题目
5. 顶部导航点可跳转任意题目
6. "显示答案"按钮可查看答案（不算作答）
7. 进度保存在浏览器本地，刷新不丢失
8. "重置进度"清除所有答题记录

### 四种练习模式
- **全部顺序** — 按编号顺序答题
- **随机出题** — 随机跳转
- **错题重做** — 只练习答错的题
- **未答题** — 跳到第一道未答题

### 统计面板
- 总体正确率和分类得分
- 每个药物类别的进度条
