
// ========== 数据定义 ==========
const ALL_DATA = [{"sku": "11547", "batch": "1月", "analyst": "朱培源", "cat": "机盖及附件", "expand": "原开品", "qty": 2.0, "comp": 1.0, "share": 0.666666666666667, "order": "N", "status": "站外出单"}, {"sku": "11650", "batch": "1月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 14.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11674", "batch": "1月", "analyst": "朱培源", "cat": "机盖及附件", "expand": "原开品", "qty": 16.0, "comp": 6.0, "share": 0.727272727272727, "order": "Y", "status": "正常"}, {"sku": "11668", "batch": "1月", "analyst": "朱培源", "cat": "机盖及附件", "expand": "原开品", "qty": 7.0, "comp": 6.0, "share": 0.538461538461538, "order": "Y", "status": "竞争无优势"}, {"sku": "11681", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "拓展品", "qty": 1.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11742", "batch": "1月", "analyst": "俞东旭", "cat": "挡泥板", "expand": "原开品", "qty": 11.0, "comp": 1.0, "share": 0.916666666666667, "order": "Y", "status": "正常"}, {"sku": "11603", "batch": "1月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 7.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "正常"}, {"sku": "11704", "batch": "1月", "analyst": "俞东旭", "cat": "车身外扩件", "expand": "拓展品", "qty": 6.0, "comp": 8.0, "share": 0.428571428571429, "order": "N", "status": "竞争无优势"}, {"sku": "11699", "batch": "1月", "analyst": "俞东旭", "cat": "车身外扩件", "expand": "原开品", "qty": 5.0, "comp": 10.0, "share": 0.333333333333333, "order": "N", "status": "竞争无优势"}, {"sku": "11982", "batch": "1月", "analyst": "朱培源", "cat": "机盖及附件", "expand": "原开品", "qty": 6.0, "comp": 3.0, "share": 0.666666666666667, "order": "Y", "status": "正常"}, {"sku": "11911", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "原开品", "qty": 33.0, "comp": 80.0, "share": 0.292035398230089, "order": "N", "status": "竞争无优势"}, {"sku": "11848", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "拓展品", "qty": 7.0, "comp": 2.0, "share": 0.777777777777778, "order": "N", "status": "竞争无优势"}, {"sku": "11875", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "拓展品", "qty": 20.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11833", "batch": "1月", "analyst": "俞东旭", "cat": "其他", "expand": "原开品", "qty": 11.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11683", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "11733", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 4.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "无市场"}, {"sku": "11751", "batch": "1月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 40.0, "comp": 9.0, "share": 0.816326530612245, "order": "Y", "status": "正常"}, {"sku": "11830", "batch": "1月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 22.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "正常"}, {"sku": "11736", "batch": "1月", "analyst": "俞东旭", "cat": "挡泥板", "expand": "原开品", "qty": 13.0, "comp": 7.0, "share": 0.65, "order": "N", "status": "正常"}, {"sku": "11745", "batch": "1月", "analyst": "朱培源", "cat": "机盖及附件", "expand": "原开品", "qty": 9.0, "comp": 13.0, "share": 0.409090909090909, "order": "Y", "status": "竞争无优势"}, {"sku": "11777", "batch": "1月", "analyst": "朱培源", "cat": "机盖及附件", "expand": "原开品", "qty": 7.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "正常"}, {"sku": "11778", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "原开品", "qty": 1.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "无市场"}, {"sku": "11780", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "Y", "status": "站外出单"}, {"sku": "11781", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 17.0, "comp": 21.0, "share": 0.447368421052632, "order": "N", "status": "竞争无优势"}, {"sku": "11792", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "拓展品", "qty": 3.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "正常"}, {"sku": "11793", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 8.0, "comp": 1.0, "share": 0.888888888888889, "order": "N", "status": "站内无价格优势"}, {"sku": "11904", "batch": "1月", "analyst": "俞东旭", "cat": "车身外扩件", "expand": "原开品", "qty": 12.0, "comp": 9.0, "share": 0.571428571428571, "order": "Y", "status": "竞争无优势"}, {"sku": "11756", "batch": "1月", "analyst": "胡煜星", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "N", "status": "无市场"}, {"sku": "11757", "batch": "1月", "analyst": "朱培源", "cat": "饰条", "expand": "拓展品", "qty": 9.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "竞争无优势"}, {"sku": "11758", "batch": "1月", "analyst": "朱培源", "cat": "饰条", "expand": "原开品", "qty": 11.0, "comp": 24.0, "share": 0.314285714285714, "order": "Y", "status": "竞争无优势"}, {"sku": "11808", "batch": "1月", "analyst": "朱培源", "cat": "饰条", "expand": "拓展品", "qty": 7.0, "comp": 11.0, "share": 0.388888888888889, "order": "N", "status": "竞争无优势"}, {"sku": "11809", "batch": "1月", "analyst": "朱培源", "cat": "饰条", "expand": "原开品", "qty": 16.0, "comp": 9.0, "share": 0.64, "order": "Y", "status": "正常"}, {"sku": "11823", "batch": "1月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 5.0, "comp": 2.0, "share": 0.714285714285714, "order": "Y", "status": "竞争无优势"}, {"sku": "11814", "batch": "1月", "analyst": "朱培源", "cat": "饰条", "expand": "原开品", "qty": 5.0, "comp": 9.0, "share": 0.357142857142857, "order": "N", "status": "站内无价格优势"}, {"sku": "11815", "batch": "1月", "analyst": "朱培源", "cat": "饰条", "expand": "原开品", "qty": 2.0, "comp": 10.0, "share": 0.166666666666667, "order": "N", "status": "竞争无优势"}, {"sku": "11824", "batch": "1月", "analyst": "朱培源", "cat": "机盖及附件", "expand": "原开品", "qty": 4.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11855", "batch": "1月", "analyst": "俞东旭", "cat": "挡泥板", "expand": "原开品", "qty": 2.0, "comp": 3.0, "share": 0.4, "order": "N", "status": "站外出单"}, {"sku": "11856", "batch": "1月", "analyst": "俞东旭", "cat": "挡泥板", "expand": "拓展品", "qty": 2.0, "comp": 12.0, "share": 0.142857142857143, "order": "N", "status": "竞争无优势"}, {"sku": "11857", "batch": "1月", "analyst": "俞东旭", "cat": "挡泥板", "expand": "拓展品", "qty": 5.0, "comp": 12.0, "share": 0.294117647058824, "order": "N", "status": "竞争无优势"}, {"sku": "12303", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 28.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "站外出单"}, {"sku": "11933", "batch": "1月", "analyst": "朱培源", "cat": "饰条", "expand": "原开品", "qty": 1.0, "comp": 5.0, "share": 0.166666666666667, "order": "N", "status": "竞争无优势"}, {"sku": "11839", "batch": "1月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 51.0, "comp": 14.0, "share": 0.784615384615385, "order": "Y", "status": "正常"}, {"sku": "11840", "batch": "1月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 71.0, "comp": 36.0, "share": 0.663551401869159, "order": "Y", "status": "竞争无优势"}, {"sku": "11794", "batch": "1月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 30.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11866", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 6.0, "comp": 28.0, "share": 0.176470588235294, "order": "N", "status": "竞争无优势"}, {"sku": "11867", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 12.0, "comp": 18.0, "share": 0.4, "order": "N", "status": "竞争无优势"}, {"sku": "11826", "batch": "1月", "analyst": "俞东旭", "cat": "挡泥板", "expand": "原开品", "qty": 11.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "正常"}, {"sku": "11876", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 6.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "无市场"}, {"sku": "11936", "batch": "1月", "analyst": "王偲涵", "cat": "饰条", "expand": "拓展品", "qty": 4.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11937", "batch": "1月", "analyst": "王偲涵", "cat": "饰条", "expand": "拓展品", "qty": 5.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "正常"}, {"sku": "11874", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 5.0, "comp": 1.0, "share": 0.833333333333333, "order": "Y", "status": "正常"}, {"sku": "11925", "batch": "1月", "analyst": "章鹏", "cat": "车门系统", "expand": "原开品", "qty": 26.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11852", "batch": "1月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 7.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "正常"}, {"sku": "12359", "batch": "2月", "analyst": "胡煜星", "cat": "车门系统", "expand": "组合件", "qty": 10.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11921", "batch": "2月", "analyst": "王偲涵", "cat": "车身外扩件", "expand": "拓展品", "qty": 40.0, "comp": 8.0, "share": 0.833333333333333, "order": "Y", "status": "正常"}, {"sku": "11922", "batch": "2月", "analyst": "王偲涵", "cat": "车身外扩件", "expand": "拓展品", "qty": 94.0, "comp": 8.0, "share": 0.92156862745098, "order": "Y", "status": "正常"}, {"sku": "11923", "batch": "2月", "analyst": "王偲涵", "cat": "车身外扩件", "expand": "拓展品", "qty": 8.0, "comp": 2.0, "share": 0.8, "order": "Y", "status": "正常"}, {"sku": "11927", "batch": "2月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "N", "status": "站外出单"}, {"sku": "11928", "batch": "2月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 2.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "无市场"}, {"sku": "11926", "batch": "2月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 22.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11998", "batch": "2月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 13.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11929", "batch": "2月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 2.0, "comp": 4.0, "share": 0.333333333333333, "order": "Y", "status": "竞争无优势"}, {"sku": "12061", "batch": "2月", "analyst": "章鹏", "cat": "车门系统", "expand": "拓展品", "qty": 14.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11990", "batch": "2月", "analyst": "胡煜星", "cat": "车身外扩件", "expand": "原开品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "站外出单"}, {"sku": "11991", "batch": "2月", "analyst": "胡煜星", "cat": "车身外扩件", "expand": "拓展品", "qty": 2.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "无市场"}, {"sku": "11981", "batch": "2月", "analyst": "章鹏", "cat": "机盖及附件", "expand": "原开品", "qty": 3.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "无市场"}, {"sku": "11890", "batch": "2月", "analyst": "王偲涵", "cat": "车门系统", "expand": "拓展品", "qty": 5.0, "comp": 5.0, "share": 0.5, "order": "N", "status": "竞争无优势"}, {"sku": "11989", "batch": "2月", "analyst": "章鹏", "cat": "挡泥板", "expand": "原开品", "qty": 8.0, "comp": 7.0, "share": 0.533333333333333, "order": "Y", "status": "无市场"}, {"sku": "12088", "batch": "2月", "analyst": "王偲涵", "cat": "饰条", "expand": "拓展品", "qty": 13.0, "comp": 13.0, "share": 0.5, "order": "Y", "status": "竞争无优势"}, {"sku": "12089", "batch": "2月", "analyst": "王偲涵", "cat": "饰条", "expand": "拓展品", "qty": 13.0, "comp": 4.0, "share": 0.764705882352941, "order": "Y", "status": "正常"}, {"sku": "12002", "batch": "2月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 3.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "无市场"}, {"sku": "11938", "batch": "2月", "analyst": "王偲涵", "cat": "饰条", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "站外出单"}, {"sku": "12005", "batch": "2月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 39.0, "comp": 1.0, "share": 0.975, "order": "N", "status": "竞争无优势"}, {"sku": "12006", "batch": "2月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 37.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12011", "batch": "2月", "analyst": "章鹏", "cat": "机盖及附件", "expand": "原开品", "qty": 17.0, "comp": 8.0, "share": 0.68, "order": "Y", "status": "竞争无优势"}, {"sku": "12021", "batch": "2月", "analyst": "王偲涵", "cat": "其他", "expand": "原开品", "qty": 9.0, "comp": 16.0, "share": 0.36, "order": "Y", "status": "竞争无优势"}, {"sku": "12023", "batch": "2月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 0.0, "comp": 8.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12058", "batch": "2月", "analyst": "章鹏", "cat": "其他", "expand": "原开品", "qty": 24.0, "comp": 36.0, "share": 0.4, "order": "N", "status": "竞争无优势"}, {"sku": "12059", "batch": "2月", "analyst": "章鹏", "cat": "其他", "expand": "原开品", "qty": 16.0, "comp": 22.0, "share": 0.421052631578947, "order": "Y", "status": "竞争无优势"}, {"sku": "12060", "batch": "2月", "analyst": "章鹏", "cat": "饰条", "expand": "原开品", "qty": 5.0, "comp": 81.0, "share": 0.0581395348837209, "order": "N", "status": "竞争无优势"}, {"sku": "12139", "batch": "2月", "analyst": "章鹏", "cat": "机盖及附件", "expand": "原开品", "qty": 40.0, "comp": 2.0, "share": 0.952380952380952, "order": "N", "status": "正常"}, {"sku": "12087", "batch": "2月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 6.0, "comp": 4.0, "share": 0.6, "order": "N", "status": "正常"}, {"sku": "12143", "batch": "2月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 1.0, "comp": 1.0, "share": 0.5, "order": "N", "status": "正常"}, {"sku": "12079", "batch": "2月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 11.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "正常"}, {"sku": "12104", "batch": "2月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 2.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12105", "batch": "2月", "analyst": "朱培源", "cat": "挡泥板", "expand": "拓展品", "qty": 6.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "站外出单"}, {"sku": "12106", "batch": "2月", "analyst": "朱培源", "cat": "挡泥板", "expand": "拓展品", "qty": 3.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "无市场"}, {"sku": "12240", "batch": "2月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 11.0, "comp": 4.0, "share": 0.733333333333333, "order": "Y", "status": "竞争无优势"}, {"sku": "12225", "batch": "2月", "analyst": "章鹏", "cat": "其他", "expand": "原开品", "qty": 4.0, "comp": 1.0, "share": 0.8, "order": "N", "status": "正常"}, {"sku": "12073", "batch": "3月", "analyst": "朱培源", "cat": "车门系统", "expand": "原开品", "qty": 9.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12074", "batch": "3月", "analyst": "朱培源", "cat": "车门系统", "expand": "拓展品", "qty": 32.0, "comp": 1.0, "share": 0.96969696969697, "order": "Y", "status": "正常"}, {"sku": "12075", "batch": "3月", "analyst": "朱培源", "cat": "车门系统", "expand": "拓展品", "qty": 4.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "无市场"}, {"sku": "12252", "batch": "3月", "analyst": "胡煜星", "cat": "车门系统", "expand": "原开品", "qty": 10.0, "comp": 16.0, "share": 0.384615384615385, "order": "Y", "status": "竞争无优势"}, {"sku": "12165", "batch": "3月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 2.0, "comp": 7.0, "share": 0.222222222222222, "order": "Y", "status": "站外出单"}, {"sku": "12247", "batch": "3月", "analyst": "胡煜星", "cat": "其他", "expand": "原开品", "qty": 21.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "11102", "batch": "3月", "analyst": "章鹏", "cat": "车门系统", "expand": "原开品", "qty": 3.0, "comp": 10.0, "share": 0.230769230769231, "order": "N", "status": "竞争无优势"}, {"sku": "12071", "batch": "3月", "analyst": "胡煜星", "cat": "车身外扩件", "expand": "拓展品", "qty": 2.0, "comp": 1.0, "share": 0.666666666666667, "order": "Y", "status": "正常"}, {"sku": "12072", "batch": "3月", "analyst": "胡煜星", "cat": "车身外扩件", "expand": "原开品", "qty": 1.0, "comp": 0.0, "share": 1.0, "order": "N", "status": "无市场"}, {"sku": "12248", "batch": "3月", "analyst": "胡煜星", "cat": "其他", "expand": "原开品", "qty": 10.0, "comp": 6.0, "share": 0.625, "order": "Y", "status": "竞争无优势"}, {"sku": "12246", "batch": "3月", "analyst": "胡煜星", "cat": "其他", "expand": "原开品", "qty": 33.0, "comp": 3.0, "share": 0.916666666666667, "order": "Y", "status": "正常"}, {"sku": "12205", "batch": "3月", "analyst": "胡煜星", "cat": "车门系统", "expand": "原开品", "qty": 16.0, "comp": 121.0, "share": 0.116788321167883, "order": "Y", "status": "竞争无优势"}, {"sku": "12206", "batch": "3月", "analyst": "胡煜星", "cat": "车门系统", "expand": "原开品", "qty": 2.0, "comp": 18.0, "share": 0.1, "order": "Y", "status": "竞争无优势"}, {"sku": "11997", "batch": "3月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 1.0, "comp": 2.0, "share": 0.333333333333333, "order": "N", "status": "正常"}, {"sku": "12262", "batch": "3月", "analyst": "章鹏", "cat": "机盖及附件", "expand": "原开品", "qty": 3.0, "comp": 2.0, "share": 0.6, "order": "Y", "status": "正常"}, {"sku": "12244", "batch": "3月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 2.0, "comp": 7.0, "share": 0.222222222222222, "order": "N", "status": "正常"}, {"sku": "12243", "batch": "3月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 4.0, "comp": 7.0, "share": 0.363636363636364, "order": "N", "status": "正常"}, {"sku": "12304", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 7.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12085", "batch": "3月", "analyst": "章鹏", "cat": "机盖及附件", "expand": "拓展品", "qty": 5.0, "comp": 8.0, "share": 0.384615384615385, "order": "Y", "status": "竞争无优势"}, {"sku": "12086", "batch": "3月", "analyst": "章鹏", "cat": "机盖及附件", "expand": "原开品", "qty": 5.0, "comp": 17.0, "share": 0.227272727272727, "order": "Y", "status": "竞争无优势"}, {"sku": "12258", "batch": "3月", "analyst": "章鹏", "cat": "机盖及附件", "expand": "原开品", "qty": 9.0, "comp": 36.0, "share": 0.2, "order": "Y", "status": "竞争无优势"}, {"sku": "12210", "batch": "3月", "analyst": "章鹏", "cat": "饰条", "expand": "原开品", "qty": 3.0, "comp": 105.0, "share": 0.0277777777777778, "order": "N", "status": "竞争无优势"}, {"sku": "12250", "batch": "3月", "analyst": "王偲涵", "cat": "饰条", "expand": "拓展品", "qty": 2.0, "comp": 3.0, "share": 0.4, "order": "Y", "status": "无市场"}, {"sku": "12251", "batch": "3月", "analyst": "王偲涵", "cat": "饰条", "expand": "拓展品", "qty": 1.0, "comp": 4.0, "share": 0.2, "order": "N", "status": "竞争无优势"}, {"sku": "12332", "batch": "3月", "analyst": "王偲涵", "cat": "饰条", "expand": "原开品", "qty": 14.0, "comp": 4.0, "share": 0.777777777777778, "order": "Y", "status": "正常"}, {"sku": "12227", "batch": "3月", "analyst": "章鹏", "cat": "其他", "expand": "原开品", "qty": 8.0, "comp": 4.0, "share": 0.666666666666667, "order": "Y", "status": "正常"}, {"sku": "12309", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 3.0, "comp": 5.0, "share": 0.375, "order": "N", "status": "正常"}, {"sku": "12310", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 4.0, "comp": 4.0, "share": 0.5, "order": "Y", "status": "正常"}, {"sku": "12311", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 1.0, "comp": 6.0, "share": 0.142857142857143, "order": "N", "status": "竞争无优势"}, {"sku": "12312", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 4.0, "comp": 8.0, "share": 0.333333333333333, "order": "Y", "status": "竞争无优势"}, {"sku": "12441", "batch": "3月", "analyst": "胡煜星", "cat": "机盖及附件", "expand": "原开品", "qty": 5.0, "comp": 6.0, "share": 0.454545454545455, "order": "Y", "status": "竞争无优势"}, {"sku": "12271", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 72.0, "comp": 2.0, "share": 0.972972972972973, "order": "Y", "status": "正常"}, {"sku": "12270", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 15.0, "comp": 1.0, "share": 0.9375, "order": "Y", "status": "正常"}, {"sku": "12318", "batch": "3月", "analyst": "胡煜星", "cat": "车门系统", "expand": "原开品", "qty": 2.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12320", "batch": "3月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 0.0, "comp": 3.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12305", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 7.0, "comp": 1.0, "share": 0.875, "order": "Y", "status": "正常"}, {"sku": "12321", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 0.0, "comp": 10.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12272", "batch": "3月", "analyst": "胡煜星", "cat": "车门系统", "expand": "原开品", "qty": 7.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12292", "batch": "3月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 4.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12333", "batch": "3月", "analyst": "朱培源", "cat": "车门系统", "expand": "原开品", "qty": 0.0, "comp": 2.0, "share": 0.0, "order": "未出单", "status": "站外出单"}, {"sku": "12334", "batch": "3月", "analyst": "朱培源", "cat": "车门系统", "expand": "原开品", "qty": 1.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12368", "batch": "3月", "analyst": "胡煜星", "cat": "其他", "expand": "原开品", "qty": 4.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12306", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 7.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12307", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 5.0, "comp": 2.0, "share": 0.714285714285714, "order": "Y", "status": "竞争无优势"}, {"sku": "12308", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 11.0, "comp": 3.0, "share": 0.785714285714286, "order": "Y", "status": "正常"}, {"sku": "12293", "batch": "3月", "analyst": "朱培源", "cat": "车门系统", "expand": "原开品", "qty": 1.0, "comp": 1.0, "share": 0.5, "order": "Y", "status": "竞争无优势"}, {"sku": "12298", "batch": "3月", "analyst": "朱培源", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 2.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12299", "batch": "3月", "analyst": "朱培源", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 4.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12396", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "原开品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12291", "batch": "3月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12290", "batch": "3月", "analyst": "朱培源", "cat": "挡泥板", "expand": "原开品", "qty": 0.0, "comp": 2.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12391", "batch": "3月", "analyst": "章鹏", "cat": "其他", "expand": "原开品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12398", "batch": "3月", "analyst": "章鹏", "cat": "其他", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12357", "batch": "3月", "analyst": "胡煜星", "cat": "其他", "expand": "原开品", "qty": 1.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "站外出单"}, {"sku": "12423", "batch": "3月", "analyst": "胡煜星", "cat": "其他", "expand": "原开品", "qty": 1.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12387", "batch": "3月", "analyst": "俞东旭", "cat": "车身外扩件", "expand": "原开品", "qty": 0.0, "comp": 7.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12388", "batch": "3月", "analyst": "俞东旭", "cat": "车身外扩件", "expand": "原开品", "qty": 0.0, "comp": 4.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12474", "batch": "3月", "analyst": "章鹏", "cat": "饰条", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12429", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 1.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12424", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12386", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 2.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}, {"sku": "12426", "batch": "3月", "analyst": "胡煜星", "cat": "车门系统", "expand": "原开品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12483", "batch": "3月", "analyst": "胡煜星", "cat": "其他", "expand": "原开品", "qty": 2.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12484", "batch": "3月", "analyst": "胡煜星", "cat": "其他", "expand": "原开品", "qty": 1.0, "comp": 0.0, "share": 1.0, "order": "Y", "status": "正常"}, {"sku": "12414", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12422", "batch": "3月", "analyst": "俞东旭", "cat": "车门系统", "expand": "拓展品", "qty": 0.0, "comp": 0.0, "share": 0, "order": "未出单", "status": "无市场"}, {"sku": "12213", "batch": "3月", "analyst": "章鹏", "cat": "机盖及附件", "expand": "原开品", "qty": 0.0, "comp": 10.0, "share": 0.0, "order": "未出单", "status": "竞争无优势"}];
const LOW_SHARE_DATA = [{"sku": "LYAM-X2815-1", "cat": "机盖及附件", "analyst": "朱培源", "expand": "原开品", "qty": 2.0, "comp": 1.0, "share": 66.7, "order": "N", "status": "站外出单", "batch": "1月"}, {"sku": "LYAP-X2057", "cat": "机盖及附件", "analyst": "朱培源", "expand": "原开品", "qty": 16.0, "comp": 6.0, "share": 72.7, "order": "Y", "status": "正常", "batch": "1月"}, {"sku": "LYAP-X2060-1", "cat": "机盖及附件", "analyst": "朱培源", "expand": "原开品", "qty": 7.0, "comp": 6.0, "share": 53.8, "order": "Y", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAM-X2416-BK", "cat": "车身外扩件", "analyst": "俞东旭", "expand": "拓展品", "qty": 6.0, "comp": 8.0, "share": 42.9, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAM-X2416-C", "cat": "车身外扩件", "analyst": "俞东旭", "expand": "原开品", "qty": 5.0, "comp": 10.0, "share": 33.3, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAM-X2267-1", "cat": "机盖及附件", "analyst": "朱培源", "expand": "原开品", "qty": 6.0, "comp": 3.0, "share": 66.7, "order": "Y", "status": "正常", "batch": "1月"}, {"sku": "LYAM-X2575-1", "cat": "车门系统", "analyst": "胡煜星", "expand": "原开品", "qty": 33.0, "comp": 80.0, "share": 29.2, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAM-X2046-L", "cat": "挡泥板", "analyst": "俞东旭", "expand": "原开品", "qty": 13.0, "comp": 7.0, "share": 65.0, "order": "N", "status": "正常", "batch": "1月"}, {"sku": "LYAP-X1914", "cat": "机盖及附件", "analyst": "朱培源", "expand": "原开品", "qty": 9.0, "comp": 13.0, "share": 40.9, "order": "Y", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X1791-3L", "cat": "车门系统", "analyst": "俞东旭", "expand": "拓展品", "qty": 17.0, "comp": 21.0, "share": 44.7, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAM-X2305-1", "cat": "车身外扩件", "analyst": "俞东旭", "expand": "原开品", "qty": 12.0, "comp": 9.0, "share": 57.1, "order": "Y", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X1908-C", "cat": "饰条", "analyst": "朱培源", "expand": "原开品", "qty": 11.0, "comp": 24.0, "share": 31.4, "order": "Y", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X1910-BK", "cat": "饰条", "analyst": "朱培源", "expand": "拓展品", "qty": 7.0, "comp": 11.0, "share": 38.9, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X1910-C", "cat": "饰条", "analyst": "朱培源", "expand": "原开品", "qty": 16.0, "comp": 9.0, "share": 64.0, "order": "Y", "status": "正常", "batch": "1月"}, {"sku": "LYAP-X1939-1", "cat": "饰条", "analyst": "王偲涵", "expand": "原开品", "qty": 5.0, "comp": 2.0, "share": 71.4, "order": "Y", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X2020", "cat": "饰条", "analyst": "朱培源", "expand": "原开品", "qty": 5.0, "comp": 9.0, "share": 35.7, "order": "N", "status": "站内无价格优势", "batch": "1月"}, {"sku": "LYAP-X2021", "cat": "饰条", "analyst": "朱培源", "expand": "原开品", "qty": 2.0, "comp": 10.0, "share": 16.7, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X2081-1", "cat": "挡泥板", "analyst": "俞东旭", "expand": "原开品", "qty": 2.0, "comp": 3.0, "share": 40.0, "order": "N", "status": "站外出单", "batch": "1月"}, {"sku": "LYAP-X2081-1L", "cat": "挡泥板", "analyst": "俞东旭", "expand": "拓展品", "qty": 2.0, "comp": 12.0, "share": 14.3, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X2081-1R", "cat": "挡泥板", "analyst": "俞东旭", "expand": "拓展品", "qty": 5.0, "comp": 12.0, "share": 29.4, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X1915", "cat": "饰条", "analyst": "朱培源", "expand": "原开品", "qty": 1.0, "comp": 5.0, "share": 16.7, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-838-1R", "cat": "饰条", "analyst": "王偲涵", "expand": "原开品", "qty": 71.0, "comp": 36.0, "share": 66.4, "order": "Y", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X1994-RL", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 6.0, "comp": 28.0, "share": 17.6, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X1994-RR", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 12.0, "comp": 18.0, "share": 40.0, "order": "N", "status": "竞争无优势", "batch": "1月"}, {"sku": "LYAP-X1799", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 2.0, "comp": 4.0, "share": 33.3, "order": "Y", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAM-X2575-4", "cat": "车门系统", "analyst": "王偲涵", "expand": "拓展品", "qty": 5.0, "comp": 5.0, "share": 50.0, "order": "N", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAM-X2732", "cat": "挡泥板", "analyst": "章鹏", "expand": "原开品", "qty": 8.0, "comp": 7.0, "share": 53.3, "order": "Y", "status": "无市场", "batch": "2月"}, {"sku": "LYAP-X1920-BK", "cat": "饰条", "analyst": "王偲涵", "expand": "拓展品", "qty": 13.0, "comp": 13.0, "share": 50.0, "order": "Y", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAP-X2089", "cat": "机盖及附件", "analyst": "章鹏", "expand": "原开品", "qty": 17.0, "comp": 8.0, "share": 68.0, "order": "Y", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAP-X2135", "cat": "其他", "analyst": "王偲涵", "expand": "原开品", "qty": 9.0, "comp": 16.0, "share": 36.0, "order": "Y", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAP-X2146", "cat": "挡泥板", "analyst": "朱培源", "expand": "原开品", "qty": 0.0, "comp": 8.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAM-X2569-1", "cat": "其他", "analyst": "章鹏", "expand": "原开品", "qty": 24.0, "comp": 36.0, "share": 40.0, "order": "N", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAM-X2570-1", "cat": "其他", "analyst": "章鹏", "expand": "原开品", "qty": 16.0, "comp": 22.0, "share": 42.1, "order": "Y", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAM-X2574-1", "cat": "饰条", "analyst": "章鹏", "expand": "原开品", "qty": 5.0, "comp": 81.0, "share": 5.8, "order": "N", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAP-X1913", "cat": "饰条", "analyst": "王偲涵", "expand": "原开品", "qty": 6.0, "comp": 4.0, "share": 60.0, "order": "N", "status": "正常", "batch": "2月"}, {"sku": "LYAM-X2706", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 1.0, "comp": 1.0, "share": 50.0, "order": "N", "status": "正常", "batch": "2月"}, {"sku": "LYAP-X2148-1", "cat": "饰条", "analyst": "王偲涵", "expand": "原开品", "qty": 11.0, "comp": 4.0, "share": 73.3, "order": "Y", "status": "竞争无优势", "batch": "2月"}, {"sku": "LYAP-X1800-1", "cat": "车门系统", "analyst": "胡煜星", "expand": "原开品", "qty": 10.0, "comp": 16.0, "share": 38.5, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1877", "cat": "挡泥板", "analyst": "朱培源", "expand": "原开品", "qty": 2.0, "comp": 7.0, "share": 22.2, "order": "Y", "status": "站外出单", "batch": "3月"}, {"sku": "LYAM-X2254-L", "cat": "车门系统", "analyst": "章鹏", "expand": "原开品", "qty": 3.0, "comp": 10.0, "share": 23.1, "order": "N", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAM-X2980-BK", "cat": "车身外扩件", "analyst": "胡煜星", "expand": "拓展品", "qty": 2.0, "comp": 1.0, "share": 66.7, "order": "Y", "status": "正常", "batch": "3月"}, {"sku": "LYAP-X2308", "cat": "其他", "analyst": "胡煜星", "expand": "原开品", "qty": 10.0, "comp": 6.0, "share": 62.5, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1800-1L", "cat": "车门系统", "analyst": "胡煜星", "expand": "原开品", "qty": 16.0, "comp": 121.0, "share": 11.7, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1800-1R", "cat": "车门系统", "analyst": "胡煜星", "expand": "原开品", "qty": 2.0, "comp": 18.0, "share": 10.0, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAM-X2896", "cat": "饰条", "analyst": "王偲涵", "expand": "原开品", "qty": 1.0, "comp": 2.0, "share": 33.3, "order": "N", "status": "正常", "batch": "3月"}, {"sku": "LYAP-X2170", "cat": "机盖及附件", "analyst": "章鹏", "expand": "原开品", "qty": 3.0, "comp": 2.0, "share": 60.0, "order": "Y", "status": "正常", "batch": "3月"}, {"sku": "LYAP-X2190-L", "cat": "饰条", "analyst": "王偲涵", "expand": "原开品", "qty": 2.0, "comp": 7.0, "share": 22.2, "order": "N", "status": "正常", "batch": "3月"}, {"sku": "LYAP-X2190-R", "cat": "饰条", "analyst": "王偲涵", "expand": "原开品", "qty": 4.0, "comp": 7.0, "share": 36.4, "order": "N", "status": "正常", "batch": "3月"}, {"sku": "LYAP-X1911-BK", "cat": "机盖及附件", "analyst": "章鹏", "expand": "拓展品", "qty": 5.0, "comp": 8.0, "share": 38.5, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1911-C", "cat": "机盖及附件", "analyst": "章鹏", "expand": "原开品", "qty": 5.0, "comp": 17.0, "share": 22.7, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1927", "cat": "机盖及附件", "analyst": "章鹏", "expand": "原开品", "qty": 9.0, "comp": 36.0, "share": 20.0, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1934", "cat": "饰条", "analyst": "章鹏", "expand": "原开品", "qty": 3.0, "comp": 105.0, "share": 2.8, "order": "N", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2148-1L", "cat": "饰条", "analyst": "王偲涵", "expand": "拓展品", "qty": 2.0, "comp": 3.0, "share": 40.0, "order": "Y", "status": "无市场", "batch": "3月"}, {"sku": "LYAP-X2148-1R", "cat": "饰条", "analyst": "王偲涵", "expand": "拓展品", "qty": 1.0, "comp": 4.0, "share": 20.0, "order": "N", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2418", "cat": "其他", "analyst": "章鹏", "expand": "原开品", "qty": 8.0, "comp": 4.0, "share": 66.7, "order": "Y", "status": "正常", "batch": "3月"}, {"sku": "MD-002-FL", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 3.0, "comp": 5.0, "share": 37.5, "order": "N", "status": "正常", "batch": "3月"}, {"sku": "MD-002-FR", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 4.0, "comp": 4.0, "share": 50.0, "order": "Y", "status": "正常", "batch": "3月"}, {"sku": "MD-002-RL", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 1.0, "comp": 6.0, "share": 14.3, "order": "N", "status": "竞争无优势", "batch": "3月"}, {"sku": "MD-002-RR", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 4.0, "comp": 8.0, "share": 33.3, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAM-X2862", "cat": "机盖及附件", "analyst": "胡煜星", "expand": "原开品", "qty": 5.0, "comp": 6.0, "share": 45.5, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2417", "cat": "挡泥板", "analyst": "朱培源", "expand": "原开品", "qty": 0.0, "comp": 3.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1788-GR", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 0.0, "comp": 10.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2429", "cat": "车门系统", "analyst": "朱培源", "expand": "原开品", "qty": 0.0, "comp": 2.0, "share": 0.0, "order": "未出单", "status": "站外出单", "batch": "3月"}, {"sku": "MD-001-RL", "cat": "车门系统", "analyst": "俞东旭", "expand": "原开品", "qty": 5.0, "comp": 2.0, "share": 71.4, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2144-1", "cat": "车门系统", "analyst": "朱培源", "expand": "原开品", "qty": 1.0, "comp": 1.0, "share": 50.0, "order": "Y", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2144-1L", "cat": "车门系统", "analyst": "朱培源", "expand": "拓展品", "qty": 0.0, "comp": 2.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2144-1R", "cat": "车门系统", "analyst": "朱培源", "expand": "拓展品", "qty": 0.0, "comp": 4.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1878", "cat": "挡泥板", "analyst": "朱培源", "expand": "原开品", "qty": 0.0, "comp": 2.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2077", "cat": "车身外扩件", "analyst": "俞东旭", "expand": "原开品", "qty": 0.0, "comp": 7.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X2085", "cat": "车身外扩件", "analyst": "俞东旭", "expand": "原开品", "qty": 0.0, "comp": 4.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1788-BN", "cat": "车门系统", "analyst": "俞东旭", "expand": "拓展品", "qty": 0.0, "comp": 2.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}, {"sku": "LYAP-X1929", "cat": "机盖及附件", "analyst": "章鹏", "expand": "原开品", "qty": 0.0, "comp": 10.0, "share": 0.0, "order": "未出单", "status": "竞争无优势", "batch": "3月"}];
const BATCH_DATA = {"1月": {"sku": 53, "qty": 613.0, "comp": 371.0, "ordered": 24, "unorder": 28, "not_order": 1, "rate": 45.3, "share": 62.3, "qty_hb": null, "rate_hb": null}, "2月": {"sku": 36, "qty": 483.0, "comp": 235.0, "ordered": 19, "unorder": 14, "not_order": 3, "rate": 52.8, "share": 67.3, "qty_hb": -130.0, "rate_hb": 7.5}, "3月": {"sku": 67, "qty": 368.0, "comp": 467.0, "ordered": 39, "unorder": 9, "not_order": 19, "rate": 58.2, "share": 44.1, "qty_hb": -115.0, "rate_hb": 5.4}};
const CATEGORY_DATA = {"机盖及附件": {"qty_1": 51, "qty_2": 60, "qty_3": 27, "rate_1": 71.4, "rate_2": 66.7, "rate_3": 83.3, "qty_hb": -33, "rate_hb": 16.6}, "挡泥板": {"qty_1": 95, "qty_2": 30, "qty_3": 6, "rate_1": 33.3, "rate_2": 50.0, "rate_3": 40.0, "qty_hb": -24, "rate_hb": -10.0}, "车门系统": {"qty_1": 184, "qty_2": 69, "qty_3": 224, "rate_1": 31.6, "rate_2": 55.6, "rate_3": 60.6, "qty_hb": 155, "rate_hb": 5.0}, "车身外扩件": {"qty_1": 23, "qty_2": 144, "qty_3": 3, "rate_1": 33.3, "rate_2": 60.0, "rate_3": 25.0, "qty_hb": -141, "rate_hb": -35.0}, "其他": {"qty_1": 11, "qty_2": 53, "qty_3": 81, "rate_1": 100.0, "rate_2": 50.0, "rate_3": 81.8, "qty_hb": 28, "rate_hb": 31.8}, "饰条": {"qty_1": 249, "qty_2": 127, "qty_3": 27, "rate_1": 57.1, "rate_2": 44.4, "rate_3": 25.0, "qty_hb": -100, "rate_hb": -19.4}};
const ANALYST_DATA = {"朱培源": {"qty_1": 153, "qty_2": 22, "qty_3": 53, "rate_1": 58.8, "rate_2": 40.0, "rate_3": 53.8, "sku_1": 17, "sku_2": 5, "sku_3": 13, "qty_hb": 31, "rate_hb": 13.8}, "胡煜星": {"qty_1": 65, "qty_2": 12, "qty_3": 118, "rate_1": 33.3, "rate_2": 33.3, "rate_3": 88.2, "sku_1": 9, "sku_2": 3, "sku_3": 17, "qty_hb": 106, "rate_hb": 54.9}, "俞东旭": {"qty_1": 171, "qty_2": 40, "qty_3": 137, "rate_1": 26.3, "rate_2": 50.0, "rate_3": 50.0, "sku_1": 19, "sku_2": 6, "sku_3": 20, "qty_hb": 97, "rate_hb": 0.0}, "王偲涵": {"qty_1": 198, "qty_2": 278, "qty_3": 24, "rate_1": 71.4, "rate_2": 61.5, "rate_3": 33.3, "sku_1": 7, "sku_2": 13, "sku_3": 6, "qty_hb": -254, "rate_hb": -28.2}, "章鹏": {"qty_1": 26, "qty_2": 131, "qty_3": 36, "rate_1": 100.0, "rate_2": 55.6, "rate_3": 45.5, "sku_1": 1, "sku_2": 9, "sku_3": 11, "qty_hb": -95, "rate_hb": -10.1}};
const EXPAND_DATA = {"原开品": {"qty_1": 485, "qty_2": 260, "qty_3": 321, "rate_1": 51.4, "rate_2": 45.5, "rate_3": 63.5, "sku_1": 35, "sku_2": 22, "sku_3": 52, "qty_hb": 61, "rate_hb": 18.0}, "拓展品": {"qty_1": 128, "qty_2": 213, "qty_3": 47, "rate_1": 33.3, "rate_2": 61.5, "rate_3": 40.0, "sku_1": 18, "sku_2": 13, "sku_3": 15, "qty_hb": -166, "rate_hb": -21.5}, "组合件": {"qty_1": 0, "qty_2": 10, "qty_3": 0, "rate_1": 0, "rate_2": 100.0, "rate_3": 0, "sku_1": 0, "sku_2": 1, "sku_3": 0, "qty_hb": -10, "rate_hb": -100.0}};
const MARKET_DATA = {"站外出单": 11, "正常": 66, "竞争无优势": 54, "无市场": 23, "站内无价格优势": 2};

const COLORS = ['#0f3460','#e07b24','#08845a','#c0392b','#8e44ad','#2980b9','#16a085','#d35400','#7f8c8d'];

// ========== 环比辅助函数 ==========
function fmtHb(val, suffix) {
  if (val === null || val === undefined) return '<span class="hb-flat">-</span>';
  suffix = suffix || '';
  if (val > 0) return '<span class="hb-up">+' + val + suffix + '</span>';
  if (val < 0) return '<span class="hb-down">' + val + suffix + '</span>';
  return '<span class="hb-flat">0' + suffix + '</span>';
}

// ========== 图表函数 ==========
function mkBar(id, labels, datasets) {
  var ctx = document.getElementById(id);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: datasets.length > 1,
          position: 'top',
          labels: { font: { size: 10 } }
        }
      },
      scales: {
        x: { ticks: { font: { size: 10 }, maxRotation: 30 } },
        y: { ticks: { font: { size: 10 } }, beginAtZero: true }
      }
    }
  });
}
function mkLine(id, labels, datasets) {
  var ctx = document.getElementById(id);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: datasets.length > 1,
          position: 'top',
          labels: { font: { size: 10 } }
        }
      },
      scales: {
        x: { ticks: { font: { size: 10 } } },
        y: { ticks: { font: { size: 10 } } }
      }
    }
  });
}
function mkPie(id, labels, data) {
  var ctx = document.getElementById(id);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: { labels: labels, datasets: [{ data: data, backgroundColor: COLORS, borderWidth: 1 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'right', labels: { font: { size: 10 }, boxWidth: 12 } } }
    }
  });
}

// ========== 渲染品线表格 ==========
function renderCatTable() {
  var html = '';
  for (var cat in CATEGORY_DATA) {
    var d = CATEGORY_DATA[cat];
    var qtyHb = d.qty_hb > 0 ? '<span style="color:#08845a">+' + d.qty_hb + '</span>' : '<span style="color:#c0392b">' + d.qty_hb + '</span>';
    var rateHb = d.rate_hb > 0 ? '<span style="color:#08845a">+' + d.rate_hb + '%</span>' : '<span style="color:#c0392b">' + d.rate_hb + '%</span>';
    html += '<tr><td style="text-align:left;font-weight:600">' + cat + '</td><td>' + d.sku_3 + '</td><td>' + d.qty_3 + '</td><td>' + qtyHb + '</td><td>' + d.rate_3 + '%</td><td>' + rateHb + '</td></tr>';
  }
  document.getElementById('cat-tbody').innerHTML = html;
}

// ========== 渲染分析人表格 ==========
function renderAnalystTable() {
  var html = '';
  for (var name in ANALYST_DATA) {
    var d = ANALYST_DATA[name];
    var qtyHb = d.qty_hb > 0 ? '<span style="color:#08845a">+' + d.qty_hb + '</span>' : '<span style="color:#c0392b">' + d.qty_hb + '</span>';
    var rateHb = d.rate_hb > 0 ? '<span style="color:#08845a">+' + d.rate_hb + '%</span>' : '<span style="color:#c0392b">' + d.rate_hb + '%</span>';
    html += '<tr><td style="text-align:left;font-weight:600">' + name + '</td><td>' + d.sku_3 + '</td><td>' + d.qty_3 + '</td><td>' + qtyHb + '</td><td class="highlight">' + d.rate_3 + '%</td><td>' + rateHb + '</td></tr>';
  }
  document.getElementById('analyst-tbody').innerHTML = html;
}

// ========== 渲染拓展类型表格 ==========
function renderExpandTable() {
  var html = '';
  for (var exp in EXPAND_DATA) {
    var d = EXPAND_DATA[exp];
    var qtyHb = d.qty_hb > 0 ? '<span style="color:#08845a">+' + d.qty_hb + '</span>' : '<span style="color:#c0392b">' + d.qty_hb + '</span>';
    var rateHb = d.rate_hb > 0 ? '<span style="color:#08845a">+' + d.rate_hb + '%</span>' : '<span style="color:#c0392b">' + d.rate_hb + '%</span>';
    html += '<tr><td style="text-align:left;font-weight:600">' + exp + '</td><td>' + d.sku_3 + '</td><td>' + d.qty_3 + '</td><td>' + qtyHb + '</td><td>' + d.rate_3 + '%</td><td>' + rateHb + '</td></tr>';
  }
  document.getElementById('expand-tbody').innerHTML = html;
}

// ========== 渲染出单情况表格 ==========
function renderOrderTable() {
  var html = '';
  var batches = [['1月', '1月新品'], ['2月', '2月新品'], ['3月', '3月新品']];
  for (var i = 0; i < batches.length; i++) {
    var k = batches[i][0];
    var label = batches[i][1];
    var d = BATCH_DATA[k];
    var qty_hb_html = d.qty_hb !== null ? fmtHb(d.qty_hb, '') : '<span class="hb-flat">-</span>';
    var rate_hb_html = d.rate_hb !== null ? fmtHb(d.rate_hb, '%') : '<span class="hb-flat">-</span>';
    html += '<tr><td>' + label + '</td><td>' + d.sku + '</td><td>' + d.qty + '</td><td>' + qty_hb_html + '</td><td style="color:#08845a;font-weight:700">' + d.ordered + '</td><td style="color:#e07b24;font-weight:700">' + d.unorder + '</td><td>' + d.not_order + '</td><td class="highlight">' + d.rate + '%</td><td>' + rate_hb_html + '</td></tr>';
  }
  document.getElementById('order-tbody').innerHTML = html;
}

// ========== 渲染市场状态表格 ==========
function renderMarketTable() {
  var html = '';
  var total = Object.values(MARKET_DATA).reduce(function(a,b){return a+b;}, 0);
  for (var status in MARKET_DATA) {
    var count = MARKET_DATA[status];
    var pct = (count / total * 100).toFixed(1);
    html += '<tr><td style="text-align:left">' + status + '</td><td>' + count + '</td><td>' + pct + '%</td></tr>';
  }
  document.getElementById('market-tbody').innerHTML = html;
  var normalCount = MARKET_DATA['正常'] || 0;
  mkBar('chartMarketCompare', ['正常', '异常'], [{ label: '数量', data: [normalCount, total - normalCount], backgroundColor: ['#08845a', '#c0392b'] }]);
}

// ========== 渲染低占比新品表格 ==========
function renderLowShare() {
  var batch = document.getElementById('low-share-batch').value;
  var filtered = batch === 'all' ? LOW_SHARE_DATA : LOW_SHARE_DATA.filter(function(d){return d.batch === batch;});
  var html = '';
  for (var i = 0; i < filtered.length; i++) {
    var d = filtered[i];
    var sharePct = d.share > 0 ? d.share.toFixed(1) + '%' : '0%';
    var shareColor = d.share >= 75 ? '#08845a' : '#c0392b';
    var orderColor = d.order === 'Y' ? '#08845a' : d.order === 'N' ? '#e07b24' : '#c0392b';
    var statusColor = d.status === '正常' ? '#08845a' : '#c0392b';
    var batchColor = d.batch === '1月' ? '#adb5bd' : d.batch === '2月' ? '#667eea' : '#e74c3c';
    html += '<tr><td><span style="background:' + batchColor + ';color:white;padding:2px 8px;border-radius:10px;font-size:10px">' + d.batch + '</span></td><td style="text-align:left;font-weight:600">' + d.sku + '</td><td>' + d.cat + '</td><td>' + d.analyst + '</td><td>' + d.expand + '</td><td>' + d.qty + '</td><td>' + d.comp + '</td><td style="color:' + shareColor + ';font-weight:700">' + sharePct + '</td><td style="color:' + orderColor + ';font-weight:600">' + d.order + '</td><td style="color:' + statusColor + '">' + d.status + '</td></tr>';
  }
  document.getElementById('lowmkt-tbody').innerHTML = html;
}

// ========== 渲染全量明细表格 ==========
function renderDetailTable() {
  var batch = document.getElementById('detail-batch').value;
  var filtered = batch === 'all' ? ALL_DATA : ALL_DATA.filter(function(d){return d.batch === batch;});
  var html = '';
  for (var i = 0; i < filtered.length; i++) {
    var d = filtered[i];
    var isOrdered = d.order === 'Y';
    var bgClass = isOrdered ? 'row-ordered' : '';
    var sharePct = d.share > 0 ? d.share.toFixed(1) + '%' : '0%';
    var orderColor = isOrdered ? '#08845a' : '#e07b24';
    var statusColor = d.status === '正常' ? '#08845a' : '#c0392b';
    var batchColor = d.batch === '1月' ? '#adb5bd' : d.batch === '2月' ? '#667eea' : '#e74c3c';
    html += '<tr class="' + bgClass + '"><td>' + d.sku + '</td><td style="text-align:left;font-weight:600">' + d.sku + '</td><td><span style="background:' + batchColor + ';color:white;padding:2px 8px;border-radius:10px;font-size:10px">' + d.batch + '</span></td><td>' + d.analyst + '</td><td>' + d.cat + '</td><td>' + d.expand + '</td><td>' + d.qty + '</td><td>' + d.comp + '</td><td>' + sharePct + '</td><td style="color:' + orderColor + ';font-weight:600">' + d.order + '</td><td style="color:' + statusColor + '">' + d.status + '</td></tr>';
  }
  document.getElementById('detail-tbody').innerHTML = html;
}

// ========== 导航切换 ==========
var sections = ['overview','pinxian','analyst','expand','order','unorder','lowshare','detail'];
var initializedCharts = {};

function showSection(name, el) {
  for (var i = 0; i < sections.length; i++) {
    var s = sections[i];
    var wrap = document.getElementById('section-' + s);
    if (wrap) wrap.style.display = s === name ? 'block' : 'none';
  }
  var links = document.querySelectorAll('.sidebar a');
  for (var j = 0; j < links.length; j++) links[j].classList.remove('active');
  if (el) el.classList.add('active');
  
  // 触发该section的图表重绘
  if (initializedCharts[name]) {
    Object.values(initializedCharts[name]).forEach(function(chart) { chart.resize(); });
  }
  return false;
}

// ========== 初始化 ==========
document.addEventListener('DOMContentLoaded', function() {
  renderCatTable();
  renderAnalystTable();
  renderExpandTable();
  renderOrderTable();
  renderMarketTable();
  renderLowShare();
  renderDetailTable();
  
  var catLabels = Object.keys(CATEGORY_DATA);
  
  // 数据总览图表 - 默认可见
  initializedCharts['overview'] = {};
  mkBar('chartBatchQty', ['1月新品', '2月新品', '3月新品'], [{ label: '销量', data: [BATCH_DATA['1月'].qty, BATCH_DATA['2月'].qty, BATCH_DATA['3月'].qty], backgroundColor: ['#adb5bd', '#667eea', '#e74c3c'] }]);
  mkBar('chartCategoryQty', catLabels, [
    { label: '1月销量', data: catLabels.map(function(k){return CATEGORY_DATA[k].qty_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月销量', data: catLabels.map(function(k){return CATEGORY_DATA[k].qty_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月销量', data: catLabels.map(function(k){return CATEGORY_DATA[k].qty_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  mkBar('chartCategoryRate', catLabels, [
    { label: '1月出单率', data: catLabels.map(function(k){return CATEGORY_DATA[k].rate_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月出单率', data: catLabels.map(function(k){return CATEGORY_DATA[k].rate_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月出单率', data: catLabels.map(function(k){return CATEGORY_DATA[k].rate_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  mkBar('chartExpand', Object.keys(EXPAND_DATA), [
    { label: '1月销量', data: Object.values(EXPAND_DATA).map(function(v){return v.qty_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月销量', data: Object.values(EXPAND_DATA).map(function(v){return v.qty_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月销量', data: Object.values(EXPAND_DATA).map(function(v){return v.qty_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  mkBar('chartAnalyst', Object.keys(ANALYST_DATA), [
    { label: '1月销量', data: Object.values(ANALYST_DATA).map(function(v){return v.qty_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月销量', data: Object.values(ANALYST_DATA).map(function(v){return v.qty_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月销量', data: Object.values(ANALYST_DATA).map(function(v){return v.qty_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  
  // 品线维度图表
  initializedCharts['pinxian'] = {};
  initializedCharts['pinxian']['chartCatQty'] = mkBar('chartCatQty', catLabels, [
    { label: '1月销量', data: catLabels.map(function(k){return CATEGORY_DATA[k].qty_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月销量', data: catLabels.map(function(k){return CATEGORY_DATA[k].qty_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月销量', data: catLabels.map(function(k){return CATEGORY_DATA[k].qty_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  initializedCharts['pinxian']['chartCatRate'] = mkBar('chartCatRate', catLabels, [
    { label: '1月出单率', data: catLabels.map(function(k){return CATEGORY_DATA[k].rate_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月出单率', data: catLabels.map(function(k){return CATEGORY_DATA[k].rate_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月出单率', data: catLabels.map(function(k){return CATEGORY_DATA[k].rate_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  
  // 分析人维度图表
  initializedCharts['analyst'] = {};
  initializedCharts['analyst']['chartAnalystQty'] = mkBar('chartAnalystQty', Object.keys(ANALYST_DATA), [
    { label: '1月销量', data: Object.values(ANALYST_DATA).map(function(v){return v.qty_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月销量', data: Object.values(ANALYST_DATA).map(function(v){return v.qty_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月销量', data: Object.values(ANALYST_DATA).map(function(v){return v.qty_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  initializedCharts['analyst']['chartAnalystRate'] = mkBar('chartAnalystRate', Object.keys(ANALYST_DATA), [
    { label: '1月出单率', data: Object.values(ANALYST_DATA).map(function(v){return v.rate_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月出单率', data: Object.values(ANALYST_DATA).map(function(v){return v.rate_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月出单率', data: Object.values(ANALYST_DATA).map(function(v){return v.rate_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  
  // 拓展类型图表
  initializedCharts['expand'] = {};
  initializedCharts['expand']['chartExpandQty'] = mkBar('chartExpandQty', Object.keys(EXPAND_DATA), [
    { label: '1月销量', data: Object.values(EXPAND_DATA).map(function(v){return v.qty_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月销量', data: Object.values(EXPAND_DATA).map(function(v){return v.qty_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月销量', data: Object.values(EXPAND_DATA).map(function(v){return v.qty_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  initializedCharts['expand']['chartExpandRate'] = mkBar('chartExpandRate', Object.keys(EXPAND_DATA), [
    { label: '1月出单率', data: Object.values(EXPAND_DATA).map(function(v){return v.rate_1 || 0}), backgroundColor: '#adb5bd' },
    { label: '2月出单率', data: Object.values(EXPAND_DATA).map(function(v){return v.rate_2 || 0}), backgroundColor: '#667eea' },
    { label: '3月出单率', data: Object.values(EXPAND_DATA).map(function(v){return v.rate_3 || 0}), backgroundColor: '#e74c3c' }
  ]);
  
  // 出单情况图表
  initializedCharts['order'] = {};
  initializedCharts['order']['chartOrderBatch'] = mkBar('chartOrderBatch', ['1月新品', '2月新品', '3月新品'], [
    { label: '8日Y出单', data: [BATCH_DATA['1月'].ordered, BATCH_DATA['2月'].ordered, BATCH_DATA['3月'].ordered], backgroundColor: '#08845a' },
    { label: '8日N出单', data: [BATCH_DATA['1月'].unorder, BATCH_DATA['2月'].unorder, BATCH_DATA['3月'].unorder], backgroundColor: '#e07b24' },
    { label: '未出单', data: [BATCH_DATA['1月'].not_order, BATCH_DATA['2月'].not_order, BATCH_DATA['3月'].not_order], backgroundColor: '#c0392b' }
  ]);
  initializedCharts['order']['chartOrderRate'] = mkLine('chartOrderRate', ['1月新品', '2月新品', '3月新品'], [{label: '出单率(%)', data: [BATCH_DATA['1月'].rate, BATCH_DATA['2月'].rate, BATCH_DATA['3月'].rate], borderColor: '#0f3460', backgroundColor: 'rgba(15,52,96,0.1)', fill: true, tension: 0.3}]);
  
  // 未出单市场图表
  initializedCharts['unorder'] = {};
  initializedCharts['unorder']['chartMarketPie'] = mkPie('chartMarketPie', Object.keys(MARKET_DATA), Object.values(MARKET_DATA));
  initializedCharts['unorder']['chartMarketCompare'] = mkBar('chartMarketCompare', ['正常', '异常'], [{ label: '数量', data: [MARKET_DATA['正常'] || 0, Object.values(MARKET_DATA).reduce(function(a,b){return a+b;}, 0) - (MARKET_DATA['正常'] || 0)], backgroundColor: ['#08845a', '#c0392b'] }]);
  
  // 隐藏非首屏section
  for (var i = 1; i < sections.length; i++) {
    var wrap = document.getElementById('section-' + sections[i]);
    if (wrap) wrap.style.display = 'none';
  }
});
