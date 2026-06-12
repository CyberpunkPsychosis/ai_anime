#!/usr/bin/env python3
"""按镜头编号拼接视频片段，快速生成预览成片。

用法:
    python3 scripts/assemble.py episodes/ep01

将 episodes/ep01/05_clips/ 下的 shot_*.mp4 按编号排序拼接，
输出到 episodes/ep01/07_final/preview.mp4。需要本机安装 ffmpeg。
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(f"用法: python3 {sys.argv[0]} episodes/ep01")

    episode = Path(sys.argv[1])
    clips_dir = episode / "05_clips"
    out_dir = episode / "07_final"

    clips = sorted(clips_dir.glob("shot_*.mp4"))
    if not clips:
        sys.exit(f"{clips_dir} 下没有找到 shot_*.mp4，请先完成图生视频步骤")

    print(f"找到 {len(clips)} 个片段:")
    for c in clips:
        print(f"  {c.name}")

    out_dir.mkdir(parents=True, exist_ok=True)
    concat_list = out_dir / "concat_list.txt"
    concat_list.write_text(
        "".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8"
    )

    output = out_dir / "preview.mp4"
    # 各工具生成的片段编码参数不一致，统一重编码后拼接最稳
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24",
        "-c:a", "aac",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    concat_list.unlink()
    print(f"\n完成: {output}")


if __name__ == "__main__":
    main()
