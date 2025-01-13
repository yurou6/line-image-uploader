# LINE Image Uploader

這是一個簡單的工具，用於將圖片上傳到 GitHub 並獲取可用於 LINE Bot 的圖片 URL。

## 功能
- 自動上傳圖片到 GitHub 倉庫
- 生成可用於 LINE Bot 的圖片 URL
- 支援多種圖片格式（JPG, PNG, GIF, etc.）
- 自動記錄上傳歷史

## 安裝
1. 克隆倉庫
```bash
git clone https://github.com/your-username/line-image-uploader.git
cd line-image-uploader
```

2. 建立虛擬環境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
.\venv\Scripts\activate  # Windows
```

3. 安裝依賴
```bash
pip install -r requirements.txt
```

## 配置
1. 在 GitHub 上生成個人訪問令牌（Personal Access Token）
2. 首次運行程式時會要求輸入：
   - GitHub Token
   - GitHub 倉庫名稱

## 使用方法
```bash
python github_uploader.py path/to/your/image.jpg
```

## 支援的圖片格式
- JPG/JPEG
- PNG
- GIF
- SVG
- WebP
- BMP
- ICO

## 注意事項
- 圖片大小限制為 10MB
- 需要有效的 GitHub Token
- GitHub 倉庫必須是公開的，這樣 LINE Bot 才能訪問圖片

## License
MIT
