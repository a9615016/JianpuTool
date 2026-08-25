# 部署到 Streamlit Community Cloud（含每月 99 付費牆）

## 這次加入了什麼

- 新增 `paywall.py`：簡易「授權碼」付費牆
  - 使用者要先輸入授權碼才能看到轉換功能
  - 授權碼可以用 `代碼:2026-08` 這種格式，讓它「只在當月有效」，
    很適合「每月 99」這種訂閱情境：你每個月手動發一組新代碼給付款的人就好
  - 目前**沒有接真的金流**，付款方式先用轉帳 / LINE Pay 等人工收款，
    之後要接 Stripe 或綠界時，只要把 `paywall.py` 裡「輸入授權碼」那段
    換成「金流付款成功後自動核發代碼」即可，其他頁面完全不用改
- 新增 `packages.txt`：讓 Streamlit Cloud 安裝 `ffmpeg`、`lilypond` 等系統套件
- 新增 `access_codes.example.txt`：授權碼設定範例（**沒有用到 `.streamlit` 資料夾**）

## 授權碼怎麼設定（兩種方式，擇一即可）

`paywall.py` 會依序找授權碼，找到就用：

1. **Streamlit Cloud 後台 Secrets（正式上線建議用這個）**
   到 App 的 **Settings → Secrets**，直接在網頁上貼上：

   ```toml
   ACCESS_CODES = [
       "JIANPU-2026-08:2026-08",
   ]
   ```

   這個只存在 Streamlit 後台，**不會出現在你的 GitHub repo 裡**，也完全不需要
   建立 `.streamlit` 資料夾。之後每個月要收費，回來這裡把新代碼加進清單即可。

2. **根目錄的 `access_codes.txt`（本機測試用）**
   複製 `access_codes.example.txt`，改名為 `access_codes.txt`，一行一組代碼：

   ```text
   TEST99
   JIANPU-2026-08:2026-08
   ```

   這個檔案已經在 `.gitignore` 裡被排除，就算你把整包資料夾推上 GitHub，
   也不會被上傳。**如果雲端後台的 Secrets 有設定，會優先用 Secrets**，
   `access_codes.txt` 主要是給本機開發測試方便用的。

## 部署步驟

1. 把整個 `JianpuTool` 資料夾推到一個 **GitHub repo**（public 或 private 都可以）
   - 記得**不要**把你本機測試用的 `access_codes.txt` 上傳（`.gitignore` 已經
     幫你排除，除非你是用網頁拖拉上傳，那樣要自己手動不要選這個檔案）
   - 建議先刪掉 `outputs/`、`demucs_test*/`、`*.pdf`、`*.mid`、`*.wav`、`*.mp3` 等
     測試產生的檔案，這些不需要上傳，會讓 repo 變得很肥大
2. 到 https://share.streamlit.io 用 GitHub 帳號登入
3. 選擇「New app」，選你剛剛的 repo，Main file 填 `streamlit_app.py`
4. 部署前先到 App 的 **Settings → Secrets**，貼上正式的授權碼（見上面第 1 種方式）
5. 按下 Deploy，等待安裝套件（第一次會比較久，因為要裝 TensorFlow / Demucs 等）

## ⚠️ 重要限制（請務必先看過）

這個工具本身用到 **TensorFlow + BasicPitch + Demucs + LilyPond**，
屬於偏重的音訊 / AI 處理流程：

- Streamlit Community Cloud **免費方案**記憶體只有 1GB，
  Demucs 人聲分離 + BasicPitch 分析在處理較長歌曲時，
  **有蠻高機率會記憶體不足或執行逾時**
- `packages.txt` 只能透過 `apt-get` 安裝 LilyPond，
  版本會跟原本 Dockerfile 指定的 `2.22.2` 不同（會抓 Debian 內建版本），
  多數情況下 `jianpu-ly` 仍可運作，但無法保證輸出的簡譜排版跟你原本測試的
  結果 100% 一致
- 如果之後發現免費方案跑不動，建議兩個方向：
  1. 升級 Streamlit Cloud 方案，或改用有更多資源的平台（例如你原本 Dockerfile
     設定的 Hugging Face Spaces，也可以直接沿用同一個付費牆邏輯）
  2. 把 Demucs / BasicPitch 這種重運算搬到後端 API（`main.py` 那支 FastAPI
     已經有雛形），Streamlit 只負責前端上傳與付費驗證

付費牆本身（`paywall.py`）跟資源多寡無關，兩種部署方式都可以直接用。

## 之後要接 Stripe / 綠界時怎麼做

1. 打開 `paywall.py`
2. 把 `require_access()` 裡「輸入授權碼」的表單，換成：
   - 呼叫 Stripe Checkout / 綠界訂單 API 產生付款連結
   - 付款完成後，透過 webhook 把 `st.session_state["paywall_unlocked"] = True`
     （或是寫入資料庫記錄該使用者已付費，改用登入帳號比對，而不是單純 session）
3. `streamlit_app.py` 其他部分完全不用改，因為都是呼叫 `require_access()` 這個
   統一的入口
