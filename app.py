import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class CBTStudyApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Jesus_boy CBT Exam Portal")
        self.root.configure(bg="#0f172a")
        self.root.attributes("-fullscreen", True)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        self.current_frame = None
        self.auth_mode = "login"

        self.users = {
            "Jesus_admin": "Jesus_boy",
            "Jesus": "david@123"
        }

        self.logged_in_user = None

        self.practice_timer_seconds = 0
        self.practice_timer_running = False
        self.practice_timer_job = None
        self.current_exam_name = ""
        self.current_exam_year = ""

        self.root.bind("<Escape>", self.exit_fullscreen)

        self.show_intro_screen()

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

    def clear_screen(self):
        self.stop_practice_timer()
        if self.current_frame is not None:
            self.current_frame.destroy()

    def stop_practice_timer(self):
        self.practice_timer_running = False
        if self.practice_timer_job:
            try:
                self.root.after_cancel(self.practice_timer_job)
            except Exception:
                pass
            self.practice_timer_job = None

    # =========================
    # INTRO / LOADING SCREEN
    # =========================
    def show_intro_screen(self):
        self.clear_screen()

        self.intro_frame = tk.Frame(self.root, bg="#0b1220")
        self.intro_frame.pack(fill="both", expand=True)
        self.current_frame = self.intro_frame

        self.canvas = tk.Canvas(
            self.intro_frame,
            bg="#0b1220",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.update()

        w = self.screen_w
        h = self.screen_h

        self.canvas.create_rectangle(0, 0, w, h, fill="#0b1220", outline="")
        self.canvas.create_line(100, 120, w - 100, 120, fill="#1e293b", width=2)
        self.canvas.create_line(100, h - 120, w - 100, h - 120, fill="#1e293b", width=2)

        self.canvas.create_text(
            130, 75,
            text="Jesus_boy CBT",
            fill="#38bdf8",
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        )

        self.title_x = -800
        self.title_y = h // 2 - 90
        self.title = self.canvas.create_text(
            self.title_x,
            self.title_y,
            text="WELCOME TO Jesus_boy CBT",
            fill="#f8fafc",
            font=("Segoe UI", 42, "bold"),
            anchor="w"
        )

        self.subtitle_x = w + 600
        self.subtitle_y = h // 2 - 25
        self.subtitle = self.canvas.create_text(
            self.subtitle_x,
            self.subtitle_y,
            text="Professional CBT Practice for JAMB, WAEC and NECO",
            fill="#94a3b8",
            font=("Segoe UI", 22),
            anchor="e"
        )

        self.accent_line = self.canvas.create_rectangle(
            140, self.title_y + 60, 140, self.title_y + 68,
            fill="#22c55e",
            outline=""
        )

        self.loading_text = self.canvas.create_text(
            w // 2,
            h - 180,
            text="Loading",
            fill="#cbd5e1",
            font=("Segoe UI", 18, "bold")
        )

        self.progress_bg = self.canvas.create_rectangle(
            w // 2 - 250, h - 145, w // 2 + 250, h - 120,
            fill="#1e293b", outline=""
        )

        self.progress_fill = self.canvas.create_rectangle(
            w // 2 - 250, h - 145, w // 2 - 250, h - 120,
            fill="#38bdf8", outline=""
        )

        self.canvas.create_text(
            w // 2,
            h - 90,
            text="Press ESC to exit full screen",
            fill="#64748b",
            font=("Segoe UI", 11)
        )

        self.dot_count = 0
        self.progress_step = 0
        self.total_progress_steps = 10000 // 100

        self.animate_title()
        self.animate_subtitle()
        self.animate_loading()
        self.animate_progress()

        self.root.after(10000, self.show_auth_page)

    def animate_title(self):
        target_x = 140
        if self.current_frame != self.intro_frame:
            return
        if self.title_x < target_x:
            self.title_x += 28
            self.canvas.coords(self.title, self.title_x, self.title_y)

            line_end = min(self.title_x + 360, 560)
            self.canvas.coords(
                self.accent_line,
                140, self.title_y + 60, line_end, self.title_y + 68
            )

            self.root.after(12, self.animate_title)

    def animate_subtitle(self):
        target_x = self.screen_w - 160
        if self.current_frame != self.intro_frame:
            return
        if self.subtitle_x > target_x:
            self.subtitle_x -= 24
            self.canvas.coords(self.subtitle, self.subtitle_x, self.subtitle_y)
            self.root.after(12, self.animate_subtitle)

    def animate_loading(self):
        if self.current_frame != self.intro_frame:
            return
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.canvas.itemconfig(self.loading_text, text=f"Loading{dots}")
        self.root.after(350, self.animate_loading)

    def animate_progress(self):
        if self.current_frame != self.intro_frame:
            return

        self.progress_step += 1
        w = self.screen_w
        left = w // 2 - 250
        total_width = 500
        fill_width = (self.progress_step / self.total_progress_steps) * total_width
        self.canvas.coords(
            self.progress_fill,
            left, self.screen_h - 145,
            left + fill_width, self.screen_h - 120
        )

        if self.progress_step < self.total_progress_steps:
            self.root.after(100, self.animate_progress)

    # =========================
    # AUTH PAGE
    # =========================
    def show_auth_page(self):
        self.clear_screen()

        self.auth_frame = tk.Frame(self.root, bg="#0f172a")
        self.auth_frame.pack(fill="both", expand=True)
        self.current_frame = self.auth_frame

        container = tk.Frame(self.auth_frame, bg="#0f172a")
        container.pack(fill="both", expand=True, padx=70, pady=45)

        left_panel = tk.Frame(container, bg="#111827", width=620)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 20))
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="JESUS_BOY CBT PORTAL",
            bg="#111827",
            fg="#38bdf8",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=40, pady=(45, 15))

        tk.Label(
            left_panel,
            text="Practice smarter.\nPrepare better.\nScore higher.",
            bg="#111827",
            fg="#f8fafc",
            justify="left",
            font=("Segoe UI", 32, "bold")
        ).pack(anchor="w", padx=40, pady=(10, 18))

        tk.Label(
            left_panel,
            text="Access professional CBT practice for JAMB, WAEC and NECO with a beautiful dashboard and year-based exam practice.",
            bg="#111827",
            fg="#94a3b8",
            justify="left",
            wraplength=500,
            font=("Segoe UI", 14)
        ).pack(anchor="w", padx=40, pady=(0, 30))

        self.make_feature_card(left_panel, "JAMB Practice", "Prepare with past questions and yearly exam categories.").pack(fill="x", padx=40, pady=8)
        self.make_feature_card(left_panel, "WAEC Practice", "Revise with organized subject practice and exam years.").pack(fill="x", padx=40, pady=8)
        self.make_feature_card(left_panel, "NECO Practice", "Train with structured mock practice and quick access tools.").pack(fill="x", padx=40, pady=8)

        tk.Label(
            left_panel,
            text="Default login:\nUsername: Jesus_admin\nPassword: Jesus_boy",
            bg="#111827",
            fg="#22c55e",
            justify="left",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=40, pady=(28, 20))

        right_panel = tk.Frame(container, bg="#1e293b", width=460)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        tk.Label(
            right_panel,
            text="Account Access",
            bg="#1e293b",
            fg="#f8fafc",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=(40, 10))

        toggle_wrap = tk.Frame(right_panel, bg="#1e293b")
        toggle_wrap.pack(pady=(10, 18))

        self.login_tab_btn = tk.Button(
            toggle_wrap,
            text="Login",
            command=lambda: self.switch_auth_mode("login"),
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            bd=0,
            padx=28,
            pady=12,
            cursor="hand2"
        )
        self.login_tab_btn.pack(side="left", padx=6)

        self.signup_tab_btn = tk.Button(
            toggle_wrap,
            text="Sign Up",
            command=lambda: self.switch_auth_mode("signup"),
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            bd=0,
            padx=28,
            pady=12,
            cursor="hand2"
        )
        self.signup_tab_btn.pack(side="left", padx=6)

        form = tk.Frame(right_panel, bg="#1e293b")
        form.pack(fill="x", padx=40, pady=10)

        self.auth_title_label = tk.Label(
            form,
            text="Login to Continue",
            bg="#1e293b",
            fg="#f8fafc",
            font=("Segoe UI", 19, "bold")
        )
        self.auth_title_label.pack(anchor="w", pady=(5, 18))

        tk.Label(form, text="Username", bg="#1e293b", fg="#cbd5e1", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.username_entry = tk.Entry(
            form,
            font=("Segoe UI", 13),
            bg="#0f172a",
            fg="#f8fafc",
            insertbackground="#f8fafc",
            relief="flat",
            bd=0
        )
        self.username_entry.pack(fill="x", pady=(8, 18), ipady=12)

        tk.Label(form, text="Password", bg="#1e293b", fg="#cbd5e1", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.password_entry = tk.Entry(
            form,
            font=("Segoe UI", 13),
            bg="#0f172a",
            fg="#f8fafc",
            insertbackground="#f8fafc",
            relief="flat",
            bd=0,
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(8, 18), ipady=12)

        self.confirm_label = tk.Label(
            form,
            text="Confirm Password",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Segoe UI", 11, "bold")
        )
        self.confirm_entry = tk.Entry(
            form,
            font=("Segoe UI", 13),
            bg="#0f172a",
            fg="#f8fafc",
            insertbackground="#f8fafc",
            relief="flat",
            bd=0,
            show="*"
        )

        self.auth_action_btn = tk.Button(
            form,
            text="Login",
            bg="#38bdf8",
            fg="#0f172a",
            activebackground="#38bdf8",
            activeforeground="#0f172a",
            font=("Segoe UI", 13, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=14,
            cursor="hand2",
            command=self.handle_auth
        )
        self.auth_action_btn.pack(fill="x", pady=(10, 12))

        tk.Button(
            form,
            text="Exit Full Screen",
            bg="#334155",
            fg="#f8fafc",
            activebackground="#334155",
            activeforeground="#f8fafc",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=12,
            cursor="hand2",
            command=lambda: self.root.attributes("-fullscreen", False)
        ).pack(fill="x")

        self.switch_auth_mode("login")

        self.username_entry.focus_set()
        self.root.bind("<Return>", self.handle_enter_key)

    def handle_enter_key(self, event=None):
        if self.current_frame == self.auth_frame:
            self.handle_auth()

    def switch_auth_mode(self, mode):
        self.auth_mode = mode

        if mode == "login":
            self.login_tab_btn.configure(bg="#38bdf8", fg="#0f172a")
            self.signup_tab_btn.configure(bg="#334155", fg="#f8fafc")
            self.auth_title_label.configure(text="Login to Continue")
            self.auth_action_btn.configure(text="Login")
            self.confirm_label.pack_forget()
            self.confirm_entry.pack_forget()
        else:
            self.signup_tab_btn.configure(bg="#22c55e", fg="#0f172a")
            self.login_tab_btn.configure(bg="#334155", fg="#f8fafc")
            self.auth_title_label.configure(text="Create New Account")
            self.auth_action_btn.configure(text="Sign Up")
            self.confirm_label.pack(anchor="w")
            self.confirm_entry.pack(fill="x", pady=(8, 18), ipady=12)

    def handle_auth(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Missing Details", "Please enter username and password.")
            return

        if self.auth_mode == "login":
            if username in self.users and self.users[username] == password:
                self.logged_in_user = username
                self.show_home_page()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
        else:
            confirm = self.confirm_entry.get().strip()

            if not confirm:
                messagebox.showerror("Missing Details", "Please confirm your password.")
                return

            if password != confirm:
                messagebox.showerror("Password Error", "Passwords do not match.")
                return

            if username in self.users:
                messagebox.showerror("Account Exists", "That username already exists.")
                return

            self.users[username] = password
            messagebox.showinfo("Success", "Account created successfully. You can now log in.")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_entry.delete(0, tk.END)
            self.switch_auth_mode("login")

    def make_feature_card(self, parent, title, text):
        card = tk.Frame(parent, bg="#1f2937")
        tk.Label(
            card,
            text=title,
            bg="#1f2937",
            fg="#f8fafc",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(
            card,
            text=text,
            bg="#1f2937",
            fg="#94a3b8",
            wraplength=500,
            justify="left",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 14))
        return card

    # =========================
    # HOME HELPERS
    # =========================
    def get_first_name(self, username):
        if not username:
            return "Champion"
        cleaned = username.replace("_", " ").replace("-", " ").strip()
        return cleaned.split()[0].title()

    def get_user_greeting(self, username):
        hour = datetime.now().hour
        first_name = self.get_first_name(username)

        if 5 <= hour < 12:
            time_greeting = "Good morning"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
        elif 17 <= hour < 22:
            time_greeting = "Good evening"
        else:
            time_greeting = "Welcome back"

        return f"{time_greeting}, {first_name}"

    def create_stat_card(self, parent, title, value, subtext, color):
        card = tk.Frame(parent, bg="#111827", bd=0, relief="flat")
        tk.Frame(card, bg=color, height=5).pack(fill="x")
        tk.Label(
            card,
            text=title,
            bg="#111827",
            fg="#94a3b8",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 6))
        tk.Label(
            card,
            text=value,
            bg="#111827",
            fg="#f8fafc",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=18)
        tk.Label(
            card,
            text=subtext,
            bg="#111827",
            fg="#64748b",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=18, pady=(4, 16))
        return card

    # =========================
    # BEAUTIFUL HOME PAGE
    # =========================
    def show_home_page(self):
        self.clear_screen()

        self.home_frame = tk.Frame(self.root, bg="#08111f")
        self.home_frame.pack(fill="both", expand=True)
        self.current_frame = self.home_frame

        username = self.logged_in_user if self.logged_in_user else "User"
        greeting = self.get_user_greeting(username)
        first_name = self.get_first_name(username)

        top_bar = tk.Frame(self.home_frame, bg="#0b1628", height=82)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        brand_left = tk.Frame(top_bar, bg="#0b1628")
        brand_left.pack(side="left", padx=28)

        tk.Label(
            brand_left,
            text="JESUS_BOY CBT PORTAL",
            bg="#0b1628",
            fg="#38bdf8",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(14, 0))

        tk.Label(
            brand_left,
            text="Professional Exam Practice Dashboard",
            bg="#0b1628",
            fg="#94a3b8",
            font=("Segoe UI", 11)
        ).pack(anchor="w")

        user_right = tk.Frame(top_bar, bg="#0b1628")
        user_right.pack(side="right", padx=20, pady=16)

        tk.Label(
            user_right,
            text=f"Signed in as: {username}",
            bg="#0b1628",
            fg="#e2e8f0",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="e")

        tk.Label(
            user_right,
            text="Ready to practice and improve",
            bg="#0b1628",
            fg="#64748b",
            font=("Segoe UI", 10)
        ).pack(anchor="e")

        main = tk.Frame(self.home_frame, bg="#08111f")
        main.pack(fill="both", expand=True, padx=28, pady=22)

        hero = tk.Frame(main, bg="#0f1c32", height=185)
        hero.pack(fill="x", pady=(0, 18))
        hero.pack_propagate(False)

        hero_left = tk.Frame(hero, bg="#0f1c32")
        hero_left.pack(side="left", fill="both", expand=True, padx=28, pady=24)

        tk.Label(
            hero_left,
            text=greeting,
            bg="#0f1c32",
            fg="#38bdf8",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        tk.Label(
            hero_left,
            text=f"Welcome to your exam success hub, {first_name}.",
            bg="#0f1c32",
            fg="#f8fafc",
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w", pady=(8, 8))

        tk.Label(
            hero_left,
            text="Choose an exam board, select a year, and begin timed practice in a beautiful focused workspace.",
            bg="#0f1c32",
            fg="#94a3b8",
            wraplength=700,
            justify="left",
            font=("Segoe UI", 13)
        ).pack(anchor="w", pady=(0, 12))

        action_row = tk.Frame(hero_left, bg="#0f1c32")
        action_row.pack(anchor="w", pady=(8, 0))

        tk.Button(
            action_row,
            text="Open JAMB",
            bg="#38bdf8",
            fg="#0f172a",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=lambda: self.open_exam_main_page("JAMB")
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            action_row,
            text="Open WAEC",
            bg="#22c55e",
            fg="#0f172a",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=lambda: self.open_exam_main_page("WAEC")
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            action_row,
            text="Open NECO",
            bg="#f59e0b",
            fg="#0f172a",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=lambda: self.open_exam_main_page("NECO")
        ).pack(side="left")

        hero_right = tk.Frame(hero, bg="#13233f", width=280)
        hero_right.pack(side="right", fill="y", padx=24, pady=22)
        hero_right.pack_propagate(False)

        tk.Label(
            hero_right,
            text="Today Focus",
            bg="#13233f",
            fg="#f8fafc",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 8))

        tk.Label(
            hero_right,
            text="• Timed practice\n• Year-based revision\n• Professional dashboard\n• Simple, focused learning",
            bg="#13233f",
            fg="#cbd5e1",
            justify="left",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=18)

        stats_row = tk.Frame(main, bg="#08111f")
        stats_row.pack(fill="x", pady=(0, 18))

        self.create_stat_card(stats_row, "Exam Boards", "3", "JAMB, WAEC, NECO", "#38bdf8").pack(side="left", fill="x", expand=True, padx=8)
        self.create_stat_card(stats_row, "Practice Years", "7", "2019 to 2025 ready", "#22c55e").pack(side="left", fill="x", expand=True, padx=8)
        self.create_stat_card(stats_row, "Mode", "Timed", "Every practice page includes a timer", "#f59e0b").pack(side="left", fill="x", expand=True, padx=8)
        self.create_stat_card(stats_row, "Status", "Active", "You are signed in and ready", "#a855f7").pack(side="left", fill="x", expand=True, padx=8)

        section_title = tk.Frame(main, bg="#08111f")
        section_title.pack(fill="x", pady=(0, 10))

        tk.Label(
            section_title,
            text="Choose Your Exam Practice",
            bg="#08111f",
            fg="#f8fafc",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        tk.Label(
            section_title,
            text="Pick any exam board below and open a specific year for timed practice.",
            bg="#08111f",
            fg="#94a3b8",
            font=("Segoe UI", 12)
        ).pack(anchor="w", pady=(4, 0))

        cards_wrap = tk.Frame(main, bg="#08111f")
        cards_wrap.pack(fill="both", expand=True)

        self.make_exam_card(
            cards_wrap,
            "JAMB Practice",
            "Unified exam preparation with beautiful year access for mock and revision.",
            "#38bdf8",
            "JAMB"
        ).pack(side="left", fill="both", expand=True, padx=10)

        self.make_exam_card(
            cards_wrap,
            "WAEC Practice",
            "Senior secondary exam practice with organized yearly questions and timed sessions.",
            "#22c55e",
            "WAEC"
        ).pack(side="left", fill="both", expand=True, padx=10)

        self.make_exam_card(
            cards_wrap,
            "NECO Practice",
            "National exam revision with fast access, clean layout and timed practice.",
            "#f59e0b",
            "NECO"
        ).pack(side="left", fill="both", expand=True, padx=10)

        bottom_bar = tk.Frame(self.home_frame, bg="#0b1628", height=65)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)

        tk.Button(
            bottom_bar,
            text="Log Out",
            bg="#ef4444",
            fg="#f8fafc",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=self.show_auth_page
        ).pack(side="left", padx=18, pady=12)

        tk.Button(
            bottom_bar,
            text="Exit Full Screen",
            bg="#334155",
            fg="#f8fafc",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=lambda: self.root.attributes("-fullscreen", False)
        ).pack(side="right", padx=18, pady=12)

    def make_exam_card(self, parent, title, description, accent_color, exam_name):
        card = tk.Frame(parent, bg="#111827", bd=0, relief="flat")

        top = tk.Frame(card, bg="#111827")
        top.pack(fill="x", padx=22, pady=(22, 10))

        tk.Label(
            top,
            text=title,
            bg="#111827",
            fg="#f8fafc",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        tk.Frame(card, bg=accent_color, height=5).pack(fill="x", padx=22, pady=(0, 16))

        tk.Label(
            card,
            text=description,
            bg="#111827",
            fg="#94a3b8",
            justify="left",
            wraplength=320,
            font=("Segoe UI", 12)
        ).pack(anchor="w", padx=22, pady=(0, 18))

        tk.Label(
            card,
            text="Available Years",
            bg="#111827",
            fg="#cbd5e1",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 12))

        years_frame = tk.Frame(card, bg="#111827")
        years_frame.pack(fill="x", padx=22)

        years = ["2025", "2024", "2023", "2022", "2021"]
        for i, year in enumerate(years):
            btn = tk.Button(
                years_frame,
                text=year,
                bg="#1e293b",
                fg="#f8fafc",
                activebackground=accent_color,
                activeforeground="#0f172a",
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                bd=0,
                padx=14,
                pady=10,
                cursor="hand2",
                command=lambda e=exam_name, y=year: self.open_exam_year_page(e, y)
            )
            btn.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="ew")

        years_frame.grid_columnconfigure(0, weight=1)
        years_frame.grid_columnconfigure(1, weight=1)

        tk.Button(
            card,
            text=f"Open {exam_name} Dashboard",
            bg=accent_color,
            fg="#0f172a",
            activebackground=accent_color,
            activeforeground="#0f172a",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            bd=0,
            padx=16,
            pady=13,
            cursor="hand2",
            command=lambda e=exam_name: self.open_exam_main_page(e)
        ).pack(fill="x", padx=22, pady=(22, 24))

        return card

    # =========================
    # EXAM DASHBOARD
    # =========================
    def open_exam_main_page(self, exam_name):
        self.clear_screen()

        page = tk.Frame(self.root, bg="#08111f")
        page.pack(fill="both", expand=True)
        self.current_frame = page

        top = tk.Frame(page, bg="#0b1628", height=80)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(
            top,
            text=f"{exam_name} Practice Dashboard",
            bg="#0b1628",
            fg="#f8fafc",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left", padx=28, pady=18)

        tk.Button(
            top,
            text="Back to Home",
            bg="#38bdf8",
            fg="#0f172a",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=self.show_home_page
        ).pack(side="right", padx=20, pady=16)

        main = tk.Frame(page, bg="#08111f")
        main.pack(fill="both", expand=True, padx=28, pady=24)

        hero = tk.Frame(main, bg="#0f1c32", height=140)
        hero.pack(fill="x", pady=(0, 20))
        hero.pack_propagate(False)

        tk.Label(
            hero,
            text=f"Choose a year for {exam_name}",
            bg="#0f1c32",
            fg="#f8fafc",
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w", padx=26, pady=(28, 6))

        tk.Label(
            hero,
            text=f"Every {exam_name} practice page includes a running timer so you can build exam speed and discipline.",
            bg="#0f1c32",
            fg="#94a3b8",
            font=("Segoe UI", 13)
        ).pack(anchor="w", padx=26)

        year_wrap = tk.Frame(main, bg="#08111f")
        year_wrap.pack(pady=10)

        years = ["2025", "2024", "2023", "2022", "2021", "2020", "2019"]
        for index, year in enumerate(years):
            btn = tk.Button(
                year_wrap,
                text=year,
                bg="#111827",
                fg="#f8fafc",
                activebackground="#38bdf8",
                activeforeground="#0f172a",
                font=("Segoe UI", 14, "bold"),
                relief="flat",
                bd=0,
                padx=34,
                pady=22,
                width=14,
                cursor="hand2",
                command=lambda e=exam_name, y=year: self.open_exam_year_page(e, y)
            )
            btn.grid(row=index // 3, column=index % 3, padx=14, pady=14)

    # =========================
    # PRACTICE TIMER
    # =========================
    def format_time(self, total_seconds):
        mins = total_seconds // 60
        secs = total_seconds % 60
        hours = mins // 60
        mins = mins % 60
        return f"{hours:02d}:{mins:02d}:{secs:02d}"

    def start_practice_timer(self):
        self.practice_timer_running = True
        self.update_practice_timer()

    def update_practice_timer(self):
        if not self.practice_timer_running:
            return

        self.practice_timer_seconds += 1

        if hasattr(self, "practice_timer_label") and self.practice_timer_label.winfo_exists():
            self.practice_timer_label.config(
                text=self.format_time(self.practice_timer_seconds)
            )

        self.practice_timer_job = self.root.after(1000, self.update_practice_timer)

    def reset_practice_timer(self):
        self.practice_timer_seconds = 0
        if hasattr(self, "practice_timer_label") and self.practice_timer_label.winfo_exists():
            self.practice_timer_label.config(text="00:00:00")

    # =========================
    # EXAM YEAR PAGE
    # =========================
    def open_exam_year_page(self, exam_name, year):
        self.clear_screen()

        self.current_exam_name = exam_name
        self.current_exam_year = year

        page = tk.Frame(self.root, bg="#08111f")
        page.pack(fill="both", expand=True)
        self.current_frame = page

        top = tk.Frame(page, bg="#0b1628", height=84)
        top.pack(fill="x")
        top.pack_propagate(False)

        left_top = tk.Frame(top, bg="#0b1628")
        left_top.pack(side="left", padx=24, pady=12)

        tk.Label(
            left_top,
            text=f"{exam_name} {year}",
            bg="#0b1628",
            fg="#f8fafc",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        tk.Label(
            left_top,
            text="Timed practice workspace",
            bg="#0b1628",
            fg="#94a3b8",
            font=("Segoe UI", 11)
        ).pack(anchor="w")

        timer_box = tk.Frame(top, bg="#13233f", padx=18, pady=10)
        timer_box.pack(side="right", padx=20, pady=14)

        tk.Label(
            timer_box,
            text="Practice Timer",
            bg="#13233f",
            fg="#94a3b8",
            font=("Segoe UI", 10, "bold")
        ).pack()

        self.practice_timer_label = tk.Label(
            timer_box,
            text="00:00:00",
            bg="#13233f",
            fg="#22c55e",
            font=("Consolas", 20, "bold")
        )
        self.practice_timer_label.pack()

        main = tk.Frame(page, bg="#08111f")
        main.pack(fill="both", expand=True, padx=28, pady=22)

        intro = tk.Frame(main, bg="#0f1c32", height=120)
        intro.pack(fill="x", pady=(0, 18))
        intro.pack_propagate(False)

        tk.Label(
            intro,
            text=f"{exam_name} {year} Practice Center",
            bg="#0f1c32",
            fg="#f8fafc",
            font=("Segoe UI", 26, "bold")
        ).pack(anchor="w", padx=24, pady=(24, 6))

        tk.Label(
            intro,
            text="Select a section below to begin timed objective, theory, study notes or mock practice.",
            bg="#0f1c32",
            fg="#94a3b8",
            font=("Segoe UI", 12)
        ).pack(anchor="w", padx=24)

        panel = tk.Frame(main, bg="#08111f")
        panel.pack(fill="both", expand=True)

        items = [
            (f"{exam_name} {year} Objective Questions", "#38bdf8"),
            (f"{exam_name} {year} Theory Questions", "#22c55e"),
            (f"{exam_name} {year} Study Notes", "#f59e0b"),
            (f"{exam_name} {year} Timed Mock Practice", "#a855f7")
        ]

        for item, color in items:
            row = tk.Frame(panel, bg="#111827", height=82)
            row.pack(fill="x", pady=8)
            row.pack_propagate(False)

            color_bar = tk.Frame(row, bg=color, width=7)
            color_bar.pack(side="left", fill="y")

            content = tk.Frame(row, bg="#111827")
            content.pack(side="left", fill="both", expand=True, padx=18, pady=14)

            tk.Label(
                content,
                text=item,
                bg="#111827",
                fg="#f8fafc",
                font=("Segoe UI", 14, "bold")
            ).pack(anchor="w")

            tk.Label(
                content,
                text="Open this practice section and continue with the running timer.",
                bg="#111827",
                fg="#94a3b8",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(4, 0))

            tk.Button(
                row,
                text="Open",
                bg=color,
                fg="#0f172a",
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                bd=0,
                padx=18,
                pady=10,
                cursor="hand2",
                command=lambda n=item: self.open_placeholder(n)
            ).pack(side="right", padx=18)

        btn_wrap = tk.Frame(main, bg="#08111f")
        btn_wrap.pack(fill="x", pady=(12, 0))

        tk.Button(
            btn_wrap,
            text="Reset Timer",
            bg="#f59e0b",
            fg="#0f172a",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=11,
            cursor="hand2",
            command=self.reset_practice_timer
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_wrap,
            text="Back to Home",
            bg="#38bdf8",
            fg="#0f172a",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=11,
            cursor="hand2",
            command=self.show_home_page
        ).pack(side="left", padx=8)

        tk.Button(
            btn_wrap,
            text=f"Back to {exam_name}",
            bg="#334155",
            fg="#f8fafc",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=11,
            cursor="hand2",
            command=lambda e=exam_name: self.open_exam_main_page(e)
        ).pack(side="left", padx=8)

        self.reset_practice_timer()
        self.start_practice_timer()

    def open_placeholder(self, title):
        messagebox.showinfo("Coming Next", f"{title} page will open here when you connect your question database.")


root = tk.Tk()
app = CBTStudyApp(root)
root.mainloop()