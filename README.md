# Bilibili Followers Fetcher

[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Aiohttp](https://img.shields.io/badge/aiohttp-latest-blue)](https://docs.aiohttp.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux-lightgrey)]()

获取B站UP主的粉丝列表，并导出为HTML或JSON格式。

## 作者信息

- **B站主页**：[https://space.bilibili.com/630095673](https://space.bilibili.com/630095673)
- **GitHub项目主页**：[https://github.com/yht-tutong/bilibili_followers_fetcher](https://github.com/yht-tutong/bilibili_followers_fetcher)
- **QQ交流群**：[点击链接加入群聊【我是交流群喵】](https://qm.qq.com/q/ZyivYoMzmy)

## 功能特性

- 获取粉丝基本信息（UID、用户名、头像）
- 获取关注时间
- 获取粉丝的粉丝数
- 过滤默认头像用户
- 过滤 `bili_` 开头用户
- 按关注时间排序
- 支持导出为 HTML 或 JSON 格式
- Cookie 配置分离到独立文件

## 配置方法

1. 在浏览器中登录B站后，获取您的 SESSDATA
2. 复制 `config.json.example` 为 `config.json`，填入您的 SESSDATA

```cmd
copy config.json.example config.json
```

3. 编辑 `config.json`，将 `sessdata` 值替换为您的 SESSDATA

```json
{
  "sessdata": "你的SESSDATA内容"
}
```

**注意**：SESSDATA 包含敏感信息，请妥善保管，不要上传到公共仓库！`config.json` 已配置在 `.gitignore` 中，不会被提交到 Git 仓库。

## 使用方法

### 基本用法

```cmd
# 默认：导出JSON和HTML，过滤默认头像和bili_开头用户
python bilibili_followers_fetcher.py

# 查看帮助
python bilibili_followers_fetcher.py -h
```

### 命令行参数

| 参数 | 缩写 | 选项 | 说明 |
|------|------|------|------|
| `--format` | `-f` | `json` / `html` / `both` | 导出格式（默认：both） |
| `--filter` | - | `none` / `avatar` / `bili` / `both` | 过滤选项（默认：both） |
| `--no-sort` | - | - | 不按关注时间排序 |

### 导出格式

```cmd
# 只导出JSON
python bilibili_followers_fetcher.py -f json

# 只导出HTML
python bilibili_followers_fetcher.py -f html

# 导出两种格式（默认）
python bilibili_followers_fetcher.py -f both
```

### 过滤选项

```cmd
# 不过滤任何用户
python bilibili_followers_fetcher.py --filter none

# 只过滤默认头像用户
python bilibili_followers_fetcher.py --filter avatar

# 只过滤 bili_ 开头用户
python bilibili_followers_fetcher.py --filter bili

# 同时过滤两者（默认）
python bilibili_followers_fetcher.py --filter both
```

### 排序选项

```cmd
# 不按关注时间排序
python bilibili_followers_fetcher.py --no-sort
```

### 组合使用

```cmd
# 导出JSON，只过滤默认头像，不排序
python bilibili_followers_fetcher.py -f json --filter avatar --no-sort

# 导出HTML，不过滤任何用户
python bilibili_followers_fetcher.py -f html --filter none
```

## 输出文件

运行后会生成以下文件：

| 文件 | 说明 |
|------|------|
| `bilibili_followers.json` | JSON格式的粉丝列表 |
| `bilibili_followers.html` | HTML格式的粉丝列表（需要style.css） |
| `style.css` | HTML样式文件 |

## HTML页面展示

HTML页面以表格形式展示粉丝列表，包含以下列：

| 列名 | 说明 |
|------|------|
| # | 序号 |
| 头像 | 用户头像 |
| 用户名 | 点击可跳转到B站空间 |
| 关注时间 | 关注时间（格式：YYYY-MM-DD HH:MM） |
| 粉丝数 | 该用户的粉丝数量 |

## 注意事项

1. **SESSDATA配置**：首次使用需要在 `config.json` 中配置您的B站 SESSDATA
2. **API限制**：B站API有访问频率限制，大量请求可能导致被限流
3. **数据完整性**：默认会获取前20页粉丝（每页50个），共1000个粉丝
4. **安全提示**：SESSDATA 包含敏感信息，请妥善保管，不要上传到公共仓库！

## 依赖

- Python 3.7+
- aiohttp

## 下载可执行文件

如果不想自己编译，可以直接下载预编译的可执行文件：

前往 [Releases](https://github.com/yht-tutong/bilibili_followers_fetcher/releases/tag/v0.0.1) 页面下载最新版本的 `bilibili_followers_fetcher`。

## 打包成可执行文件

使用 pyinstaller 打包：

```cmd
pip install pyinstaller
pyinstaller --onefile --name bilibili_followers_fetcher bilibili_followers_fetcher.py
```

打包后会在 `dist` 目录生成 `bilibili_followers_fetcher.exe` 文件。

## 参考来源

本项目参考了 [https://itxiaozhang.com/bilibili-followers-data-fetcher-python-tutorial-guide/](https://itxiaozhang.com/bilibili-followers-data-fetcher-python-tutorial-guide/) 的代码实现。

## License

MIT License
