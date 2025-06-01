# 使用官方Python轻量镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制代码和配置文件
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 容器启动默认执行脚本
CMD ["python", "main.py"]
