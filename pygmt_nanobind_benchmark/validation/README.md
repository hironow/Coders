# Validation Directory

出力検証・比較スクリプト集

## 📁 Available Scripts

### 1. `validate_output.py` - 出力検証

pygmt_nbとPyGMTの出力が同一であることを検証します。

**使い方**:
```bash
uv run python validation/validate_output.py
```

**検証内容**:
- ファイルサイズ比較
- PostScriptヘッダー確認
- PNG変換後のピクセル単位比較（ImageMagick使用）

**出力例**:
```
TEST: Basemap
[Validating pygmt_nb output...]
  ✓ File size: 23,308 bytes
  ✓ Valid PostScript header

[Comparing outputs...]
  pygmt_nb: 23,308 bytes
  PyGMT:    23,280 bytes
  Ratio:    1.001x
  ✓ File sizes are similar

[Converting to PNG for pixel comparison...]
  RMSE: 0 (0)
  ✅ Images are identical!
```

### 2. `compare_operation.py` - 操作比較

特定のGMT module functionをpygmt_nbとPyGMTで詳細比較します。

**使い方**:
```bash
# info関数を比較
uv run python validation/compare_operation.py info

# select関数を比較
uv run python validation/compare_operation.py select

# blockmean関数を比較
uv run python validation/compare_operation.py blockmean

# makecpt関数を比較
uv run python validation/compare_operation.py makecpt
```

**出力例**:
```
COMPARING: info
Test data: output/validation/test_data.txt
  1000 random points in [0, 10] × [0, 10]

[pygmt_nb]
  Time: 10.34 ms
  Result:
  0 10 0 10

[PyGMT]
  Time: 10.57 ms
  Result:
  0 10 0 10

[Comparison]
  Speedup: 1.02x
  ✅ Results are identical
```

### 3. その他の検証スクリプト

- `validate_basic.py` - 基本的な検証
- `validate_detailed.py` - 詳細な検証
- `validate_pixel_identical.py` - ピクセル単位の比較
- `visual_comparison.py` - 視覚的比較
- `benchmark_validation.py` - ベンチマーク検証

## 📊 Output Files

検証結果は `output/validation/` に保存されます：

- `output/validation/*.ps` - pygmt_nb出力
- `output/validation/*.eps` - PyGMT出力
- `output/validation/*.png` - PNG変換結果
- `output/validation/test_data*.txt` - テストデータ

## 🎯 Use Cases

### デバッグ時
特定の関数の実装を確認したい場合：
```bash
uv run python validation/compare_operation.py info
```

### 正確性検証
出力が本当に同一か確認したい場合：
```bash
uv run python validation/validate_output.py
```

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
