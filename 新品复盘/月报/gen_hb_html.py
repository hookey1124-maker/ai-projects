import json

with open('report_data.json', 'r', encoding='utf-8') as f:
    D = json.load(f)

# 输出统计信息
print(f'低占比新品总数: {len(D["low_share"])}')
batch_counts = {}
for item in D['low_share']:
    b = item['batch']
    batch_counts[b] = batch_counts.get(b, 0) + 1
print(f'各批次数量: {batch_counts}')

# 保存数据到临时JSON供HTML使用
with open('temp_data.json', 'w', encoding='utf-8') as f:
    json.dump({
        'low_share': D['low_share'],
        'category': D['category'],
        'analyst': D['analyst'],
        'expand': D['expand'],
        'batch': D['batch'],
        'market_dist': {"正常": 66, "竞争无优跌": 54, "无市场": 23, "站外出单": 11, "站内无价格优跌": 2}
    }, f, ensure_ascii=False, indent=2)

print('数据准备完成！')
