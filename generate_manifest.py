import os
import hashlib
import json
import argparse

# --- 配置部分 ---
# 客户端文件存放的根目录。在 GitHub Actions 中，就是仓库被克隆到的当前目录。
CLIENT_FILES_BASE_DIR = os.getcwd()
# 清单文件将要生成并保存的完整路径。
OUTPUT_MANIFEST_PATH = os.path.join(CLIENT_FILES_BASE_DIR, 'client_manifest.json')
# --- 配置部分结束 ---

EXCLUDE_PATHS = [
    os.path.normpath('.github/'),
    os.path.normpath('.git/'),
    os.path.normpath('generate_manifest.py'),
    os.path.normpath('client_manifest.json'),
    os.path.normpath('.gitignore'),
    os.path.normpath('README.md'),
    os.path.normpath('LICENSE'),
    os.path.normpath('java/'),
    os.path.normpath('assets/')
]

def calculate_sha256(filepath):
    """计算文件的 SHA-256 哈希值"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def generate_manifest(base_dir, output_file, client_version):
    """
    扫描指定目录，生成 client_manifest.json 文件。
    """
    manifest_data = {
        "clientVersion": client_version,
        "files": []
    }
    
    print(f"--- 开始扫描目录: {base_dir} ---")
    
    for root, _, files in os.walk(base_dir):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            
            relative_path = os.path.relpath(full_path, base_dir)
            
            should_exclude = False
            for exclude_path in EXCLUDE_PATHS:
                if os.path.isdir(os.path.join(base_dir, exclude_path)) and relative_path.startswith(exclude_path):
                    should_exclude = True
                    break
                elif relative_path == exclude_path:
                    should_exclude = True
                    break
            
            if should_exclude:
                print(f"  忽略文件: {relative_path}")
                continue
            
            try:
                file_size = os.path.getsize(full_path)
                file_sha256 = calculate_sha256(full_path)
                
                manifest_data["files"].append({
                    "path": relative_path.replace("\\", "/"),
                    "size": file_size,
                    "sha256": file_sha256
                })
                print(f"  添加文件: {relative_path} (SHA256: {file_sha256[:10]}...)")
            except Exception as e:
                print(f"  错误处理文件 {relative_path}: {e}")
    
    try:
        # *** 修正：确保父目录存在，处理文件名本身作为路径的情况 ***
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # *******************************************************
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        print(f"--- 成功生成清单文件: {output_file} (版本: {client_version}) ---")
    except Exception as e:
        print(f"--- 写入清单文件失败: {e} ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动生成 Minecraft 启动器客户端文件清单。")
    parser.add_argument('-v', '--version', type=str,
                        default="auto_generated",
                        help="客户端版本号。")
    parser.add_argument('--base-dir', type=str,
                        default=os.getcwd(),
                        help="客户端文件存放的根目录。")
    parser.add_argument('--output-path', type=str,
                        default="client_manifest.json",
                        help="生成的清单文件完整路径。")
    
    args = parser.parse_args()

    generate_manifest(args.base_dir, args.output_path, args.version)
