# Dockerfile

# Pythonイメージの指定
FROM python:3.10

# 作業ディレクトリを設定
WORKDIR /app

# pipenvのインストール
RUN pip install pipenv

# Pipfileをコピー
COPY Pipfile Pipfile.lock ./

# パッケージのインストール
RUN pipenv install --system --deploy

# スクリプトとその他のファイルをコピー
COPY . .

# PYTHONPATHにモジュールのパスを追加
ENV PYTHONPATH="/app:${PYTHONPATH}"

# スクリプトを実行
CMD [ "python", "./discordBot/example.py" ]