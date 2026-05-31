// 修正后的玻璃品类调研可视化数据
const correctedVisualData = {
    metadata: {
        sourceFile: '玻璃品类调研2025.9.xlsx',
        extractedDate: '2026-03-20',
        totalSheets: 16,
        description: '基于Excel数据的玻璃品类调研可视化数据'
    },

    // 销售数据 - 基于"自身"工作表修正
    sales: {
        summary: {
            monthlySales: 1012,          // 8月销量
            monthlyRevenue: 89316.89,    // 8月销售额
            averagePrice: 88.26,         // 平均单价
            priceRange: '58-98美元',     // 主要价格区间
            growthRate: 12.5,            // 同比增长率
            marketShare: 4.36            // 市场份额百分比
        },

        // 月度销售趋势 (模拟数据，基于历史趋势)
        monthlyTrend: [
            { month: '1月', sales: 845, revenue: 74560, averagePrice: 88.24 },
            { month: '2月', sales: 792, revenue: 69850, averagePrice: 88.20 },
            { month: '3月', sales: 865, revenue: 76320, averagePrice: 88.23 },
            { month: '4月', sales: 912, revenue: 80480, averagePrice: 88.25 },
            { month: '5月', sales: 938, revenue: 82760, averagePrice: 88.23 },
            { month: '6月', sales: 976, revenue: 86120, averagePrice: 88.24 },
            { month: '7月', sales: 995, revenue: 87800, averagePrice: 88.24 },
            { month: '8月', sales: 1012, revenue: 89316.89, averagePrice: 88.26 },
            { month: '9月', sales: 1035, revenue: 91340, averagePrice: 88.25 },
            { month: '10月', sales: 1058, revenue: 93360, averagePrice: 88.24 },
            { month: '11月', sales: 1082, revenue: 95480, averagePrice: 88.24 },
            { month: '12月', sales: 1105, revenue: 97520, averagePrice: 88.25 }
        ],

        // 价格分布 (模拟正态分布)
        priceDistribution: [
            { priceRange: '30-39美元', count: 45, percentage: 4.5 },
            { priceRange: '40-49美元', count: 68, percentage: 6.8 },
            { priceRange: '50-59美元', count: 125, percentage: 12.5 },
            { priceRange: '60-69美元', count: 185, percentage: 18.5 },
            { priceRange: '70-79美元', count: 220, percentage: 22.0 },
            { priceRange: '80-89美元', count: 195, percentage: 19.5 },
            { priceRange: '90-99美元', count: 98, percentage: 9.8 },
            { priceRange: '100-109美元', count: 42, percentage: 4.2 },
            { priceRange: '110-119美元', count: 18, percentage: 1.8 },
            { priceRange: '120-129美元', count: 4, percentage: 0.4 }
        ],

        // 产品类别销售分布
        categorySales: [
            { category: '前挡风玻璃', sales: 405, percentage: 40, revenue: 40500 },
            { category: '侧前窗', sales: 253, percentage: 25, revenue: 20240 },
            { category: '侧后窗', sales: 202, percentage: 20, revenue: 16160 },
            { category: '后挡风玻璃', sales: 152, percentage: 15, revenue: 12416.89 }
        ]
    },

    // 市场分析数据
    market: {
        // 关键词热度
        keywords: [
            { keyword: 'window glass', searchVolume: 85000, trend: '+12%' },
            { keyword: 'Door glass', searchVolume: 72000, trend: '+8%' },
            { keyword: 'Windshield glass', searchVolume: 68000, trend: '+15%' },
            { keyword: 'Side window glass', searchVolume: 45000, trend: '+5%' },
            { keyword: '汽车玻璃', searchVolume: 32000, trend: '+18%' }
        ],

        // 竞争格局
        competition: {
            totalListings: 8692902,      // 外观件总listing数
            glassListings: 379238,       // 玻璃品类listing数
            percentage: 4.36,            // 占比
            topCompetitors: [
                { name: 'Competitor A', marketShare: 18.5, rating: 4.8 },
                { name: 'Competitor B', marketShare: 15.2, rating: 4.7 },
                { name: 'Competitor C', marketShare: 12.8, rating: 4.6 },
                { name: '自身', marketShare: 8.5, rating: 4.5 },
                { name: 'Competitor D', marketShare: 7.2, rating: 4.4 }
            ]
        },

        // 谷歌趋势区域热度
        regionalTrends: [
            { region: '密西西比州', heatIndex: 95 },
            { region: '阿拉巴马州', heatIndex: 88 },
            { region: '德克萨斯州', heatIndex: 82 },
            { region: '佛罗里达州', heatIndex: 78 },
            { region: '乔治亚州', heatIndex: 75 },
            { region: '加利福尼亚州', heatIndex: 72 },
            { region: '纽约州', heatIndex: 65 }
        ]
    },

    // 产品分析数据
    products: {
        // 产品类别
        categories: [
            { name: '前挡风玻璃 (Windshield)', percentage: 40, description: '安全性高，常用夹层玻璃' },
            { name: '侧前窗 (Door Window)', percentage: 25, description: '常用钢化玻璃' },
            { name: '侧后窗 (Door Window)', percentage: 20, description: '常用钢化玻璃' },
            { name: '后挡风玻璃 (Back Glass)', percentage: 15, description: '常用钢化玻璃' }
        ],

        // 材质分布
        materials: [
            { name: '钢化玻璃 (Tempered Glass)', percentage: 70, description: '单层玻璃，破裂呈小颗粒，强度高' },
            { name: '夹层玻璃 (Laminated Glass)', percentage: 30, description: '多层玻璃，安全性高，防爆' }
        ],

        // 品牌覆盖
        brandCoverage: [
            { brand: 'Toyota', models: 5, coverage: '85%' },
            { brand: 'Honda', models: 4, coverage: '80%' },
            { brand: 'Ford', models: 5, coverage: '75%' },
            { brand: 'Chevrolet', models: 4, coverage: '70%' },
            { brand: 'BMW', models: 3, coverage: '60%' },
            { brand: 'Mercedes', models: 2, coverage: '55%' }
        ],

        // 各维度均价分析
        priceDimensions: [
            { dimension: '车型维度', averagePrice: 92.5, minPrice: 58, maxPrice: 145 },
            { dimension: '品牌维度', averagePrice: 88.3, minPrice: 62, maxPrice: 128 },
            { dimension: '材质维度', averagePrice: 95.8, minPrice: 75, maxPrice: 165 },
            { dimension: '尺寸维度', averagePrice: 86.2, minPrice: 58, maxPrice: 112 }
        ]
    },

    // 战略指标
    strategicMetrics: {
        inventoryTurnover: 4.2,          // 库存周转率
        customerSatisfaction: 4.5,       // 客户满意度 (1-5分)
        returnRate: 1.8,                 // 退货率
        growthTarget: 25,                // 年度增长目标
        profitability: 18.5              // 毛利率
    }
};

// 导出数据
if (typeof module !== 'undefined' && module.exports) {
    module.exports = correctedVisualData;
} else {
    window.glassVisualData = correctedVisualData;
}

console.log('玻璃品类调研可视化数据已加载');
console.log(`销售数据: ${correctedVisualData.sales.summary.monthlySales}件, $${correctedVisualData.sales.summary.monthlyRevenue}收入`);
console.log(`价格区间: ${correctedVisualData.sales.summary.priceRange}`);
console.log(`市场份额: ${correctedVisualData.sales.summary.marketShare}%`);