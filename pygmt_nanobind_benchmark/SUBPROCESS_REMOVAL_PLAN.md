# Subprocess Removal Plan: Virtual File Implementation

**Date**: 2025-11-11
**Status**: 🚨 **CRITICAL** - subprocess依存が残存
**Priority**: **HIGHEST** - nanobindベース・subprocessなし前提に反する

---

## 現状分析

### 1. クリーンアップ完了 ✅

```bash
# 削除済み
- figure_classic.py.bak (45KB) ✅
- __pycache__/ ディレクトリ全て ✅
```

### 2. 現在のディレクトリ構造

```
python/pygmt_nb/
├── __init__.py
├── figure.py              # Figure class (257 lines)
├── clib/
│   └── __init__.py       # Session, Grid classes
├── helpers/              # (空ディレクトリ)
└── src/                  # 8 plotting methods
    ├── __init__.py
    ├── basemap.py        ✅ 100% nanobind
    ├── coast.py          ⚠️  subprocess import (未使用)
    ├── colorbar.py       ⚠️  subprocess import (未使用)
    ├── grdcontour.py     ⚠️  subprocess import (未使用)
    ├── grdimage.py       ⚠️  subprocess import (未使用)
    ├── logo.py           ⚠️  subprocess import (未使用)
    ├── plot.py           ❌ subprocess実使用 (data input)
    └── text.py           ❌ subprocess実使用 (data input)
```

### 3. subprocess使用状況（詳細）

#### 🚨 実際に使用しているファイル (2)

**src/plot.py:94-108**
```python
# TODO: Implement proper data passing via virtual files
if x is not None and y is not None:
    import subprocess
    data_str = "\n".join(f"{xi} {yi}" for xi, yi in zip(x, y))

    # Use subprocess for data input (temporary solution)
    cmd = ["gmt", "plot"] + args
    subprocess.run(cmd, input=data_str, text=True, check=True, capture_output=True)
```

**問題点**:
- データ入力にsubprocessを使用
- nanobindの103x speedup効果が失われる
- INSTRUCTIONS要件「using **only** nanobind」に違反

**src/text.py:92-114**
```python
import subprocess

# Handle single or multiple text entries
data_str = "\n".join(f"{xi} {yi} {t}" for xi, yi in zip(x, y, text))

cmd = ["gmt", "text"] + args
subprocess.run(cmd, input=data_str, text=True, check=True, capture_output=True)
```

**問題点**:
- テキストアノテーション配置にsubprocessを使用
- plot()と同じ問題

#### ⚠️ Import のみで未使用 (6)

以下のファイルは`import subprocess`があるが実際には使用していない：
- src/coast.py
- src/colorbar.py
- src/grdcontour.py
- src/grdimage.py
- src/logo.py

**対応**: 不要なimportを削除すべき

---

## PyGMT の Virtual File アーキテクチャ

### Virtual File とは

GMT C APIの機能で、メモリ上のデータをファイルパスのように扱える仕組み：

```python
# PyGMT の例
with session.virtualfile_from_vectors(x, y) as vfile:
    session.call_module("plot", f"{vfile} -JX10c -R0/10/0/10")
```

### PyGMT が使用するGMT C API関数

1. **GMT_Open_VirtualFile** - virtual fileを開く
2. **GMT_Close_VirtualFile** - virtual fileを閉じる
3. **GMT_Create_Data** - データ構造を作成
4. **GMT_Put_Vector** - ベクトルデータを格納
5. **GMT_Put_Matrix** - 行列データを格納

### PyGMT の実装パターン

```python
# pygmt/clib/session.py より

@contextlib.contextmanager
def open_virtualfile(self, family, geometry, direction, data):
    """Open a GMT virtual file"""
    c_open_virtualfile = self.get_libgmt_func("GMT_Open_VirtualFile", ...)
    c_close_virtualfile = self.get_libgmt_func("GMT_Close_VirtualFile", ...)

    # Open virtual file
    vfname = ctypes.create_string_buffer(GMT_VF_LEN)
    status = c_open_virtualfile(self.session_pointer, family_int,
                                 geometry_int, direction_int, data, vfname)

    try:
        yield vfname.value.decode()
    finally:
        # Close virtual file
        c_close_virtualfile(self.session_pointer, vfname)

@contextlib.contextmanager
def virtualfile_from_vectors(self, vectors):
    """Store 1-D vectors as dataset in virtual file"""
    # Create GMT dataset
    dataset = self.create_data(family="GMT_IS_DATASET",
                               geometry="GMT_IS_POINT", ...)
    # Put vectors into dataset
    for col, vector in enumerate(vectors):
        self.put_vector(dataset, col, vector)
    # Open virtual file with dataset
    with self.open_virtualfile("GMT_IS_DATASET", "GMT_IS_POINT",
                               "GMT_IN|GMT_IS_REFERENCE", dataset) as vfile:
        yield vfile
```

---

## pygmt_nb での実装不足

### 現在のnanobind bindings (src/bindings.cpp)

**実装済み**:
- ✅ Session class
- ✅ call_module() - GMT moduleの実行
- ✅ Grid class - grid読み込み
- ✅ get_current_figure() - PostScriptデータ取得

**未実装** (🚨):
- ❌ open_virtualfile() / close_virtualfile()
- ❌ create_data() - データ構造作成
- ❌ put_vector() - ベクトルデータ格納
- ❌ put_matrix() - 行列データ格納

### 結果

**plot(x, y)** や **text(x, y, text)** のような配列入力がnanobind経由で処理できない
→ 仕方なくsubprocessを使用 (一時回避策)

---

## 実装計画

### Phase 2A: Virtual File Support 追加 (最優先)

**目的**: subprocessを完全に削除し、100% nanobindベースにする

#### Task 1: C++ bindings 拡張 (src/bindings.cpp)

**追加すべきメソッド**:

```cpp
class Session {
public:
    // Virtual file support
    std::string open_virtualfile(const std::string& family,
                                 const std::string& geometry,
                                 const std::string& direction,
                                 void* data);
    void close_virtualfile(const std::string& vfname);

    // Data creation
    void* create_data(const std::string& family,
                     const std::string& geometry,
                     const std::string& mode,
                     const std::vector<uint64_t>& dim);

    // Vector/Matrix input
    void put_vector(void* dataset, int column,
                   nb::ndarray<double, nb::shape<-1>, nb::c_contig> vector);
    void put_matrix(void* dataset,
                   nb::ndarray<double, nb::shape<-1, -1>, nb::c_contig> matrix);
};
```

**使用するGMT C API**:
- `GMT_Open_VirtualFile()`
- `GMT_Close_VirtualFile()`
- `GMT_Create_Data()`
- `GMT_Put_Vector()`
- `GMT_Put_Matrix()`

#### Task 2: Python wrapper (python/pygmt_nb/clib/__init__.py)

**追加すべきメソッド**:

```python
class Session(_CoreSession):
    @contextlib.contextmanager
    def virtualfile_from_vectors(self, *vectors):
        """Store 1-D vectors in virtual file (for plot, etc.)"""
        # Create dataset
        # Put vectors
        # Open virtual file
        # Yield vfile name
        # Close virtual file
        pass

    @contextlib.contextmanager
    def virtualfile_from_matrix(self, matrix):
        """Store 2-D matrix in virtual file"""
        pass
```

#### Task 3: plot.py と text.py を修正

**現在の実装** (subprocess使用):
```python
# plot.py
if x is not None and y is not None:
    import subprocess  # ❌
    data_str = "\n".join(f"{xi} {yi}" for xi, yi in zip(x, y))
    subprocess.run(["gmt", "plot"] + args, input=data_str, ...)
```

**修正後の実装** (nanobind使用):
```python
# plot.py
if x is not None and y is not None:
    import numpy as np
    with self._session.virtualfile_from_vectors(
        np.array(x), np.array(y)
    ) as vfile:
        self._session.call_module("plot", f"{vfile} " + " ".join(args))
```

#### Task 4: 不要なsubprocess import削除

```python
# 以下のファイルから `import subprocess` を削除
- src/coast.py
- src/colorbar.py
- src/grdcontour.py
- src/grdimage.py
- src/logo.py
```

### Task 5: テスト実行・検証

```bash
# 全テスト実行
python -m pytest tests/ -v

# plot/text のテストが通ることを確認
python -m pytest tests/test_figure.py::test_plot -v
python -m pytest tests/test_figure.py::test_text -v
```

---

## 実装優先度

### 🔴 Phase 2A (Week 1-2): Virtual File Implementation

| Task | Effort | Priority | Status |
|------|--------|----------|--------|
| 1. bindings.cpp拡張 | 3 days | 🔴 CRITICAL | ⏸️ Not Started |
| 2. Python wrapper | 1 day | 🔴 CRITICAL | ⏸️ Not Started |
| 3. plot.py修正 | 2 hours | 🔴 CRITICAL | ⏸️ Not Started |
| 4. text.py修正 | 2 hours | 🔴 CRITICAL | ⏸️ Not Started |
| 5. import削除 | 30 min | 🟡 HIGH | ⏸️ Not Started |
| 6. テスト検証 | 1 day | 🟡 HIGH | ⏸️ Not Started |

**Total**: ~1 week

### 🟡 Phase 2B (Week 3-6): Missing Functions

実装する55関数全てがvirtual fileサポートに依存するため、
Phase 2Aの完了が必須。

---

## なぜこれが最優先か

### 1. INSTRUCTIONS要件違反

> **Requirement 1**: Re-implement the gmt-python (PyGMT) interface using **only** nanobind

現状: plot()とtext()がsubprocessを使用 → 要件違反

### 2. パフォーマンス損失

- nanobind: 103x speedup ⚡
- subprocess: 1x (baseline) 🐌

plot()とtext()でsubprocessを使うと、せっかくのnanobind最適化が台無し。

### 3. 新機能実装の阻害

残りの55関数の多くがデータ入力を必要とする：
- histogram(data) - データヒストグラム
- contour(x, y, z) - コンター図
- plot3d(x, y, z) - 3Dプロット

virtual fileサポートがないと、これらも全てsubprocessになってしまう。

### 4. アーキテクチャの一貫性

現状:
- basemap, coast, colorbar → 100% nanobind ✅
- plot, text → subprocess混在 ❌

統一されたアーキテクチャにすべき。

---

## 参考資料

### PyGMT実装

**Virtual file実装**:
- `/home/user/Coders/external/pygmt/pygmt/clib/session.py:1287-2253`
  - `open_virtualfile()`
  - `virtualfile_from_vectors()`
  - `virtualfile_from_matrix()`
  - `virtualfile_in()` / `virtualfile_out()`

**使用例**:
- `/home/user/Coders/external/pygmt/pygmt/src/plot.py`
- `/home/user/Coders/external/pygmt/pygmt/src/text.py`

### GMT C API ドキュメント

- GMT Developer Documentation: https://docs.generic-mapping-tools.org/dev/devdocs/api.html
- Virtual Files: https://docs.generic-mapping-tools.org/dev/devdocs/api.html#virtual-files

---

## 次のアクション

1. **今すぐ**: 不要なsubprocess importを削除 (30分)
2. **Phase 2A開始**: Virtual file実装 (1週間)
3. **Phase 2B**: 55関数実装 (4週間)

**優先度**:
```
Phase 2A (Virtual File) > Phase 2B (Missing Functions) > Phase 3 (Benchmarks)
```

Virtual fileサポートなしでは、真のnanobind実装は不可能。

---

**結論**: 現在の構造は良好だが、**subplot依存を完全に除去するためにvirtual file実装が緊急に必要**。
