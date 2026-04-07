<div id="top"></div>

## 使用技術一覧
<p style="display: inline">
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
  <img src="https://img.shields.io/badge/-Discord-5865F2.svg?logo=discord&logoColor=white&style=for-the-badge">
  <img src="https://img.shields.io/badge/-OpenAI-412991.svg?logo=openaigym&logoColor=white&style=for-the-badge">
  <img src="https://img.shields.io/badge/-MySQL-4479A1.svg?logo=mysql&logoColor=white&style=for-the-badge">
  <img src="https://img.shields.io/badge/-VoiceVox-FF6B6B.svg?style=for-the-badge">
</p>

## プロジェクト名

GPTchan（仮）

## プロジェクトについて

Discord上で動作する、GPTAPI内蔵のAIチャットボットです。
OpenAIのGPT APIを使用してテキスト応答を生成し、同時にVoiceVoxで音声合成を行い音声通話（一方向）が可能です。チャットログは逐次MySQLデータベースに保存し、会話の継続性を保ちます。

<p align="right">(<a href="#top">トップへ</a>)</p>

## 環境
> **⚠️ Windows Only**: このプロジェクトはWindows 64-bitでテストされています。macOS/Linuxでは環境構築が異なる可能性があります。

| 言語・フレームワーク| バージョン |
| --------------------- | ---------- |
| Python                | 3.11.4     |
| MySQL                 | 9.6.0      |
 

## 依存関係

詳細は[requirements.txt](requirements.txt)を参照してください。<br>主要なパッケージは以下
- discord.py
- openai
- python-dotenv
- mysql-connector-python
- voicevox-core

その他のパッケージのバージョンは requirements.txt を参照してください。<br>また、**VoiceVox.Core**はWindows版とmacOS/Linux版でセットアップが異なります。
[詳しくはこちら](https://github.com/VOICEVOX/voicevox_core/releases)
<p align="right">(<a href="#top">トップへ</a>)</p>

## 副次ファイル・機能

- **.envファイル**: APIキーやDB情報を記載。以下を記載すること。

> ```
> OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxx
> DISCORD_TOKEN=xxxxxxxxxxxxxxxxxxxxx
> DB_HOST=localhost
> DB_USER=root
> DB_PASSWORD=your_mysql_password
> ```

[OPENAI APIキーの取得はこちらを参考に](https://note.com/ai_dev_lab/n/nbf092fa1d1ec)  
[Discord BOTのトークン取得はこちらを参考に](https://qiita.com/1ntegrale9/items/cb285053f2fa5d0cccdf)  
[MySQLのユーザー作成はこちらを参考に](https://qiita.com/gatapon/items/92b942fa7081cfe17482)

- **SubRolls.txt**: ボットのロール（性格）を手動編集可能。後述するコマンドでも編集されます。
- **output.wav**: VoiceVoxAPIから生成された最新の音声です。自動的に上書きされ続けます。
- **データベース**: MySQLで`DCdatabase.chat_logs`テーブルが自動作成されます。
- **ログ**: discord.logにエラーログが出力されます。


<p align="right">(<a href="#top">トップへ</a>)</p>

### コマンド一覧

| コマンド          | 実行する処理                        |
| -----------      | ---------------------------------- |
| `!talk <メッセージ>`|  GPT APIで応答を生成して返信。 |
| `!roll <ロール>` |  ボットの性格や設定を追加（最大10個、SubRolls.txtに保存）。 |
| `!vc` | ボイスチャンネルに接続。 |
| `!leave` | ボイスチャンネルから退出。 |
| メンション | ボットにメンションすると自動で会話開始。 |

- ボイスチャンネル接続中は、応答が自動で音声再生されます。
- チャットログは自動保存され、次回の会話で活用されます。

<p align="right">(<a href="#top">トップへ</a>)</p>
