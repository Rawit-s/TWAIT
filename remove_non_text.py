import subprocess
import os
import sys
from tkinter import Tk, filedialog

# rpfm_cli.exe의 경로 설정
if getattr(sys, 'frozen', False):  # PyInstaller로 빌드된 경우
    base_path = sys._MEIPASS
else:  # Python 스크립트 실행 시
    base_path = os.path.dirname(os.path.abspath(__file__))

rpfm_cli_path = os.path.join(base_path, "rpfm_cli.exe")

# 실행 파일이 존재하는지 확인
if not os.path.exists(rpfm_cli_path):
    print(f"❌ Error: rpfm_cli.exe not found at {rpfm_cli_path}")
    sys.exit(1)

def select_pack_folder():
    """사용자가 Pack 파일이 있는 폴더를 선택하도록 함"""
    root = Tk()
    root.withdraw()  # 창 숨기기
    return filedialog.askdirectory(title="Select Folder Containing Pack Files")

def chunk_list(lst, chunk_size):
    """리스트를 chunk_size만큼 나누는 함수"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]

def remove_non_text_folders(pack_file_path, game_name, pack_index, total_packs):
    """Pack 파일에서 'text/' 폴더를 제외한 모든 항목 제거"""

    # Pack 파일 내부의 모든 항목 목록 가져오기
    list_command = [
        rpfm_cli_path,
        "--game", game_name,
        "pack", "list",
        "--pack-path", pack_file_path
    ]
    result = subprocess.run(list_command, capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        print(f"❌ Error in {os.path.basename(pack_file_path)}: {result.stderr}")
        return

    items = result.stdout.splitlines()
    
    # 'text/' 폴더 제외한 파일 및 폴더 목록 만들기
    files_to_remove = [item for item in items if not item.startswith("text/") and not item.endswith("/")]
    folders_to_remove = [item for item in items if not item.startswith("text/") and item.endswith("/")]

    total_items = len(files_to_remove) + len(folders_to_remove)
    if total_items == 0:
        print(f"✅ No items to remove in {os.path.basename(pack_file_path)}\n")
        return

    print(f"📁 Processing [{pack_index+1}/{total_packs}]: {os.path.basename(pack_file_path)}")
    print(f"   - 🔍 Found {total_items} items to remove")

    deleted_items = 0
    chunk_size = 200  # 배치 처리 크기

    # 파일 삭제 (배치 처리)
    for file_chunk in chunk_list(files_to_remove, chunk_size):
        remove_command = [
            rpfm_cli_path,
            "--game", game_name,
            "pack", "delete",
            "--pack-path", pack_file_path,
        ] + ["--file-path"] + file_chunk
        subprocess.run(remove_command, capture_output=True, text=True, shell=True)
        
        deleted_items += len(file_chunk)
        print(f"   - 🚀 Progress: {deleted_items}/{total_items} ({(deleted_items / total_items) * 100:.1f}%)")

    # 폴더 삭제 (배치 처리)
    for folder_chunk in chunk_list(folders_to_remove, chunk_size):
        remove_command = [
            rpfm_cli_path,
            "--game", game_name,
            "pack", "delete",
            "--pack-path", pack_file_path,
        ] + ["--folder-path"] + folder_chunk
        subprocess.run(remove_command, capture_output=True, text=True, shell=True)
        
        deleted_items += len(folder_chunk)
        print(f"   - 🚀 Progress: {deleted_items}/{total_items} ({(deleted_items / total_items) * 100:.1f}%)")

    print(f"✅ Finished processing [{pack_index+1}/{total_packs}]: {os.path.basename(pack_file_path)}\n")

def main():
    """메인 실행 함수"""
    pack_folder_path = select_pack_folder()
    if not pack_folder_path:
        print("No folder selected. Exiting...")
        return

    game_name = "warhammer_3"
    pack_files = [f for f in os.listdir(pack_folder_path) if f.endswith(".pack")]
    total_packs = len(pack_files)

    if total_packs == 0:
        print("❌ No .pack files found in the selected folder.")
        return

    print(f"🔹 Total {total_packs} pack files found.")

    for index, file_name in enumerate(pack_files):
        pack_file_path = os.path.join(pack_folder_path, file_name)
        remove_non_text_folders(pack_file_path, game_name, index, total_packs)

    print("🎉 All pack files processed successfully!")

if __name__ == "__main__":
    main()
