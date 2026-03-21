from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Investment Analysis Report', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

# PDFの作成
pdf = PDF()
pdf.add_page()

# 日付の追加
today = datetime.date.today().strftime("%Y-%m-%d")
pdf.set_font('Arial', '', 10)
pdf.cell(0, 10, f'Date: {today}', 0, 1, 'R')

# セクション1: ダッシュボード
pdf.chapter_title('1. Portfolio Dashboard Overview')
pdf.chapter_body('This dashboard summarizes dividend, yield, real-time prices, and monthly performance. It highlights the balance between communication sectors and growth stocks.')
# 前に作ったダッシュボード画像を挿入 (ファイル名は適宜合わせてください)
pdf.image('stock_dashboard.png', x=10, w=190) 
pdf.ln(10)

# セクション2: 為替相関分析
pdf.add_page()
pdf.chapter_title('2. Market Correlation: Toyota vs USD/JPY')
pdf.chapter_body('Analysis of the relationship between Toyota stock and the USD/JPY exchange rate. Recent trends show a decoupling, where stock prices fell despite yen depreciation.')
# 為替相関画像を挿入
pdf.image('market_correlation.png', x=10, w=190)

# セクション3: 分析考察
pdf.ln(5)
pdf.chapter_title('3. Strategic Insights')
analysis_text = (
    "- SoftBank maintains the highest yield (4.5%), serving as a core income gain asset.\n"
    "- Toyota (7203.T) shows a temporary correction, potentially due to the 5.9 trillion yen TOB financing concerns.\n"
    "- The portfolio remains stable due to the strong performance of NTT and Tokio Marine."
)
pdf.chapter_body(analysis_text)

# 保存
pdf.output('Investment_Report_Ryoma.pdf')
print("SUCCESS: Investment_Report_Ryoma.pdf created!")