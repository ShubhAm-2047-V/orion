import tkinter as tk
from tkinter import ttk
import math
import time
import threading
import queue
import sys
import os

class JarvisUIState:
    def __init__(self):
        self.state = "idle"          # "idle", "listening", "processing", "speaking"
        self.status_text = "System Online"
        self.spoken_text = ""
        self.voice_active = True
        self.speech_muted = False
        self.logs_queue = queue.Queue()
        self.gui_instance = None

    def set_state(self, state, status_text=None):
        self.state = state
        if status_text:
            self.status_text = status_text
        elif state == "idle":
            self.status_text = "System Online"
        elif state == "listening":
            self.status_text = "Listening..."
        elif state == "processing":
            self.status_text = "Processing..."
        elif state == "speaking":
            self.status_text = "Speaking..."

    def log(self, text):
        self.logs_queue.put(text)

# Global UI state instance
ui_state = JarvisUIState()

class RedirectText:
    def __init__(self, ui_state_obj):
        self.ui_state = ui_state_obj
        self.original_stdout = sys.stdout

    def write(self, string):
        try:
            self.original_stdout.write(string)
        except Exception:
            pass
        if string.strip():
            self.ui_state.log(string)

    def flush(self):
        try:
            self.original_stdout.flush()
        except Exception:
            pass

def blend_colors(color1, color2, factor):
    # Interpolate between hex colors
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        
    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
        
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    blended = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * factor) for i in range(3))
    return rgb_to_hex(blended)

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        ui_state.gui_instance = self
        
        # Window settings
        self.root.title("Jarvis Assistant")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Geometry constants
        self.width = 240
        self.base_height = 280
        self.height = self.base_height
        
        # Set high-tech premium background colors
        self.bg_color = "#080b11"       # Deep Obsidian Black
        self.fg_color = "#00f0ff"       # Electric Neon Cyan
        self.accent_color = "#121b2d"   # Cool slate glass tile
        self.text_color = "#e2e8f0"
        
        self.root.configure(bg=self.bg_color)
        
        # Glowing container frame with 1px border
        self.main_container = tk.Frame(
            self.root,
            bg=self.bg_color,
            highlightbackground=self.fg_color,
            highlightthickness=1
        )
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Screen position (bottom right corner)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - self.width - 40
        self.y = screen_height - self.height - 80
        self.root.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        
        # Interactive features
        self.drag_data = {"x": 0, "y": 0}
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.drag)
        self.root.bind("<Button-3>", self.show_context_menu) # Right-click context menu
        
        # Futuristic visual nodes list: (angle in radians, orbit speed, radius, size)
        self.nodes = [
            {"angle": 0.0, "speed": 0.02, "radius": 42, "size": 3},
            {"angle": 1.57, "speed": -0.03, "radius": 52, "size": 3},
            {"angle": 3.14, "speed": 0.015, "radius": 62, "size": 2},
            {"angle": 4.71, "speed": -0.025, "radius": 48, "size": 3}
        ]
        
        # Create UI structures
        self.setup_canvas()
        self.setup_labels()
        self.setup_controls()
        self.setup_log_pane()
        self.setup_input_box()
        self.setup_context_menu()
        
        # Animation states
        self.angle_outer = 0
        self.angle_inner = 0
        self.pulse_phase = 0
        self.topmost_counter = 0
        
        # Redirect stdout
        self.redirector = RedirectText(ui_state)
        sys.stdout = self.redirector
        
        # Apply rounded window corners
        self.apply_rounded_corners()
        
        # Run animator
        self.animate()

    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drag(self, event):
        deltax = event.x - self.drag_data["x"]
        deltay = event.y - self.drag_data["y"]
        self.x += deltax
        self.y += deltay
        self.root.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def setup_canvas(self):
        self.canvas_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.canvas_frame.pack(fill=tk.BOTH, expand=False, pady=(15, 0))
        
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            width=200, 
            height=160, 
            bg=self.bg_color, 
            highlightthickness=0
        )
        self.canvas.pack()

    def setup_labels(self):
        self.status_label = tk.Label(
            self.main_container,
            text="System Online",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.status_label.pack(fill=tk.X, pady=(2, 0))

        self.speech_label = tk.Label(
            self.main_container,
            text="Hello, sir. Say 'Jarvis' or click keyboard.",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg="#64748b",
            wraplength=220,
            justify=tk.CENTER
        )
        self.speech_label.pack(fill=tk.X, padx=15, pady=(2, 8))

    def setup_controls(self):
        # Controls Dock (glowing floating bar)
        self.controls_dock = tk.Frame(
            self.main_container,
            bg=self.accent_color,
            highlightbackground="#1e293b",
            highlightthickness=1,
            bd=0
        )
        self.controls_dock.pack(fill=tk.X, padx=20, pady=(0, 15))

        # Keyboard Icon
        self.btn_keyboard = tk.Button(
            self.controls_dock,
            text="⌨",
            font=("Segoe UI", 12),
            bg=self.accent_color,
            fg=self.fg_color,
            activebackground="#1e2e4a",
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.toggle_input_box
        )
        self.btn_keyboard.pack(side=tk.LEFT, expand=True, padx=2, ipadx=4, ipady=2)
        self.btn_keyboard.bind("<Enter>", lambda e: self.btn_keyboard.configure(bg="#1e2e4a", fg="#ffffff"))
        self.btn_keyboard.bind("<Leave>", lambda e: self.btn_keyboard.configure(bg=self.accent_color, fg=self.fg_color))

        # Voice Toggle
        self.btn_voice = tk.Button(
            self.controls_dock,
            text="🎤",
            font=("Segoe UI", 11),
            bg=self.accent_color,
            fg="#10b981",
            activebackground="#1e2e4a",
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.toggle_voice_mute
        )
        self.btn_voice.pack(side=tk.LEFT, expand=True, padx=2, ipadx=4, ipady=2)
        self.btn_voice.bind("<Enter>", lambda e: self.btn_voice.configure(bg="#1e2e4a", fg="#34d399") if ui_state.voice_active else self.btn_voice.configure(bg="#ef4444", fg="#ffffff"))
        self.btn_voice.bind("<Leave>", lambda e: self.btn_voice.configure(bg=self.accent_color, fg="#10b981") if ui_state.voice_active else self.btn_voice.configure(bg="#3b151a", fg="#f87171"))

        # Speaker Toggle
        self.btn_speaker = tk.Button(
            self.controls_dock,
            text="🔊",
            font=("Segoe UI", 11),
            bg=self.accent_color,
            fg="#a855f7",
            activebackground="#1e2e4a",
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.toggle_speaker_mute
        )
        self.btn_speaker.pack(side=tk.LEFT, expand=True, padx=2, ipadx=4, ipady=2)
        self.btn_speaker.bind("<Enter>", lambda e: self.btn_speaker.configure(bg="#1e2e4a", fg="#c084fc") if not ui_state.speech_muted else self.btn_speaker.configure(bg="#ef4444", fg="#ffffff"))
        self.btn_speaker.bind("<Leave>", lambda e: self.btn_speaker.configure(bg=self.accent_color, fg="#a855f7") if not ui_state.speech_muted else self.btn_speaker.configure(bg="#3b151a", fg="#f87171"))

        # Close Application
        self.btn_close = tk.Button(
            self.controls_dock,
            text="❌",
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg="#f87171",
            activebackground="#ef4444",
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.exit_app
        )
        self.btn_close.pack(side=tk.LEFT, expand=True, padx=2, ipadx=4, ipady=2)
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.configure(bg="#ef4444", fg="#ffffff"))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.configure(bg=self.accent_color, fg="#f87171"))

    def setup_log_pane(self):
        self.log_visible = False
        self.log_frame = tk.Frame(self.main_container, bg="#020617")
        
        self.log_text = tk.Text(
            self.log_frame,
            font=("Consolas", 8),
            bg="#020617",
            fg="#38bdf8",
            insertbackground="#38bdf8",
            relief="flat",
            highlightthickness=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)

    def setup_input_box(self):
        self.input_visible = False
        self.input_frame = tk.Frame(self.main_container, bg=self.bg_color)
        
        self.cmd_entry = tk.Entry(
            self.input_frame,
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg=self.text_color,
            insertbackground=self.fg_color,
            relief="flat",
            highlightthickness=1,
            highlightcolor=self.fg_color,
            highlightbackground="#1e293b"
        )
        self.cmd_entry.pack(fill=tk.X, padx=15, pady=(2, 10))
        self.cmd_entry.bind("<Return>", self.submit_typed_command)

    def setup_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0, bg=self.accent_color, fg=self.text_color, activebackground=self.fg_color, activeforeground=self.bg_color)
        self.menu.add_command(label="⌨ Type Command", command=self.toggle_input_box)
        self.menu.add_command(label="💬 Toggle Log Terminal", command=self.toggle_log_pane)
        self.menu.add_command(label="🎤 Toggle Listening", command=self.toggle_voice_mute)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Exit Jarvis", command=self.exit_app)

    def show_context_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def toggle_input_box(self):
        if self.input_visible:
            self.input_frame.pack_forget()
            self.input_visible = False
            self.adjust_window_size()
        else:
            self.input_frame.pack(fill=tk.X, after=self.speech_label)
            self.input_visible = True
            self.cmd_entry.focus_set()
            self.adjust_window_size()

    def toggle_log_pane(self):
        if self.log_visible:
            self.log_frame.pack_forget()
            self.log_visible = False
            self.adjust_window_size()
        else:
            self.log_frame.pack(fill=tk.BOTH, expand=True)
            self.log_visible = True
            self.adjust_window_size()

    def toggle_voice_mute(self):
        ui_state.voice_active = not ui_state.voice_active
        if ui_state.voice_active:
            self.btn_voice.configure(bg=self.accent_color, fg="#10b981", text="🎤")
            ui_state.set_state("idle", "System Online")
            ui_state.log("[GUI]: Voice listening activated.")
        else:
            self.btn_voice.configure(bg="#3b151a", fg="#f87171", text="🔇")
            ui_state.set_state("idle", "Voice Listening Muted")
            ui_state.log("[GUI]: Voice listening deactivated.")

    def toggle_speaker_mute(self):
        ui_state.speech_muted = not ui_state.speech_muted
        if not ui_state.speech_muted:
            self.btn_speaker.configure(bg=self.accent_color, fg="#a855f7", text="🔊")
            ui_state.log("[GUI]: Jarvis speaking voice activated.")
        else:
            self.btn_speaker.configure(bg="#3b151a", fg="#f87171", text="🔈")
            ui_state.log("[GUI]: Jarvis speaking voice muted.")

    def ensure_topmost(self):
        try:
            self.root.attributes("-topmost", True)
            self.root.lift()
        except Exception:
            pass

    def show_and_focus(self):
        try:
            self.root.deiconify()
            self.ensure_topmost()
            self.root.focus_force()
        except Exception:
            pass

    def adjust_window_size(self):
        old_height = self.height
        h = self.base_height
        if self.input_visible:
            h += 35
        if self.log_visible:
            h += 180
            
        self.height = h
        self.y = (self.y + old_height) - self.height
        self.root.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        self.apply_rounded_corners()

    def apply_rounded_corners(self):
        try:
            import ctypes
            hwnd = self.root.winfo_id()
            rgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, self.width, self.height, 24, 24)
            ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)
        except Exception:
            pass

    def submit_typed_command(self, event=None):
        cmd = self.cmd_entry.get().strip()
        if cmd:
            self.cmd_entry.delete(0, tk.END)
            ui_state.log(f"\n[USER] (Console): {cmd}")
            
            from main import parse_and_execute
            ui_state.set_state("processing", "Processing typed command...")
            
            def run():
                try:
                    parse_and_execute(cmd)
                except Exception as e:
                    ui_state.log(f"[ERROR]: Command failed: {e}")
                finally:
                    if ui_state.state == "processing":
                        ui_state.set_state("idle")
            
            threading.Thread(target=run, daemon=True).start()
            self.toggle_input_box()

    def exit_app(self):
        ui_state.log("[SYSTEM]: Initiating system shutdown sequence...")
        try:
            self.root.destroy()
        except Exception:
            pass
        import os
        os._exit(0)

    def update_logs(self):
        while not ui_state.logs_queue.empty():
            try:
                line = ui_state.logs_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, line)
                
                num_lines = self.log_text.index('end-1c').split('.')[0]
                if int(num_lines) > 500:
                    self.log_text.delete('1.0', '100.0')
                    
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
            except queue.Empty:
                break

    def animate(self):
        self.canvas.delete("all")
        
        state = ui_state.state
        
        # Color definitions based on state
        if state == "listening":
            color = "#10b981"       # Emerald Green
            glow_color = "#042f2e"
            node_color = "#34d399"
            conn_color = "#065f46"
            speed_mult = 2.0
            core_min, core_max = 24, 30
        elif state == "processing":
            color = "#f59e0b"       # Amber Gold
            glow_color = "#451a03"
            node_color = "#fbbf24"
            conn_color = "#78350f"
            speed_mult = 3.5
            core_min, core_max = 20, 24
        elif state == "speaking":
            color = "#a855f7"       # Vibrant Purple
            glow_color = "#3b0764"
            node_color = "#c084fc"
            conn_color = "#581c87"
            speed_mult = 1.5
            core_min, core_max = 25, 32
        else: # Idle
            if ui_state.voice_active:
                color = "#00f0ff"   # Electric Neon Cyan
                glow_color = "#082f49"
                node_color = "#38bdf8"
                conn_color = "#0369a1"
            else:
                color = "#64748b"   # Slate Grey
                glow_color = "#1e293b"
                node_color = "#94a3b8"
                conn_color = "#334155"
            speed_mult = 1.0
            core_min, core_max = 22, 26
            
        # Update container outline dynamically (glowing window border)
        self.main_container.configure(highlightbackground=color)
        
        # Update pulse parameters
        self.pulse_phase += 0.08 if state != "speaking" else 0.15
        pulse = (math.sin(self.pulse_phase) + 1.0) / 2.0
        core_r = core_min + pulse * (core_max - core_min)
        
        center_x, center_y = 100, 80
        
        # 1. Draw volumetric radial core glow (concentric circles fading outward)
        for i in range(8, 0, -1):
            r = core_r + i * 4
            factor = (9 - i) / 9.0
            blend = blend_colors(glow_color, color, factor)
            self.canvas.create_oval(
                center_x - r, center_y - r,
                center_x + r, center_y + r,
                fill=blend, outline=""
            )
            
        # 2. Draw connections (webs) and particles
        coords = []
        for node in self.nodes:
            node["angle"] = (node["angle"] + node["speed"] * speed_mult) % (2 * math.pi)
            nx = center_x + node["radius"] * math.cos(node["angle"])
            ny = center_y + node["radius"] * math.sin(node["angle"])
            coords.append((nx, ny))
            
            # Draw dash vector to core
            self.canvas.create_line(
                center_x, center_y, nx, ny,
                fill=conn_color, width=1, dash=(4, 4) if state == "idle" else None
            )
            
        # Draw node-to-node orbital webs
        num_nodes = len(coords)
        for i in range(num_nodes):
            x1, y1 = coords[i]
            x2, y2 = coords[(i + 1) % num_nodes]
            self.canvas.create_line(x1, y1, x2, y2, fill=conn_color, width=1)
            
        # Draw orbital node particles
        for i, (nx, ny) in enumerate(coords):
            size = self.nodes[i]["size"]
            self.canvas.create_oval(
                nx - size, ny - size,
                nx + size, ny + size,
                fill=node_color, outline=color, width=1
            )
            
        # 3. State-specific animations
        if state == "listening":
            # Emerald green expanding radar ripples
            ripple_r = core_r + 20 + (self.pulse_phase * 6 % 30)
            self.canvas.create_oval(
                center_x - ripple_r, center_y - ripple_r,
                center_x + ripple_r, center_y + ripple_r,
                outline="#34d399", width=1
            )
        elif state == "processing":
            # Gyroscopic HUD loader
            hud_r = core_r + 25
            self.canvas.create_arc(
                center_x - hud_r, center_y - hud_r,
                center_x + hud_r, center_y + hud_r,
                start=(time.time() * 200) % 360, extent=60,
                style=tk.ARC, outline=color, width=2
            )
            self.canvas.create_arc(
                center_x - hud_r, center_y - hud_r,
                center_x + hud_r, center_y + hud_r,
                start=((time.time() * 200) + 180) % 360, extent=60,
                style=tk.ARC, outline=color, width=2
            )
        elif state == "speaking":
            # Dual smooth flowing audio spectrum waves (Siri style)
            wave_points1 = []
            for x in range(15, 185, 5):
                y = center_y + math.sin((x / 25.0) + self.pulse_phase * 2.0) * 15 * pulse
                wave_points1.extend([x, y])
            self.canvas.create_line(wave_points1, smooth=True, fill="#c084fc", width=2)
            
            wave_points2 = []
            for x in range(15, 185, 5):
                y = center_y + math.cos((x / 20.0) - self.pulse_phase * 1.5) * 10 * pulse
                wave_points2.extend([x, y])
            self.canvas.create_line(wave_points2, smooth=True, fill="#22d3ee", width=1.5)

        # Sync labels
        self.status_label.configure(text=ui_state.status_text, fg=color)
        
        # Sync subtext speech log
        if ui_state.spoken_text:
            text_disp = ui_state.spoken_text
            if len(text_disp) > 75:
                text_disp = text_disp[:72] + "..."
            self.speech_label.configure(text=text_disp)
            
        self.update_logs()
        
        # Periodically ensure topmost state (counter-based to avoid overhead)
        self.topmost_counter += 1
        if self.topmost_counter >= 10: # every 400ms
            self.topmost_counter = 0
            self.ensure_topmost()
                
        # Loop animation (approx 25 fps)
        self.root.after(40, self.animate)

def start_gui():
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()
