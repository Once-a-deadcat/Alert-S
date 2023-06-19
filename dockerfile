# Dockerfile

# Pythonイメージの指定
FROM python:3.8

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

# スクリプトを実行
CMD [ "python", "./SwitchbotFunc.py" ]