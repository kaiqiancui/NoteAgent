# 前端开发计划

## 🎯 核心目标

构建一个简洁高效的视频学习界面，实现：
1. 视频播放 + 时间跳转
2. 快速笔记标记 + 编辑
3. AI 助手问答

## 📋 功能清单

### 必须实现（MVP）

#### 1. 视频播放器模块
- [ ] 视频上传组件
- [ ] 视频播放控制（播放/暂停/进度条）
- [ ] 时间显示（当前时间 / 总时长）
- [ ] 音量控制
- [ ] 全屏支持
- [ ] 时间跳转接口（供笔记调用）

#### 2. 笔记管理模块
- [ ] 快速标记按钮（三种类型）
  - 🔴 重要知识点
  - 🟡 疑问
  - 🟢 灵感/补充
- [ ] 笔记列表显示
- [ ] 时间戳点击跳转
- [ ] Markdown 编辑器
- [ ] 笔记保存（自动保存）
- [ ] 笔记导出（Markdown 文件）

#### 3. AI 助手模块
- [ ] 截图按钮（捕获当前帧）
- [ ] 问题输入框
- [ ] WebSocket 连接
- [ ] 流式回答显示
- [ ] 回答插入笔记功能

#### 4. 布局与交互
- [ ] 左右分栏布局（70% / 30%）
- [ ] Tab 切换（笔记 / AI）
- [ ] 响应式设计（可选，优先桌面端）

### 增强功能（可选）

- [ ] 键盘快捷键（空格播放/暂停等）
- [ ] 专注模式（隐藏右侧面板）
- [ ] 拖拽调整分栏宽度
- [ ] 实时字幕显示
- [ ] 视频分析结果展示

## 🏗️ 技术栈

### 核心技术
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具（快速热更新）

### UI 组件库
- **Ant Design** - 成熟的 React UI 库
  - 优点：组件丰富、开箱即用、文档完善
  - 组件：Button, Input, Tabs, Card, message 等

### 功能库
- **Axios** - HTTP 请求
- **react-markdown** - Markdown 渲染
- **HTML5 Video API** - 视频播放（或 video.js）

### 状态管理
- **React useState + useContext** - 简单场景足够
- 不使用 Redux/Zustand（避免过度工程）

## 📁 项目结构

```
frontend/
├── public/
│   └── index.html
│
├── src/
│   ├── main.tsx                 # 入口文件
│   ├── App.tsx                  # 根组件
│   ├── App.css                  # 全局样式
│   │
│   ├── components/              # UI 组件
│   │   ├── Layout/
│   │   │   ├── MainLayout.tsx       # 主布局（左右分栏）
│   │   │   └── MainLayout.css
│   │   │
│   │   ├── VideoPlayer/
│   │   │   ├── VideoPlayer.tsx      # 视频播放器
│   │   │   ├── VideoUploader.tsx    # 视频上传
│   │   │   └── VideoPlayer.css
│   │   │
│   │   ├── NotePanel/
│   │   │   ├── NotePanel.tsx        # 笔记面板容器
│   │   │   ├── NoteList.tsx         # 笔记列表
│   │   │   ├── NoteItem.tsx         # 单条笔记
│   │   │   ├── NoteEditor.tsx       # 笔记编辑器
│   │   │   ├── QuickMarkButton.tsx  # 快速标记按钮
│   │   │   └── NotePanel.css
│   │   │
│   │   └── AIPanel/
│   │       ├── AIPanel.tsx          # AI 面板容器
│   │       ├── ScreenshotButton.tsx # 截图按钮
│   │       ├── QuestionInput.tsx    # 问题输入
│   │       ├── StreamAnswer.tsx     # 流式回答显示
│   │       └── AIPanel.css
│   │
│   ├── services/                # API 服务
│   │   ├── api.ts              # Axios 配置
│   │   ├── videoApi.ts         # 视频相关 API
│   │   ├── noteApi.ts          # 笔记相关 API
│   │   └── websocket.ts        # WebSocket 客户端
│   │
│   ├── hooks/                   # 自定义 Hooks
│   │   ├── useVideoPlayer.ts   # 视频播放器逻辑
│   │   ├── useNotes.ts         # 笔记管理逻辑
│   │   └── useAI.ts            # AI 交互逻辑
│   │
│   ├── types/                   # TypeScript 类型
│   │   └── index.ts            # 所有类型定义
│   │
│   └── utils/                   # 工具函数
│       ├── timeFormat.ts       # 时间格式化
│       └── markdown.ts         # Markdown 处理
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 🔄 开发流程

### Phase 1: 项目初始化（今天）

**时间**: 1-2 小时

**任务**:
1. 创建 Vite + React + TypeScript 项目
2. 安装依赖（Ant Design, Axios, react-markdown）
3. 配置 Vite（代理、端口等）
4. 创建基础目录结构
5. 定义 TypeScript 类型

**产出**:
- ✅ 项目可以运行
- ✅ 能看到 "Hello World"
- ✅ 热更新正常

### Phase 2: 基础布局（1-2 天）

**任务**:
1. 实现 MainLayout 组件（左右分栏）
2. 实现 Tab 切换（笔记 / AI）
3. 添加基础样式

**产出**:
- ✅ 布局框架完成
- ✅ Tab 切换正常

### Phase 3: 视频播放器（2-3 天）

**任务**:
1. 视频上传组件
   - 文件选择
   - 上传进度显示
   - 上传成功处理
2. 视频播放器
   - HTML5 video 基础控制
   - 播放/暂停
   - 进度条
   - 时间显示
3. 时间跳转功能（接受外部调用）

**产出**:
- ✅ 能上传视频
- ✅ 能播放视频
- ✅ 能跳转到指定时间

### Phase 4: 笔记功能（3-4 天）

**任务**:
1. 快速标记按钮
   - 三种类型按钮
   - 点击创建笔记
   - 自动记录当前时间
2. 笔记列表
   - 显示所有笔记
   - 时间戳点击跳转
   - 按时间排序
3. 笔记编辑器
   - Markdown 输入
   - 实时预览
   - 自动保存
4. 笔记导出
   - 生成 Markdown 文件
   - 下载到本地

**产出**:
- ✅ 能创建笔记
- ✅ 能编辑笔记
- ✅ 能跳转视频
- ✅ 能导出笔记

### Phase 5: AI 助手（3-4 天）

**任务**:
1. 截图功能
   - 捕获当前视频帧
   - Canvas 转 base64
   - 显示截图预览
2. WebSocket 连接
   - 连接后端 WebSocket
   - 发送问题
   - 接收流式回答
3. 问答界面
   - 问题输入框
   - 回答实时显示
   - 插入笔记功能

**产出**:
- ✅ 能截图
- ✅ 能提问
- ✅ 能看到 AI 回答
- ✅ 能插入笔记

### Phase 6: 联调与优化（2-3 天）

**任务**:
1. 前后端完整联调
2. 错误处理
3. Loading 状态
4. 用户体验优化
5. Bug 修复

**产出**:
- ✅ 完整流程打通
- ✅ 错误提示友好
- ✅ 体验流畅

### Phase 7: 增强功能（可选，1 周）

**任务**:
1. 键盘快捷键
2. 专注模式
3. 拖拽调整分栏
4. UI 美化

## 🎨 UI 设计原则

### 布局
- **左侧（70%）**: 视频播放器
- **右侧（30%）**: 笔记/AI 面板（Tab 切换）
- **顶部**: 简洁的标题栏（可选）

### 配色方案
- 主色调：蓝色系（专业、清爽）
- 辅助色：
  - 红色：重要笔记
  - 黄色：疑问
  - 绿色：灵感
- 背景：浅灰色（#f0f2f5）

### 交互原则
- **极简**：减少不必要的按钮和装饰
- **高效**：常用功能一键触达
- **反馈**：操作立即给出视觉反馈

## 📊 开发时间估算

| 阶段 | 任务 | 估计时间 |
|------|------|---------|
| Phase 1 | 项目初始化 | 1-2 小时 |
| Phase 2 | 基础布局 | 1-2 天 |
| Phase 3 | 视频播放器 | 2-3 天 |
| Phase 4 | 笔记功能 | 3-4 天 |
| Phase 5 | AI 助手 | 3-4 天 |
| Phase 6 | 联调优化 | 2-3 天 |
| Phase 7 | 增强功能 | 1 周（可选） |
| **总计** | **MVP** | **2-3 周** |

## 🔧 开发环境要求

- Node.js 18+
- npm 或 yarn
- VSCode（推荐）
- 浏览器：Chrome/Edge（开发调试）

## 📝 开发规范

### 命名规范
- **组件**: PascalCase（如 `VideoPlayer.tsx`）
- **函数**: camelCase（如 `handlePlay`）
- **常量**: UPPER_SNAKE_CASE（如 `API_BASE_URL`）

### 文件组织
- 一个组件一个文件夹
- 组件文件 + 样式文件放在一起
- 相关的子组件放在同一文件夹

### 代码风格
- 使用 TypeScript 严格模式
- 使用函数组件 + Hooks
- 使用 ESLint + Prettier

## 🎯 成功标准

### MVP 完成标准
- [ ] 能上传视频并播放
- [ ] 能创建和编辑笔记
- [ ] 笔记时间戳能跳转视频
- [ ] 能截图并向 AI 提问
- [ ] AI 能流式返回回答
- [ ] 能导出 Markdown 笔记

### 用户体验标准
- [ ] 界面简洁清爽
- [ ] 操作响应迅速（< 100ms）
- [ ] 错误提示友好
- [ ] 加载状态明确

## 🚀 立即开始

**第一步：创建项目**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

**第二步：安装依赖**
```bash
npm install antd axios react-markdown
```

**第三步：配置 Vite**
修改 `vite.config.ts`，添加代理配置。

**第四步：创建目录结构**
按照上面的结构创建文件夹。

**第五步：开始开发**
从 MainLayout 开始，逐步实现各个模块。

---

**准备好了吗？让我们开始创建项目！** 🎉
