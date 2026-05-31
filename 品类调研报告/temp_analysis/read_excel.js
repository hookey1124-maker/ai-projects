const XLSX = require('xlsx');
const path = require('path');

const filePath = path.join(__dirname, '../玻璃品类调研2025.9.xlsx');
console.log('Reading file:', filePath);

try {
    const workbook = XLSX.readFile(filePath);
    console.log('Sheet names:', workbook.SheetNames);
    
    // 读取每个工作表的前几行
    workbook.SheetNames.forEach((sheetName, index) => {
        console.log(`\n=== Sheet ${index + 1}: ${sheetName} ===`);
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });
        
        // 显示前5行，最多10列
        const rowsToShow = Math.min(data.length, 5);
        for (let i = 0; i < rowsToShow; i++) {
            const row = data[i].slice(0, 10).map(cell => 
                cell === null ? '' : String(cell).substring(0, 50)
            );
            console.log(`Row ${i + 1}:`, row);
        }
        console.log(`Total rows: ${data.length}, cols: ${data[0] ? data[0].length : 0}`);
    });
} catch (error) {
    console.error('Error reading file:', error.message);
}
