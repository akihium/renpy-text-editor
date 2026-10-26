# はじめに — Ren’Py Text Editor

表形式の画面でセリフを書き、書式を確認しながら Ren’Py スクリプトを出力できるデスクトップ GUI エディターです。

[English](quickstart.en.md) · [日本語](quickstart.ja.md) · [简体中文](quickstart.zh-CN.md) · [繁體中文](quickstart.zh-TW.md)

## ダウンロードと起動

- [Windows 10/11 x64 版をダウンロード](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-Windows-x64.zip)
- [macOS 14 以降・Apple Silicon 版をダウンロード](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-macOS-arm64.zip)
- [すべてのリリースと更新内容](https://github.com/akihium/renpy-text-editor/releases/latest)

お使いのパソコンに合う ZIP を選んでください。配布版には Python のインストールは不要です。Windows では ZIP **全体**を展開し、フォルダー内の `RenPy Text Editor.exe` を起動します。周囲のファイルやフォルダーもそのまま保持してください。macOS では ZIP を展開し、`RenPy Text Editor.app` を開きます。

## サンプルプロジェクトを開く

1. アプリを起動し、メイン画面の **表示言語** で **日本語** を選びます。
2. **プロジェクトを開く** をクリックし、ZIP を展開したフォルダーへ移動します。
3. 基本的なセリフの例は `examples/ja/sample.advdb`、背景・クリック待ち・選択肢の分岐を試す場合は `examples/ja/branches.advdb` を開きます。
4. 編集前に **名前を付けて保存／移動** をクリックし、自分用のファイル名と保存先を指定します。素材も一緒にコピーされます。
5. 章／セクションを選んで行を表示します。セリフのセルで文字を選択し、書式ボタンを試してください。ビジュアルモードとタグモードを切り替えると、見た目と Ren’Py タグを確認できます。

配布パッケージには次の 4 言語のサンプルが含まれます。

| 言語 | 展開したパッケージ内のフォルダー |
| --- | --- |
| 日本語 | `examples/ja/` |
| 英語 | `examples/en/` |
| 簡体字中国語 | `examples/zh_CN/` |
| 繁体字中国語 | `examples/zh_TW/` |

**ソースコードの ZIP** を取得した場合、サンプルの場所は `examples/localized/<言語>/` です。[ソースからの起動手順](https://github.com/akihium/renpy-text-editor#run-from-source)に沿って Python と依存ライブラリーを用意してください。

**プロジェクトを開く** では `.advdb` を選びます。`.xlsx` は Excel のインポート／エクスポート用、`renpy_game/adv_generated/` は出力済みスクリプトの例です。表示言語の切り替えは画面の項目に適用され、プロジェクト内のセリフは翻訳しません。別の言語のセリフを試すには、その言語のサンプルを開いてください。

## 自分のプロジェクトを作る

**新規プロジェクト** をクリックし、ファイル名と保存先を選びます。表にキャラクター ID、セリフ、メモを入力します。メイン画面のキャラクター管理で表示名と色を設定できます。

- **Tab / Shift+Tab：** 次／前のセルへ移動。
- **Enter：** 編集を確定し、次の行のキャラクター欄へ移動。最終行では新しい行を追加。
- **Shift+Enter：** セリフ内で改行。
- **Ctrl+S / Cmd+S：** 保存。書式や元に戻す操作は Windows では Ctrl、macOS では Command を使用。

章／セクション管理で分岐先を作り、選択肢の移動先に指定します。メイン画面から背景やフォントも追加できます。**テキストのみ** は演出を削除せずに非表示にします。

手動でプロジェクトを移動するときは、`story.advdb` と対応する `story_assets/` を一緒に移動してください。**名前を付けて保存／移動** では両方をコピーできます。

## エクスポート

Ren’Py の `game` フォルダーに出力すると、生成ファイルは `adv_generated/` に保存されます。付属サンプルを手書きスクリプトから開始する例：

```renpy
label start:
    call adv_opening
    return
```

自分のセクションでは、`adv_opening` を出力ファイル内のラベルに置き換えてください。Word／PDF ではタイトルとセリフ ID の有無を指定できます。RPY の ID 設定は独立しています。

アプリはオフラインで動作します。Ren’Py SDK やゲーム内プレビューは含まれないため、公開前に Ren’Py で出力結果を確認してください。配布版は商用の開発者証明書による署名・macOS の公証を行っていません。
