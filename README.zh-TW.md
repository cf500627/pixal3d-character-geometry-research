# 風格化人物幾何研究：研究原始碼發布

本目錄整理既有 Windows AMD 推論相容工作、幾何評估工具、V2 表示讀取器與
匿名化研究報告。這是研究紀錄與工具，尚未完成可用的人物生成產品；沒有
微調模型、模型權重、訓練集或商業角色資料。本次沒有訓練或新增研究實驗。

**RELEASE_STATUS = RESEARCH_SOURCE_RELEASE；PUBLICATION = PUBLISHED。**
使用者已授權建立公開倉庫並推送這份已審閱的原始碼包。
使用者已批准自寫程式與文件採 MIT，
版權名稱為 **Pixal3D Character Geometry Research contributors**。必要的第三方
原始 LICENSE／NOTICE／版權聲明可以保留公開作者 email；私人與操作資訊仍排除。
AMD 依賴的完整乾淨安裝維持 **NOT_VERIFIED**；授權批准不能取代實際安裝驗證。
決定記錄見 [USER_DECISIONS.md](USER_DECISIONS.md)。
實際驗證範圍見 [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)。

公開倉庫：
[stylized-character-geometry-research](https://github.com/cf500627/stylized-character-geometry-research)。
原始碼包已公開發布；遠端檔案清單、逐檔內容與匿名公開讀取已核對。

## 五條既有發現

所有數字直接沿用既有報告，來源檔名、章節及定義見
[reports/SOURCES.md](reports/SOURCES.md)，本次不產生新的量測結論。

1. 同一 target 的 AMD／官方 CUDA 對照：Char-A active Jaccard **99.904090%**、
   旗標變動 **0.124523%**、頂點 L2 p95 **0.002255804 cell**。
   來源 `STAGE10B_OFFICIAL_CUDA_REFERENCE_RESULT.md`，R1 同一 B target 表。
2. 表示與 VAE 的誤差分開：Char-A FACE 絕對深度 p95，V2／官方直接 O-Voxel／
   預訓練 VAE 分別為 **0.031032h／0.225903h／6.198786h**。
   來源 `STAGE9CR_ORIENTATION_DEPTH_RESULT.md`，全部可見像素深度分布表。
3. 相近的格數仍有結構損失：Char-A recall **96.353%**、共同格旗標錯誤
   **7.397%**、頂點 L2 p95 **0.718284 cell**。
   來源 `STAGE10A_VAE_LOSS_DIAGNOSIS_RESULT.md`，B1／B2／B3。
4. 投影參數改變帶號偏移：Char-A B BODY 的深度 median，由 project=0 的
   **-1.101703h** 變為 project=0.9 的 **-0.085617h**。
   來源 `STAGE10D_OFFICIAL_POSTPROCESS_PARAMETER_SWEEP_RESULT.md`，SOURCE-visible
   逐 ROI ALL 表。負值是更靠近相機，不能直接宣稱所有表面都向外移。
5. V2 的暫定固定欄位計價達 **3,915 通道**；這不是通用最大值，也不是已完成
   的神經網路介面。來源 `V2_1024_FIXED_CHANNEL_DIAGNOSTICS_RESULT.md`，一頁結論及 A。

## AMD 推論與安裝

歷史驗證環境：Windows 10 22H2、RX 7900 XTX、Python 3.12.14、
Torch 2.9.1+rocm7.2.1、HIP 7.2。逐項版本與來源、補丁基線、安裝方式、官方權重
連結及 R1 完整對照見 [amd_windows_port/README.md](amd_windows_port/README.md)、
[CHANGELOG.md](amd_windows_port/CHANGELOG.md) 與 [VALIDATION.md](amd_windows_port/VALIDATION.md)。

補丁分別對應 Pixal3D `f7cf38429b0bd264f1995f0f8743a88b1c728b94` 與 TRELLIS.2
`75fbf0183001ed9876c8dbb35de6b68552ee08bd`。torch_native 稀疏卷積只支援前向，
不能訓練 shape SC-VAE。完整 CuMesh／nvdiffrast／FlexGEMM extension 及官方
to_glb remesh 無法在此 AMD 路徑使用，也沒有打包這些程式。
合成球體包裝重放也已通過新的原始 pinned source 副本、所附 patch／卷積 overlay
及重新編譯的 HIP hash extension 驗證。新 GPU worker 使用這份新 source 與重建
模組；latent／decoded arrays 與既有 Stage10A 參考完全一致，mesh 與先前合成
球體重放逐位元相同，並完成正常 cleanup 及成功退出。範圍記錄見
[examples/validation/REPLAY_VERIFICATION.json](examples/validation/REPLAY_VERIFICATION.json)。
這項 source／build 檢查仍沿用已安裝的 Torch／HIP、O-Voxel I/O 與官方權重；
AMD 依賴的完整乾淨安裝維持 **NOT_VERIFIED**。

## 合成球體 CPU 範例

使用新的 Python 3.12 環境：

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r eval_harness/requirements.txt
```

接著依 [eval_harness/README.md](eval_harness/README.md) 編譯既有 CPU 量測工具，
以設定檔選擇自己的執行檔及新輸出目錄，重放固定鏡頭的球體 identity control。
例子只使用 Stage10A 自行生成的封閉球體：**2,562 頂點／5,120 面**，
**629,228 個 SOURCE 可見像素**；來源為 Stage10A 報告 A1。
設定檔使用相對路徑；實際執行位置由使用者指定。發布 QA 是重現與包裝驗證，
不產生新的研究結論。完整容量審计、固定渲染及其他研究程式的限制見工具說明。

## V2、結論與未解問題

[v2_representation/](v2_representation/README.md) 提供原樣純函式及 schema 摘錄，
省略綁定舊機器的 launcher，沒有修改組裝數學。這是研究程式碼，沒有完整 producer
或三視圖模型；固定 latent／support 測試尚未學習圖片條件或 occupied cells。
G3D LINK02 仍有 **51 條 pointer 錯誤、72 個 sign 錯誤及 9 個未引用 patch**，
無法得到合法自由解碼網格；來源 G3D LINK02 `RESULT.md` 實測比較。
FP16／BF16 精度敏感性見 [LIMITATIONS.md](v2_representation/LIMITATIONS.md)。

[FINDINGS.md](reports/FINDINGS.md) 區分表示、VAE 與後處理的損失定義；
[POSTPROCESS_FINDINGS.md](reports/POSTPROCESS_FINDINGS.md) 整理投影、面數與解析度；
[OPEN_QUESTIONS.md](reports/OPEN_QUESTIONS.md) 記錄已關閉路線及未解問題。
待查項目包括 B@1536 的 NaN 匯出、只微調 decoder、project=1.0 與只修朝向。
兩份英文 issue 僅存於 [drafts/issues/](drafts/issues/)，沒有發出。

**USER_VISUAL_ACCEPTANCE = PENDING。** 沒有自動挑選視覺勝者；幾何 TrueNormal
也不代表切線法線貼圖接縫已修復。

## 素材、授權與致謝

量測使用三個未包含在本發布中的商業風格化角色模型，以 Char-A／Char-B／Char-C
匿名表示；後處理 sweep 只量了其中兩個。沒有角色具名對照、素材清單、衍生網格、
target、latent、渲染、角色比較頁、逐像素陣列或權重。範例僅使用獨立生成的球體。

自寫程式與文件採使用者已批准的 MIT，版權名稱為
**Pixal3D Character Geometry Research contributors**。上游衍生檔保留原授權、
NOTICE 與版權聲明；必要聲明內的公開作者 email 可保留。
見 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)、[FILE_PROVENANCE.csv](FILE_PROVENANCE.csv)
及待決清單。授權不明的檔案不納入。

致謝 Pixal3D、TRELLIS.2、Direct3D-S2、NumPy、PyTorch 與 AMD ROCm/HIP。
Direct3D-S2 僅有現存 Pixal3D NOTICE 的 attribution，未打包其程式碼。
這份已審閱的原始碼包已公開發布。兩份 upstream issue 草稿
仍未提交；本次發布請求沒有授權另發公開貼文。
