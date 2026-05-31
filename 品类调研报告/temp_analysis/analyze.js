const XLSX = require('xlsx');
const path = require('path');
const fs = require('fs');

const filePath = path.join(__dirname, '../玻璃品类调研2025.9.xlsx');
console.log('Analyzing Excel file...');

try {
    const workbook = XLSX.readFile(filePath);
    const analysis = {
        sheets: [],
        summary: {
            totalSheets: workbook.SheetNames.length,
            sheetNames: workbook.SheetNames
        }
    };
    
    // 分析每个工作表
    workbook.SheetNames.forEach((sheetName, index) => {
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });
        
        // 计算基本统计信息
        const rowCount = data.length;
        const colCount = rowCount > 0 ? data[0].length : 0;
        
        // 提取非空单元格数量
        let nonEmptyCells = 0;
        let textCells = 0;
        let numericCells = 0;
        let formulaCells = 0;
        let imageRefs = 0;
        
        // 提取前几行内容作为预览
        const previewRows = Math.min(data.length, 5);
        const preview = [];
        for (let i = 0; i < previewRows; i++) {
            preview.push(data[i].slice(0, 10).map(cell => 
                cell === null ? '' : String(cell).substring(0, 100)
            ));
        }
        
        // 分析内容类型
        let contentSummary = '';
        if (sheetName === '信息') {
            contentSummary = '产品分类、材质介绍、汽车玻璃基础知识';
        } else if (sheetName === '市场') {
            contentSummary = '市场趋势、关键词分析、竞争情况';
        } else if (sheetName === '自身') {
            contentSummary = '自身产品线、价格分析、市场占比';
        } else if (sheetName === '销售数据') {
            contentSummary = '详细销售数据记录';
        } else if (sheetName === '产品情况') {
            contentSummary = '产品规格、库存情况';
        } else if (sheetName.includes('均价')) {
            contentSummary = '价格分析、维度对比';
        } else if (sheetName.includes('销售表')) {
            contentSummary = '销售报表、业绩统计';
        } else {
            contentSummary = '数据表格';
        }
        
        // 检查是否有图片引用
        let hasImages = false;
        for (let i = 0; i < Math.min(data.length, 10); i++) {
            for (let j = 0; j < Math.min(data[i].length, 10); j++) {
                const cell = String(data[i][j] || '');
                if (cell.includes('DISPIMG')) {
                    hasImages = true;
                    imageRefs++;
                }
                if (cell.includes('=') && cell.includes('(')) {
                    formulaCells++;
                }
            }
        }
        
        analysis.sheets.push({
            name: sheetName,
            index: index + 1,
            rowCount,
            colCount,
            contentSummary,
            hasImages,
            imageRefs,
            preview,
            keyMetrics: {
                nonEmptyCells,
                textCells,
                numericCells,
                formulaCells
            }
        });
    });
    
    // 保存分析结果
    const outputPath = path.join(__dirname, 'analysis.json');
    fs.writeFileSync(outputPath, JSON.stringify(analysis, null, 2), 'utf8');
    console.log(`Analysis saved to ${outputPath}`);
    
    // 打印摘要
    console.log('\n=== Excel文件分析摘要 ===');
    console.log(`文件: ${path.basename(filePath)}`);
    console.log(`工作表数量: ${analysis.summary.totalSheets}`);
    console.log('\n工作表列表:');
    analysis.sheets.forEach(sheet => {
        console.log(`  ${sheet.index}. ${sheet.name} (${sheet.rowCount}行×${sheet.colCount}列) - ${sheet.contentSummary}`);
    });
    
} catch (error) {
    console.error('分析错误:', error.message);
    process.exit(1);
}
