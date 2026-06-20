# 本地 Mac 部署方案（交给本地 Claude Code 执行）

> 这份文档是给「本地 Mac 上的 Claude Code」看的执行手册。
> 目标：在用户的 Mac（Apple Silicon，24G 统一内存）上，用 **Draw Things** 本地、免费、无限抽卡地
> 完成动漫短片《放学后的橡皮》的出图和图生视频。

## 0. 背景与现有素材

- 项目仓库里 `production/` 下已有：
  - 剧本：`production/episodes/ep01/01_script/script.md`
  - **分镜表（最重要）**：`production/episodes/ep01/03_storyboard/storyboard.md`
    —— 里面每个镜头都有「出图提示词」和「运动提示词」，以及角色提示词速查表
  - 拼接脚本：`production/scripts/assemble.py`
- 产出要存到对应目录：角色图 `02_characters/`、首帧图 `04_frames/`、视频 `05_clips/`、成片 `07_final/`

## 1. 为什么用 Draw Things（不用 ComfyUI）

- Mac 的 MPS 后端**不支持 Float8**，ComfyUI 跑 Wan 2.2 会报 `Float8_e4m3fn ... MPS backend` 错误。
- Draw Things 是 Apple Silicon 原生、自研 Metal FlashAttention v2，比 ComfyUI 快 20-40%。
- 24G 统一内存 CPU/GPU 共享，没有独显的"VRAM 不够"问题。
- Draw Things 自带 **MCP Server / API Server**，本地 Claude Code 可直接驱动它，不用手点。

## 2. 安装与模型（本地 Claude Code 执行 + 用户配合 GUI 操作）

> Draw Things 是 GUI App，模型下载在 App 内完成；Claude Code 负责驱动 API，
> 但**安装和首次下模型这步需要用户在 App 界面点几下**，请引导用户完成。

1. **装 Draw Things**：Mac App Store 搜 "Draw Things"，免费。
2. **下出图模型**（角色立绘 + 首帧图用，二次元向）：
   - 在 Draw Things 模型管理里下载一个**动漫向 SDXL 模型**，推荐 Illustrious / NoobAI / Animagine 系列
     （这类对日系动漫、赛璐璐上色最对口；24G 跑 SDXL 毫无压力）。
3. **下视频模型**（图生视频用）：
   - 下载 **Wan 2.2 Image-to-Video**，选 **Q8 量化**版本（24G 内存的推荐档）。
   - 若 Wan 2.2 太慢或不稳，备选更轻的 **Wan 2.1 I2V** 或 **LTX-Video**。

## 3. 打开 API / MCP Server（让本地 Claude Code 能调）

- 在 Draw Things 设置里启用 **API Server**（HTTP，默认本机端口，记下端口号）。
- 如要用 MCP：Draw Things 提供 MCP Server，可把它接到本地 Claude Code 的 MCP 配置里，
  Claude Code 即可直接调用"生图/生视频"工具。
- ⚠️ **本地 Claude Code 注意**：Draw Things 的 API 端点 / MCP 工具名以**当前版本的官方文档/设置页为准**，
  先在设置里确认实际端口和接口，再写调用代码，别照搬假设的字段。

## 4. 出角色立绘（text2image）

用分镜表文末「角色提示词速查表」里的提示词，每个角色出一张正面立绘，纯色背景：
- 小羽 → 存 `02_characters/xiaoyu_front.png`
- 凛 → 存 `02_characters/rin_front.png`
- 比例用 3:4（竖），抽到满意为止（本地免费，多抽几张挑）。
- ✅ 这是最关键的一步：立绘定了，后面所有镜头垫这张图保证不换脸。

## 5. 逐镜头出首帧图（text2image，垫角色参考图）

读 `03_storyboard/storyboard.md`，对每个 shot：
- 用该镜头的「出图提示词」+ 对应角色立绘作为参考图（Draw Things 的 image-to-image / 参考图功能）。
- 比例按镜头景别选（远景 16:9，近景/特写可 16:9 保持统一）。
- 每镜抽 3-5 张挑一张，存 `04_frames/shot_01.png`、`shot_02.png` …（编号对齐分镜表）。

## 6. 逐镜头图生视频（image2video，Wan 2.2）

对每张首帧图：
- 输入 = `04_frames/shot_XX.png`，提示词 = 该镜头的「运动提示词」。
- 时长选 5 秒，输出 `05_clips/shot_XX.mp4`。
- Draw Things 可导出 ProRes 4444（带 alpha、无损），剪辑质量好；预览用 mp4 即可。
- ⚠️ 24G Mac 上 Wan 视频较慢（每条可能数分钟），但免费、可无限抽卡。
  建议先低步数/低分辨率快抽预览，满意的镜头再高质量重跑。

## 7. 拼接成片

```bash
python3 production/scripts/assemble.py production/episodes/ep01
```
按编号拼接 `05_clips/shot_*.mp4` → 输出 `07_final/preview.mp4`（需本机有 ffmpeg：`brew install ffmpeg`）。
精剪、配音、字幕用剪映。

## 8. 性能预期与省时技巧

- 出图（SDXL）：每张几秒~十几秒，很快，随便抽。
- 视频（Wan 2.2 Q8）：每条 5 秒片段可能 2-10 分钟，取决于步数/分辨率。
- 省时：① 视频先用低分辨率 + 少步数批量出草稿，定节奏；② 只对保留镜头出高清；
  ③ 16 个镜头可分批跑，挂着让它出。

## 9. 给本地 Claude Code 的执行顺序小结

1. 确认 Draw Things 已装、API/MCP Server 已开、出图模型 + Wan 2.2 已下载（缺则引导用户在 App 内下）。
2. 读 `03_storyboard/storyboard.md` 拿全部提示词。
3. 出 2 张角色立绘 → 用户挑 → 存 `02_characters/`。
4. 逐镜头出首帧图（垫立绘）→ 存 `04_frames/`。
5. 逐镜头图生视频 → 存 `05_clips/`。
6. 跑 `assemble.py` 出预览。
7. 全程：生成是异步/较慢的，给用户进度反馈；抽卡结果让用户参与挑选。
