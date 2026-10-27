# Crafting Apps Catalog

12 款 Crafting Apps 的能力目录。每款应用都是独立的 Rust 原生程序，对标 Adobe 对应工具。

## Quick Reference

| 应用 | 对标 | CLI 命令数 | MCP 工具数 | 默认控制端口 |
|------|------|-----------|-----------|-------------|
| PhotoCraft | Photoshop | 858 | 21 | 7979 (认证) |
| VectorCraft | Illustrator | 743 | 32 | 7979 |
| FilmCraft | Premiere Pro | 693 | 17 | 9876 |
| EffectCraft | After Effects | 669 | 27 | 9877 |
| SoundCraft | Audition | 465 | 17 | 动态 |
| DesignCraft | InDesign | 536 | 25 | 动态 |
| LightCraft | Lightroom | 296 | 318 | 7980 |
| GridCraft | Excel | 315 | 21 | 动态 |
| WordCraft | Word | 460 | 16 | 动态 |
| DeckCraft | PowerPoint | 226 | 25 | 动态 |
| CADCraft | AutoCAD | 305 | 11 | 动态 |
| PdfCraft | Acrobat | 161 | 161 | 文件 |

## PhotoCraft — Photoshop 替代

**能力：**
- 图层、蒙版、混合模式
- 画笔、钢笔、文字排版
- 曲线色阶调整
- PSD 文件读写（99%+ 测试样本无损）
- AI 生成与 2D 合成

**常用命令族：**
- `open.*` / `save.*` / `export.*` — 文件操作
- `layer.*` — 图层管理
- `filter.*` — 滤镜
- `adjust.*` — 调整（曲线、色阶、亮度等）
- `tool.*` — 工具操作

**控制通道：** 认证变体，需 token

## VectorCraft — Illustrator 替代

**能力：**
- 钢笔工具、节点选择
- 布尔运算、形状生成
- 吸附辅助线
- SVG/PDF 导入导出

**常用命令族：**
- `shape.*` — 形状
- `path.*` — 路径
- `fill.*` / `stroke.*` — 填充描边
- `group.*` / `ungroup.*` — 编组
- `export.*` — 导出

## FilmCraft — Premiere Pro 替代

**能力：**
- 多轨时间线
- 三点剪辑
- 素材监视器
- 曲线、色轮、LUT 调色
- 自研 H.264/ProRes/VP9 解码

**常用命令族：**
- `import.*` — 导入素材
- `timeline.*` — 时间线操作
- `effect.*` — 特效
- `export.*` — 导出

**特殊：** 需要 JSONL 脚本文件

**时间单位：** ticks at 254,016,000,000/s，支持秒/帧/时间码

## EffectCraft — After Effects 替代

**能力：**
- 图层动画
- 关键帧
- 特效链
- 表达式
- 渲染队列

**常用命令族：**
- `layer.*` — 图层
- `effect.*` — 特效
- `keyframe.*` — 关键帧
- `render.*` — 渲染

## SoundCraft — Audition 替代

**能力：**
- 多轨音频编辑
- 剪辑、淡入淡出
- 效果链（EQ、压缩、混响等）
- 频谱分析
- 音频导出

**常用命令族：**
- `import.*` — 导入
- `clip.*` — 剪辑
- `effect.*` — 效果
- `bounce.*` — 导出

## DesignCraft — InDesign 替代

**能力：**
- 页面布局
- 文本框架
- 图片放置
- 母版页
- 多格式导出（PDF / EPUB / PPTX / HTML / XML）

**命令数：** 536（`designcraft-cli commands` 查看全部，`describe COMMAND` 查详情）

**调用风格：** `designcraft-cli run --cmd ID=JSON`（或 `--sample` 用内置样例文档测试）

**常用命令族：**
- `file.*` — 文档生命周期与导出（new/open/save/exportPdf/exportEpub/exportPptx/package）
- `page.*` — 页面（insert/delete/move/transition）
- `text.*` — 文本（placeCaret/insert/delete/thread/select）
- `image.*` — 图片（place/replace/fit）
- `style.*` / `table.*` / `layout.*` / `effect.*` — 样式、表格、版式、效果

> 安装位置：`C:\Program Files\DesignCraft\designcraft-cli.exe`，v0.13.0。

## LightCraft — Lightroom 替代

**能力：**
- RAW 开发
- 色调曲线
- 颜色分级
- 批量导出
- 照片管理

**常用命令族：**
- `import.*` — 导入
- `develop.*` — 开发
- `export.*` — 导出
- `catalog.*` — 目录管理

**注意：** MCP 工具数高达 318，是最细粒度的应用

## GridCraft — Excel 替代

**能力：**
- 单元格读写
- 公式计算
- 图表生成
- 排序筛选
- 透视表

**常用命令族：**
- `write.*` — 写入
- `read.*` — 读取
- `calculate.*` — 计算
- `format.*` — 格式
- `chart.*` — 图表

## WordCraft — Word 替代

**能力：**
- 文本编辑
- 段落格式
- 表格
- 页眉页脚
- DOCX 导出

**常用命令族：**
- `insert.*` — 插入
- `format.*` — 格式
- `table.*` — 表格
- `save.*` — 保存

## DeckCraft — PowerPoint 替代

**能力：**
- 幻灯片创建
- 布局模板
- 形状文本
- 动画
- 演示导出

**常用命令族：**
- `slide.*` — 幻灯片
- `shape.*` — 形状
- `animation.*` — 动画
- `export.*` — 导出

## CADCraft — AutoCAD 替代

**能力：**
- 2D 绘图
- 尺寸标注
- 图层管理
- DXF/DWG 导入导出
- PNG 渲染

**常用命令族：**
- `draw.*` — 绘图
- `dimension.*` — 标注
- `layer.*` — 图层
- `export.*` — 导出

## PdfCraft — Acrobat 替代

**能力：**
- PDF 文档信息（`info`）— 页数、作者、书签、链接、加密状态等
- 文本提取（`text`）— 按页提取文本，页间用分页符分隔
- 页面渲染（`render`）— 渲染为 PNG/JPG/TIF/PAM 图片
- 页面编辑（`edit`）— 旋转、删除、移动、插入空白页、设置标题/作者
- 合并（`combine`）— 多 PDF 合并为一
- 拆分/提取（`split` / `extract`）— 按页码范围提取或拆分
- 批量处理（`batch`）— convert/ocr/optimize 批量处理
- 文档体检（`check`）— 检查多个文件
- 伪脱敏检测（`audit`）— 检测伪脱敏（发现则失败）
- 自动化工具（`tools` / `run`）— 通过 JSON Schema 运行工具
- MCP 服务器（`mcp`）— stdin/stdout MCP 服务器
- 桌面应用控制（`ui`）— 通过控制通道驱动桌面应用

**CLI 语法：** 子命令风格（`pdfcraft-cli <子命令> [参数]`），非 Group A-E

**常用命令：**
```bash
pdfcraft-cli info <file.pdf>              # 文档信息
pdfcraft-cli text <file.pdf> --page 1     # 提取文本
pdfcraft-cli render <file.pdf> --page 1 --out page.png
pdfcraft-cli edit <in.pdf> --out out.pdf --delete 2,4
pdfcraft-cli combine a.pdf b.pdf --out merged.pdf
pdfcraft-cli split <in.pdf> --every 5 --out-dir pages/
pdfcraft-cli extract <in.pdf> --pages 1,3,5-8 --out out.pdf
pdfcraft-cli batch <dir> --steps convert,ocr,optimize --out-dir out/
```

**特殊：** 控制通道基于文件（`--control FILE`），桌面应用启动时用 `pdfcraft --control FILE`，然后 `pdfcraft-cli ui --control FILE <method>` 驱动

**安装路径：** `C:\Program Files\PdfCraft\pdfcraft-cli.exe`（默认）

## Installation

所有应用通过 ArtCraft Launcher 安装，或从 GitHub releases 直接下载：

```
https://github.com/storytold/<craft-name>/releases
```

详见 installation.md。

## Verification

安装后验证：

```bash
# 检查应用状态
artcraft-toolbox-cli apps_status

# 测试 CLI
photocraft-cli command_list | head -20

# 检查控制通道
photocraft --control 7979 --control-token-file token.txt
```

## Notes

- 所有应用处于 early alpha 阶段，重要文件请备份
- 命令数和 MCP 工具数来自 2026-10 快照，可能随版本变化
- 控制端口默认值可能变化，以启动时的输出为准
- 动态端口应用需要 `--port PORT` 指定
