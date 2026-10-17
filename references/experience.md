# 分发经验（huashu-design）

跨项目复现过、或测量过、对任何用户都成立的发现。`learn.py` 开工前会按主题把匹配的条目带出来。

维护规则见 `references/evolution.md`：只在仓库里手改；reference 吸收了某条就删掉它；一个用户的口味不进这里。

## S1 · verified · topics: direction, color, typography

- 发现：不加约束时，三个方向会一起滑向暖奶油底＋高反差衬线标题＋陶土色点缀。这是模型自己的默认审美（Anthropic 的交互配色），Anthropic 官方 frontend-design skill（2026）把它列为 AI 生成页面的头号特征。
- 下次：想法卡阶段最多允许一张落在「浅暖底＋衬线」；`design_lint.py compare` 会报家族重合。
- 证据：skill 自测的三版咖啡站、多个真实项目的三方向截图都落在这里（2026-10 盘点）；官方原文 https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md

## S2 · verified · topics: direction, layout

- 发现：三版只换配色字体、共用一个布局骨架，评审和用户都会一眼认出是换皮。差异要落在信息的组织方式上。
- 下次：三张想法卡的「信息组织方式」必须各不相同；`compare` 的骨架相关过高就回到卡片重做。
- 证据：盲测评审；2026-10 盘点里调研报告、说明书、数据看板三组三方向都是同一骨架。

## S3 · verified · topics: readability, quiet, whitespace

- 发现：安静、奢侈留白的风格做过头会变成大片死白加微缩字号，第一眼像页面没渲染完，输给普通的基线版本。
- 下次：正文 ≥14px（deck ≥24px）、标签 ≥12px、对比度 ≥4.5:1 是任何风格都不豁免的底线；`design_lint.py check` 会亮红灯。
- 证据：盲测评审；skill 自测咖啡站有 28 处小于 12px 的文字。

## S4 · verified · topics: assets, logo, single-file

- 发现：要双击打开的单文件 HTML，用相对路径引用图片和 logo，挪个目录就全部裂图。
- 下次：单文件交付一律 base64 内嵌；`design_lint.py check` 报图裂。
- 证据：盲测里六个产品按钮全部裂图直接输掉评审。

## S5 · verified · topics: review, taste

- 发现：审查 agent 给的高分不等于用户买账，评审打分会系统性地偏向「规整、克制」的版本。
- 下次：评审只用来找事实问题和明显缺陷；品味的最终判断以用户的选择为准，冲突时把用户的话记成 preference。
- 证据：多个项目里 9 分以上的版本被用户否掉、低分版本被选中。
