"""Record completed safe-window installation; do not relabel it as game testing."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'backups/questbook_v6_20261017'
install=json.loads((B/'installation.json').read_text(encoding='utf-8'));assert install['installed'] and install['all_hashes_match']
for name in ['README.md','HANDOVER.md','资料库总索引.md','交接启动词_规划AI.md','GLM_交接启动词.md']:
    p=R/'docs'/name;s=p.read_text(encoding='utf-8')
    s=s.replace('第6版任务已改写、尚未安装','第6版任务已备份安装到test')
    s=s.replace('test客户端仍在运行，未覆盖实例、未操作游戏或存档、母本未同步。下方第5版安装记录为已退回的历史版本，不代表第6版已在游戏中生效。',
        '客户端退出后已于23:18备份安装到test，79份文件逐件哈希一致；独立测试世界另有备份，原世界文件元数据与options哈希未变。未启动或操作游戏，母本未同步，游戏验收仍由用户负责。下方第5版安装记录为历史版本。')
    p.write_text(s,encoding='utf-8')
p=R/'docs/交接启动词_通用规则.md';s=p.read_text(encoding='utf-8').replace('当前游戏仍是第5版，不能声称第6版已安装。','第6版已于客户端退出后备份安装到test；79份文件哈希一致，游戏验收未做，母本未同步。')
p.write_text(s,encoding='utf-8')
p=R/'docs/FTB任务v6_王途与分级武库重写.md';s=p.read_text(encoding='utf-8')
s=s.replace('任务已在仓库落盘并制作独立更新包；发现test游戏进程仍在运行，因此没有覆盖实例，也没有操作任何世界或进行游戏测试。',
    '任务已在仓库落盘并制作独立更新包。先发现test进程在运行；随后确认客户端退出，已于23:18备份并安装到test，79份游戏文件逐件哈希一致。未启动或控制游戏，未改写世界存档，未做游戏验收。')
s=s.replace('游戏测试继续交由用户；本轮未启动、关闭或自动操作游戏，未安装到正在运行的test，也未同步母本。',
    '游戏测试继续交由用户；本轮未启动、关闭或自动操作游戏，安装在客户端已退出的安全窗口进行，未同步母本。旧任务与相关脚本、原独立测试世界备份位于`backups/questbook_v6_20261017/test_before_install_20261017_231846`。原世界全部文件元数据和options的SHA-256保持不变；原任务目录另在实例FTB目录保留了带时间戳的恢复副本。安装证据为`backups/questbook_v6_20261017/installation.json`。')
p.write_text(s,encoding='utf-8')
print('Recorded v6 installed; gameplay acceptance remains user-owned')
