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
| DesignCraft | InDesign | 446 | 25 | 动态 |
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
- PDF 导出

**常用命令族：**
- `page.*` — 页面
- `text.*` — 文本
- `image.*` — 图片
- `export.*` — 导出

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
- PDF 读取
- 页面操作（合并、拆分、旋转）
- 文本提取
- 格式转换（PDF↔图片）
- 表单填写

**常用命令族：**
- `read.*` — 读取
- `merge.*` / `split.*` — 合并拆分
- `export.*` — 导出
- `form.*` — 表单

**特殊：** 控制通道基于文件（`--control FILE`）

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
