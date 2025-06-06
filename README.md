# Strands マルチエージェント システム

AWS Strands Agents SDK を使用して構築された本格運用対応のマルチエージェントシステムで、専門特化したAIエージェントが連携して複雑なビジネスワークフローを処理します。

## 🎯 概要

このシステムは、複雑なビジネス課題を解決するために連携する4つの専門エージェントを組み合わせています：

- **🔍 データアナリストエージェント**: データファイル（CSV、Excel）の処理・分析、統計分析、インサイト生成
- **🌐 リサーチエージェント**: ウェブ調査、市場分析、ファクトチェック、外部情報収集
- **📝 レポート生成エージェント**: 複数形式での専門的なレポート、プレゼンテーション、文書作成
- **🎯 コーディネーターエージェント**: マルチエージェントワークフローの統制とタスク配分管理

## 🚀 クイックスタート

### 前提条件

- Python 3.11+
- Bedrockアクセス権を持つAWSアカウント
- Docker（コンテナ化デプロイメント用、オプション）

### 1. インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd strands-multi-agent-system

# 仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. 設定

```bash
# 環境テンプレートをコピー
cp .env.example .env

# AWSクレデンシャルと設定で.envを編集
# 最低限以下を設定:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_DEFAULT_REGION
```

### 3. アプリケーションの実行

```bash
# Streamlitインターフェースを開始
streamlit run app.py
```

ブラウザで http://localhost:8501 を開いてください。

## 🐳 Dockerデプロイメント

### Docker Composeを使用（推奨）

```bash
# 全サービスをビルドして開始
docker-compose up -d

# ログを表示
docker-compose logs -f strands-app

# サービスを停止
docker-compose down
```

### Dockerのみを使用

```bash
# イメージをビルド
docker build -t strands-multi-agent .

# コンテナを実行
docker run -p 8501:8501 --env-file .env strands-multi-agent
```

## 📋 使用例

### 1. データ分析とレポート生成

1. ウェブインターフェースからCSV/Excelファイルをアップロード
2. 分析タイプを選択（統計要約、トレンド、相関）
3. レポートセクションと出力形式を選択
4. システムが自動的に以下を実行：
   - データアナリストエージェントでデータを分析
   - 関連する市場調査を実施
   - 包括的なレポートを生成

### 2. 市場調査

1. 調査トピックを入力（例：「電気自動車市場」）
2. 調査観点を選択（市場規模、競合、トレンド）
3. データソースと地理的焦点を選択
4. 詳細な市場分析レポートを取得

### 3. 競合情報分析

1. 自社/製品と競合他社を入力
2. 分析基準を選択（機能、価格、市場シェア）
3. 比較用の内部データをアップロード（オプション）
4. 競合ポジショニング分析を受け取る

### 4. カスタムマルチエージェントタスク

1. 複雑なタスクを自然言語で記述
2. 使用するエージェントを選択
3. 関連ファイルをアップロード
4. 複数エージェントからの統合結果を取得

## 🏗️ アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │    │   Coordinator   │    │  Data Analyst   │
│                 │◄──►│     Agent       │◄──►│     Agent       │
│  - ファイルアップロード │    │                 │    │                 │
│  - タスク設定     │    │ - ワークフロー管理  │    │ - データ分析     │
│  - 結果表示      │    │ - エージェント間連携 │    │ - 統計          │
└─────────────────┘    │ - 統制          │    │ - インサイト     │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Research      │    │ Report Generator│
                       │     Agent       │    │     Agent       │
                       │                 │    │                 │
                       │ - ウェブ検索     │    │ - PDFレポート    │
                       │ - 市場データ     │    │ - Word文書      │
                       │ - ファクトチェック │    │ - HTML出力      │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ コアコンポーネント

### エージェント

- **CoordinatorAgent** (`src/agents/coordinator.py`): ワークフローの統制
- **DataAnalystAgent** (`src/agents/data_analyst.py`): データ処理と分析
- **ResearchAgent** (`src/agents/research_agent.py`): 外部情報収集
- **ReportGeneratorAgent** (`src/agents/report_generator.py`): 文書作成

### ツール

- **Data Tools** (`src/tools/data_tools.py`): CSV/Excel処理、統計分析
- **Search Tools** (`src/tools/search_tools.py`): ウェブ検索、コンテンツ抽出
- **Document Tools** (`src/tools/document_tools.py`): レポート生成、ファイル処理

### 設定

- **Settings** (`src/config/settings.py`): 集約設定管理
- **環境変数**: AWSクレデンシャル、APIキー、エージェントパラメータ

## 🔧 設定オプション

### 環境変数

| 変数 | 説明 | デフォルト |
| `AWS_ACCESS_KEY_ID` | AWSアクセスキー | 必須 |
| `AWS_SECRET_ACCESS_KEY` | AWSシークレットキー | 必須 |
| `AWS_DEFAULT_REGION` | AWSリージョン | us-east-1 |
| `BEDROCK_MODEL_ID` | 使用するBedrockモデル | claude-3-5-sonnet |
| `AGENT_MAX_ITERATIONS` | エージェント最大イテレーション数 | 10 |
| `AGENT_TIMEOUT_SECONDS` | エージェントタイムアウト | 300 |
| `LOG_LEVEL` | ログレベル | INFO |
| `ENABLE_TRACING` | 観測可能性を有効化 | true |

### エージェント設定

エージェントは設定ファイルでカスタマイズできます：

```python
# 例: エージェント動作を変更
settings.agent_max_iterations = 15
settings.agent_timeout_seconds = 600
```

## 📊 監視と観測可能性

### 組み込み監視

- **エージェントダッシュボード**: リアルタイムエージェントステータスとパフォーマンス
- **タスク履歴**: 完全なワークフロー追跡
- **結果管理**: 組織化された出力ストレージ

### オプション: Langfuse統合

詳細トレーシングを有効化するには以下を設定：

```bash
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_secret
ENABLE_TRACING=true
```

### オプション: Prometheus & Grafana

高度な監視のためdocker-compose.ymlに含まれています：

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## 🧪 テスト

```bash
# ユニットテストを実行
pytest tests/

# カバレッジ付きで実行
pytest --cov=src tests/

# 特定のテストファイルを実行
pytest tests/test_data_analyst.py
```

## 📁 プロジェクト構造

```
strands-multi-agent-system/
├── src/
│   ├── agents/           # エージェント実装
│   ├── tools/            # カスタムツール
│   └── config/           # 設定
├── tests/                # テストファイル
├── app.py               # Streamlitインターフェース
├── requirements.txt     # Python依存関係
├── Dockerfile          # コンテナ設定
├── docker-compose.yml  # マルチサービスデプロイメント
└── README.md           # このファイル
```

## 🚀 本番デプロイメント

### AWS ECS/Fargate

1. イメージをビルドしてECRにプッシュ
2. ECSタスク定義を作成
3. Fargateクラスターにデプロイ
4. ロードバランサーを設定

### AWS Lambda（サーバーレス）

イベント駆動実行の場合：
1. アプリケーションをパッケージ化
2. Lambda関数としてデプロイ
3. トリガーを設定（S3、API Gateway）

### Kubernetes

```bash
# Kubernetesマニフェストを適用
kubectl apply -f k8s/
```

## 🔒 セキュリティ

- **IAMロール**: 本番環境ではアクセスキーの代わりにIAMロールを使用
- **シークレット管理**: 機密データにはAWS Secrets Managerを使用
- **ネットワークセキュリティ**: 適切なセキュリティグループでプライベートサブネットにデプロイ
- **暗号化**: 保存時と転送時の暗号化を有効化

## 🤝 コントリビューション

1. リポジトリをフォーク
2. フィーチャーブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'Add amazing feature'`）
4. ブランチにプッシュ（`git push origin feature/amazing-feature`）
5. プルリクエストを開く

## 📝 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細はLICENSEファイルを参照してください。

## 🆘 トラブルシューティング

### よくある問題

1. **AWSクレデンシャルエラー**
   ```bash
   # クレデンシャルを確認
   aws configure list
   aws bedrock list-foundation-models --region us-east-1
   ```

2. **ポートが既に使用中**
   ```bash
   # ポート8501を使用しているプロセスを探して終了
   lsof -ti:8501 | xargs kill -9
   ```

3. **メモリ問題**
   ```bash
   # Dockerメモリ割り当てを増加
   # または.envでAGENT_MAX_ITERATIONSを削減
   ```

### ヘルプの取得

- ログを確認: `docker-compose logs -f strands-app`
- Streamlitインターフェースでエージェント出力を確認
- デバッグログを有効化: `LOG_LEVEL=DEBUG`

## 🎯 ロードマップ

- [ ] 音声インターフェース統合
- [ ] 追加エージェントタイプ（法務、財務）
- [ ] リアルタイムコラボレーション機能
- [ ] 高度ワークフローデザイナー
- [ ] クラウドネイティブデプロイメントテンプレート
- [ ] モバイルアプリケーションサポート

## 📞 サポート

問題や質問については：
- GitHubでイシューを開く
- トラブルシューティングセクションを確認
- ドキュメントを確認

---

AWS Strands Agents SDKを使用して❤️で構築
