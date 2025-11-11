# Validation Directory

出力検証・比較スクリプト集

## 📁 Main Validation

### `validate.py` - 包括的検証スイート

全ての検証機能を統合した完全版。以下を含みます：

1. **Output Validation** - 出力ファイル検証（basemap, coast, plot）
2. **Operation Comparison** - 操作比較（info, select, blockmean, makecpt）

**実行**:
```bash
uv run python validation/validate.py
```

**結果例**:
```
✅ Total Passed: 6/7 (86%)
📁 Output Directory: output/validation/

Output Validation:
  Basemap              ✅ PASS
  Coast                ✅ PASS
  Plot                 ✅ PASS
  Passed: 3/3 (100%)

Operation Comparison:
  info                 ❌ FAIL
  select               ✅ PASS
  blockmean            ✅ PASS
  makecpt              ✅ PASS
  Passed: 3/4 (75%)
```

### 検証内容詳細

**Output Validation:**
- ファイルサイズ比較
- PostScriptヘッダー確認
- 出力ファイルの妥当性検証

**Operation Comparison:**
- 実行時間比較
- 出力結果の一致性確認
- 機能レベルでの互換性検証

## 📊 Output Files

検証結果は `output/validation/` に保存されます：

- `validate_basemap_nb.ps` / `validate_basemap_pygmt.eps` - Basemap出力
- `validate_coast_nb.ps` / `validate_coast_pygmt.eps` - Coast出力
- `validate_plot_nb.ps` / `validate_plot_pygmt.eps` - Plot出力
- `test_data.txt` / `test_data_xyz.txt` - テストデータ
- `validation_results.txt` - 検証結果ログ

## 📝 Requirements

- **必須**: pygmt_nb（ビルド済み）
- **必須**: PyGMT（比較用）
- **オプション**: ImageMagick（ピクセル比較用）

**ImageMagickのインストール**:
```bash
# macOS
brew install imagemagick

# Ubuntu
sudo apt-get install imagemagick
```

## 🔧 Troubleshooting

### "PyGMT not available"
```bash
pip install pygmt
```

### "ImageMagick 'compare' not found"
```bash
brew install imagemagick  # macOS
```

### "Module 'pygmt_nb' not found"
```bash
pip install -e .
```

## 📖 関連ドキュメント

- [../docs/BENCHMARK_VALIDATION.md](../docs/BENCHMARK_VALIDATION.md) - ベンチマーク検証レポート
- [../docs/VALIDATION.md](../docs/VALIDATION.md) - バリデーション結果
- [../benchmarks/](../benchmarks/) - ベンチマークスクリプト
