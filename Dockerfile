# 使用官方Python轻量镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制代码和配置文件
COPY . /app

# 设置环境变量 TZ
ENV TZ=Asia/Shanghai

# 创建符号链接并设置时区
# 安装依赖
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    pip install --no-cache-dir -r requirements.txt

# 容器启动默认执行脚本
CMD ["python", "main.py"]
