# ExcelTool

Excel操作のための便利ツール集。Pythonで開発されています。

## 機能

### 1. VLOOKUP風機能（GUI版 - 推奨）

2つのExcelファイルを比較して、キーワード列でマッチングし、指定列のデータをコピーするツールです。

**Apple UI/UXに準拠した親しみやすいGUIアプリケーション**を提供しています。

#### GUIアプリケーションの起動

```powershell
python app.py
```

GUIアプリケーションでは、以下の操作が可能です：
- 直感的なファイル選択（ドラッグ&ドロップ対応のファイル選択ダイアログ）
- 視覚的な列マッピング設定
- リアルタイムの進捗表示
- 処理結果の詳細な表示

### 2. VLOOKUP風機能（コマンドライン版 - excel_tool.py）

GUI版と同じ機能をコマンドラインから実行できます。

**主な特徴:**
- 複数のキーワード列（1つ以上）でマッチング可能
- 複数の列を同時にコピー可能
- JSON設定ファイルで柔軟に設定可能

### 2. Excelファイルキーワード検索機能（excel_search.py）

指定フォルダ内のExcelファイルからキーワードを検索し、ファイルパス、ファイル名、ファイル編集日のリストを作成するツールです。NAS環境での高速かつ安定した検索を想定しています。

**主な特徴:**
- 1つ以上のキーワードを同時に検索可能
- マルチスレッド処理による高速検索
- 再帰的なフォルダ検索に対応
- Excelファイル内の全シート・全セルを検索
- エラーハンドリングによる安定した処理（ネットワークエラー、アクセス権限エラーなどに対応）
- 検索結果をExcelまたはCSV形式で出力

## セットアップ

### 1. 仮想環境の有効化

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. 依存パッケージのインストール

```powershell
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## 使用方法

### GUIアプリケーションの使い方（推奨）

1. **アプリケーションの起動**
   ```powershell
   python app.py
   ```

2. **ファイルの選択**
   - 「ソースファイル（参照元）」ボタンをクリックして、参照元のExcelファイルを選択
   - 「ターゲットファイル（更新対象）」ボタンをクリックして、更新対象のExcelファイルを選択
   - 「出力ファイル」に結果を保存するファイルパスを入力（または参照ボタンで選択）

3. **列マッピングの設定**
   - 「マッチング列」セクションで「+ マッピングを追加」をクリック
   - ソース列とターゲット列をドロップダウンから選択
   - 必要に応じて複数のマッピング列を追加
   - 「コピー列」セクションでも同様に設定

4. **処理の実行**
   - 「処理を実行」ボタンをクリック
   - 進捗が表示され、完了すると結果が表示されます

### コマンドライン版の使い方

### VLOOKUP風機能の使い方（コマンドライン版）

#### 1. サンプル設定ファイルの作成

```powershell
python excel_tool.py --create-sample
```

これで `config_sample.json` が作成されます。

#### 2. 設定ファイルの編集

`config_sample.json` を編集して、以下の項目を設定します：

- `source_file`: ソース（参照元）Excelファイルのパス
- `target_file`: ターゲット（更新対象）Excelファイルのパス
- `output_file`: 出力先Excelファイルのパス
- `source_sheet`: ソースファイルのシート名またはインデックス（省略可、デフォルト: 0）
- `target_sheet`: ターゲットファイルのシート名またはインデックス（省略可、デフォルト: 0）
- `match_columns`: マッチングに使用する列のペア（配列）
  - `source`: ソースファイルの列名
  - `target`: ターゲットファイルの列名
- `copy_columns`: コピーする列のペア（配列）
  - `source`: ソースファイルのコピー元列名
  - `target`: ターゲットファイルのコピー先列名

**設定例:**

```json
{
  "source_file": "master_data.xlsx",
  "target_file": "work_data.xlsx",
  "output_file": "result.xlsx",
  "match_columns": [
    {
      "source": "ID",
      "target": "ID"
    },
    {
      "source": "コード",
      "target": "商品コード"
    }
  ],
  "copy_columns": [
    {
      "source": "商品名",
      "target": "商品名"
    },
    {
      "source": "価格",
      "target": "単価"
    }
  ]
}
```

#### 3. ツールの実行

```powershell
python excel_tool.py config.json
```

#### 動作の流れ

1. ソースファイルとターゲットファイルを読み込み
2. `match_columns` で指定された列の組み合わせでマッチング
3. マッチした行について、`copy_columns` で指定された列のデータをコピー
4. 結果を `output_file` に保存

**注意:**
- 複数のキーワード列を指定した場合、すべての列が一致する行のみマッチします
- マッチしなかった行は、元のデータがそのまま保持されます

### Excelファイルキーワード検索機能の使い方

#### 1. サンプル設定ファイルの作成

```powershell
python excel_search.py --create-sample
```

これで `config_search_sample.json` が作成されます。

#### 2. 設定ファイルの編集

`config_search_sample.json` を編集して、以下の項目を設定します：

- `search_path`: 検索対象フォルダのパス（NASパスも指定可能、例: `\\\\nas-server\\share\\excel_files`）
- `keywords`: 検索キーワードのリスト（1つ以上）
- `output_file`: 出力ファイルのパス（.xlsx または .csv）
- `recursive`: 下層フォルダも検索するか（省略可、デフォルト: `true`）
- `max_workers`: 並列処理のワーカー数（省略可、デフォルト: `4`）
- `case_sensitive`: 大文字小文字を区別するか（省略可、デフォルト: `false`）

**設定例:**

```json
{
  "search_path": "\\\\nas-server\\share\\excel_files",
  "keywords": [
    "プロジェクトA",
    "2024年度",
    "売上"
  ],
  "output_file": "search_results.xlsx",
  "recursive": true,
  "max_workers": 8,
  "case_sensitive": false
}
```

#### 3. ツールの実行

```powershell
python excel_search.py config_search.json
```

#### 動作の流れ

1. 指定パスからExcelファイル（.xlsx, .xlsm, .xls）を検索
2. 各Excelファイルの全シート・全セルからキーワードを検索
3. 1つ以上のキーワードが見つかったファイルについて、以下を記録：
   - ファイルパス
   - ファイル名
   - ファイル編集日時
   - マッチしたキーワード
4. 結果をExcelまたはCSV形式で保存

**注意:**
- 複数のキーワードを指定した場合、1つでも見つかればそのファイルは結果に含まれます
- NAS環境での使用を想定しており、ネットワークエラーやアクセス権限エラーに対して適切に処理されます
- 並列処理により大量のファイルでも高速に検索できます
- 検索の進捗は100ファイルごとに表示されます


