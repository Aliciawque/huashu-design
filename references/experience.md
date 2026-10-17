# 分发经验（huashu-design）

跨项目复现过、或测量过、对任何用户都成立的发现。`learn.py` 开工前会按主题把匹配的条目带出来。

维护规则见 `references/evolution.md`：只在仓库里手改；reference 吸收了某条就删掉它；一个用户的口味不进这里。

## S1 · verified · topics: direction, color, typography

- 发现：不加约束时，三个方向会一起滑向暖奶油底＋高反差衬线标题＋陶土色点缀。这是模型自己的默认审美（Anthropic 的交互配色），Anthropic 官方 frontend-design skill（2026）把它列为 AI 生成页面聚类特征的第一条。
- 下次：想法卡阶段最多允许一张落在「浅暖底＋衬线」；`design_lint.py compare` 会报家族重合。
- 证据：skill 开发期的内部自测与多个项目的三方向截图（2026-10 盘点，未公开）；官方原文 https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md

## S2 · verified · topics: direction, layout

- 发现：三版只换配色字体、共用一个布局骨架，评审和用户都会一眼认出是换皮。差异要落在信息的组织方式上。
- 下次：三张想法卡的「信息组织方式」必须各不相同；`compare` 的骨架相关过高就回到卡片重做。
- 证据：skill 开发期的内部盲测与 2026-10 盘点（未公开）。

## S3 · verified · topics: readability, quiet, whitespace

- 发现：安静、奢侈留白的风格做过头会变成大片死白加微缩字号，第一眼像页面没渲染完，输给普通的基线版本。
- 下次：字号与对比度底线（网页正文 ≥14px、deck ≥24px、手机长图 ≥36px 画布像素，对比度 ≥4.5:1）任何风格都不豁免；`design_lint.py check` 会亮红灯。
- 证据：skill 开发期的内部盲测评审（未公开）。

## S4 · verified · topics: assets, logo, single-file

- 发现：要双击打开的单文件 HTML，用相对路径引用图片和 logo，挪个目录就全部裂图。
- 下次：单文件交付一律 base64 内嵌；`design_lint.py check` 对相对路径图片亮黄灯、对已裂的图亮红灯。
- 证据：盲测里六个产品按钮全部裂图直接输掉评审。
