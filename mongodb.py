import tkinter as tk
from tkinter import messagebox
import pymongo
from bson.objectid import ObjectId  # Dùng để xử lý _id của MongoDB


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý Công Việc (MongoDB)")
        self.root.geometry("500x500")

        # --- KẾT NỐI MONGODB ---
        try:
            self.client = pymongo.MongoClient("mongodb://localhost:27017/")
            self.db = self.client["TaskManager"]
            self.tasks_col = self.db["Tasks"]
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối MongoDB: {e}")
            root.destroy()
            return

        # Biến lưu trữ danh sách các object lấy từ DB (để mapping ID khi click Listbox)
        self.current_tasks_data = []

        # --- GIAO DIỆN ---

        # 1. Nhập liệu
        input_frame = tk.Frame(root, padx=10, pady=10)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="Tên công việc:").grid(row=0, column=0, sticky="w")
        self.entry_title = tk.Entry(input_frame, width=40)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Mô tả chi tiết:").grid(row=1, column=0, sticky="nw")
        self.text_desc = tk.Text(input_frame, width=30, height=4)
        self.text_desc.grid(row=1, column=1, padx=5, pady=5)

        # 2. Các nút chức năng
        btn_frame = tk.Frame(root, pady=5)
        btn_frame.pack()

        tk.Button(btn_frame, text="Thêm công việc", command=self.add_task, bg="#4CAF50", fg="white").pack(side="left",
                                                                                                          padx=5)
        tk.Button(btn_frame, text="Đánh dấu hoàn thành", command=self.mark_done, bg="#2196F3", fg="white").pack(
            side="left", padx=5)
        tk.Button(btn_frame, text="Xóa công việc", command=self.delete_task, bg="#f44336", fg="white").pack(side="left",
                                                                                                            padx=5)

        # 3. Listbox hiển thị danh sách
        list_frame = tk.Frame(root, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True)

        tk.Label(list_frame, text="Danh sách công việc:").pack(anchor="w")

        self.listbox = tk.Listbox(list_frame, font=("Arial", 10))
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # Load dữ liệu ban đầu
        self.load_tasks()

    # --- CHỨC NĂNG ---

    def load_tasks(self):
        """Lấy toàn bộ công việc từ MongoDB và hiển thị"""
        self.listbox.delete(0, tk.END)  # Xóa listbox cũ
        self.current_tasks_data = []  # Reset danh sách tạm

        # Lấy dữ liệu từ DB
        cursor = self.tasks_col.find()

        for task in cursor:
            self.current_tasks_data.append(task)  # Lưu object vào list tạm để lấy _id sau này
            display_text = f"{task['title']} - [{task['status']}]"
            self.listbox.insert(tk.END, display_text)

    def add_task(self):
        title = self.entry_title.get().strip()
        description = self.text_desc.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên công việc!")
            return

        new_task = {
            "title": title,
            "description": description,
            "status": "Chưa hoàn thành"
        }

        try:
            self.tasks_col.insert_one(new_task)
            messagebox.showinfo("Thành công", "Đã thêm công việc mới!")
            # Reset form
            self.entry_title.delete(0, tk.END)
            self.text_desc.delete("1.0", tk.END)
            # Tải lại danh sách
            self.load_tasks()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm: {e}")

    def get_selected_task_id(self):
        """Hàm phụ trợ lấy _id của dòng đang chọn"""
        try:
            index = self.listbox.curselection()[0]  # Lấy index dòng đang chọn
            task_data = self.current_tasks_data[index]  # Lấy data tương ứng trong list tạm
            return task_data["_id"]
        except IndexError:
            return None

    def mark_done(self):
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một công việc!")
            return

        try:
            self.tasks_col.update_one(
                {"_id": task_id},
                {"$set": {"status": "Hoàn thành"}}
            )
            self.load_tasks()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")

    def delete_task(self):
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một công việc để xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa công việc này?")
        if confirm:
            try:
                self.tasks_col.delete_one({"_id": task_id})
                messagebox.showinfo("Thành công", "Đã xóa công việc.")
                self.load_tasks()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()