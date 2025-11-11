# Benchmarks Directory

パフォーマンスベンチマークスクリプト集

## 📁 Main Benchmark

### `benchmark.py` - 包括的ベンチマークスイート

全てのベンチマークを統合した完全版。以下を含みます：

1. **Basic Operations** - 基本操作（basemap, plot, coast, info）
2. **Function Coverage** - 関数カバレッジ（histogram, makecpt, select, blockmean）
3. **Real-World Workflows** - 実世界ワークフロー（animation, batch processing）

**実行**:
```bash
uv run python benchmarks/benchmark.py
```

**結果例**:
```
🚀 Average Speedup: 9.78x faster with pygmt_nb
   Range: 0.99x - 21.22x
   Benchmarks: 10 tests

💡 Key Insights:
   - pygmt_nb provides 9.8x average performance improvement
   - Direct GMT C API via nanobind (zero subprocess overhead)
   - Modern mode session persistence (no repeated session creation)
   - Consistent speedup across basic operations and complex workflows
```

結果は `output/benchmark_results.txt` に保存されます。

### その他のベンチマークスクリプト

個別のベンチマークスクリプトも利用可能（後方互換性のため）:

- `quick_benchmark.py` - 単一操作のクイックベンチマーク
- `real_world_benchmark.py` - 実世界ワークフロー（完全版）
- `real_world_benchmark_quick.py` - 実世界ワークフロー（クイック版）

**推奨**: 統合された `benchmark.py` を使用してください。

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
