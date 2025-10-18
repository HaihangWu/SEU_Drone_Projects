import os
import json
import requests
from tqdm import tqdm
from pathlib import Path

# === Configuration ===
base_dir = Path(r"C:\Users\hthh1\Downloads\ADT")
cdn_file = base_dir / "ADT_download_urls.json"  # JSON file with all sequences

# === Sequences you need ===
DATASET_DICT = {
    "room0": {
        "agent_0": "Apartment_release_decoration_seq136_M1292",
        "agent_1": "Apartment_release_decoration_seq137_M1292",
        "agent_2": "Apartment_release_decoration_seq139_M1292"
    },
    "room1": {
        "agent_0": "Apartment_release_decoration_seq134_M1292",
        "agent_1": "Apartment_release_decoration_skeleton_seq133_M1292",
        "agent_2": "Apartment_release_decoration_skeleton_seq135_M1292"
    }
}

TEST_DATASET_DICT = {
    "room0": "Apartment_release_decoration_seq133_M1292",
    "room1": "Apartment_release_decoration_seq139_M1292"
}

# === Resume-capable downloader ===
def download_with_resume(url, dest_path):
    dest_path = Path(dest_path)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".part")
    max_retries=3

    # Skip if already fully downloaded
    if dest_path.exists() and not temp_path.exists():
        print(f"✔ Already downloaded: {dest_path.name}")
        return

    headers = {}
    if temp_path.exists():
        downloaded = temp_path.stat().st_size
        headers["Range"] = f"bytes={downloaded}-"
    else:
        downloaded = 0

    for attempt in range(max_retries):

        try:
            with requests.get(url, stream=True, headers=headers, timeout=(10, 1800)) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0)) + downloaded
                mode = "ab" if downloaded > 0 else "wb"
                with open(temp_path, mode) as f, tqdm(
                    total=total,
                    initial=downloaded,
                    unit="B",
                    unit_scale=True,
                    desc=dest_path.name,
                    ncols=80,
                ) as bar:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))

            # Safely rename
            if dest_path.exists():
                dest_path.unlink()  # delete old file if exists
            temp_path.rename(dest_path)
            print(f"✅ Finished: {dest_path.name}")
            return

        except Exception as e:
            print(f"⚠️ Attempt {attempt+1}/{max_retries} failed for {dest_path.name}: {e}")
            import time; time.sleep(5)

    print(f"❌ Failed after {max_retries} attempts: {dest_path.name}")


# === Main logic ===
def main():
    if not cdn_file.exists():
        print(f"❌ CDN file not found: {cdn_file}")
        return

    # Collect only the sequences you need
    required_scenes = set()
    for room in DATASET_DICT.values():
        required_scenes.update(room.values())
    required_scenes.update(TEST_DATASET_DICT.values())

    urls_to_download = []
    with open(cdn_file, "r") as f:
        data = json.load(f)
        sequences = data.get("sequences", {})

        for scene_name, files_dict in sequences.items():
            if scene_name in required_scenes:
                for file_info in files_dict.values():
                    if "download_url" in file_info and "filename" in file_info:
                        urls_to_download.append((file_info["download_url"], file_info["filename"]))

    print(f"Found {len(urls_to_download)} files to download for selected sequences.")

    # Download all files
    for url, filename in urls_to_download:
        dest_path = base_dir / filename
        download_with_resume(url, dest_path)

if __name__ == "__main__":
    main()


# import os
# import requests
# from tqdm import tqdm
#
#
# def download_with_resume(url, filename):
#     # 已下载的大小
#     resume_header = {}
#     if os.path.exists(filename):
#         downloaded_size = os.path.getsize(filename)
#         resume_header = {"Range": f"bytes={downloaded_size}-"}
#     else:
#         downloaded_size = 0
#
#     # 发送请求
#     response = requests.get(url, headers=resume_header, stream=True)
#
#     # 总大小（可能从某个偏移量开始）
#     total_size = int(response.headers.get("content-length", 0)) + downloaded_size
#
#     # 打开文件（追加写入模式）
#     with open(filename, "ab") as f, tqdm(
#             total=total_size, initial=downloaded_size,
#             unit="B", unit_scale=True, desc=filename
#     ) as pbar:
#         for chunk in response.iter_content(chunk_size=1024):
#             if chunk:
#                 f.write(chunk)
#                 pbar.update(len(chunk))
#
#     print("✅ Download complete!")
#
#
# # 示例用法
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/b34888ed0f754554f4a9c25d0a15e493ac8186580078cdf19ed0e463323dce9b?Expires=1761713983&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=cSE82WGLq%2FOxC1gQIruUed4bgLQ%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-00%22&response-content-type=application%2Foctet-stream", r"E:\scannet\scans.tar.part-00.zip")
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/de9f0733a91a1ea74e7d69d5e72104f7001ec531b8d6bede17583bab945892b1?Expires=1761719233&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=2JYs21YWSCIYqvayHHu1ozlgquM%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-01%22&response-content-type=application%2Foctet-stream",r"E:\scannet\scans.tar.part-01.zip")
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/9de97605678b9faa3a02ad534cc5d8986102b6264ab4a5f825f83528141e3f35?Expires=1761719175&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=q667%2BB3BWlnsHJNRCcmhr59UGiA%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-02%22&response-content-type=application%2Foctet-stream",r"E:\scannet\scans.tar.part-02.zip")
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/1574c9d9767582eba661ae4307c98fd9b1a31404f301d353d0d4dc96ca3fa6c6?Expires=1761719260&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=ieZwVCruLB5kaOe7lS7xp4Qz2Vw%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-03%22&response-content-type=application%2Foctet-stream",r"E:\scannet\scans.tar.part-03.zip")
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/d9d07d0e33102e370c89dd15d59998114b5a4d68d763660df0daa7adcb6681f7?Expires=1761719269&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=f9Dn4%2F5pMDyH2g5rNnZ6zRtTbSo%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-04%22&response-content-type=application%2Foctet-stream",r"E:\scannet\scans.tar.part-04.zip")
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/ca95d565201cce3dc85b30f8fef385e16be3a8120cd0848605ebff3f75a308a7?Expires=1761719278&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=m2UnT8xeGN9k6b6TTSroTyCViwE%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-05%22&response-content-type=application%2Foctet-stream",r"E:\scannet\scans.tar.part-05.zip")
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/602e6a3dcef743c29328fd54aff995c3b6495180b7e7e59679e86d88b15f9418?Expires=1761719279&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=jqtzRSqBn6dV1TkK1J%2FGdUMnvQ4%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-06%22&response-content-type=application%2Foctet-stream",r"E:\scannet\scans.tar.part-06.zip")
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/e14284bd41adfc98eb185d47c594919f0cbd38c1a75cc7a53f6706975f995c32?Expires=1761719279&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=vawPi5VUCB%2FJy7%2BafwTTPBkdmXY%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-07%22&response-content-type=application%2Foctet-stream",r"E:\scannet\scans.tar.part-07.zip")
#
# download_with_resume("https://cdn-xlab-data.openxlab.org.cn/objects/910e53ba95cda02a466d8a77099a3e1346596f241cb6b00e20c65c09e274ea2c?Expires=1761719279&OSSAccessKeyId=LTAI5tSqABbitQcgeNNd8dAE&Signature=Fkcr2LIQS2AvPYpefDYy3Ylnkmk%3D&response-content-disposition=attachment%3B%20filename%3D%22scans.tar.part-08%22&response-content-type=application%2Foctet-stream",r"E:\scannet\scans.tar.part-08.zip")