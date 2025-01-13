import os
import sys
import base64
import json
import mimetypes
from pathlib import Path
from github import Github, InputFileContent
from datetime import datetime

class ImageValidator:
    SUPPORTED_FORMATS = {
        '.jpg', '.jpeg', '.png', '.gif', '.svg', 
        '.webp', '.bmp', '.ico'
    }
    
    @classmethod
    def is_valid_image(cls, file_path: Path) -> bool:
        """驗證文件是否為支援的圖片格式"""
        # 檢查副檔名
        if file_path.suffix.lower() not in cls.SUPPORTED_FORMATS:
            return False
            
        # 檢查文件是否存在且大小大於0
        if not file_path.exists() or file_path.stat().st_size == 0:
            return False
            
        return True

class Config:
    def __init__(self):
        self.config_path = Path.home() / '.image_uploader' / 'config.json'
        self.load_config()

    def load_config(self):
        if not self.config_path.exists():
            self.create_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.settings = json.load(f)

    def create_default_config(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "github_token": "",
            "repository": "",
            "watch_folder": str(Path.home() / "Pictures" / "upload"),
            "output_folder": str(Path.home() / "Pictures" / "processed"),
            "max_file_size_mb": 10
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        
        self.settings = default_config

class GitHubImageUploader:
    def __init__(self, config: Config):
        self.config = config
        self.github = Github(config.settings['github_token'])
        self.repo = self.github.get_repo(config.settings['repository'])
        
        # 確保必要的資料夾存在
        Path(config.settings['watch_folder']).mkdir(parents=True, exist_ok=True)
        Path(config.settings['output_folder']).mkdir(parents=True, exist_ok=True)

    def upload_image(self, image_path: Path) -> str:
        """上傳圖片並返回URL"""
        try:
            # 驗證圖片
            if not ImageValidator.is_valid_image(image_path):
                raise ValueError(f"不支援的圖片格式或無效的文件: {image_path}")
            
            # 檢查文件大小
            file_size_mb = image_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.settings['max_file_size_mb']:
                raise ValueError(f"文件大小超過限制 ({file_size_mb:.1f}MB > {self.config.settings['max_file_size_mb']}MB)")
            
            # 讀取圖片文件
            with open(image_path, "rb") as image_file:
                content = image_file.read()
            
            # 生成目標路徑 (保持原始檔名，但加上時間戳)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"images/{timestamp}_{image_path.name}"
            file_name = file_name.replace('\\', '/')

            # 上傳到 GitHub
            result = self.repo.create_file(
                path=file_name,
                message=f"Upload image {file_name}",
                content=content,
                branch="main"
            )
            
            # 獲取原始URL
            raw_url = f"https://raw.githubusercontent.com/{self.repo.full_name}/main/{file_name}"
            
            # 記錄上傳信息
            self._save_upload_info(image_path.name, raw_url, file_size_mb)
            
            return raw_url

        except Exception as e:
            print(f"上傳錯誤: {str(e)}")
            return None

    def _save_upload_info(self, filename: str, url: str, size_mb: float):
        """保存上傳記錄"""
        log_file = Path(self.config.settings['output_folder']) / 'upload_log.txt'
        with open(log_file, 'a', encoding='utf-8') as f:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'filename': filename,
                'url': url,
                'size_mb': round(size_mb, 2),
                'mime_type': mimetypes.guess_type(filename)[0]
            }
            f.write(json.dumps(log_entry) + '\n')

def setup_config():
    """初始設定助手"""
    config = Config()
    
    if not config.settings['github_token']:
        print("請輸入 GitHub Token:")
        config.settings['github_token'] = input().strip()
    
    if not config.settings['repository']:
        print("請輸入 GitHub 倉庫 (格式: username/repository):")
        config.settings['repository'] = input().strip()
    
    print(f"支援的圖片格式: {', '.join(ImageValidator.SUPPORTED_FORMATS)}")
    
    with open(config.config_path, 'w', encoding='utf-8') as f:
        json.dump(config.settings, f, indent=4)
    
    return config

def main():
    # 檢查是否需要初始設定
    config = Config()
    if not config.settings['github_token'] or not config.settings['repository']:
        config = setup_config()
    
    uploader = GitHubImageUploader(config)
    
    # 命令列參數處理
    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
        url = uploader.upload_image(image_path)
        path = url.split('/main/')[1]
        print(url)
        if url:
            print(f"上傳成功: {url}")
            print(f"GitHub 倉庫位置: https://github.com/{config.settings['repository']}/blob/main/{path}")
        else:
            print("上傳失敗")
    else:
        print(f"\n支援的圖片格式: {', '.join(ImageValidator.SUPPORTED_FORMATS)}")
        print(f"最大文件大小: {config.settings['max_file_size_mb']}MB")
        print(f"\n使用方式: python {sys.argv[0]} <圖片路徑>")
        print(f"監控資料夾: {config.settings['watch_folder']}")
        print(f"輸出資料夾: {config.settings['output_folder']}")

if __name__ == "__main__":
    main()