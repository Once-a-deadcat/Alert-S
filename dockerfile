# Dockerfile

# Pythonイメージの指定
FROM python:3.10

# 作業ディレクトリを設定
WORKDIR /app

# pipenvのインストール
RUN pip install pipenv

# スクリプトとその他のファイルをコピー
COPY . .

# パッケージのインストール
RUN pipenv install --system --deploy

# PYTHONPATHにモジュールのパスを追加
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# スクリプトを実行
CMD [ "python", "src/adapters/discord_bot.py" ]
