[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/Sixtyseconds5/ai-excited/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/Sixtyseconds5/ai-excited/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

# Golden Koi from a Teacup

A golden koi bursts out of a small blue-and-white porcelain teacup into a deep indigo, star-filled sky, water exploding in golden light — with a tiny paper boat riding on its back. The image is drawn entirely in pure Python (standard library only), so it renders anywhere with no dependencies.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024×683). The output is fully deterministic: one fixed seed drives every star and droplet, so repeated runs produce byte-identical files.

Built for the [ai-excited-01 bounty on make.fun](https://make.fun/bounty/ai-excited-01).
