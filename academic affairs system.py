import psycopg2
import tkinter as tk
from functools import partial
from tkinter import ttk,messagebox

class AAS:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("教务管理系统")
        self.root.geometry("800x600+50+50")
        self.root.configure(bg="#F5F5F5")

        # 样式配置
        self.style=ttk.Style()
        self.configure_styles()

        # 数据库配置
        self.db_config={
            "host": "localhost",
            "port": "54321",
            "database": "aas",
            "user": "system",
            "password": "yzf20050310"
        }

        self.current_user=None
        self.user_type=None
        self.show_login_ui()

    def configure_styles(self):
        """配置全局UI样式"""
        self.style.theme_use("clam")
        self.style.configure("TFrame",background="#F5F5F5")
        self.style.configure("TButton",font=("微软雅黑",15),padding=8)
        self.style.configure("Text.TLabel",font=("微软雅黑",15,"bold"))

        # 定义颜色主题
        colors={
            "red": "#E74C3C",
            "green": "#4CAF50",
            "orange": "#FF9800",
            "blue": "#2196F3",
            "purple": "#9C27B0"
        }

        # 按钮样式配置
        for name,color in colors.items():
            self.style.configure(f"{name}.TButton",
                                 foreground="white",
                                 background=color,
                                 bordercolor=color,
                                 focuscolor=color,
                                 padding=12,
                                 relief="flat")

    def db_connect(self):
        """创建数据库连接"""
        return psycopg2.connect(**self.db_config)

    def login(self):
        """处理登录逻辑"""
        user_id=self.id_entry.get().strip()
        user_type=self.user_type.get()

        if not user_id:
            messagebox.showwarning("输入错误","请输入账号！")
            return

        try:
            with self.db_connect() as conn:
                with conn.cursor() as cursor:
                    table="s" if user_type=="student" else "t"
                    cursor.execute(
                        f"SELECT {table}no FROM aas.{table} WHERE {table}no = %s",
                        (user_id,)
                    )
                    if cursor.fetchone():
                        self.current_user=user_id
                        self.user_type=user_type
                        self.show_main_ui()
                    else:
                        messagebox.showerror("登录失败","账号或身份错误！")
        except Exception as e:
            messagebox.showerror("系统错误",f"数据库连接失败：{str(e)}")

    def show_login_ui(self):
        """显示登录界面"""
        self.clear_window()

        main_frame=ttk.Frame(self.root,style="TFrame")
        main_frame.pack(expand=True,fill="both",padx=80,pady=80)

        # 登录框容器
        login_box=ttk.Frame(main_frame,style="TFrame")
        login_box.pack(expand=True)

        # 标题部分
        title_frame=ttk.Frame(login_box)
        title_frame.pack(pady=(0,30))
        ttk.Label(title_frame,
                  text="  教 务 管 理 系 统  ",
                  font=("微软雅黑",35,"bold"),
                  background="#3F51B5",
                  foreground="white").pack(padx=30,pady=15)

        # 登录表单
        form_frame=ttk.Frame(login_box)
        form_frame.pack()

        # 账号输入
        ttk.Label(form_frame,text="  账 号：",font=("微软雅黑",15)).grid(row=0,column=0,pady=15,sticky="e")
        self.id_entry=ttk.Entry(form_frame,font=("微软雅黑",15),width=24)
        self.id_entry.grid(row=0,column=1,padx=15,pady=15)

        # 身份选择
        ttk.Label(form_frame,text="  身 份：",font=("微软雅黑",15)).grid(row=1,column=0,pady=15,sticky="e")
        self.user_type=tk.StringVar(value="student")
        ttk.Radiobutton(form_frame,text="  学 生",variable=self.user_type,
                        value="student").grid(row=1, column=1, sticky="w", padx=15, ipadx=10, ipady=5)
        ttk.Radiobutton(form_frame,text="  教 师",variable=self.user_type,
                        value="teacher").grid(row=1, column=1, sticky="e", padx=15, ipadx=10, ipady=5)

        # 登录按钮
        btn_frame=ttk.Frame(login_box)
        btn_frame.pack(pady=50)
        ttk.Button(btn_frame,text="登      录",
                   command=self.login,
                   style="green.TButton").pack(ipadx=10)

    def show_main_ui(self):
        """显示主功能界面"""
        self.clear_window()

        # 主容器
        main_frame=ttk.Frame(self.root)
        main_frame.pack(expand=True,fill="both",padx=20,pady=20)

        # 标题栏
        header_frame=ttk.Frame(main_frame)
        header_frame.pack(fill="x",pady=(0,30))
        ttk.Label(header_frame,
                  text=f" 欢迎回来，{'同学' if self.user_type=='student' else '老师'} {self.current_user} ",
                  font=("微软雅黑",25,"bold"),
                  background="#3F51B5",
                  foreground="white").pack(side="left",padx=10)
        ttk.Button(header_frame,text="退出登录",
                   command=self.show_login_ui,
                   style="red.TButton").pack(side="right",padx=10)

        # 功能按钮区
        func_frame=ttk.Frame(main_frame)
        func_frame.pack(expand=True)

        button_config={
            "student": [
                ("选课管理","green",self.show_course_selection),
                ("退课管理","orange",self.show_course_withdrawal),
                ("学生评教","blue",self.show_student_evaluations),
                ("我的课表","purple",partial(self.show_schedule,"student"))
            ],
            "teacher": [
                ("开课管理","green",self.show_create_course),
                ("成绩管理","orange",self.show_register_grade),
                ("评教反馈","blue",self.show_teacher_evaluations),
                ("我的课表","purple",partial(self.show_schedule,"teacher"))
            ]
        }

        # 创建按钮网格
        buttons=button_config[self.user_type]
        for idx,(text,color,cmd) in enumerate(buttons):
            row,col=divmod(idx,2)
            btn=ttk.Button(func_frame,
                           text=text,
                           command=cmd,
                           style=f"{color}.TButton")
            btn.grid(row=row,column=col,padx=30,pady=30,sticky="nsew",ipadx=20)
            func_frame.grid_columnconfigure(col,weight=1)

        func_frame.grid_rowconfigure(0,weight=1)
        func_frame.grid_rowconfigure(1,weight=1)

    def _course_operation_ui(self,**kwargs):
        """通用课程操作界面模板"""
        top=tk.Toplevel(self.root)
        top.title(kwargs["title"])
        top.geometry(f"{kwargs['window_size'][0]}x{kwargs['window_size'][1]}+100+100")

        # 主容器
        main_frame=ttk.Frame(top)
        main_frame.pack(expand=True,fill="both",padx=20,pady=20)

        # 表格容器
        table_frame=ttk.Frame(main_frame)
        table_frame.pack(expand=True,fill="both")

        # 创建表格
        tree,_=self._create_scrollable_table(
            parent=table_frame,
            columns=kwargs["columns"],
            height=15,
            use_scroll_x=True if len(kwargs["columns"])>3 else False
        )

        # 加载数据
        try:
            with self.db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(kwargs["query"],(self.current_user,))
                    for row in cursor.fetchall():
                        tree.insert("","end",values=row)
        except Exception as e:
            messagebox.showerror("数据错误",f"加载课程失败：{str(e)}")
            top.destroy()
            return

        # 操作按钮
        btn_frame=ttk.Frame(main_frame)
        btn_frame.pack(pady=15)

        def execute_operation():
            selected=tree.selection()
            if not selected:
                messagebox.showwarning("操作提示","请先选择课程！")
                return

            course_id=tree.item(selected[0])["values"][0]
            try:
                with self.db_connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(kwargs["operation"],
                                       (self.current_user,course_id))
                        conn.commit()
                messagebox.showinfo("操作成功","课程操作成功！")
                top.destroy()
            except psycopg2.Error as e:
                messagebox.showerror("操作失败",f"课程操作失败：{str(e)}")

        ttk.Button(btn_frame,
                   text="确认操作",
                   command=execute_operation,
                   style="green.TButton").pack(padx=20,ipadx=30)

    def _create_scrollable_table(self,parent,columns,height=15,use_scroll_x=False):
        """创建表格组件"""
        container=ttk.Frame(parent)
        container.pack(expand=True,fill="both")

        # 创建滚动条
        y_scroll=ttk.Scrollbar(container)
        y_scroll.pack(side="right",fill="y")

        x_scroll=None
        if use_scroll_x:
            x_scroll=ttk.Scrollbar(container,orient="horizontal")
            x_scroll.pack(side="bottom",fill="x")

        # 创建视图
        tree=ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set if x_scroll else None,
            height=height,
            selectmode="browse"
        )

        # 配置列
        for col in columns:
            tree.heading(col,text=col,anchor="center")
            tree.column(col,width=10,anchor="center",minwidth=100)

        tree.pack(side="left",expand=True,fill="both")
        y_scroll.config(command=tree.yview)
        if x_scroll:
            x_scroll.config(command=tree.xview)

        return tree,(x_scroll,y_scroll) if x_scroll else y_scroll

    def show_course_selection(self):
        """选课管理功能"""
        self._course_operation_ui(
            title="选课管理",
            query="""
                SELECT c.cno, c.cname, c.credit, 
                       COALESCE(pre.cname, '无') AS precname
                FROM aas.c
                LEFT JOIN (
                    SELECT pc.cno, c.cname 
                    FROM aas.pc
                    JOIN aas.c ON pc.precno = c.cno
                ) pre ON c.cno = pre.cno
                WHERE c.cno NOT IN (
                    SELECT cno FROM aas.sc WHERE sno = %s
                )
                ORDER BY c.cno
            """,
            columns=("课程号","课程名","学分","先修课程"),
            operation="INSERT INTO aas.sc (sno, cno) VALUES (%s, %s)",
            window_size=(800,600)
        )

    def show_course_withdrawal(self):
        """退课管理功能"""
        self._course_operation_ui(
            title="退课管理",
            query="""
                SELECT sc.cno, c.cname, c.credit 
                FROM aas.sc 
                JOIN aas.c ON sc.cno = c.cno 
                WHERE sno = %s
                ORDER BY c.cno
            """,
            columns=("课程号","课程名","学分"),
            operation="DELETE FROM aas.sc WHERE sno = %s AND cno = %s",
            window_size=(800,600)
        )

    def show_student_evaluations(self):
        """学生评教功能"""
        top=tk.Toplevel(self.root)
        top.title("学生评教")
        top.geometry("800x600+100+100")

        # 主容器
        main_frame=ttk.Frame(top)
        main_frame.pack(expand=True,fill="both",padx=20,pady=20)

        # 创建表格
        tree,_=self._create_scrollable_table(
            parent=main_frame,
            columns=("课程号","课程名","职工号","职工名","评教分数"),
            height=15
        )

        # 加载数据
        try:
            with self.db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT DISTINCT ON (sc.cno, hc.tno)
                            sc.cno, c.cname, hc.tno, t.tname, et.evaluation
                        FROM aas.sc 
                        JOIN aas.hc ON sc.cno = hc.cno 
                        JOIN aas.t ON hc.tno = t.tno 
                        JOIN aas.c ON sc.cno = c.cno 
                        LEFT JOIN aas.et ON sc.sno = et.sno 
                            AND sc.cno = et.cno 
                            AND hc.tno = et.tno
                        WHERE sc.sno = %s
                        ORDER BY sc.cno, hc.tno
                    """,(self.current_user,))

                    for row in cursor.fetchall():
                        tree.insert("","end",values=row)
        except Exception as e:
            messagebox.showerror("数据错误",f"加载评教失败：{str(e)}")
            top.destroy()
            return

        # 评价编辑区
        edit_frame=ttk.Frame(main_frame)
        edit_frame.pack(pady=15)

        ttk.Label(edit_frame,text="  输入分数：",style="Text.TLabel").grid(row=0,column=0,padx=5)
        eval_entry=ttk.Entry(edit_frame,width=60)
        eval_entry.grid(row=0,column=1,padx=5)

        def save_evaluation():
            selected=tree.selection()
            if not selected:
                messagebox.showwarning("操作提示","请先选择课程！")
                return

            evaluation=eval_entry.get().strip()
            if not evaluation:
                messagebox.showwarning("输入错误","评教分数不能为空！")
                return

            values=tree.item(selected[0])["values"]
            try:
                with self.db_connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO aas.et (sno, cno, tno, evaluation)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (sno, cno, tno) 
                            DO UPDATE SET evaluation = EXCLUDED.evaluation
                        """,(self.current_user,values[0],values[2],evaluation))
                        conn.commit()
                messagebox.showinfo("操作成功","提交评教成功！")
                tree.item(selected[0],values=(*values[:4],evaluation))
            except Exception as e:
                messagebox.showerror("操作失败",f"提交评教失败：{str(e)}")

        ttk.Button(edit_frame,
                   text="提交评教",
                   command=save_evaluation,
                   style="green.TButton").grid(row=0,column=2,padx=10)

    def show_create_course(self):
        """开课管理功能"""
        top=tk.Toplevel(self.root)
        top.title("开课管理")
        top.geometry("800x600+100+100")

        # 主容器
        main_frame=ttk.Frame(top)
        main_frame.pack(expand=True,fill="both",padx=30,pady=30)

        # 表单字段
        fields=[
            ("  课程号:  ","cno"),
            ("  课程名:  ","cname"),
            ("  课程学分:  ","credit")
        ]
        entries=[]

        for idx,(label,_) in enumerate(fields):
            ttk.Label(main_frame,text=label,style="Text.TLabel").grid(row=idx,column=0,pady=20,sticky="e")
            entry=ttk.Entry(main_frame,width=85)
            entry.grid(row=idx,column=1,padx=5,pady=8)
            entries.append(entry)

        def submit_course():
            values=[e.get().strip() for e in entries]
            if not all(values):
                messagebox.showwarning("输入错误","所有字段必须填写！")
                return

            try:
                with self.db_connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO aas.c (cno, cname, credit)
                            VALUES (%s, %s, %s)
                        """,values)
                        conn.commit()
                messagebox.showinfo("操作成功","提交开课成功！")
                top.destroy()
            except psycopg2.IntegrityError:
                messagebox.showerror("操作失败","课程号已存在！")
            except Exception as e:
                messagebox.showerror("操作失败",f"提交开课失败：{str(e)}")

        btn_frame=ttk.Frame(main_frame)
        btn_frame.grid(row=len(fields),column=0,columnspan=2,pady=15)
        ttk.Button(btn_frame,
                   text="提交开课",
                   command=submit_course,
                   style="green.TButton").pack(ipadx=30)

    def show_register_grade(self):
        """成绩管理功能"""
        top=tk.Toplevel(self.root)
        top.title("成绩管理")
        top.geometry("800x600+100+100")

        # 主容器
        main_frame=ttk.Frame(top)
        main_frame.pack(expand=True,fill="both",padx=20,pady=20)

        # 课程选择区
        course_frame=ttk.Frame(main_frame)
        course_frame.pack(fill="x",pady=10)

        ttk.Label(course_frame,text="  选择课程：",style="Text.TLabel").pack(side="left",padx=5)
        course_var=tk.StringVar()
        course_combobox=ttk.Combobox(course_frame,textvariable=course_var,width=60)
        course_combobox.pack(side="left",padx=5)

        # 加载教师课程
        try:
            with self.db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT DISTINCT c.cno, c.cname 
                        FROM aas.hc 
                        JOIN aas.c ON hc.cno = c.cno 
                        WHERE tno = %s
                        ORDER BY c.cno
                    """,(self.current_user,))
                    courses=[f"{row[0]} {row[1]}" for row in cursor.fetchall()]
                    course_combobox["values"]=courses
        except Exception as e:
            messagebox.showerror("数据错误",f"加载课程失败：{str(e)}")
            top.destroy()
            return

        # 学生成绩表格
        table_frame=ttk.Frame(main_frame)
        table_frame.pack(expand=True,fill="both",pady=10)

        tree,_=self._create_scrollable_table(
            parent=table_frame,
            columns=("学号","姓名","成绩"),
            height=15
        )

        def load_students():
            if not course_var.get():
                messagebox.showwarning("操作提示","请先选择课程！")
                return

            cno=course_var.get().split()[0]
            try:
                with self.db_connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT s.sno, s.sname, sc.score 
                            FROM aas.sc 
                            JOIN aas.s ON sc.sno = s.sno 
                            WHERE sc.cno = %s
                            ORDER BY s.sno
                        """,(cno,))

                        for row in tree.get_children():
                            tree.delete(row)

                        for sno,name,score in cursor.fetchall():
                            tree.insert("","end",values=(sno,name,score or "未录入"))
            except Exception as e:
                messagebox.showerror("数据错误",f"加载学生失败：{str(e)}")

        ttk.Button(course_frame,
                   text="加载学生",
                   command=load_students,
                   style="blue.TButton").pack(side="left",padx=10)

        # 成绩录入区
        grade_frame=ttk.Frame(main_frame)
        grade_frame.pack(fill="x",pady=10)

        ttk.Label(grade_frame,text="  输入成绩：",style="Text.TLabel").pack(side="left",padx=5)
        grade_entry=ttk.Entry(grade_frame,width=20)
        grade_entry.pack(side="left",padx=5)

        def update_grade():
            selected=tree.selection()
            if not selected:
                messagebox.showwarning("操作提示","请选择学生！")
                return

            try:
                score=float(grade_entry.get())
                if not (0<=score<=100):
                    raise ValueError
            except ValueError:
                messagebox.showerror("输入错误","请输入0-100之间的数字！")
                return

            cno=course_var.get().split()[0]
            sno=tree.item(selected[0])["values"][0]

            try:
                with self.db_connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            UPDATE aas.sc 
                            SET score = %s 
                            WHERE sno = %s AND cno = %s
                        """,(score,sno,cno))
                        conn.commit()
                messagebox.showinfo("操作成功","提交成绩成功！")
                load_students()
            except Exception as e:
                messagebox.showerror("操作失败",f"提交成绩失败：{str(e)}")

        ttk.Button(grade_frame,
                   text="提交成绩",
                   command=update_grade,
                   style="green.TButton").pack(side="left",padx=10)

    def show_teacher_evaluations(self):
        """评教反馈功能"""
        top=tk.Toplevel(self.root)
        top.title("评教反馈")
        top.geometry("800x600+100+100")

        # 主容器
        main_frame=ttk.Frame(top)
        main_frame.pack(expand=True,fill="both",padx=20,pady=20)

        # 创建表格
        tree,_=self._create_scrollable_table(
            parent=main_frame,
            columns=("学号","学生名","课程名","评教分数"),
            height=15
        )

        # 加载数据
        try:
            with self.db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            SUBSTRING(et.sno, 1, 4) || '****' AS sno,
                            SUBSTRING(s.sname, 1, 1) || '**' AS sname,
                            c.cname, 
                            et.evaluation
                        FROM aas.et
                        JOIN aas.s ON et.sno = s.sno
                        JOIN aas.c ON et.cno = c.cno
                        WHERE et.tno = %s
                        ORDER BY c.cno, et.sno
                    """,(self.current_user,))

                    for row in cursor.fetchall():
                        tree.insert("","end",values=row)
        except Exception as e:
            messagebox.showerror("数据错误",f"加载评教失败：{str(e)}")
            top.destroy()

    def show_schedule(self,user_type):
        """我的课表功能"""
        top=tk.Toplevel(self.root)
        top.title("我的课表")
        top.geometry("800x600+100+100")

        # 主容器
        main_frame=ttk.Frame(top)
        main_frame.pack(expand=True,fill="both",padx=20,pady=20)

        # 创建表格
        columns=("课程名","星期几","开始课节","结束课节","教学楼","教室号","教师") \
            if user_type=="student" else \
            ("课程名称","星期几","开始课节","结束课节","教学楼","教室")

        tree,_=self._create_scrollable_table(
            parent=main_frame,
            columns=columns,
            height=15,
            use_scroll_x=True
        )

        # 加载数据
        try:
            with self.db_connect() as conn:
                with conn.cursor() as cursor:
                    if user_type=="student":
                        cursor.execute("""
                            SELECT c.cname, m.week, m.mstart, m.mend, 
                                   r.building, r.rno, t.tname
                            FROM aas.sc 
                            JOIN aas.ac ON sc.cno = ac.cno 
                            JOIN aas.m ON ac.mno = m.mno 
                            JOIN aas.r ON ac.rno = r.rno 
                            JOIN aas.hc ON ac.cno = hc.cno AND ac.mno = hc.mno 
                            JOIN aas.t ON hc.tno = t.tno 
                            JOIN aas.c ON sc.cno = c.cno 
                            WHERE sc.sno = %s
                            ORDER BY m.week, m.mstart
                        """,(self.current_user,))
                    else:
                        cursor.execute("""
                            SELECT c.cname, m.week, m.mstart, m.mend, 
                                   r.building, r.rno
                            FROM aas.hc 
                            JOIN aas.ac ON hc.mno = ac.mno AND hc.cno = ac.cno 
                            JOIN aas.c ON hc.cno = c.cno 
                            JOIN aas.m ON ac.mno = m.mno 
                            JOIN aas.r ON ac.rno = r.rno 
                            WHERE hc.tno = %s
                            ORDER BY m.week, m.mstart
                        """,(self.current_user,))

                    for row in cursor.fetchall():
                        tree.insert("","end",values=row)
        except Exception as e:
            messagebox.showerror("数据错误",f"加载课表失败：{str(e)}")
            top.destroy()

    def clear_window(self):
        """清空当前窗口内容"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """运行主循环"""
        self.root.mainloop()


if __name__=="__main__":
    app=AAS()
    app.run()
