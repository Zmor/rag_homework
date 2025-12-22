# 部署指南

## 概述

本指南介绍如何将RAG系统部署到不同的环境中，包括本地开发环境、服务器部署和容器化部署。

## 环境要求

### 系统要求

- **操作系统**: Linux/macOS/Windows
- **Python版本**: 3.8+
- **内存**: 至少4GB RAM（推荐8GB+）
- **存储**: 至少1GB可用空间
- **网络**: 稳定的互联网连接（用于API调用）

### 依赖要求

```bash
# 系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install python3-pip python3-venv git

# 系统依赖（CentOS/RHEL）
sudo yum install python3-pip python3-venv git

# 系统依赖（macOS）
brew install python3 git
```

## 本地部署

### 1. 环境准备

```bash
# 创建项目目录
mkdir rag_system
cd rag_system

# 克隆代码（如果是从Git仓库）
# git clone <repository-url> .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# Windows: venv\Scripts\activate

# 升级pip
pip install --upgrade pip
```

### 2. 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 或者使用pip安装包
pip install -e .
```

### 3. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用您喜欢的编辑器
```

### 4. 验证安装

```bash
# 运行测试
pytest tests/ -v

# 运行示例
python examples/demo.py
```

## 服务器部署

### 1. 服务器准备

```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 创建用户（可选）
sudo useradd -m -s /bin/bash raguser
sudo usermod -aG sudo raguser

# 切换到新用户
su - raguser
```

### 2. 安装依赖

```bash
# 安装Python和Git
sudo apt-get install python3-pip python3-venv git -y

# 安装其他依赖
sudo apt-get install build-essential curl -y
```

### 3. 部署应用

```bash
# 创建应用目录
mkdir ~/apps
cd ~/apps

# 克隆项目（如果是从Git仓库）
# git clone <repository-url> rag_system
cd rag_system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置系统服务

创建systemd服务文件：

```bash
sudo nano /etc/systemd/system/rag-system.service
```

内容如下：

```ini
[Unit]
Description=RAG System Service
After=network.target

[Service]
Type=simple
User=raguser
WorkingDirectory=/home/raguser/apps/rag_system
Environment=PATH=/home/raguser/apps/rag_system/venv/bin
ExecStart=/home/raguser/apps/rag_system/venv/bin/python examples/cli.py --mode interactive
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable rag-system

# 启动服务
sudo systemctl start rag-system

# 查看状态
sudo systemctl status rag-system

# 查看日志
sudo journalctl -u rag-system -f
```

## Docker部署

### 1. 创建Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY src/ ./src/
COPY examples/ ./examples/
COPY .env.example ./.env

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建非root用户
RUN useradd -m -u 1000 raguser && chown -R raguser:raguser /app
USER raguser

# 设置环境变量
ENV PYTHONPATH=/app/src

# 运行应用
CMD ["python", "examples/demo.py"]
```

### 2. 构建镜像

```bash
# 构建镜像
docker build -t rag-system:latest .

# 查看镜像
docker images rag-system
```

### 3. 运行容器

```bash
# 运行容器
docker run -d \
  --name rag-system \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/chroma_db:/app/chroma_db \
  rag-system:latest

# 查看日志
docker logs -f rag-system

# 进入容器
docker exec -it rag-system bash
```

### 4. Docker Compose部署

创建`docker-compose.yml`：

```yaml
version: '3.8'

services:
  rag-system:
    build: .
    container_name: rag-system
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./chroma_db:/app/chroma_db
    networks:
      - rag-network
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.path.insert(0, '/app/src'); from rag_system import RAGSystem; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  rag-network:
    driver: bridge

volumes:
  logs:
  chroma_db:
```

部署：

```bash
# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## Kubernetes部署

### 1. 创建ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rag-system-config
data:
  .env: |
    EMBEDDING_API_KEY=your_embedding_api_key
    EMBEDDING_BASE_URL=https://your-api-endpoint.com/api/inference/v1
    EMBEDDING_MODEL_NAME=bge-large-zh-v1.5
    RERANKER_API_KEY=your_reranker_api_key
    RERANKER_BASE_URL=https://your-api-endpoint.com/api/inference/v1
    RERANKER_MODEL_NAME=bge-reranker-v2-m3
    LLM_API_KEY=your_llm_api_key
    LLM_BASE_URL=https://your-api-endpoint.com/api/inference/v1
    LLM_MODEL_NAME=GLM-4.6-FP8
    CHROMA_COLLECTION_NAME=rag_collection
    CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
    LOG_LEVEL=INFO
    LOG_FILE_PATH=/app/logs/rag_system.log
```

### 2. 创建Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rag-system
  template:
    metadata:
      labels:
        app: rag-system
    spec:
      containers:
      - name: rag-system
        image: rag-system:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: rag-system-config
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.path.insert(0, '/app/src'); from rag_system import RAGSystem; RAGSystem()"
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.path.insert(0, '/app/src'); from rag_system import RAGSystem; RAGSystem()"
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: logs
        emptyDir: {}
      - name: data
        persistentVolumeClaim:
          claimName: rag-system-data
```

### 3. 创建Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rag-system-service
spec:
  selector:
    app: rag-system
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### 4. 创建PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rag-system-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

## 环境配置

### 生产环境配置

```bash
# 生产环境环境变量
export ENVIRONMENT=production
export LOG_LEVEL=WARNING
export CHROMA_PERSIST_DIRECTORY=/var/lib/rag_system/chroma_db
export LOG_FILE_PATH=/var/log/rag_system/rag_system.log

# 性能优化
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1
```

### 监控和日志

```bash
# 安装监控工具
sudo apt-get install htop iotop nethogs -y

# 配置日志轮转
sudo nano /etc/logrotate.d/rag-system
```

日志轮转配置：

```
/var/log/rag_system/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 raguser raguser
    postrotate
        systemctl reload rag-system
    endscript
}
```

## 备份和恢复

### 数据库备份

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/rag_system"
DATE=$(date +%Y%m%d_%H%M%S)
DATA_DIR="/var/lib/rag_system/chroma_db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 停止服务
sudo systemctl stop rag-system

# 备份数据
tar -czf $BACKUP_DIR/chroma_db_$DATE.tar.gz -C $DATA_DIR .

# 启动服务
sudo systemctl start rag-system

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: chroma_db_$DATE.tar.gz"
```

### 自动备份

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /home/raguser/backup.sh >> /var/log/rag_backup.log 2>&1
```

## 安全考虑

### 1. 网络安全

- 使用HTTPS进行API调用
- 配置防火墙规则
- 限制不必要的端口访问

### 2. 数据安全

- 加密敏感数据
- 定期备份重要数据
- 实施访问控制

### 3. API安全

- 定期轮换API密钥
- 监控API使用情况
- 实施速率限制

## 性能优化

### 1. 系统优化

```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 1024" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 1024" >> /etc/sysctl.conf
sysctl -p
```

### 2. 应用优化

```python
# 使用连接池
# 启用缓存
# 优化批处理大小
# 调整超时参数
```

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查日志文件
   - 验证配置文件
   - 检查端口冲突

2. **性能问题**
   - 监控系统资源
   - 优化数据库查询
   - 调整并发设置

3. **内存泄漏**
   - 监控内存使用
   - 检查资源释放
   - 实施重启策略

### 日志分析

```bash
# 查看系统日志
journalctl -u rag-system -n 100

# 查看应用日志
tail -f /var/log/rag_system/rag_system.log

# 分析错误模式
grep ERROR /var/log/rag_system/rag_system.log | tail -20
```

## 扩展和缩放

### 水平扩展

- 使用负载均衡器
- 部署多个实例
- 共享数据库和存储

### 垂直扩展

- 增加CPU和内存
- 优化单实例性能
- 使用更快的存储

## 更新和维护

### 更新流程

1. 备份当前数据和配置
2. 测试新版本
3. 部署更新
4. 验证功能
5. 监控性能

### 维护计划

- **每日**: 检查日志和监控
- **每周**: 清理临时文件
- **每月**: 更新依赖和安全补丁
- **每季度**: 性能调优和容量规划