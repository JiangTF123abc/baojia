# 故障排除指南

## 问题：新建项目点击确认没有反应，后端返回500错误

### 诊断结果

✅ 数据库连接正常  
✅ 数据库表已创建  
✅ 管理员账号存在  
✅ Flask应用可以创建  

### 可能的原因和解决方案

#### 1. 后端服务未启动或崩溃

**检查方法：**
```bash
# 查看后端窗口是否有错误信息
# 或者手动启动后端
cd backend
python run.py
```

**解决方案：**
- 如果看到错误信息，记录下来
- 如果端口被占用，更改端口或关闭占用进程

#### 2. CORS跨域问题

**症状：** 浏览器控制台显示CORS错误

**解决方案：** 添加CORS支持

在 `backend/app/__init__.py` 中添加：

```python
from flask_cors import CORS

def create_app(config=None) -> Flask:
    app = Flask(__name__)
    
    # ... 现有配置 ...
    
    # 添加CORS支持
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # ... 其余代码 ...
```

然后安装flask-cors：
```bash
pip install flask-cors
```

#### 3. 认证问题

**症状：** 401 Unauthorized错误

**解决方案：**
- 检查是否已登录
- 检查JWT token是否有效
- 清除浏览器缓存和localStorage

#### 4. 数据库连接超时

**症状：** 请求很慢然后超时

**解决方案：** 使用本地SQLite数据库进行测试

```bash
# 设置环境变量使用测试配置
set FLASK_ENV=testing
python run.py
```

### 快速修复步骤

1. **重启后端服务**
   ```bash
   # 关闭现有后端窗口
   # 重新运行
   cd backend
   python run.py
   ```

2. **检查后端日志**
   - 查看后端窗口的输出
   - 查找错误堆栈信息

3. **测试API**
   ```bash
   cd backend
   python test_api.py
   ```

4. **使用浏览器开发者工具**
   - 打开F12开发者工具
   - 查看Network标签
   - 查看Console标签的错误信息
   - 检查请求的详细信息（Headers, Payload, Response）

### 临时解决方案：使用SQLite

如果SQL Server连接有问题，可以临时使用SQLite：

1. 修改 `backend/.env`：
   ```
   FLASK_ENV=testing
   ```

2. 重新初始化数据库：
   ```bash
   cd backend
   python init_db.py
   ```

3. 启动服务：
   ```bash
   python run.py
   ```

### 获取更多帮助

如果问题仍然存在，请提供：
1. 后端窗口的完整错误信息
2. 浏览器控制台的错误信息
3. Network标签中失败请求的详细信息
