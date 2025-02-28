import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, font
import customtkinter as ctk
import threading
import json
import requests
import bs4
import lxml
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import urllib3
import os
import time
from datetime import datetime
import locale
import base64
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw, ImageFont
import webbrowser

# Set appearance mode and default color theme
ctk.set_appearance_mode("system")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Modern theme and icon assets
class ThemeAndIcons:
    """Class to manage themes, icons, and UI assets"""
    
    # Modern color theme with updated palette
    THEME = {
        'primary': '#3b82f6',      # Bright blue - primary brand color
        'primary_hover': '#2563eb', # Darker blue for hover states
        'secondary': '#10b981',    # Emerald green - secondary color
        'secondary_hover': '#059669', # Darker green for hover states
        'accent': '#f43f5e',       # Rose - for warnings/important actions
        'accent_hover': '#e11d48', # Darker rose for hover states
        'dark': '#1e293b',         # Slate dark - for headers
        'light': '#f8fafc',        # Slate light - for backgrounds
        'text_dark': '#0f172a',    # Dark text
        'text_light': '#f1f5f9',   # Light text
        'warning': '#fbbf24',      # Amber - for warnings
        'success': '#22c55e',      # Green - for success
        'error': '#ef4444',        # Red - for errors
        'info': '#06b6d4',         # Cyan - for info
        'border': '#cbd5e1',       # Border color
        'hover': '#e2e8f0',        # Hover color
        'disabled': '#94a3b8',     # Disabled color
        'card': '#ffffff',         # Card background
        'card_dark': '#1e293b',    # Card background in dark mode
        'shadow': 'rgba(0,0,0,0.1)'# Shadow color
    }
    
    # Modern button styles
    BUTTON_STYLES = {
        'primary': {
            'fg_color': THEME['primary'],
            'hover_color': THEME['primary_hover'],
            'text_color': THEME['text_light'],
            'corner_radius': 8
        },
        'secondary': {
            'fg_color': THEME['secondary'],
            'hover_color': THEME['secondary_hover'],
            'text_color': THEME['text_light'],
            'corner_radius': 8
        },
        'danger': {
            'fg_color': THEME['error'],
            'hover_color': THEME['accent_hover'],
            'text_color': THEME['text_light'],
            'corner_radius': 8
        },
        'outline': {
            'fg_color': 'transparent',
            'hover_color': THEME['hover'],
            'text_color': THEME['primary'],
            'corner_radius': 8,
            'border_color': THEME['primary'],
            'border_width': 1
        }
    }
    
    # Modern input styles
    INPUT_STYLES = {
        'corner_radius': 6,
        'border_width': 1,
        'fg_color': THEME['light'],
        'border_color': THEME['border'],
        'text_color': THEME['text_dark']
    }
    
    # Animation durations
    ANIMATIONS = {
        'short': 150,  # ms
        'medium': 300, # ms
        'long': 500    # ms
    }
    
    @staticmethod
    def get_text_color():
        """Return the appropriate text color based on the current theme"""
        current_mode = ctk.get_appearance_mode()
        return ThemeAndIcons.THEME['text_light'] if current_mode == "Dark" else ThemeAndIcons.THEME['text_dark']
    
    @staticmethod
    def get_label_text_color():
        """Return the appropriate label text color based on the current theme"""
        current_mode = ctk.get_appearance_mode()
        return ThemeAndIcons.THEME['text_light'] if current_mode == "Dark" else ThemeAndIcons.THEME['dark']
    
    @staticmethod
    def get_icon(icon_name, size=(20, 20)):
        """Load an icon from the icons directory and return a PhotoImage object"""
        # Just return None to use text-based fallback icons
        # This will trigger the text fallback in the calling code
        return None
    
    @staticmethod
    def create_text_icon(icon_name, size=(20, 20)):
        """Create a simple text-based icon as a fallback"""
        # This is a simplified version that doesn't create an actual icon
        # It just returns None, and the caller should handle this by using text
        return None

    @staticmethod
    def get_icon_text(icon_name):
        """Return a text representation of an icon as fallback"""
        icon_map = {
            'logo': "🔗",
            'browse': "📂",
            'load': "📥",
            'start': "▶️",
            'pause': "⏸️",
            'stop': "⏹️",
            'save': "💾",
            'reset': "🔄",
            'export': "📤",
            'globe': "🌐",
            'flag_en': "🇬🇧",
            'flag_tr': "🇹🇷"
        }
        return icon_map.get(icon_name, "📌")

    @staticmethod
    def apply_theme_to_widget(widget, widget_type='frame'):
        """Apply theme styles to a widget based on its type"""
        current_mode = ctk.get_appearance_mode()
        is_dark_mode = current_mode == "Dark"
        
        if widget_type == 'frame':
            widget.configure(fg_color=ThemeAndIcons.THEME['card_dark'] if is_dark_mode else ThemeAndIcons.THEME['card'])
        elif widget_type == 'button_primary':
            widget.configure(**ThemeAndIcons.BUTTON_STYLES['primary'])
        elif widget_type == 'button_secondary':
            widget.configure(**ThemeAndIcons.BUTTON_STYLES['secondary'])
        elif widget_type == 'button_danger':
            widget.configure(**ThemeAndIcons.BUTTON_STYLES['danger'])
        elif widget_type == 'button_outline':
            widget.configure(**ThemeAndIcons.BUTTON_STYLES['outline'])
        elif widget_type == 'input':
            if is_dark_mode:
                widget.configure(
                    corner_radius=ThemeAndIcons.INPUT_STYLES['corner_radius'],
                    border_width=ThemeAndIcons.INPUT_STYLES['border_width'],
                    fg_color=ThemeAndIcons.THEME['dark'],
                    border_color=ThemeAndIcons.THEME['border'],
                    text_color=ThemeAndIcons.THEME['text_light']
                )
            else:
                widget.configure(**ThemeAndIcons.INPUT_STYLES)
            
    @staticmethod
    def create_rounded_frame(parent, **kwargs):
        """Create a frame with rounded corners using a canvas"""
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 10
            
        return ctk.CTkFrame(parent, **kwargs)

class BacklinkBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WordPress Backlink Pro")
        self.root.geometry("1280x800")
        self.root.minsize(1280, 800)
        
        # Initialize variables first
        self.setup_variables()
        
        # Initialize status variables
        self.time_text = ctk.StringVar(value="")
        self.status_text = ctk.StringVar(value="Ready")
        
        # Configure the main container with padding
        self.container = ThemeAndIcons.create_rounded_frame(self.root, fg_color="transparent")
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create status bar first
        self.create_status_bar()
        
        # Create modern tabview with larger tabs
        self.tabview = ctk.CTkTabview(self.container, corner_radius=10)
        self.tabview.pack(fill=tk.BOTH, expand=True)
        
        # Configure tab font and size
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            height=40
        )
        
        # Add tabs
        self.main_tab = self.tabview.add("Main")
        self.settings_tab = self.tabview.add("Settings")
        self.stats_tab = self.tabview.add("Statistics")
        
        # Language selector
        self.lang_var = ctk.StringVar(value="en")
        
        # Initialize translations
        self.translations = {
            "en": {
                "main_tab": "Main",
                "settings_tab": "Settings",
                "links_file": "Links File",
                "browse": "Browse",
                "load": "Load",
                "start": "Start",
                "pause": "Pause",
                "stop": "Stop",
                "progress": "Progress",
                "current_link": "Current Link",
                "log": "Activity Log",
                "ready": "Ready",
                "comment_settings": "Comment Settings",
                "author": "Author",
                "email": "Email",
                "url": "URL",
                "comment": "Comment",
                "success_file": "Success File",
                "timing_settings": "Timing Settings",
                "delay": "Delay between requests (seconds)",
                "save_settings": "Save Settings",
                "load_settings": "Load Settings",
                "reset_default": "Reset to Default",
                "stats": "Statistics",
                "about": "About"
            },
            "tr": {
                "main_tab": "Ana Sayfa",
                "settings_tab": "Ayarlar",
                "links_file": "Bağlantı Dosyası",
                "browse": "Gözat",
                "load": "Yükle",
                "start": "Başlat",
                "pause": "Duraklat",
                "stop": "Durdur",
                "progress": "İlerleme",
                "current_link": "Mevcut Bağlantı",
                "log": "Etkinlik Günlüğü",
                "ready": "Hazır",
                "comment_settings": "Yorum Ayarları",
                "author": "Yazar",
                "email": "E-posta",
                "url": "URL",
                "comment": "Yorum",
                "success_file": "Başarılı Dosyası",
                "timing_settings": "Zamanlama Ayarları",
                "delay": "İstekler arası gecikme (saniye)",
                "save_settings": "Ayarları Kaydet",
                "load_settings": "Ayarları Yükle",
                "reset_default": "Varsayılana Sıfırla",
                "stats": "İstatistikler",
                "about": "Hakkında"
            }
        }
        
        # Create language selector
        self.create_language_selector()
        
        # Initialize UI
        self.create_widgets()
        self.load_config()
        
        # Configure dark/light mode switch
        self.theme_switch = ctk.CTkSwitch(
            self.container, 
            text="Dark Mode",
            command=self.toggle_theme,
            progress_color=ThemeAndIcons.THEME['primary'],
            button_color=ThemeAndIcons.THEME['primary'],
            button_hover_color=ThemeAndIcons.THEME['primary_hover']
        )
        self.theme_switch.pack(side=tk.RIGHT, padx=10)
        
        # Add app version
        version_label = ctk.CTkLabel(
            self.container, 
            text="v1.0.0",
            font=ctk.CTkFont(family="Helvetica", size=10),
            text_color=ThemeAndIcons.THEME['disabled']
        )
        version_label.pack(side=tk.RIGHT, padx=10)
        
        # Select the main tab by default
        self.tabview.set("Main")

    def get_text(self, key):
        """Get translated text for the current language"""
        return self.translations.get(self.lang_var.get(), {}).get(key, key)

    def create_language_selector(self):
        """Create modern language selector buttons with flags"""
        lang_frame = ThemeAndIcons.create_rounded_frame(self.container, fg_color="transparent")
        lang_frame.pack(side=tk.LEFT, padx=10)
        
        # English button with flag
        en_icon = ThemeAndIcons.get_icon('flag_en', size=(24, 24))
        en_text = "" if en_icon else ThemeAndIcons.get_icon_text('flag_en') + " "
        en_btn = ctk.CTkButton(
            lang_frame, 
            text=f"{en_text}English",
            image=en_icon,
            width=120,
            height=32,
            command=lambda: self.change_language("en")
        )
        if en_icon:
            en_btn.image = en_icon  # Keep a reference
        
        # Apply different style based on current language
        if self.lang_var.get() == "en":
            ThemeAndIcons.apply_theme_to_widget(en_btn, 'button_primary')
        else:
            ThemeAndIcons.apply_theme_to_widget(en_btn, 'button_outline')
            
        en_btn.pack(side=tk.LEFT, padx=5)
        
        # Turkish button with flag
        tr_icon = ThemeAndIcons.get_icon('flag_tr', size=(24, 24))
        tr_text = "" if tr_icon else ThemeAndIcons.get_icon_text('flag_tr') + " "
        tr_btn = ctk.CTkButton(
            lang_frame, 
            text=f"{tr_text}Türkçe",
            image=tr_icon,
            width=120,
            height=32,
            command=lambda: self.change_language("tr")
        )
        if tr_icon:
            tr_btn.image = tr_icon  # Keep a reference
        
        # Apply different style based on current language
        if self.lang_var.get() == "tr":
            ThemeAndIcons.apply_theme_to_widget(tr_btn, 'button_primary')
        else:
            ThemeAndIcons.apply_theme_to_widget(tr_btn, 'button_outline')
            
        tr_btn.pack(side=tk.LEFT, padx=5)
        
        # Store references to buttons for updating later
        self.lang_buttons = {
            "en": en_btn,
            "tr": tr_btn
        }

    def toggle_theme(self):
        """Toggle between light and dark theme with smooth transition"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        
        # Update the switch text
        self.theme_switch.configure(text=f"{'Dark' if new_mode == 'Light' else 'Light'} Mode")
        
        # Apply the theme change with a smooth transition
        ctk.set_appearance_mode(new_mode)
        
        # Update UI elements that need special handling for dark/light mode
        if new_mode == "Dark":
            # Update specific elements for dark mode
            if hasattr(self, 'log_text'):
                self.log_text.config(
                    bg=ThemeAndIcons.THEME['card_dark'], 
                    fg=ThemeAndIcons.THEME['text_light']
                )
                
                # Update log text tags for dark mode
                self.log_text.tag_configure("timestamp", foreground=ThemeAndIcons.THEME['primary'])
                self.log_text.tag_configure("info", foreground=ThemeAndIcons.THEME['info'])
                self.log_text.tag_configure("success", foreground=ThemeAndIcons.THEME['success'])
                self.log_text.tag_configure("warning", foreground=ThemeAndIcons.THEME['warning'])
                self.log_text.tag_configure("error", foreground=ThemeAndIcons.THEME['error'])
                
                # Update background colors for dark mode
                info_bg = self._adjust_color(ThemeAndIcons.THEME['info'], 0.1)
                success_bg = self._adjust_color(ThemeAndIcons.THEME['success'], 0.1)
                warning_bg = self._adjust_color(ThemeAndIcons.THEME['warning'], 0.1)
                error_bg = self._adjust_color(ThemeAndIcons.THEME['error'], 0.1)
                
                self.log_text.tag_configure("info_bg", background=info_bg)
                self.log_text.tag_configure("success_bg", background=success_bg)
                self.log_text.tag_configure("warning_bg", background=warning_bg)
                self.log_text.tag_configure("error_bg", background=error_bg)
                
            # Update status bar for dark mode
            if hasattr(self, 'status_frame'):
                self.status_frame.configure(fg_color=ThemeAndIcons.THEME['primary'])
                
            # Update all labels with appropriate text color
            for widget in self.root.winfo_children():
                self._update_widget_colors_for_dark_mode(widget)
                
            # Update all frames with appropriate background color
            self._update_frames_for_dark_mode(self.root)
        else:
            # Update specific elements for light mode
            if hasattr(self, 'log_text'):
                self.log_text.config(
                    bg=ThemeAndIcons.THEME['light'], 
                    fg=ThemeAndIcons.THEME['text_dark']
                )
                
                # Update log text tags for light mode
                self.log_text.tag_configure("timestamp", foreground=ThemeAndIcons.THEME['primary'])
                self.log_text.tag_configure("info", foreground=ThemeAndIcons.THEME['info'])
                self.log_text.tag_configure("success", foreground=ThemeAndIcons.THEME['success'])
                self.log_text.tag_configure("warning", foreground=ThemeAndIcons.THEME['warning'])
                self.log_text.tag_configure("error", foreground=ThemeAndIcons.THEME['error'])
                
                # Update background colors for light mode
                info_bg = self._adjust_color(ThemeAndIcons.THEME['info'], 0.1)
                success_bg = self._adjust_color(ThemeAndIcons.THEME['success'], 0.1)
                warning_bg = self._adjust_color(ThemeAndIcons.THEME['warning'], 0.1)
                error_bg = self._adjust_color(ThemeAndIcons.THEME['error'], 0.1)
                
                self.log_text.tag_configure("info_bg", background=info_bg)
                self.log_text.tag_configure("success_bg", background=success_bg)
                self.log_text.tag_configure("warning_bg", background=warning_bg)
                self.log_text.tag_configure("error_bg", background=error_bg)
                
            # Update status bar for light mode
            if hasattr(self, 'status_frame'):
                self.status_frame.configure(fg_color=ThemeAndIcons.THEME['dark'])
                
            # Update all labels with appropriate text color
            for widget in self.root.winfo_children():
                self._update_widget_colors_for_light_mode(widget)
                
            # Update all frames with appropriate background color
            self._update_frames_for_light_mode(self.root)
        
        # Show a brief notification about the theme change
        self.log(f"Theme changed to {new_mode} mode", "info")
    
    def _update_widget_colors_for_dark_mode(self, widget):
        """Recursively update widget colors for dark mode"""
        if widget.winfo_children():
            for child in widget.winfo_children():
                self._update_widget_colors_for_dark_mode(child)
                
        if isinstance(widget, ctk.CTkLabel):
            # Skip labels that should maintain their color (like titles with custom colors)
            if not (hasattr(widget, '_user_specified_color') and widget._user_specified_color):
                widget.configure(text_color=ThemeAndIcons.THEME['text_light'])
        elif isinstance(widget, ctk.CTkEntry) or isinstance(widget, ctk.CTkTextbox):
            widget.configure(text_color=ThemeAndIcons.THEME['text_light'])
            if isinstance(widget, ctk.CTkEntry) and widget._state != "disabled":
                widget.configure(fg_color=ThemeAndIcons.THEME['dark'])
                
    def _update_widget_colors_for_light_mode(self, widget):
        """Recursively update widget colors for light mode"""
        if widget.winfo_children():
            for child in widget.winfo_children():
                self._update_widget_colors_for_light_mode(child)
                
        if isinstance(widget, ctk.CTkLabel):
            # Skip labels that should maintain their color (like titles with custom colors)
            if not (hasattr(widget, '_user_specified_color') and widget._user_specified_color):
                widget.configure(text_color=ThemeAndIcons.THEME['text_dark'])
        elif isinstance(widget, ctk.CTkEntry) or isinstance(widget, ctk.CTkTextbox):
            widget.configure(text_color=ThemeAndIcons.THEME['text_dark'])
            if isinstance(widget, ctk.CTkEntry) and widget._state != "disabled":
                widget.configure(fg_color=ThemeAndIcons.THEME['light'])
    
    def _update_frames_for_dark_mode(self, widget):
        """Recursively update frame colors for dark mode"""
        if widget.winfo_children():
            for child in widget.winfo_children():
                self._update_frames_for_dark_mode(child)
                
        if isinstance(widget, ctk.CTkFrame) and not widget._fg_color == "transparent":
            widget.configure(fg_color=ThemeAndIcons.THEME['card_dark'])
            
    def _update_frames_for_light_mode(self, widget):
        """Recursively update frame colors for light mode"""
        if widget.winfo_children():
            for child in widget.winfo_children():
                self._update_frames_for_light_mode(child)
                
        if isinstance(widget, ctk.CTkFrame) and not widget._fg_color == "transparent":
            widget.configure(fg_color=ThemeAndIcons.THEME['card'])
    
    def create_status_bar(self):
        """Create modern status bar"""
        self.status_frame = ctk.CTkFrame(self.container, height=36, fg_color=ThemeAndIcons.THEME['dark'], corner_radius=8)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Status indicator dot
        self.status_indicator = ctk.CTkLabel(
            self.status_frame, 
            text="●", 
            font=ctk.CTkFont(size=16),
            text_color=ThemeAndIcons.THEME['success'],
            width=20
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            textvariable=self.status_text,
            text_color=ThemeAndIcons.THEME['text_light']
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Time label with icon
        time_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        time_frame.pack(side=tk.RIGHT, padx=10)
        
        # Clock icon (text-based for simplicity)
        clock_label = ctk.CTkLabel(
            time_frame, 
            text="🕒", 
            font=ctk.CTkFont(size=14),
            text_color=ThemeAndIcons.THEME['text_light']
        )
        clock_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Time text
        self.time_label = ctk.CTkLabel(
            time_frame, 
            textvariable=self.time_text,
            text_color=ThemeAndIcons.THEME['text_light']
        )
        self.time_label.pack(side=tk.LEFT)
        
        # Update time
        self.update_time()
        
    def update_status(self, message, status_type="info"):
        """Update status bar with message and appropriate color"""
        self.status_text.set(message)
        
        # Update status indicator color based on status type
        if status_type == "success":
            self.status_indicator.configure(text_color=ThemeAndIcons.THEME['success'])
        elif status_type == "warning":
            self.status_indicator.configure(text_color=ThemeAndIcons.THEME['warning'])
        elif status_type == "error":
            self.status_indicator.configure(text_color=ThemeAndIcons.THEME['error'])
        else:  # info
            self.status_indicator.configure(text_color=ThemeAndIcons.THEME['info'])

    def setup_variables(self):
        # Variables
        self.links = []
        self.current_link_index = 0
        self.running = False
        self.paused = False
        self.thread = None
        
        # Status and time variables
        self.status_text = ctk.StringVar(value="Ready")
        self.time_text = ctk.StringVar(value="")
        
        self.headers = {
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'sec-fetch-dest': 'document',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'accept-language': 'en-US,en;q=0.9',
        }
        
        # Default post data
        self.post_data = {
            'author': '',
            'email': '',
            'url': '',
            'comment': '',
            'comment_post_ID': '',
            'comment_parent': '',
            'submit': 'Post Comment',
            'ak_js': ''
        }
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'session_start': None,
            'session_duration': 0
        }

    def create_widgets(self):
        # Main tab
        self.setup_main_tab()
        
        # Settings tab
        self.setup_settings_tab()
        
        # Stats tab
        self.setup_stats_tab()

    def setup_main_tab(self):
        # Header frame with logo
        header_frame = ThemeAndIcons.create_rounded_frame(self.main_tab, fg_color="transparent")
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Logo image
        logo_img = ThemeAndIcons.get_icon('logo', size=(40, 40))
        if logo_img:
            logo_label = ctk.CTkLabel(header_frame, image=logo_img, text="")
            logo_label.image = logo_img  # Keep a reference to prevent garbage collection
            logo_label.pack(side=tk.LEFT, padx=(0, 15))
        else:
            # Use text fallback
            logo_text = ThemeAndIcons.get_icon_text('logo')
            logo_label = ctk.CTkLabel(header_frame, text=logo_text, font=ctk.CTkFont(size=30))
            logo_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Title and subtitle
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = ctk.CTkLabel(title_frame, text="WordPress Backlink Pro", 
                               font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), 
                               text_color=ThemeAndIcons.THEME['primary'])
        title_label._user_specified_color = True  # Mark as having a custom color
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ctk.CTkLabel(title_frame, 
                                 text="Automated comment backlink tool for WordPress sites", 
                                 font=ctk.CTkFont(family="Helvetica", size=12),
                                 text_color=ThemeAndIcons.get_label_text_color())
        subtitle_label.pack(anchor=tk.W)
        
        # Main content area with two columns
        content_frame = ThemeAndIcons.create_rounded_frame(self.main_tab, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left column - Controls
        left_frame = ThemeAndIcons.create_rounded_frame(content_frame, fg_color="transparent")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Links file selection with improved layout
        file_frame = ThemeAndIcons.create_rounded_frame(left_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add label for the frame
        ctk.CTkLabel(file_frame, text="Links File", 
                  font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                  text_color=ThemeAndIcons.get_label_text_color()).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        file_input_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.links_file_var = ctk.StringVar(value="links.txt")
        links_entry = ctk.CTkEntry(file_input_frame, textvariable=self.links_file_var, 
                                height=38,
                                placeholder_text="Path to links file...")
        ThemeAndIcons.apply_theme_to_widget(links_entry, 'input')
        links_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Add icons to buttons
        browse_icon = ThemeAndIcons.get_icon('browse')
        browse_text = "" if browse_icon else ThemeAndIcons.get_icon_text('browse') + " "
        browse_btn = ctk.CTkButton(file_input_frame, text=f"{browse_text}Browse", 
                              image=browse_icon,
                              command=self.browse_links_file,
                              height=38)
        if browse_icon:
            browse_btn.image = browse_icon  # Keep a reference
        ThemeAndIcons.apply_theme_to_widget(browse_btn, 'button_primary')
        browse_btn.pack(side=tk.LEFT, padx=2)
        
        load_icon = ThemeAndIcons.get_icon('load')
        load_text = "" if load_icon else ThemeAndIcons.get_icon_text('load') + " "
        load_btn = ctk.CTkButton(file_input_frame, text=f"{load_text}Load", 
                            image=load_icon,
                            command=self.load_links,
                            height=38)
        if load_icon:
            load_btn.image = load_icon  # Keep a reference
        ThemeAndIcons.apply_theme_to_widget(load_btn, 'button_primary')
        load_btn.pack(side=tk.LEFT, padx=2)
        
        # Control buttons with better styling
        controls_frame = ThemeAndIcons.create_rounded_frame(left_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Add label for the frame
        ctk.CTkLabel(controls_frame, text="Controls", 
                  font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                  text_color=ThemeAndIcons.get_label_text_color()).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        # Create a frame for the buttons
        button_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Start button with icon
        start_icon = ThemeAndIcons.get_icon('start')
        start_text = "" if start_icon else ThemeAndIcons.get_icon_text('start') + " "
        self.start_btn = ctk.CTkButton(button_frame, text=f"{start_text}Start", 
                                  image=start_icon,
                                  command=self.start_bot,
                                  height=40)
        if start_icon:
            self.start_btn.image = start_icon  # Keep a reference
        ThemeAndIcons.apply_theme_to_widget(self.start_btn, 'button_primary')
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Pause button with icon
        pause_icon = ThemeAndIcons.get_icon('pause')
        pause_text = "" if pause_icon else ThemeAndIcons.get_icon_text('pause') + " "
        self.pause_btn = ctk.CTkButton(button_frame, text=f"{pause_text}Pause", 
                                  image=pause_icon,
                                  command=self.pause_bot,
                                  height=40)
        if pause_icon:
            self.pause_btn.image = pause_icon  # Keep a reference
        ThemeAndIcons.apply_theme_to_widget(self.pause_btn, 'button_secondary')
        self.pause_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Stop button with icon
        stop_icon = ThemeAndIcons.get_icon('stop')
        stop_text = "" if stop_icon else ThemeAndIcons.get_icon_text('stop') + " "
        self.stop_btn = ctk.CTkButton(button_frame, text=f"{stop_text}Stop", 
                                 image=stop_icon,
                                 command=self.stop_bot,
                                 height=40)
        if stop_icon:
            self.stop_btn.image = stop_icon  # Keep a reference
        ThemeAndIcons.apply_theme_to_widget(self.stop_btn, 'button_danger')
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Add tooltips for the buttons
        self.create_tooltip(self.start_btn, "Start the backlink process")
        self.create_tooltip(self.pause_btn, "Pause/Resume the backlink process")
        self.create_tooltip(self.stop_btn, "Stop the backlink process")
        
        # Progress frame with improved visuals
        progress_frame = ThemeAndIcons.create_rounded_frame(left_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add label for the frame
        ctk.CTkLabel(progress_frame, text="Progress", 
                  font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                  text_color=ThemeAndIcons.get_label_text_color()).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        progress_content = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Current link section
        link_label_frame = ctk.CTkFrame(progress_content, fg_color="transparent")
        link_label_frame.pack(fill=tk.X, pady=(0, 10))
        
        ctk.CTkLabel(link_label_frame, text="Current Link:", 
                 font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                 text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT, anchor=tk.W)
        
        self.current_link_var = ctk.StringVar(value="No link loaded")
        current_link_entry = ctk.CTkEntry(progress_content, textvariable=self.current_link_var, 
                                     height=35, state="readonly")
        ThemeAndIcons.apply_theme_to_widget(current_link_entry, 'input')
        current_link_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Progress section
        progress_label_frame = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_label_frame.pack(fill=tk.X, pady=(0, 5))
        
        ctk.CTkLabel(progress_label_frame, text="Progress:", 
                 font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                 text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT, anchor=tk.W)
        
        self.progress_var = ctk.StringVar(value="0/0")
        ctk.CTkLabel(progress_label_frame, textvariable=self.progress_var, 
                 font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side=tk.RIGHT)
        
        # Progress bar with percentage
        progress_bar_frame = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_bar_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_bar_frame, 
                                          height=15,
                                          corner_radius=5,
                                          mode='determinate',
                                          progress_color=ThemeAndIcons.THEME['primary'])
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.progress_bar.set(0)
        
        self.progress_percentage = ctk.StringVar(value="0%")
        ctk.CTkLabel(progress_bar_frame, textvariable=self.progress_percentage, 
                 font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                 text_color=ThemeAndIcons.THEME['secondary']).pack(anchor=tk.E)
        
        # Right column - Log area
        right_frame = ThemeAndIcons.create_rounded_frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Add label for the frame with an icon
        log_header_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        log_header_frame.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        # Add an icon for the log header
        log_icon_text = "📋"
        log_icon_label = ctk.CTkLabel(
            log_header_frame, 
            text=log_icon_text, 
            font=ctk.CTkFont(size=18),
            text_color=ThemeAndIcons.THEME['primary']
        )
        log_icon_label.pack(side=tk.LEFT, padx=(0, 5))
        
        ctk.CTkLabel(log_header_frame, text="Activity Log", 
                  font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
                  text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT)
        
        # Add clear log button
        clear_log_btn = ctk.CTkButton(
            log_header_frame, 
            text="Clear", 
            command=self.clear_log,
            width=80,
            height=28
        )
        ThemeAndIcons.apply_theme_to_widget(clear_log_btn, 'button_outline')
        clear_log_btn.pack(side=tk.RIGHT)
        
        # Add save log button
        save_log_btn = ctk.CTkButton(
            log_header_frame, 
            text="Save", 
            command=self.save_log,
            width=80,
            height=28
        )
        ThemeAndIcons.apply_theme_to_widget(save_log_btn, 'button_outline')
        save_log_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        log_content = ctk.CTkFrame(right_frame, fg_color="transparent")
        log_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create a custom styled Text widget for the log with improved styling
        log_frame = ctk.CTkFrame(log_content, corner_radius=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a custom frame for the log with a header
        log_container = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create the actual log text widget with improved styling
        self.log_text = scrolledtext.ScrolledText(
            log_container, 
            height=15, 
            bg=ThemeAndIcons.THEME['card_dark'] if ctk.get_appearance_mode() == "Dark" else ThemeAndIcons.THEME['light'],
            fg=ThemeAndIcons.THEME['text_light'] if ctk.get_appearance_mode() == "Dark" else ThemeAndIcons.THEME['text_dark'],
            font=("Consolas", 11),
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Add log text tags for different message types with improved styling
        self.log_text.tag_configure("timestamp", foreground=ThemeAndIcons.THEME['primary'])
        self.log_text.tag_configure("info_icon", foreground=ThemeAndIcons.THEME['info'])
        self.log_text.tag_configure("success_icon", foreground=ThemeAndIcons.THEME['success'])
        self.log_text.tag_configure("warning_icon", foreground=ThemeAndIcons.THEME['warning'])
        self.log_text.tag_configure("error_icon", foreground=ThemeAndIcons.THEME['error'])
        
        # Configure message type tags with background colors for better visibility
        info_bg = self._adjust_color(ThemeAndIcons.THEME['info'], 0.1)
        success_bg = self._adjust_color(ThemeAndIcons.THEME['success'], 0.1)
        warning_bg = self._adjust_color(ThemeAndIcons.THEME['warning'], 0.1)
        error_bg = self._adjust_color(ThemeAndIcons.THEME['error'], 0.1)
        
        self.log_text.tag_configure("info", foreground=ThemeAndIcons.THEME['info'])
        self.log_text.tag_configure("success", foreground=ThemeAndIcons.THEME['success'])
        self.log_text.tag_configure("warning", foreground=ThemeAndIcons.THEME['warning'])
        self.log_text.tag_configure("error", foreground=ThemeAndIcons.THEME['error'])
        
        # Configure message background tags
        self.log_text.tag_configure("info_bg", background=info_bg)
        self.log_text.tag_configure("success_bg", background=success_bg)
        self.log_text.tag_configure("warning_bg", background=warning_bg)
        self.log_text.tag_configure("error_bg", background=error_bg)
        
        # Add auto-scroll checkbox
        autoscroll_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        autoscroll_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.autoscroll_var = ctk.BooleanVar(value=True)
        autoscroll_cb = ctk.CTkCheckBox(
            autoscroll_frame, 
            text="Auto-scroll", 
            variable=self.autoscroll_var,
            text_color=ThemeAndIcons.get_label_text_color(),
            onvalue=True, 
            offvalue=False
        )
        autoscroll_cb.pack(side=tk.RIGHT)
        
        # Status bar with better styling
        status_frame = ctk.CTkFrame(self.main_tab, height=30, fg_color=ThemeAndIcons.THEME['dark'])
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(10, 20))
        
        self.status_var = ctk.CTkLabel(status_frame, textvariable=self.status_text, 
                             anchor="w",
                             text_color=ThemeAndIcons.THEME['text_light'])
        self.status_var.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
        # Add current time at the right of status bar
        self.time_var = ctk.CTkLabel(status_frame, textvariable=self.time_text,
                                 text_color=ThemeAndIcons.THEME['text_light'])
        self.time_var.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Update time every second
        self.update_time()
    
    def setup_settings_tab(self):
        # Main container with padding
        settings_container = ThemeAndIcons.create_rounded_frame(self.settings_tab, fg_color="transparent")
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Comment settings frame
        comment_frame = ThemeAndIcons.create_rounded_frame(settings_container)
        comment_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add label for the frame
        ctk.CTkLabel(comment_frame, text="Comment Settings", 
                  font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
                  text_color=ThemeAndIcons.get_label_text_color()).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        # Create a frame for each field to organize them vertically
        fields_frame = ctk.CTkFrame(comment_frame, fg_color="transparent")
        fields_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Author
        author_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        author_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(author_frame, text="Author:", 
                  font=ctk.CTkFont(family="Helvetica", size=12),
                  width=80,
                  text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT, padx=5)
                  
        self.author_var = ctk.StringVar()
        author_entry = ctk.CTkEntry(author_frame, textvariable=self.author_var, 
                                height=35,
                                placeholder_text="Your name...")
        ThemeAndIcons.apply_theme_to_widget(author_entry, 'input')
        author_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Email
        email_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        email_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(email_frame, text="Email:", 
                  font=ctk.CTkFont(family="Helvetica", size=12),
                  width=80,
                  text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT, padx=5)
                  
        self.email_var = ctk.StringVar()
        email_entry = ctk.CTkEntry(email_frame, textvariable=self.email_var, 
                               height=35,
                               placeholder_text="your.email@example.com")
        ThemeAndIcons.apply_theme_to_widget(email_entry, 'input')
        email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # URL
        url_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        url_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(url_frame, text="URL:", 
                  font=ctk.CTkFont(family="Helvetica", size=12),
                  width=80,
                  text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT, padx=5)
                  
        self.url_var = ctk.StringVar()
        url_entry = ctk.CTkEntry(url_frame, textvariable=self.url_var, 
                             height=35,
                             placeholder_text="https://yourwebsite.com")
        ThemeAndIcons.apply_theme_to_widget(url_entry, 'input')
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Comment
        comment_input_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        comment_input_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(comment_input_frame, text="Comment:", 
                  font=ctk.CTkFont(family="Helvetica", size=12),
                  width=80,
                  text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
                  
        self.comment_text = ctk.CTkTextbox(comment_input_frame, 
                                       height=100,
                                       corner_radius=6)
        self.comment_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Success file frame
        success_frame = ThemeAndIcons.create_rounded_frame(settings_container)
        success_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Add label for the frame
        ctk.CTkLabel(success_frame, text="Success File", 
                  font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
                  text_color=ThemeAndIcons.get_label_text_color()).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        success_input_frame = ctk.CTkFrame(success_frame, fg_color="transparent")
        success_input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(success_input_frame, text="File Path:", 
                  font=ctk.CTkFont(family="Helvetica", size=12),
                  width=80,
                  text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT, padx=5)
                  
        self.success_file_var = ctk.StringVar(value="success.txt")
        success_entry = ctk.CTkEntry(success_input_frame, textvariable=self.success_file_var, 
                                 height=35,
                                 placeholder_text="Path to success file...")
        ThemeAndIcons.apply_theme_to_widget(success_entry, 'input')
        success_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Timing settings frame
        timing_frame = ThemeAndIcons.create_rounded_frame(settings_container)
        timing_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add label for the frame
        ctk.CTkLabel(timing_frame, text="Timing Settings", 
                  font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
                  text_color=ThemeAndIcons.get_label_text_color()).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        timing_input_frame = ctk.CTkFrame(timing_frame, fg_color="transparent")
        timing_input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(timing_input_frame, text="Delay between requests (seconds):", 
                  font=ctk.CTkFont(family="Helvetica", size=12),
                  text_color=ThemeAndIcons.get_label_text_color()).pack(side=tk.LEFT, padx=5)
                  
        self.delay_var = ctk.StringVar(value="2")
        delay_entry = ctk.CTkEntry(timing_input_frame, textvariable=self.delay_var, 
                               width=70,
                               height=35)
        ThemeAndIcons.apply_theme_to_widget(delay_entry, 'input')
        delay_entry.pack(side=tk.LEFT, padx=5)
        
        # Button frame
        button_frame = ctk.CTkFrame(settings_container, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=5, pady=15)
        
        # Save button with icon
        save_icon = ThemeAndIcons.get_icon('save')
        save_text = "" if save_icon else ThemeAndIcons.get_icon_text('save') + " "
        save_btn = ctk.CTkButton(button_frame, text=f"{save_text}Save Settings", 
                             image=save_icon,
                             command=self.save_config,
                             height=40)
        if save_icon:
            save_btn.image = save_icon  # Keep a reference
        ThemeAndIcons.apply_theme_to_widget(save_btn, 'button_primary')
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Load button with icon
        load_icon = ThemeAndIcons.get_icon('load')
        load_text = "" if load_icon else ThemeAndIcons.get_icon_text('load') + " "
        load_btn = ctk.CTkButton(button_frame, text=f"{load_text}Load Settings", 
                             image=load_icon,
                             command=self.load_config,
                             height=40)
        if load_icon:
            load_btn.image = load_icon  # Keep a reference
        ThemeAndIcons.apply_theme_to_widget(load_btn, 'button_secondary')
        load_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Reset button with icon
        reset_icon = ThemeAndIcons.get_icon('reset')
        reset_text = "" if reset_icon else ThemeAndIcons.get_icon_text('reset') + " "
        reset_btn = ctk.CTkButton(button_frame, text=f"{reset_text}Reset to Default", 
                              image=reset_icon,
                              command=self.reset_config,
                              height=40)
        if reset_icon:
            reset_btn.image = reset_icon  # Keep a reference
        ThemeAndIcons.apply_theme_to_widget(reset_btn, 'button_danger')
        reset_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def setup_stats_tab(self):
        """Setup statistics tab to display usage data"""
        # Main container
        stats_container = ThemeAndIcons.create_rounded_frame(self.stats_tab, fg_color="transparent")
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title with icon
        title_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Try to load stats icon
        stats_icon = ThemeAndIcons.get_icon('globe', size=(30, 30))
        if stats_icon:
            icon_label = ctk.CTkLabel(title_frame, image=stats_icon, text="")
            icon_label.image = stats_icon
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
        else:
            # Use text fallback
            globe_text = ThemeAndIcons.get_icon_text('globe')
            icon_label = ctk.CTkLabel(title_frame, text=globe_text, font=ctk.CTkFont(size=24))
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ctk.CTkLabel(title_frame, text="Session Statistics", 
                 font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
                 text_color=ThemeAndIcons.THEME['primary']).pack(side=tk.LEFT)
        
        # Stats cards container
        cards_container = ctk.CTkFrame(stats_container, fg_color="transparent")
        cards_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a grid of stat cards (2x3)
        for i in range(2):
            cards_container.columnconfigure(i, weight=1)
        for i in range(3):
            cards_container.rowconfigure(i, weight=1)
        
        # Session Duration Card
        duration_card = ThemeAndIcons.create_rounded_frame(cards_container)
        duration_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(duration_card, text="Session Duration", 
                 font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                 text_color=ThemeAndIcons.THEME['dark']).pack(anchor=tk.CENTER, pady=(15, 5))
                 
        self.session_duration_var = ctk.StringVar(value="00:00:00")
        ctk.CTkLabel(duration_card, textvariable=self.session_duration_var,
                 font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                 text_color=ThemeAndIcons.THEME['primary']).pack(anchor=tk.CENTER, pady=(5, 15))
        
        # Success Rate Card
        success_card = ThemeAndIcons.create_rounded_frame(cards_container)
        success_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(success_card, text="Success Rate", 
                 font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                 text_color=ThemeAndIcons.THEME['dark']).pack(anchor=tk.CENTER, pady=(15, 5))
                 
        self.success_rate_var = ctk.StringVar(value="0%")
        ctk.CTkLabel(success_card, textvariable=self.success_rate_var,
                 font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                 text_color=ThemeAndIcons.THEME['success']).pack(anchor=tk.CENTER, pady=(5, 15))
        
        # Total Processed Card
        processed_card = ThemeAndIcons.create_rounded_frame(cards_container)
        processed_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(processed_card, text="Total Processed", 
                 font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                 text_color=ThemeAndIcons.THEME['dark']).pack(anchor=tk.CENTER, pady=(15, 5))
                 
        self.total_processed_var = ctk.StringVar(value="0")
        ctk.CTkLabel(processed_card, textvariable=self.total_processed_var,
                 font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                 text_color=ThemeAndIcons.THEME['primary']).pack(anchor=tk.CENTER, pady=(5, 15))
        
        # Success/Failed Card
        success_failed_card = ThemeAndIcons.create_rounded_frame(cards_container)
        success_failed_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(success_failed_card, text="Success / Failed", 
                 font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                 text_color=ThemeAndIcons.THEME['dark']).pack(anchor=tk.CENTER, pady=(15, 5))
        
        # Create a frame for the success/failed counters
        counters_frame = ctk.CTkFrame(success_failed_card, fg_color="transparent")
        counters_frame.pack(anchor=tk.CENTER, pady=(5, 15))
        
        # Success counter
        self.total_success_var = ctk.StringVar(value="0")
        ctk.CTkLabel(counters_frame, textvariable=self.total_success_var,
                 font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                 text_color=ThemeAndIcons.THEME['success']).pack(side=tk.LEFT, padx=(0, 10))
                 
        ctk.CTkLabel(counters_frame, text="/",
                 font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                 text_color=ThemeAndIcons.THEME['dark']).pack(side=tk.LEFT)
                 
        # Failed counter
        self.total_failed_var = ctk.StringVar(value="0")
        ctk.CTkLabel(counters_frame, textvariable=self.total_failed_var,
                 font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                 text_color=ThemeAndIcons.THEME['error']).pack(side=tk.LEFT, padx=(10, 0))
        
        # Average Time Card
        avg_time_card = ThemeAndIcons.create_rounded_frame(cards_container)
        avg_time_card.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(avg_time_card, text="Average Time Per Link", 
                 font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                 text_color=ThemeAndIcons.THEME['dark']).pack(anchor=tk.CENTER, pady=(15, 5))
                 
        self.avg_time_var = ctk.StringVar(value="0.0 sec")
        ctk.CTkLabel(avg_time_card, textvariable=self.avg_time_var,
                 font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                 text_color=ThemeAndIcons.THEME['info']).pack(anchor=tk.CENTER, pady=(5, 15))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=10, pady=20)
        
        # Reset button with icon
        reset_icon = ThemeAndIcons.get_icon('reset')
        reset_text = "" if reset_icon else ThemeAndIcons.get_icon_text('reset') + " "
        reset_btn = ctk.CTkButton(btn_frame, text=f"{reset_text}Reset Statistics", 
                              image=reset_icon,
                              command=self.reset_statistics,
                              height=40)
        if reset_icon:
            reset_btn.image = reset_icon
        ThemeAndIcons.apply_theme_to_widget(reset_btn, 'button_primary')
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button with icon
        export_icon = ThemeAndIcons.get_icon('export')
        export_text = "" if export_icon else ThemeAndIcons.get_icon_text('export') + " "
        export_btn = ctk.CTkButton(btn_frame, text=f"{export_text}Export Statistics", 
                               image=export_icon,
                               command=self.export_statistics,
                               height=40)
        if export_icon:
            export_btn.image = export_icon
        ThemeAndIcons.apply_theme_to_widget(export_btn, 'button_secondary')
        export_btn.pack(side=tk.LEFT, padx=5)
    
    def update_time(self):
        """Update the time display in the status bar"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_text.set(current_time)
        
        # Also update session duration if the bot is running
        if self.stats['session_start'] and self.running:
            duration = datetime.now() - self.stats['session_start']
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.session_duration_var.set(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
            
            # Update statistics
            self.update_statistics()
        
        # Schedule the next update
        self.root.after(1000, self.update_time)
    
    def create_tooltip(self, widget, text):
        """Create a modern tooltip for a given widget"""
        def enter(event):
            # Destroy any existing tooltip
            if hasattr(self, 'tooltip') and self.tooltip.winfo_exists():
                self.tooltip.destroy()
                
            # Add a slight delay before showing tooltip
            self.tooltip_timer = widget.after(300, lambda: self._create_and_show_tooltip(widget, text))
            
        def leave(event):
            if hasattr(self, 'tooltip_timer'):
                try:
                    widget.after_cancel(self.tooltip_timer)
                    delattr(self, 'tooltip_timer')
                except (AttributeError, tk.TclError):
                    pass
                    
            if hasattr(self, 'tooltip') and self.tooltip.winfo_exists():
                try:
                    self.tooltip.destroy()
                except tk.TclError:
                    pass
                
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
    
    def _show_tooltip(self, text):
        """Show the tooltip with animation effect"""
        if not hasattr(self, 'tooltip') or not self.tooltip.winfo_exists():
            return
            
        # Create a frame with rounded corners
        frame = ctk.CTkFrame(
            self.tooltip,
            fg_color=ThemeAndIcons.THEME['dark'],
            corner_radius=6
        )
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add the tooltip text
        label = ctk.CTkLabel(
            frame, 
            text=text, 
            justify=tk.LEFT,
            text_color=ThemeAndIcons.THEME['text_light'],
            font=ctk.CTkFont(family="Helvetica", size=11),
            padx=10, 
            pady=6
        )
        label.pack()
        
        # Add a subtle animation effect
        self.tooltip.attributes('-alpha', 0.0)
        for i in range(11):
            if not hasattr(self, 'tooltip') or not self.tooltip.winfo_exists():
                break
            try:
                self.tooltip.attributes('-alpha', i/10)
                self.tooltip.update()
                time.sleep(0.01)
            except (tk.TclError, RuntimeError):
                # Handle case where tooltip was destroyed during animation
                break
    
    def _create_and_show_tooltip(self, widget, text):
        """Create and show the tooltip with animation effect"""
        # Get widget position
        x = widget.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 5
        
        # Create a toplevel window
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create a frame with rounded corners
        frame = ctk.CTkFrame(
            self.tooltip,
            fg_color=ThemeAndIcons.THEME['dark'],
            corner_radius=6
        )
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add the tooltip text
        label = ctk.CTkLabel(
            frame, 
            text=text, 
            justify=tk.LEFT,
            text_color=ThemeAndIcons.THEME['text_light'],
            font=ctk.CTkFont(family="Helvetica", size=11),
            padx=10, 
            pady=6
        )
        label.pack()
        
        # Add a subtle animation effect
        self.tooltip.attributes('-alpha', 0.0)
        for i in range(11):
            if not hasattr(self, 'tooltip') or not self.tooltip.winfo_exists():
                break
            try:
                self.tooltip.attributes('-alpha', i/10)
                self.tooltip.update()
                time.sleep(0.01)
            except (tk.TclError, RuntimeError):
                # Handle case where tooltip was destroyed during animation
                break
    
    def change_language(self, lang):
        """Change the interface language"""
        if lang != self.lang_var.get() and lang in self.translations:
            self.lang_var.set(lang)
            
            # Update all text elements
            try:
                tab_names = [self.get_text("main_tab"), self.get_text("settings_tab"), self.get_text("stats")]
                for i, name in enumerate(tab_names):
                    if hasattr(self.tabview._segmented_button, "set_text"):
                        # For newer versions that might have this method
                        self.tabview._segmented_button.set_text(i, name)
                    elif hasattr(self.tabview, "_segmented_button") and hasattr(self.tabview._segmented_button, "_buttons"):
                        # Direct access to buttons if available
                        button_keys = list(self.tabview._segmented_button._buttons.keys())
                        if i < len(button_keys):
                            self.tabview._segmented_button._buttons[button_keys[i]].configure(text=name)
            except Exception as e:
                self.log(f"Error updating tab names: {str(e)}", "error")
            
            # Update language button styles
            if hasattr(self, 'lang_buttons'):
                for lang_code, button in self.lang_buttons.items():
                    if lang_code == lang:
                        ThemeAndIcons.apply_theme_to_widget(button, 'button_primary')
                    else:
                        ThemeAndIcons.apply_theme_to_widget(button, 'button_outline')
            
            # Recreate widgets with new language
            # This is a simplified approach - in a real app, you'd update each widget's text
            for widget in self.main_tab.winfo_children():
                widget.destroy()
            for widget in self.settings_tab.winfo_children():
                widget.destroy()
            for widget in self.stats_tab.winfo_children():
                widget.destroy()
            
            self.setup_main_tab()
            self.setup_settings_tab()
            self.setup_stats_tab()
            
            # Update status bar
            self.status_text.set(self.get_text("ready"))
    
    def reset_statistics(self):
        """Reset the statistics counters"""
        self.stats = {
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'session_start': datetime.now() if self.running else None,
            'session_duration': 0
        }
        self.update_statistics()
        self.log("Statistics reset", "info")
    
    def export_statistics(self):
        """Export the statistics to a CSV file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="backlink_stats.csv"
            )
            if not filename:
                return
            
            with open(filename, "w") as f:
                f.write("Statistic,Value\n")
                f.write(f"Date,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Processed,{self.stats['total_processed']}\n")
                f.write(f"Total Success,{self.stats['total_success']}\n")
                f.write(f"Total Failed,{self.stats['total_failed']}\n")
                
                success_rate = 0
                if self.stats['total_processed'] > 0:
                    success_rate = (self.stats['total_success'] / self.stats['total_processed']) * 100
                f.write(f"Success Rate,{success_rate:.2f}%\n")
                
                if self.stats['session_start']:
                    duration = datetime.now() - self.stats['session_start']
                    f.write(f"Session Duration,{int(duration.total_seconds())} seconds\n")
                
            self.log(f"Statistics exported to {filename}", "success")
        except Exception as e:
            self.log(f"Error exporting statistics: {str(e)}", "error")
    
    def update_statistics(self):
        """Update the statistics display"""
        # Calculate success rate
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['total_success'] / self.stats['total_processed']) * 100
            self.success_rate_var.set(f"{success_rate:.1f}%")
        else:
            self.success_rate_var.set("0%")
        
        # Update other stats
        self.total_processed_var.set(str(self.stats['total_processed']))
        self.total_success_var.set(str(self.stats['total_success']))
        self.total_failed_var.set(str(self.stats['total_failed']))
        
        # Calculate average time per link
        if self.stats['total_processed'] > 0 and self.stats['session_start']:
            duration = datetime.now() - self.stats['session_start']
            avg_time = duration.total_seconds() / self.stats['total_processed']
            self.avg_time_var.set(f"{avg_time:.1f} sec")
        else:
            self.avg_time_var.set("0.0 sec")
    
    def browse_links_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.links_file_var.set(filename)
    
    def load_links(self):
        links_file = self.links_file_var.get()
        if not links_file:
            messagebox.showerror("Error", "Please select a links file.")
            return
        
        try:
            with open(links_file, 'r') as f:
                lines = f.readlines()
                # Filter out empty lines, comments, and header lines like "Success Linkler"
                self.links = [line.strip() for line in lines 
                              if line.strip() and 
                              not line.strip().startswith('#') and 
                              line.strip().startswith('http')]
            
            if not self.links:
                self.log(f"No valid links found in {links_file}", "warning")
                messagebox.showwarning("Warning", "No valid links found in the file. Please check format.")
                return
                
            self.log(f"Loaded {len(self.links)} links from {links_file}", "success")
            self.progress_var.set(f"0/{len(self.links)}")
            self.progress_percentage.set("0%")
            self.progress_bar['maximum'] = len(self.links)
            self.progress_bar['value'] = 0
        except Exception as e:
            self.log(f"Error loading links: {str(e)}", "error")
            messagebox.showerror("Error", f"Failed to load links: {str(e)}")
    
    def save_config(self):
        config = {
            'author': self.author_var.get(),
            'email': self.email_var.get(),
            'url': self.url_var.get(),
            'comment': self.comment_text.get("1.0", tk.END).strip(),
            'success_file': self.success_file_var.get(),
            'delay': self.delay_var.get(),
            'language': self.lang_var.get()
        }
        
        try:
            with open('bot_config.json', 'w') as f:
                json.dump(config, f, indent=4)
            self.log("Configuration saved successfully", "success")
            
            # Update post data
            self.post_data['author'] = config['author']
            self.post_data['email'] = config['email']
            self.post_data['url'] = config['url']
            self.post_data['comment'] = config['comment']
        except Exception as e:
            self.log(f"Error saving configuration: {str(e)}", "error")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        try:
            # First try to load from bot_config.json
            if os.path.exists('bot_config.json'):
                with open('bot_config.json', 'r') as f:
                    config = json.load(f)
                
                self.author_var.set(config.get('author', ''))
                self.email_var.set(config.get('email', ''))
                self.url_var.set(config.get('url', ''))
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.insert("1.0", config.get('comment', ''))
                self.success_file_var.set(config.get('success_file', 'success.txt'))
                self.delay_var.set(config.get('delay', '2'))
                
                # Set language if specified
                if 'language' in config and config['language'] in self.translations:
                    self.change_language(config['language'])
                    self.lang_var.set(config['language'])
                
                self.log("Configuration loaded from bot_config.json", "success")
            # If not found, try to load from postData.json
            elif os.path.exists('postData.json'):
                with open('postData.json', 'r') as f:
                    post_data = json.load(f)
                
                self.author_var.set(post_data.get('author', ''))
                self.email_var.set(post_data.get('email', ''))
                self.url_var.set(post_data.get('url', ''))
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.insert("1.0", post_data.get('comment', ''))
                
                self.post_data = post_data
                self.log("Configuration loaded from postData.json", "info")
            else:
                self.log("No configuration files found. Using defaults.", "info")
        except Exception as e:
            self.log(f"Error loading configuration: {str(e)}", "error")
    
    def reset_config(self):
        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to default?")
        if not confirm:
            return
            
        self.author_var.set('')
        self.email_var.set('')
        self.url_var.set('')
        self.comment_text.delete("1.0", tk.END)
        self.success_file_var.set('success.txt')
        self.delay_var.set('2')
        self.log("Settings reset to default values", "info")
    
    def clear_log(self):
        """Clear the log text widget"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("Log cleared", "info")
        
    def _adjust_color(self, hex_color, transparency):
        """Adjust color transparency for background highlighting"""
        # Convert hex to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Get background color based on theme
        if ctk.get_appearance_mode() == "Dark":
            bg_r, bg_g, bg_b = int(ThemeAndIcons.THEME['card_dark'][1:3], 16), int(ThemeAndIcons.THEME['card_dark'][3:5], 16), int(ThemeAndIcons.THEME['card_dark'][5:7], 16)
        else:
            bg_r, bg_g, bg_b = int(ThemeAndIcons.THEME['light'][1:3], 16), int(ThemeAndIcons.THEME['light'][3:5], 16), int(ThemeAndIcons.THEME['light'][5:7], 16)
        
        # Blend colors
        blended_r = int(r * transparency + bg_r * (1 - transparency))
        blended_g = int(g * transparency + bg_g * (1 - transparency))
        blended_b = int(b * transparency + bg_b * (1 - transparency))
        
        # Convert back to hex
        return f'#{blended_r:02x}{blended_g:02x}{blended_b:02x}'

    def log(self, message, log_type="info"):
        """Add a message to the log with improved formatting and icons"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Define icons for different message types
        icons = {
            "info": "ℹ️ ",
            "success": "✅ ",
            "warning": "⚠️ ",
            "error": "❌ "
        }
        
        icon = icons.get(log_type, "ℹ️ ")
        icon_tag = f"{log_type}_icon"
        bg_tag = f"{log_type}_bg"
        
        self.log_text.config(state=tk.NORMAL)
        
        # Get current end position
        end_pos = self.log_text.index(tk.END)
        line_start = f"{float(end_pos) - 1.0:.1f}"
        
        # Insert timestamp with special formatting
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Insert icon with appropriate color
        self.log_text.insert(tk.END, icon, icon_tag)
        
        # Insert the actual message with appropriate color
        self.log_text.insert(tk.END, f"{message}\n", log_type)
        
        # Apply background color to the entire line
        line_end = self.log_text.index(tk.END + "-1c")
        self.log_text.tag_add(bg_tag, line_start, line_end)
        
        # Auto-scroll if enabled
        if hasattr(self, 'autoscroll_var') and self.autoscroll_var.get():
            self.log_text.see(tk.END)
            
        self.log_text.config(state=tk.DISABLED)
        
        # Update status bar with the same message and type
        self.update_status(message, log_type)
        
        # Auto-save log if it gets too large (more than 1000 lines)
        if float(self.log_text.index('end-1c').split('.')[0]) > 1000:
            self.save_log()
    
    def save_log(self):
        """Save the current log to a file"""
        try:
            log_filename = f"backlink_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(log_filename, "w") as f:
                f.write(self.log_text.get("1.0", tk.END))
            
            # Clear log
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete("1.0", tk.END)
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Log saved to {log_filename}\n", "info")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        except Exception as e:
            self.log(f"Error saving log: {str(e)}", "error")
    
    def start_bot(self):
        if self.running:
            if self.paused:
                self.paused = False
                self.log("Bot resumed", "info")
                self.pause_btn.configure(text="Pause")
                return
            messagebox.showinfo("Info", "Bot is already running")
            return
        
        if not self.links:
            messagebox.showerror("Error", "No links loaded. Please load links first.")
            return
        
        # Check if user information is filled
        if not self.author_var.get() or not self.email_var.get() or not self.url_var.get() or not self.comment_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Please fill in all required comment fields in the Settings tab before starting.")
            # Switch to settings tab
            self.tabview.set("Settings")  # Use set method instead of select
            return
            
        # Update post data from settings
        self.post_data['author'] = self.author_var.get()
        self.post_data['email'] = self.email_var.get()
        self.post_data['url'] = self.url_var.get()
        self.post_data['comment'] = self.comment_text.get("1.0", tk.END).strip()
        
        # Initialize stats for this session
        self.stats['session_start'] = datetime.now()
        
        self.current_link_index = 0
        self.running = True
        self.thread = threading.Thread(target=self.run_bot, daemon=True)
        self.thread.start()
        self.log("Bot started", "success")
        
        # Update UI
        self.start_btn.configure(state=tk.DISABLED)
        self.pause_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.NORMAL)
    
    def pause_bot(self):
        if not self.running:
            messagebox.showinfo("Info", "Bot is not running")
            return
        
        self.paused = not self.paused
        if self.paused:
            status = "paused"
            self.pause_btn.configure(text="Start")
            log_type = "warning"
        else:
            status = "resumed"
            self.pause_btn.configure(text="Pause")
            log_type = "info"
            
        self.log(f"Bot {status}", log_type)
    
    def stop_bot(self):
        if not self.running:
            messagebox.showinfo("Info", "Bot is not running")
            return
        
        self.running = False
        self.paused = False
        self.log("Bot stopped", "warning")
        
        # Update UI
        self.start_btn.configure(state=tk.NORMAL)
        self.pause_btn.configure(state=tk.NORMAL, text="Pause")
        self.stop_btn.configure(state=tk.DISABLED)
    
    def run_bot(self):
        delay = float(self.delay_var.get())
        success_file = self.success_file_var.get()
        
        while self.running and self.current_link_index < len(self.links):
            if self.paused:
                time.sleep(0.5)
                continue
                
            link = self.links[self.current_link_index]
            self.current_link_var.set(link)
            self.log(f"Processing: {link}", "info")
            
            try:
                success = self.process_link(link, success_file)
                if success:
                    self.stats['total_success'] += 1
                else:
                    self.stats['total_failed'] += 1
                    
                self.stats['total_processed'] += 1
                
            except Exception as e:
                self.log(f"Error processing link: {str(e)}", "error")
                self.stats['total_failed'] += 1
                self.stats['total_processed'] += 1
            
            self.current_link_index += 1
            self.progress_var.set(f"{self.current_link_index}/{len(self.links)}")
            self.progress_bar['value'] = self.current_link_index
            
            # Calculate and update progress percentage
            if len(self.links) > 0:
                percentage = int((self.current_link_index / len(self.links)) * 100)
                self.progress_percentage.set(f"{percentage}%")
            
            # Wait for the specified delay
            time.sleep(delay)
        
        if self.current_link_index >= len(self.links):
            self.log("Bot finished processing all links", "success")
            messagebox.showinfo("Complete", f"Processing complete!\nProcessed: {self.stats['total_processed']}\nSuccess: {self.stats['total_success']}\nFailed: {self.stats['total_failed']}")
        
        self.running = False
        
        # Reset UI
        self.start_btn.configure(state=tk.NORMAL)
        self.pause_btn.configure(state=tk.NORMAL, text="Pause")
        self.stop_btn.configure(state=tk.DISABLED)
    
    def process_link(self, link, success_file):
        self.log(f"[+] Processing {link}", "info")
        
        try:
            r = requests.get(link, verify=False, timeout=30)
        except Exception as e:
            self.log(f"[-] Link Error: {link}", "error")
            self.log(f"[-] {str(e)}", "error")
            return False
        
        if not r or r.status_code != 200:
            self.log(f"[-] Status {r.status_code} for Link: {link}", "error")
            return False
        
        soup = bs(r.text, 'lxml')
        form = soup.find(id='commentform')
        
        if not form:
            self.log(f"[-] Comment Form Not Found", "warning")
            return False
        
        self.log(f"[+] Form Found {link}", "success")
        
        # Use find_all instead of deprecated findAll
        inputs = {inp['name']: inp.get('value', '') for inp in form.find_all(attrs={"name": True})}
        
        # Update dynamic fields
        post_data = self.post_data.copy()
        for field in ['comment_post_ID', 'comment_parent', 'ak_js']:
            if field in inputs:
                post_data[field] = inputs.get(field, '')
        
        link_parse = urlparse(link)
        post_link = form.get('action', f"{link_parse.scheme}://{link_parse.netloc}/wp-comments-post.php")
        
        self.log(f"[+] Submitting Form", "info")
        
        headers = self.headers.copy()
        headers['referer'] = link
        headers['origin'] = f"{link_parse.scheme}://{link_parse.netloc}"
        headers['authority'] = f"{link_parse.netloc}"
        
        try:
            r = requests.post(post_link, verify=False, data=post_data, headers=headers, timeout=30)
            
            # Check if the response indicates success
            if r.status_code in [200, 302, 303]:
                self.log(f"[+] Form Submitted Successfully to {link_parse.netloc}", "success")
                
                # Save to success file
                with open(success_file, 'a') as f:
                    f.write(f'{link}\n')
                return True
            else:
                self.log(f"[-] Form Submission Failed with Status Code: {r.status_code}", "error")
                return False
                
        except Exception as e:
            self.log(f"[-] Error Submitting Form: {str(e)}", "error")
            return False

    def exit_application(self):
        """Handle application exit"""
        if self.running:
            if not messagebox.askyesno("Confirm Exit", "The bot is still running. Are you sure you want to exit?"):
                return
            self.stop_bot()
        
        # Save any unsaved data
        try:
            self.save_config()
            self.save_log()
        except Exception as e:
            print(f"Error saving data on exit: {str(e)}")
        
        self.root.quit()

if __name__ == "__main__":
    # Configure app theme before starting
    ctk.set_appearance_mode("system")  # Default to system mode
    ctk.set_default_color_theme("blue")  # Default color theme
    
    # Create the main window
    root = ctk.CTk()
    root.title("WordPress Backlink Pro")
    
    # Set minimum window size and default size
    root.minsize(1280, 800)  # Minimum size
    root.geometry("1280x800")  # Default/starting size
    
    # Configure grid weights to make the window responsive
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Configure DPI awareness for high-resolution displays
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    # Set app icon if available
    try:
        # Skip icon loading to avoid errors
        pass
    except Exception as e:
        print(f"Error setting app icon: {str(e)}")
    
    # Ensure the necessary directories exist
    os.makedirs('logs', exist_ok=True)
    
    # Create the application
    app = BacklinkBotGUI(root)
    
    # Center the window on screen
    window_width = 1280
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_right = int(screen_width/2 - window_width/2)
    position_down = int(screen_height/2 - window_height/2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    
    # Add window close handler
    root.protocol("WM_DELETE_WINDOW", app.exit_application)
    
    # Start the application
    root.mainloop() 