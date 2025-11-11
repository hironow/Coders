# Phase 3 Implementation Plan

**対象**: tesseract_nanobind v0.3.0 → v0.4.0
**目標**: Iterator APIとレイアウト解析の完成度向上
**優先度**: 中

---

## 📋 実装予定機能

### 1. 基本Iterator API (優先度: 高)

#### ResultIterator クラス
Phase 3では、完全な30+メソッドではなく、**最も使用頻度の高い基本メソッド**のみを実装：

**実装メソッド** (6-8個):
1. ✅ `GetUTF8Text(level)` - レベル別テキスト取得
2. ✅ `Confidence(level)` - 信頼度取得
3. ✅ `BoundingBox(level)` - バウンディングボックス取得
4. ✅ `Next(level)` - 次の要素へ移動
5. ✅ `Empty(level)` - 空チェック
6. ✅ `WordRecognitionLanguage()` - 言語取得
7. ⚠️ `Begin()` - 最初に戻る（オプション）
8. ⚠️ `IsAtBeginningOf(element, level)` - 位置チェック（オプション）

**スキップするメソッド** (Phase 4以降):
- フォント属性 (WordFontAttributes)
- ベースライン (Baseline)
- 方向性 (Orientation, WordDirection)
- 辞書チェック (WordIsFromDictionary)
- デバッグ情報 (GetBlamerDebug, GetBlamerMisadaptionDebug)
- 真理値 (WordTruthUTF8Text, EquivalentToTruth)
- 高度な機能 (30+メソッド)

**実装方針**:
- C++でResultIteratorWrapperクラスを作成
- TessBaseAPI::GetIterator()を呼び出し
- Pythonから使いやすいインターフェースを提供
- メモリ管理を適切に実装

---

### 2. 追加レイアウト解析メソッド (優先度: 中)

#### GetWords (1メソッド)
**機能**: 単語レベルのコンポーネント取得（GetComponentImagesの特化版）

```python
GetWords() -> list[tuple[str, int, int, int, int, int]]
# 戻り値: [(word, confidence, x, y, w, h), ...]
```

**実装方針**:
- ResultIteratorを内部で使用
- WORDレベルでイテレート
- テキスト、信頼度、座標をまとめて返す

#### GetTextlines (1メソッド)
**機能**: 行レベルのコンポーネント取得

```python
GetTextlines() -> list[tuple[str, int, int, int, int, int]]
# 戻り値: [(line, confidence, x, y, w, h), ...]
```

**実装方針**:
- ResultIteratorを内部で使用
- TEXTLINEレベルでイテレート
- Phase 2のGetComponentImagesと類似の実装

#### GetThresholdedImage (1メソッド)
**機能**: 2値化画像の取得

```python
GetThresholdedImage() -> numpy.ndarray
# 戻り値: 2値化画像 (height, width)
```

**実装方針**:
- TessBaseAPI::GetThresholdedImage()を呼び出し
- Pix* → NumPy配列変換
- Leptonica APIを使用

---

### 3. 追加Enum (優先度: 低)

#### WritingDirection
**値**: 4個
- LEFT_TO_RIGHT = 0
- RIGHT_TO_LEFT = 1
- TOP_TO_BOTTOM = 2
- BOTTOM_TO_TOP = 3

**用途**: テキストの書字方向識別

#### TextlineOrder
**値**: 4個
- LEFT_TO_RIGHT = 0
- RIGHT_TO_LEFT = 1
- TOP_TO_BOTTOM = 2
- BOTTOM_TO_TOP = 3

**用途**: テキスト行の順序識別

---

## 📊 実装の優先順位

### Phase 3a: Iterator API (Week 1)
1. ResultIteratorWrapper C++クラス実装
2. GetIterator() メソッド実装
3. 基本6メソッドの実装
4. Python バインディング

### Phase 3b: レイアウト解析 (Week 2)
1. GetWords 実装
2. GetTextlines 実装
3. GetThresholdedImage 実装

### Phase 3c: 追加Enum (Week 2)
1. WritingDirection Enum
2. TextlineOrder Enum

---

## 🎯 成功基準

### 機能性
- ✅ GetIterator()が動作し、基本的なイテレーションが可能
- ✅ 単語・行レベルの情報取得が可能
- ✅ 2値化画像の取得が可能

### 品質
- ✅ 全テスト（140+）がパス
- ✅ Iterator使用例のテストケース追加（10+）
- ✅ メモリリークなし

### パフォーマンス
- ⚠️ パフォーマンス低下は10%以内に抑える
- ✅ tesserocrより25%以上高速を維持

### 互換性
- ✅ tesserocr API互換性: 80% → 85%+
- ✅ レイアウト解析: 11% → 44%

---

## ⚠️ 実装上の課題

### 1. Iterator のライフタイム管理
**課題**: ResultIterator は TessBaseAPI に依存し、API が破棄されると無効になる
**解決策**:
- Iteratorが API の shared_ptr/weak_ptr を保持
- または Iterator 使用中は API を保持

### 2. Python イテレータプロトコル
**課題**: PythonのforループでIteratorを使えるようにする
**解決策**:
- `__iter__()` と `__next__()` を実装
- StopIteration例外を適切に発生

### 3. メモリ管理
**課題**: Tesseract API が返すchar*の管理
**解決策**:
- 適切にdelete[]を呼び出す
- RAIIパターンを使用

---

## 📈 期待される成果

### API互換性
```
Phase 2: 30/50 (60%)
Phase 3: 36/50 (72%) → +12%
```

### レイアウト解析
```
Phase 2: 1/9 (11%)
Phase 3: 4/9 (44%) → +33%
```

### Enum実装
```
Phase 2: 5/10 (50%)
Phase 3: 7/10 (70%) → +20%
```

---

## 📝 次のフェーズ (Phase 4以降)

Phase 3完了後、以下を検討：

### Phase 4: 完全なIterator API
- 残りの20+メソッド
- フォント属性、ベースライン、方向性
- デバッグ情報

### Phase 5: 完全なレイアウト解析
- AnalyseLayout
- GetRegions
- GetConnectedComponents
- GetStrips

### Phase 6: PDF生成
- ProcessPages
- ProcessPage
- SetOutputName

---

**作成者**: Claude Code (Anthropic)
**作成日**: 2025-11-11
**ステータス**: 計画中
**リスク**: 中（Iterator実装の複雑さ）
