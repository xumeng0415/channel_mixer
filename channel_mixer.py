from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class ChannelMixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RGB通道混合器")
        self.root.geometry("900x700")
        self.root.configure(bg="white")
        
        # 设置主题样式
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # 自定义样式，背景色改为白色
        self.style.configure("TButton", 
                           font=(".Microsoft YaHei UI", 10),
                           padding=6,
                           relief="flat",
                           background="#4a90e2",
                           foreground="white")
        self.style.map("TButton", 
                      background=[("active", "#357abd")],
                      foreground=[("active", "white")])
        
        self.style.configure("TLabel", 
                           font=(".Microsoft YaHei UI", 10),
                           background="white")
        
        self.style.configure("Header.TLabel", 
                           font=(".Microsoft YaHei UI", 18, "bold"),
                           background="white",
                           foreground="#333333")
        
        self.style.configure("SubHeader.TLabel", 
                           font=(".Microsoft YaHei UI", 12, "bold"),
                           background="white",
                           foreground="#555555")
        
        self.style.configure("TFrame", 
                           background="white")
        
        # 初始化变量
        self.images = [None, None, None]
        self.image_paths = ["", "", ""]
        self.channels = ["R", "G", "B"]
        self.result_image = None
        
        # 创建GUI组件
        self.create_widgets()
    
    def create_widgets(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建垂直滚动条
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建滚动画布
        self.canvas = tk.Canvas(self.main_frame, yscrollcommand=self.scrollbar.set, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        self.scrollbar.config(command=self.canvas.yview)
        
        # 创建内容框架
        self.content_frame = ttk.Frame(self.canvas, style="TFrame")
        self.content_frame.configure(padding="20 20 20 20")
        
        # 在画布上创建内容窗口
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw", tags="content_frame")
        
        # 绑定配置事件，更新滚动区域和内容宽度
        def on_configure(event):
            # 更新滚动区域
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # 保持内容居中，动态调整宽度
            canvas_width = self.canvas.winfo_width()
            # 直接设置内容宽度为画布宽度，确保内容始终适应窗口大小
            self.canvas.itemconfig("content_frame", width=canvas_width)
        
        # 绑定配置事件
        self.content_frame.bind("<Configure>", on_configure)
        self.canvas.bind("<Configure>", on_configure)
        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", on_configure)
        
        # 添加鼠标滚轮支持
        def on_mousewheel(event):
            # 直接操作画布滚动，避免无限递归
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # 绑定鼠标滚轮事件到画布
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 标题
        title_label = ttk.Label(self.content_frame, text="RGB通道混合器", style="Header.TLabel")
        title_label.pack(pady=20, anchor=tk.CENTER)
        
        # 图片选择和通道选择框架
        input_frame = ttk.LabelFrame(self.content_frame, text="图片和通道设置", padding="15 15 15 15")
        input_frame.pack(fill=tk.X, pady=15, padx=50)  # 添加左右边距，实现居中效果
        
        for i in range(3):
            # 主框架
            main_row_frame = ttk.Frame(input_frame)
            main_row_frame.pack(fill=tk.X, pady=8)
            
            # 左侧：可点击的预览画布
            preview_frame = ttk.Frame(main_row_frame)
            preview_frame.pack(side=tk.LEFT, padx=5)
            
            # 创建画布，用于显示预览和接收点击事件
            canvas = tk.Canvas(preview_frame, width=80, height=80, bg="white", highlightthickness=1, highlightbackground="#cccccc")
            canvas.pack()
            
            # 绑定点击事件
            canvas.bind("<Button-1>", lambda event, idx=i: self.select_image(idx))
            
            # 保存画布引用
            setattr(self, f"preview_canvas_{i}", canvas)
            
            # 初始显示空白状态
            canvas.create_text(40, 40, text="点击选择图片", fill="#999999", font=(".Microsoft YaHei UI", 9))
            
            # 右侧：路径和通道设置
            right_frame = ttk.Frame(main_row_frame)
            right_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            # 路径显示
            path_label = ttk.Label(right_frame, text="未选择图片", width=60, anchor=tk.W)
            path_label.pack(side=tk.LEFT, pady=2, fill=tk.X, expand=True)
            setattr(self, f"path_label_{i}", path_label)
            
            # 通道选择下拉菜单，确保每个下拉栏都显示RGB三个通道选项
            channel_var = tk.StringVar(value=self.channels[i])
            # 明确指定所有选项，确保每个下拉栏都显示RGB三个选项
            channel_menu = ttk.OptionMenu(right_frame, channel_var, "R", "R", "G", "B", command=lambda val, idx=i: self.set_channel(idx, val))
            channel_menu.pack(side=tk.RIGHT, padx=5, pady=2)
            channel_menu.configure(width=5)
            setattr(self, f"channel_var_{i}", channel_var)
        
        # 操作按钮框架，确保按钮居中显示
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=20, anchor=tk.CENTER)  # 居中显示
        
        # 创建图片按钮
        create_btn = ttk.Button(btn_frame, text="创建混合图片", command=self.create_mixed_image, style="TButton")
        create_btn.pack(side=tk.LEFT, padx=15, pady=10)  # 增加按钮底部外边距
        create_btn.configure(width=15)
        
        # 保存图片按钮
        save_btn = ttk.Button(btn_frame, text="保存图片", command=self.save_image, style="TButton")
        save_btn.pack(side=tk.LEFT, padx=15, pady=10)  # 增加按钮底部外边距
        save_btn.configure(width=15)
        
        # 结果图片显示，居中布局
        result_label = ttk.Label(self.content_frame, text="结果图片", style="SubHeader.TLabel")
        result_label.pack(pady=20, anchor=tk.CENTER)  # 居中显示
        
        # 结果图片容器，居中布局
        result_container = ttk.Frame(self.content_frame, padding="10 10 20 20", style="TFrame")
        result_container.pack(fill=tk.X, pady=5, padx=50, anchor=tk.CENTER)  # 添加左右边距，实现居中效果
        
        # 使用适中的结果图片尺寸，确保不需要全屏就能显示
        self.result_canvas = tk.Canvas(result_container, width=400, height=400, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.result_canvas.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def select_image(self, idx):
        """选择图片"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            self.image_paths[idx] = file_path
            getattr(self, f"path_label_{idx}").config(text=file_path)
            
            # 保存原始分辨率图片用于混合
            original_img = Image.open(file_path)
            self.images[idx] = original_img
            
            # 更新小预览画布（80x80）
            small_preview_img = original_img.copy()
            small_size = 80
            
            # 创建正方形画布，背景色改为白色
            small_square_img = Image.new("RGB", (small_size, small_size), color="white")
            small_preview_img.thumbnail((small_size, small_size), Image.LANCZOS)
            
            # 计算居中位置
            img_width, img_height = small_preview_img.size
            x = (small_size - img_width) // 2
            y = (small_size - img_height) // 2
            
            # 粘贴图片到正方形画布
            small_square_img.paste(small_preview_img, (x, y))
            
            # 创建PhotoImage对象
            small_photo = ImageTk.PhotoImage(small_square_img)
            
            # 更新小预览画布
            small_canvas = getattr(self, f"preview_canvas_{idx}")
            small_canvas.delete("all")
            small_canvas.create_image(small_size//2, small_size//2, image=small_photo, anchor=tk.CENTER)
            setattr(small_canvas, "photo", small_photo)
    
    def set_channel(self, idx, channel):
        """设置通道"""
        self.channels[idx] = channel
    
    def create_mixed_image(self):
        """创建混合图片"""
        # 检查是否选择了三张图片
        if None in self.images:
            messagebox.showerror("错误", "请选择三张图片")
            return
        
        # 检查通道选择是否重复
        if len(set(self.channels)) != 3:
            messagebox.showerror("错误", "请确保每个通道(R、G、B)只被选择一次")
            return
        
        # 获取第一张图片的尺寸，其他图片将被调整为该尺寸
        width, height = self.images[0].size
        
        # 创建空的RGB通道
        r_channel = None
        g_channel = None
        b_channel = None
        
        # 处理每张图片，将其分配到对应的通道
        for img, channel in zip(self.images, self.channels):
            # 调整图片尺寸
            resized_img = img.resize((width, height))
            # 转换为灰度图
            gray_img = resized_img.convert("L")
            
            # 分配到对应的通道
            if channel == "R":
                r_channel = gray_img
            elif channel == "G":
                g_channel = gray_img
            elif channel == "B":
                b_channel = gray_img
        
        # 合并通道
        self.result_image = Image.merge("RGB", (r_channel, g_channel, b_channel))
        
        # 显示结果图片（正方形格式）
        result_img = self.result_image.copy()
        
        # 创建正方形画布，背景色改为白色
        max_size = 500
        square_img = Image.new("RGB", (max_size, max_size), color="white")
        
        # 调整图片大小，保持比例
        result_img.thumbnail((max_size, max_size), Image.LANCZOS)
        
        # 计算居中位置
        img_width, img_height = result_img.size
        x = (max_size - img_width) // 2
        y = (max_size - img_height) // 2
        
        # 将图片粘贴到正方形画布中央
        square_img.paste(result_img, (x, y))
        
        # 创建PhotoImage对象
        photo = ImageTk.PhotoImage(square_img)
        
        # 清除画布
        self.result_canvas.delete("all")
        
        # 获取画布中心
        canvas_width = self.result_canvas.winfo_width()
        canvas_height = self.result_canvas.winfo_height()
        
        # 计算画布中心位置
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # 绘制图片，居中显示
        self.result_canvas.create_image(center_x, center_y, image=photo, anchor=tk.CENTER)
        
        # 保存引用，防止垃圾回收
        self.result_canvas.photo = photo
        
        # 强制更新画布
        self.result_canvas.update()
        
        messagebox.showinfo("成功", "混合图片创建成功")
    
    def save_image(self):
        """保存图片"""
        if self.result_image is None:
            messagebox.showerror("错误", "请先创建混合图片")
            return
        
        # 创建尺寸选择对话框
        size_window = tk.Toplevel(self.root)
        size_window.title("选择导出尺寸")
        size_window.geometry("350x300")  # 增大对话框尺寸
        size_window.resizable(False, False)
        size_window.grab_set()  # 模态窗口
        size_window.configure(bg="white")  # 设置背景色为白色
        
        # 居中显示
        size_window.update_idletasks()
        x = (size_window.winfo_screenwidth() - size_window.winfo_width()) // 2
        y = (size_window.winfo_screenheight() - size_window.winfo_height()) // 2
        size_window.geometry(f"+{x}+{y}")
        
        # 尺寸选项
        sizes = ["512x512", "1024x1024", "2048x2048", "4096x4096", "8192x8192"]
        selected_size = tk.StringVar(value="1024x1024")
        
        # 标题
        ttk.Label(size_window, text="选择导出尺寸：", font=(".Microsoft YaHei UI", 12)).pack(pady=15)
        
        # 尺寸选择列表
        for size in sizes:
            ttk.Radiobutton(size_window, text=size, variable=selected_size, value=size).pack(anchor=tk.W, padx=20, pady=5)
        
        # 保存按钮
        def on_save():
            # 获取选择的尺寸
            size_str = selected_size.get()
            width, height = map(int, size_str.split("x"))
            
            # 调整图片大小
            resized_img = self.result_image.resize((width, height), Image.LANCZOS)
            
            # 关闭尺寸选择窗口
            size_window.destroy()
            
            # 打开保存对话框，强制PNG格式
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG文件", "*.png")],
                title="保存为PNG文件"
            )
            
            if file_path:
                # 确保文件扩展名为.png
                if not file_path.lower().endswith(".png"):
                    file_path += ".png"
                
                # 保存图片，强制PNG格式
                resized_img.save(file_path, format="PNG")
                messagebox.showinfo("成功", f"图片已保存到 {file_path}")
        
        # 取消按钮
        def on_cancel():
            size_window.destroy()
        
        # 按钮框架
        btn_frame = tk.Frame(size_window, bg="white")
        btn_frame.pack(pady=30)
        
        # 使用普通的tk.Button，确保按钮可见
        save_btn = tk.Button(btn_frame, text="保存", command=on_save, font=(".Microsoft YaHei UI", 10), 
                            bg="#4a90e2", fg="white", width=10, height=1)
        save_btn.pack(side=tk.LEFT, padx=15)
        
        cancel_btn = tk.Button(btn_frame, text="取消", command=on_cancel, font=(".Microsoft YaHei UI", 10), 
                              bg="#999999", fg="white", width=10, height=1)
        cancel_btn.pack(side=tk.LEFT, padx=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChannelMixerApp(root)
    root.mainloop()