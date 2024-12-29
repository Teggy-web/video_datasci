import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import cv2
from PIL import Image, ImageTk

def run_detection_script(video_path):
    """运行检测脚本"""
    output_dir = "./output"
    command = f"python deploy/pipeline/pipeline.py --config deploy/pipeline/config/examples/infer_cfg_fall_down.yml --video_file={video_path} --device=cpu --output_dir {output_dir}"
    try:
        subprocess.run(command, shell=True, check=True)
        result_video_name = os.path.basename(video_path)  # 假设结果文件名与输入文件相同
        result_video_path = os.path.join(output_dir, result_video_name)
        return result_video_path
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"检测脚本运行失败：{e}")
        return None

def select_video():
    """选择视频文件"""
    video_path = filedialog.askopenfilename(title="选择视频文件", filetypes=[("MP4 文件", "*.mp4"), ("所有文件", "*.*")])
    if video_path:
        video_label.config(text=f"已选择视频：{os.path.basename(video_path)}")
        run_button.config(state=tk.NORMAL)
        return video_path

def display_video(video_path):
    """展示视频并实现循环播放"""
    cap = cv2.VideoCapture(video_path)
    video_width = video_panel.winfo_width()
    video_height = video_panel.winfo_height()

    def update_frame():
        nonlocal cap
        ret, frame = cap.read()
        if ret:
            # 缩放帧以适配窗口大小
            frame = cv2.resize(frame, (video_width, video_height), interpolation=cv2.INTER_AREA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            video_panel.imgtk = imgtk
            video_panel.config(image=imgtk)
            video_panel.after(10, update_frame)
        else:
            # 重新播放视频
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            update_frame()

    update_frame()

def start_detection():
    """开始检测并展示结果"""
    input_video = video_label.cget("text").replace("已选择视频：", "")
    if not input_video:
        messagebox.showerror("错误", "请先选择视频文件！")
        return

    # 运行检测脚本
    result_video_path = run_detection_script(input_video)
    if result_video_path and os.path.exists(result_video_path):
        messagebox.showinfo("检测完成", "检测完成，正在展示结果...")
        display_video(result_video_path)
    else:
        messagebox.showerror("错误", "结果视频未生成！")

# 创建主窗口
root = tk.Tk()
root.title("摔倒检测系统")
root.geometry("800x600")

# 创建界面元素
title_label = tk.Label(root, text="摔倒检测系统", font=("Arial", 20))
title_label.pack(pady=20)

video_label = tk.Label(root, text="未选择视频", font=("Arial", 14))
video_label.pack(pady=10)

select_button = tk.Button(root, text="选择视频", command=lambda: select_video())
select_button.pack(pady=5)

run_button = tk.Button(root, text="开始检测", state=tk.DISABLED, command=start_detection)
run_button.pack(pady=10)

# 创建一个可用的显示区域
video_panel = tk.Label(root, width=720, height=480)
video_panel.pack(pady=20)

# 启动主循环
root.mainloop()