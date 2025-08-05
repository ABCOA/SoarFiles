import os
import hashlib
import json
import argparse

CLIENT_FILES_BASE_DIR = os.getcwd() 
OUTPUT_MANIFEST_PATH = os.path.join(CLIENT_FILES_BASE_DIR, 'client_manifest.json') 

def calculate_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def generate_manifest(base_dir, output_file, client_version):
    manifest_data = {
        "clientVersion": client_version,
        "files": []
    }
    
    print(f"--- 开始扫描目录: {base_dir} ---")
    
    for root, _, files in os.walk(base_dir):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            
            if full_path == output_file:
                continue
            
            relative_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
            
            try:
                file_size = os.path.getsize(full_path)
                file_sha256 = calculate_sha256(full_path)
                
                manifest_data["files"].append({
                    "path": relative_path,
                    "size": file_size,
                    "sha256": file_sha256
                })
                print(f"  添加文件: {relative_path} (SHA256: {file_sha256[:10]}...)")
            except Exception as e:
                print(f"  错误处理文件 {relative_path}: {e}")
    
    try:
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
