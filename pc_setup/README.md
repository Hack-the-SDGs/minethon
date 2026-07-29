# pc_setup — 標記學生 PC

**工作人員用，每台學生電腦跑一次。** 學員不需要看這份。

目的：讓學員能寫 `create_bot("g_swim")` 而不用打伺服器位址與帳密。

## 怎麼用

```bash
python pc_setup/build_setup.py     # 產生 setup.sh / setup.ps1
```

然後在每台學生電腦上跑其中一支（macOS / Linux 用 `.sh`，Windows 用 `.ps1`）：

```bash
./pc_setup/setup.sh
```

它會寫出 `~/.htsdg.json`：

```json
{"group": 3, "computer": 24}
```

主機名稱符合 `CSIE-PC<編號>` 時（大小寫不拘、前導零會去掉）電腦編號直接從名稱取，
組別由 `GROUP_RANGES` 查表。**不符合就改問工作人員**，兩個數字都要手動輸入。

## 為什麼要有 build_setup.py 這一層

`setup.sh` 與 `setup.ps1` 都是**生成物**，不要手改——改了下次重跑就被蓋掉。

編號 → 組別的對照表只寫在 `build_setup.py` 的 `GROUP_RANGES` 一處，
bash 與 PowerShell 兩份查表函式都從它生成，所以兩邊**不可能漂移**。
`_selfcheck()` 會在生成前驗證沒有電腦編號被分到兩個組。

要改分組，改 `GROUP_RANGES` 然後重跑 `build_setup.py`，兩支腳本一起更新。

目前涵蓋 **6 組、電腦編號 1–67**（30 號刻意不屬於任何組）。

## 學員端會發生什麼

`create_bot("g_swim")` → `_event_login.resolve_account()` 讀 `~/.htsdg.json`：

| 寫法 | 使用者名稱 | 帳號類型 |
| --- | --- | --- |
| `create_bot("g_swim")` | `G<組別>_swim` | 組別共用 |
| `create_bot("swim")` | `U<電腦編號>_swim` | 個人 |

`g-` 與 `g_` 兩種前綴都接受，但**產生的使用者名稱一律用 `_`**——伺服器不接受 `-`。

密碼由組別／電腦編號推導，伺服器位址與 Drasl 驗證端點寫在
`src/minethon/_event_login.py` 的 `_DEFAULTS`。

識別檔不存在，或內容壞掉（不是 JSON、缺欄位、值是 `null`／字串／陣列、
整份是 `[]` 或裸數字），學員都會看到中文訊息叫他找工作人員重跑 setup，
**不是 traceback**。這些情況由 `tests/unit/test_event_login.py` 逐一覆蓋——
學員只被教到「看懂錯誤原因」，這條路徑不能讓他們看到 Python 例外。

## 安全性

密碼推導規則與 salt 都在會被 import 的程式碼裡，**對讀得懂 SDK 的人不是秘密**。
這是刻意的取捨：營期 5 天、隊輔在場、學員是初學者，威脅模型不成立。
真正的帳號保護在伺服器端（賽事期間限定、rate limit）。

賽後若要把 minethon 發到 PyPI，先把 `_DEFAULTS` 與 salt 抽出去——
那不是安全問題，是賽事設定不該混進通用 SDK。

背景與完整推導見 [`docs/review/findings.md`](../docs/review/findings.md) 的 F-01。
