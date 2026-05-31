# 周报系统项目总览

## 目标

本项目是基于 Vite + React + TypeScript 的周报自动生成系统。当前已存在“总销售状态”分析页，后续会扩展为多个业务状态板块，并允许不同开发者或 AI 编程工具分模块开发，最后统一整合。

## 模块划分

当前一级模块为：

1. 总销售状态：承接现有销量、销售额、市占比、在售价、出单均价等总销售分析能力。
2. 新品状态：预留新品上市、动销、爬坡、异常判断入口。
3. 广告状态：预留广告花费、ACOS、CPC、关键词、转化等分析入口。
4. 价格状态：预留在售价、出单均价、调价和价格异常入口。
5. 账号流量状态：预留会话、页面浏览、转化和流量异常入口。
6. 销量预估：预留基于历史销量、趋势和外部假设的预测入口。

## 目录结构

核心结构：

```text
src/
  dataCenter/
    types.ts
    periodParser.ts
    salesAdapter.ts
    moduleRegistry.ts

  components/
    common/
      ModulePageLayout.tsx
      KpiCard.tsx
      StatusTag.tsx
      EmptyState.tsx
      SectionCard.tsx
      FilterBar.tsx

  modules/
    salesStatus/
    newProductStatus/
    adsStatus/
    pricingStatus/
    accountTrafficStatus/
    salesForecast/
```

## 数据流向

主销售 Excel 仍由现有 `parseWorkbook` 解析，核心口径不在本次改造中改变。

推荐数据流：

```text
Excel / 独立业务报表
  -> utils/excelParser.ts 或模块独立 adapter
  -> dataCenter
  -> modules/*/*Adapter.ts
  -> modules/*/*Rules.ts
  -> modules/*/*Summary.ts
  -> modules/*/*Page.tsx
```

所有模块页面只消费已经转换好的结构化数据，不直接解析原始 Excel。

## 路由和菜单

模块菜单统一由 `src/dataCenter/moduleRegistry.ts` 管理。Sidebar 根据注册表渲染 6 个一级入口，App 使用 hash 路由切换模块，例如 `#/sales-status`、`#/ads-status`。

新增模块时优先扩展模块目录和注册表，不要在 Sidebar 中硬编码菜单。
