# Benchmarks Directory

パフォーマンスベンチマークスクリプト集

## 📁 Available Benchmarks

### 1. `benchmark.py` - 完全なベンチマークスイート

全64関数の包括的なベンチマーク。

**実行**:
```bash
just gmt-benchmark
# または
uv run python benchmarks/benchmark.py
```

### 2. `quick_benchmark.py` - クイックベンチマーク

単一の操作を素早くベンチマークします。

**使い方**:
```bash
# basemapをベンチマーク（デフォルト）
uv run python benchmarks/quick_benchmark.py

# 特定の操作をベンチマーク
uv run python benchmarks/quick_benchmark.py plot
uv run python benchmarks/quick_benchmark.py coast
uv run python benchmarks/quick_benchmark.py info
```

**出力例**:
```
BASEMAP BENCHMARK
[pygmt_nb]
  Average: 3.10 ms
  Min/Max: 2.70 - 3.93 ms

[PyGMT]
  Average: 61.82 ms
  Min/Max: 59.10 - 63.27 ms

🚀 Speedup: 19.94x faster with pygmt_nb
```

### 3. `real_world_benchmark.py` - 実世界ワークフロー

アニメーション生成、バッチ処理など、実世界のユースケースをベンチマーク。

**使い方**:
```bash
# 完全版（100フレーム、10データセット）
uv run python benchmarks/real_world_benchmark.py

# クイック版（10フレーム、5データセット）
uv run python benchmarks/real_world_benchmark_quick.py
```

**シナリオ**:
- **Animation**: 100フレームのアニメーション生成
- **Batch Processing**: 10データセットのバッチ処理
- **Parallel Processing**: マルチコアでの並列レンダリング

## 📊 Output Files

ベンチマーク結果は `output/benchmarks/` に保存されます：

- `output/benchmarks/quick_*.ps` - クイックベンチマークの出力
- `output/benchmarks/animation/` - アニメーションフレーム
- `output/benchmarks/batch/` - バッチ処理結果
- `output/benchmarks/parallel/` - 並列処理結果

## 📖 関連ドキュメント

- [../docs/BENCHMARK_VALIDATION.md](../docs/BENCHMARK_VALIDATION.md) - ベンチマーク検証レポート
- [../docs/REAL_WORLD_BENCHMARK.md](../docs/REAL_WORLD_BENCHMARK.md) - 実世界ベンチマーク結果
- [../docs/PERFORMANCE.md](../docs/PERFORMANCE.md) - パフォーマンス分析

## 💡 Tips

### ベンチマークの追加

新しいベンチマークを追加する場合：

1. `quick_benchmark.py` を参考に新しい関数を作成
2. `output_root` を使って出力先を指定
3. 10回の反復でタイミングを測定
4. 平均・最小・最大を表示

### カスタマイズ

- **iterations**: 反復回数（デフォルト: 10）
- **output_root**: 出力先ディレクトリ（自動作成）
