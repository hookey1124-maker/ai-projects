# 新品周报可视化看板

基于 Vite + Chart.js 的新品周报数据可视化工程，支持多周期数据汇总与多维度分析。

## 功能特性

- 📊 **数据总览** - KPI指标、图表可视化
- 🏷️ **品线维度** - 按品类分析销量、销售额、环比
- 👤 **分析人维度** - 按负责人分析新品表现
- 🔗 **拓展类型** - 原开品/拓展品/组合件对比
- ⏱️ **分析及时率** - 新品跟进及时程度
- 📦 **新品出单情况** - 8日内/8日外/未出单分析
- 📉 **低占比新品** - 市占<75%的新品追踪
- 💰 **PLP复盘** - 广告投放效果分析
- 📊 **四三累计** - 历史新品追踪明细

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

构建产物将输出到 `dist/` 目录

### 代码检查

```bash
# ESLint 检查
npm run lint

# 代码格式化
npm run format
```

## 项目结构

```
├── src/
│   ├── data/           # 数据模块
│   │   ├── config.js       # 全局配置
│   │   ├── kpiData.js      # KPI数据
│   │   ├── catData.js      # 品线数据
│   │   ├── anData.js       # 分析人数据
│   │   ├── tzData.js       # 拓展类型数据
│   │   ├── timelyData.js   # 及时率数据
│   │   ├── orderData.js    # 出单情况数据
│   │   ├── lowShareData.js # 低占比新品数据
│   │   ├── plpData.js      # PLP广告数据
│   │   └── cum43Data.js   # 四三累计数据
│   ├── charts/         # 图表模块
│   │   └── chartInit.js   # Chart.js初始化
│   ├── components/     # 组件模块
│   │   └── tableRender.js # 表格渲染
│   ├── utils/          # 工具函数
│   │   └── helpers.js     # 辅助函数
│   ├── styles/         # 样式文件
│   │   └── global.css     # 全局样式
│   └── index.js        # 应用入口
├── public/            # 静态资源
├── index.html         # HTML入口
├── package.json
├── vite.config.js     # Vite配置
├── .eslintrc.js        # ESLint配置
└── .prettierrc        # Prettier配置
```

## 数据规则

### 低占比新品定义
- 市场份额 < 75%
- 且存在竞品订单

### 周期外过滤
- 统计周期：4.30-5.6
- 过滤规则：实际上架日期 > 5.6 的SKU不纳入统计

### 金额单位
- 所有销售额以 USD 原值显示
- 禁止货币转换

## 使用说明

### 更新数据

1. 修改 `src/data/` 目录下对应数据文件
2. 更新 `PERIOD` 配置中的周期信息
3. 运行 `npm run dev` 查看效果

### 添加新板块

1. 在 `index.html` 添加导航链接
2. 在 `src/data/` 创建新数据模块
3. 在 `src/components/` 创建渲染逻辑
4. 在 `src/index.js` 初始化

## 技术栈

- **构建工具**: Vite 5.x
- **图表库**: Chart.js 4.x
- **代码规范**: ESLint + Prettier
- **开发服务器**: Vite Dev Server

## 许可证

ISC
