# gui_interface.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import os
import platform

from ps.cli import PSApp
from ps.errors import PSUserError
from ps.models import code_to_type
from ps.help_text import HELP_TEXT


# ========== СОВРЕМЕННЫЙ ТЁМНЫЙ ДИЗАЙН ==========
class ModernStyles:
    """Современные стили для интерфейса"""
    
    # Цветовая схема (тёмная тема)
    COLORS = {
        # Основные цвета
        'bg_dark': '#1e1e1e',          # Тёмный фон
        'bg_medium': '#252526',         # Средний фон
        'bg_light': '#2d2d30',          # Светлый фон
        'fg_primary': '#cccccc',        # Основной текст
        'fg_secondary': '#999999',       # Второстепенный текст
        'fg_bright': '#ffffff',          # Яркий текст
        
        # Акцентные цвета
        'accent_blue': '#007acc',        # Синий (выделение)
        'accent_green': '#6a9955',       # Зелёный (успех)
        'accent_red': '#f48771',          # Красный (ошибка)
        'accent_orange': '#ce9178',       # Оранжевый (предупреждение)
        'accent_purple': '#c586c0',       # Фиолетовый (инфо)
        'accent_yellow': '#dcdcaa',       # Жёлтый
        
        # Границы
        'border': '#3f3f46',              # Цвет границ
        
        # Статусы
        'success': '#89d185',             # Успех
        'error': '#f14c4c',               # Ошибка
        'warning': '#cca700',              # Предупреждение
        'info': '#3794ff',                 # Информация
        
        # Типы компонентов
        'type_product': '#4ec9b0',         # Изделие (бирюзовый)
        'type_unit': '#ce9178',            # Узел (оранжевый)
        'type_detail': '#9cdcfe',          # Деталь (голубой)
    }
    
    # Шрифты
    FONTS = {
        'default': ('Segoe UI', 10) if platform.system() == 'Windows' else ('SF Pro Text', 10),
        'bold': ('Segoe UI', 10, 'bold') if platform.system() == 'Windows' else ('SF Pro Text', 10, 'bold'),
        'mono': ('Consolas', 10) if platform.system() == 'Windows' else ('Menlo', 10),
        'small': ('Segoe UI', 9) if platform.system() == 'Windows' else ('SF Pro Text', 9),
        'title': ('Segoe UI', 12, 'bold') if platform.system() == 'Windows' else ('SF Pro Display', 12, 'bold'),
        'header': ('Segoe UI', 11, 'bold') if platform.system() == 'Windows' else ('SF Pro Display', 11, 'bold'),
    }
    
    # Иконки (символы Unicode)
    ICONS = {
        'file': '📄',
        'folder': '📁',
        'component': '🔧',
        'product': '🏭',
        'unit': '⚙️',
        'detail': '🔩',
        'spec': '🔗',
        'delete': '🗑️',
        'restore': '↩️',
        'truncate': '🧹',
        'refresh': '🔄',
        'tree': '🌳',
        'list': '📋',
        'output': '📝',
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅',
        'add': '➕',
        'edit': '✏️',
        'search': '🔍',
        'settings': '⚙️',
        'help': '❓',
        'quit': '🚪',
    }


# ========== СОВРЕМЕННЫЕ ВИДЖЕТЫ ==========

class ModernButton(tk.Frame):
    """Современная кнопка с иконкой и текстом"""
    
    def __init__(self, parent, text, icon=None, command=None, 
                 style='default', width=None, **kwargs):
        super().__init__(parent, bg=ModernStyles.COLORS['bg_medium'])
        
        self.command = command
        self.style = style
        
        # Определяем цвета в зависимости от стиля
        if style == 'primary':
            bg_color = ModernStyles.COLORS['accent_blue']
            fg_color = ModernStyles.COLORS['fg_bright']
            hover_color = '#1c8ae0'
        elif style == 'success':
            bg_color = ModernStyles.COLORS['accent_green']
            fg_color = ModernStyles.COLORS['fg_bright']
            hover_color = '#7fb06d'
        elif style == 'danger':
            bg_color = ModernStyles.COLORS['accent_red']
            fg_color = ModernStyles.COLORS['fg_bright']
            hover_color = '#ff6b6b'
        else:
            bg_color = ModernStyles.COLORS['bg_light']
            fg_color = ModernStyles.COLORS['fg_primary']
            hover_color = '#3e3e42'
        
        # Создаем внутреннюю кнопку
        self.btn = tk.Label(self, text=f"{icon} {text}" if icon else text,
                           bg=bg_color, fg=fg_color,
                           font=ModernStyles.FONTS['default'],
                           padx=15, pady=8, cursor='hand2')
        self.btn.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем события
        self.btn.bind('<Button-1>', self.on_click)
        self.btn.bind('<Enter>', lambda e: self.btn.config(bg=hover_color))
        self.btn.bind('<Leave>', lambda e: self.btn.config(bg=bg_color))
        
        if width:
            self.config(width=width)
    
    def on_click(self, event):
        if self.command:
            self.command()


class ModernEntry(ttk.Entry):
    """Современное поле ввода"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TEntry',
                       fieldbackground=ModernStyles.COLORS['bg_light'],
                       background=ModernStyles.COLORS['bg_light'],
                       foreground=ModernStyles.COLORS['fg_primary'],
                       insertcolor=ModernStyles.COLORS['fg_primary'],
                       bordercolor=ModernStyles.COLORS['border'],
                       lightcolor=ModernStyles.COLORS['border'],
                       darkcolor=ModernStyles.COLORS['border'])
        
        self.config(style='Modern.TEntry')


class ModernCombobox(ttk.Combobox):
    """Современный выпадающий список"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        style = ttk.Style()
        style.configure('Modern.TCombobox',
                       fieldbackground=ModernStyles.COLORS['bg_light'],
                       background=ModernStyles.COLORS['bg_light'],
                       foreground=ModernStyles.COLORS['fg_primary'],
                       arrowcolor=ModernStyles.COLORS['fg_primary'],
                       bordercolor=ModernStyles.COLORS['border'])
        
        self.config(style='Modern.TCombobox')


class ModernTreeview(ttk.Treeview):
    """Современное дерево с цветным оформлением"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.Treeview',
                       background=ModernStyles.COLORS['bg_light'],
                       foreground=ModernStyles.COLORS['fg_primary'],
                       fieldbackground=ModernStyles.COLORS['bg_light'],
                       bordercolor=ModernStyles.COLORS['border'],
                       lightcolor=ModernStyles.COLORS['border'],
                       darkcolor=ModernStyles.COLORS['border'])
        
        style.configure('Modern.Treeview.Heading',
                       background=ModernStyles.COLORS['bg_medium'],
                       foreground=ModernStyles.COLORS['fg_primary'],
                       relief='flat',
                       bordercolor=ModernStyles.COLORS['border'])
        
        style.map('Modern.Treeview',
                  background=[('selected', ModernStyles.COLORS['accent_blue'])],
                  foreground=[('selected', ModernStyles.COLORS['fg_bright'])])
        
        self.config(style='Modern.Treeview')


# ========== ДИАЛОГИ ==========

class ModernDialog:
    """Базовый класс для современных диалогов"""
    
    def __init__(self, parent, title, width=500, height=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.configure(bg=ModernStyles.COLORS['bg_dark'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем окно
        self.dialog.update_idletasks()
        if not height:
            height = self.dialog.winfo_height()
        
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Основной контейнер
        self.main_frame = tk.Frame(self.dialog, bg=ModernStyles.COLORS['bg_dark'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)


class InputDialog(ModernDialog):
    """Диалог ввода данных"""
    
    def __init__(self, parent, title, fields):
        super().__init__(parent, title, height=len(fields) * 70 + 100)
        
        self.result = None
        self.entries = {}
        
        # Заголовок
        tk.Label(self.main_frame, text=title, 
                font=ModernStyles.FONTS['title'],
                bg=ModernStyles.COLORS['bg_dark'],
                fg=ModernStyles.COLORS['fg_bright']).pack(pady=(0, 20))
        
        # Поля ввода
        for i, (label, field_type) in enumerate(fields):
            frame = tk.Frame(self.main_frame, bg=ModernStyles.COLORS['bg_dark'])
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame, text=label, width=20, anchor='w',
                    bg=ModernStyles.COLORS['bg_dark'],
                    fg=ModernStyles.COLORS['fg_primary'],
                    font=ModernStyles.FONTS['default']).pack(side=tk.LEFT)
            
            if isinstance(field_type, dict) and 'combobox' in field_type:
                var = tk.StringVar()
                entry = ModernCombobox(frame, textvariable=var, width=30)
                entry['values'] = field_type['combobox']
                entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            else:
                var = tk.StringVar()
                entry = ModernEntry(frame, textvariable=var, width=30)
                entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            
            self.entries[label] = var
        
        # Кнопки
        btn_frame = tk.Frame(self.main_frame, bg=ModernStyles.COLORS['bg_dark'])
        btn_frame.pack(pady=30)
        
        ModernButton(btn_frame, text="OK", icon='✅', 
                    style='primary', command=self.ok).pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, text="Отмена", icon='❌', 
                    style='default', command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def ok(self):
        self.result = {label: var.get() for label, var in self.entries.items()}
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


class ComponentInfoDialog(ModernDialog):
    """Диалог информации о компоненте"""
    
    def __init__(self, parent, component_name, references):
        super().__init__(parent, f"Информация: {component_name}", height=400)
        
        # Заголовок с иконкой в зависимости от типа
        tk.Label(self.main_frame, 
                text=f"{ModernStyles.ICONS['info']} {component_name}",
                font=ModernStyles.FONTS['title'],
                bg=ModernStyles.COLORS['bg_dark'],
                fg=ModernStyles.COLORS['fg_bright']).pack(pady=(0, 20))
        
        if references:
            # Статистика
            stats_frame = tk.Frame(self.main_frame, bg=ModernStyles.COLORS['bg_medium'])
            stats_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(stats_frame, 
                    text=f"Используется в {len(references)} месте:",
                    font=ModernStyles.FONTS['bold'],
                    bg=ModernStyles.COLORS['bg_medium'],
                    fg=ModernStyles.COLORS['fg_bright']).pack(pady=10)
            
            # Список ссылок
            list_frame = tk.Frame(self.main_frame, bg=ModernStyles.COLORS['bg_light'])
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            # Заголовки
            headers = tk.Frame(list_frame, bg=ModernStyles.COLORS['bg_medium'])
            headers.pack(fill=tk.X)
            
            tk.Label(headers, text="Родитель", width=20, anchor='w',
                    bg=ModernStyles.COLORS['bg_medium'],
                    fg=ModernStyles.COLORS['fg_secondary']).pack(side=tk.LEFT, padx=10, pady=5)
            tk.Label(headers, text="Кратность", width=10, anchor='w',
                    bg=ModernStyles.COLORS['bg_medium'],
                    fg=ModernStyles.COLORS['fg_secondary']).pack(side=tk.LEFT, padx=10, pady=5)
            
            # Список
            canvas = tk.Canvas(list_frame, bg=ModernStyles.COLORS['bg_light'],
                              highlightthickness=0)
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
            
            scrollable_frame = tk.Frame(canvas, bg=ModernStyles.COLORS['bg_light'])
            scrollable_frame.bind('<Configure>', 
                                 lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)
            
            for parent_name, qty in references:
                item_frame = tk.Frame(scrollable_frame, bg=ModernStyles.COLORS['bg_light'])
                item_frame.pack(fill=tk.X, pady=2)
                
                tk.Label(item_frame, text=parent_name, width=20, anchor='w',
                        bg=ModernStyles.COLORS['bg_light'],
                        fg=ModernStyles.COLORS['fg_primary']).pack(side=tk.LEFT, padx=10)
                tk.Label(item_frame, text=f"×{qty}", width=10, anchor='w',
                        bg=ModernStyles.COLORS['bg_light'],
                        fg=ModernStyles.COLORS['accent_yellow']).pack(side=tk.LEFT, padx=10)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        else:
            # Компонент не используется
            tk.Label(self.main_frame, 
                    text=f"{ModernStyles.ICONS['success']} Компонент нигде не используется",
                    font=ModernStyles.FONTS['default'],
                    bg=ModernStyles.COLORS['bg_dark'],
                    fg=ModernStyles.COLORS['success']).pack(pady=50)
        
        # Кнопка закрытия
        ModernButton(self.main_frame, text="Закрыть", icon='❌',
                    command=self.dialog.destroy).pack(pady=20)


# ========== ОСНОВНОЕ ПРИЛОЖЕНИЕ ==========

@dataclass
class ComponentNode:
    """Узел дерева компонентов"""
    name: str
    type: str
    ptr: int
    children: List['ComponentNode']
    parent: Optional['ComponentNode']


class ComponentTree:
    """Модель дерева компонентов"""
    
    def __init__(self, app: PSApp):
        self.app = app
        self.nodes: Dict[int, ComponentNode] = {}
        self.root_nodes: List[ComponentNode] = []
        
    def rebuild(self):
        """Перестроить дерево из данных app"""
        self.nodes.clear()
        self.root_nodes.clear()
        
        if not self.app.is_open():
            return
            
        core = self.app.core
            
        # Создаем узлы
        for ptr, rec, name in core.iter_products(include_deleted=False):
            node = ComponentNode(
                name=name,
                type=code_to_type(core._type_by_ptr.get(ptr, "?")),
                ptr=ptr,
                children=[],
                parent=None
            )
            self.nodes[ptr] = node
        
        # Строим связи
        for ptr, rec, name in core.iter_products(include_deleted=False):
            node = self.nodes[ptr]
            
            spec_ptr = rec.spec_ptr
            while spec_ptr != 1:
                try:
                    spec_rec = core.prs.read_record(spec_ptr)
                    if spec_rec.deleted == 0:
                        child_ptr = spec_rec.prod_ptr
                        if child_ptr in self.nodes:
                            child_node = self.nodes[child_ptr]
                            child_node.parent = node
                            node.children.append(child_node)
                    spec_ptr = spec_rec.next_ptr
                except:
                    break
        
        # Корневые узлы
        for node in self.nodes.values():
            if node.parent is None:
                self.root_nodes.append(node)
        
        self.root_nodes.sort(key=lambda x: x.name.lower())
    
    def get_item_info(self, tree, item_id) -> Dict:
        """Информация об элементе дерева"""
        item = tree.item(item_id)
        item_text = item['text']
        parent_id = tree.parent(item_id)
        
        return {
            'id': item_id,
            'text': item_text,
            'parent_id': parent_id,
            'is_component': parent_id == '',
            'values': item['values']
        }
    
    def find_component_references(self, component_name: str) -> List[Tuple[str, int]]:
        """Найти ссылки на компонент"""
        references = []
        
        if not self.app.is_open():
            return references
        
        core = self.app.core
        
        for ptr, rec, name in core.iter_products(include_deleted=False):
            spec_ptr = rec.spec_ptr
            while spec_ptr != 1:
                try:
                    spec_rec = core.prs.read_record(spec_ptr)
                    if spec_rec.deleted == 0:
                        child_ptr = spec_rec.prod_ptr
                        if child_ptr in self.nodes:
                            child_node = self.nodes[child_ptr]
                            if child_node.name.lower() == component_name.lower():
                                references.append((name, spec_rec.qty))
                    spec_ptr = spec_rec.next_ptr
                except:
                    break
        
        return references


class ModernPSGUI:
    """Современный GUI для управления спецификациями"""
    
    def __init__(self):
        self.app = PSApp()
        self.tree_model = ComponentTree(self.app)
        self.current_file = None
        
        # Настройка главного окна
        self.root = tk.Tk()
        self.root.title("PS Manager - Управление спецификациями")
        self.root.geometry("1400x900")
        self.root.configure(bg=ModernStyles.COLORS['bg_dark'])
        
        # Центрируем
        self.center_window()
        
        # Инициализация
        self.setup_styles()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_main_panel()
        self.setup_statusbar()
        self.setup_keyboard_shortcuts()
        
        self.update_state()
    
    def center_window(self):
        """Центрирование окна"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка Notebook (вкладки)
        style.configure('TNotebook', 
                       background=ModernStyles.COLORS['bg_dark'],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=ModernStyles.COLORS['bg_medium'],
                       foreground=ModernStyles.COLORS['fg_primary'],
                       padding=[15, 5],
                       font=ModernStyles.FONTS['default'])
        style.map('TNotebook.Tab',
                 background=[('selected', ModernStyles.COLORS['bg_light']),
                           ('active', ModernStyles.COLORS['bg_light'])],
                 foreground=[('selected', ModernStyles.COLORS['fg_bright'])])
    
    def setup_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root, bg=ModernStyles.COLORS['bg_medium'],
                         fg=ModernStyles.COLORS['fg_primary'],
                         activebackground=ModernStyles.COLORS['accent_blue'],
                         activeforeground=ModernStyles.COLORS['fg_bright'])
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0, bg=ModernStyles.COLORS['bg_medium'],
                           fg=ModernStyles.COLORS['fg_primary'],
                           activebackground=ModernStyles.COLORS['accent_blue'])
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label=f"{ModernStyles.ICONS['file']} Создать...", 
                            command=self.create_file, accelerator="Ctrl+N")
        file_menu.add_command(label=f"{ModernStyles.ICONS['folder']} Открыть...", 
                            command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label=f"{ModernStyles.ICONS['file']} Закрыть", 
                            command=self.close_file, accelerator="Ctrl+W")
        file_menu.add_separator()
        file_menu.add_command(label=f"{ModernStyles.ICONS['quit']} Выход", 
                            command=self.quit, accelerator="Ctrl+Q")
        
        # Правка
        edit_menu = tk.Menu(menubar, tearoff=0, bg=ModernStyles.COLORS['bg_medium'],
                           fg=ModernStyles.COLORS['fg_primary'],
                           activebackground=ModernStyles.COLORS['accent_blue'])
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label=f"{ModernStyles.ICONS['add']} Добавить компонент...", 
                            command=self.add_component, accelerator="Ctrl+Shift+C")
        edit_menu.add_command(label=f"{ModernStyles.ICONS['spec']} Добавить в спецификацию...", 
                            command=self.add_spec, accelerator="Ctrl+Shift+S")
        edit_menu.add_separator()
        edit_menu.add_command(label=f"{ModernStyles.ICONS['delete']} Удалить компонент", 
                            command=self.delete_item, accelerator="Del")
        edit_menu.add_command(label=f"{ModernStyles.ICONS['delete']} Удалить связь", 
                            command=self.delete_spec_link_dialog, accelerator="Ctrl+Del")
        edit_menu.add_separator()
        edit_menu.add_command(label=f"{ModernStyles.ICONS['restore']} Восстановить", 
                            command=self.restore_item, accelerator="Ctrl+R")
        edit_menu.add_command(label=f"{ModernStyles.ICONS['truncate']} Очистить (Truncate)", 
                            command=self.truncate, accelerator="Ctrl+T")
        
        # Вид
        view_menu = tk.Menu(menubar, tearoff=0, bg=ModernStyles.COLORS['bg_medium'],
                           fg=ModernStyles.COLORS['fg_primary'],
                           activebackground=ModernStyles.COLORS['accent_blue'])
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label=f"{ModernStyles.ICONS['refresh']} Обновить", 
                            command=self.refresh_view, accelerator="F5")
        view_menu.add_separator()
        view_menu.add_command(label=f"{ModernStyles.ICONS['list']} Все компоненты", 
                            command=self.show_all)
        view_menu.add_command(label=f"{ModernStyles.ICONS['tree']} Дерево", 
                            command=self.refresh_view)
        
        # Справка
        help_menu = tk.Menu(menubar, tearoff=0, bg=ModernStyles.COLORS['bg_medium'],
                           fg=ModernStyles.COLORS['fg_primary'],
                           activebackground=ModernStyles.COLORS['accent_blue'])
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label=f"{ModernStyles.ICONS['help']} Справка", 
                            command=self.show_help, accelerator="F1")
        help_menu.add_command(label=f"{ModernStyles.ICONS['info']} О программе", 
                            command=self.show_about)
    
    def setup_toolbar(self):
        """Создание современной панели инструментов"""
        # Верхняя панель с заголовком
        header = tk.Frame(self.root, bg=ModernStyles.COLORS['bg_medium'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Логотип/название
        tk.Label(header, text="⚡ PS Manager", 
                font=ModernStyles.FONTS['title'],
                bg=ModernStyles.COLORS['bg_medium'],
                fg=ModernStyles.COLORS['fg_bright']).pack(side=tk.LEFT, padx=15)
        
        # Статус файла
        self.file_indicator = tk.Label(header, text="●", 
                                       font=ModernStyles.FONTS['bold'],
                                       bg=ModernStyles.COLORS['bg_medium'],
                                       fg=ModernStyles.COLORS['error'])
        self.file_indicator.pack(side=tk.RIGHT, padx=15)
        
        # Панель инструментов
        toolbar = tk.Frame(self.root, bg=ModernStyles.COLORS['bg_dark'])
        toolbar.pack(fill=tk.X, pady=10, padx=10)
        
        # Группы кнопок
        groups = [
            {
                'buttons': [
                    ('📁', 'Создать', self.create_file, 'primary'),
                    ('📂', 'Открыть', self.open_file, 'primary'),
                ]
            },
            {
                'buttons': [
                    ('➕', 'Компонент', self.add_component, 'default'),
                    ('🔗', 'Спецификация', self.add_spec, 'default'),
                ]
            },
            {
                'buttons': [
                    ('🗑️', 'Компонент', self.delete_item, 'danger'),
                    ('🔗❌', 'Связь', self.delete_spec_link_dialog, 'danger'),
                ]
            },
            {
                'buttons': [
                    ('↩️', 'Восстановить', self.restore_item, 'success'),
                    ('🧹', 'Очистить', self.truncate, 'warning'),
                ]
            },
            {
                'buttons': [
                    ('🔄', 'Обновить', self.refresh_view, 'default'),
                    ('ℹ️', 'Инфо', self.show_component_info, 'default'),
                ]
            },
        ]
        
        for group in groups:
            frame = tk.Frame(toolbar, bg=ModernStyles.COLORS['bg_dark'])
            frame.pack(side=tk.LEFT, padx=5)
            
            for icon, text, cmd, style in group['buttons']:
                btn = ModernButton(frame, text=text, icon=icon, 
                                  command=cmd, style=style)
                btn.pack(side=tk.LEFT, padx=2)
    
    def setup_main_panel(self):
        """Создание основной панели"""
        # Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Дерево"
        self.tree_frame = tk.Frame(self.notebook, bg=ModernStyles.COLORS['bg_dark'])
        self.notebook.add(self.tree_frame, text=f" {ModernStyles.ICONS['tree']} Дерево компонентов ")
        self.setup_tree_view()
        
        # Вкладка "Список"
        self.list_frame = tk.Frame(self.notebook, bg=ModernStyles.COLORS['bg_dark'])
        self.notebook.add(self.list_frame, text=f" {ModernStyles.ICONS['list']} Список компонентов ")
        self.setup_list_view()
        
        # Вкладка "Вывод"
        self.output_frame = tk.Frame(self.notebook, bg=ModernStyles.COLORS['bg_dark'])
        self.notebook.add(self.output_frame, text=f" {ModernStyles.ICONS['output']} Вывод ")
        self.setup_output_view()
    
    def setup_tree_view(self):
        """Настройка древовидного просмотра"""
        # Панель поиска
        search_frame = tk.Frame(self.tree_frame, bg=ModernStyles.COLORS['bg_medium'])
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text=f"{ModernStyles.ICONS['search']} Поиск:", 
                bg=ModernStyles.COLORS['bg_medium'],
                fg=ModernStyles.COLORS['fg_primary']).pack(side=tk.LEFT, padx=10, pady=8)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_tree())
        
        search_entry = ModernEntry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Дерево
        tree_container = tk.Frame(self.tree_frame, bg=ModernStyles.COLORS['bg_dark'])
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ModernTreeview(tree_container, columns=("type",), show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Полосы прокрутки
        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, 
                                 command=self.tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=v_scroll.set)
        
        # Теги для раскрашивания типов
        self.tree.tag_configure('product', foreground=ModernStyles.COLORS['type_product'])
        self.tree.tag_configure('unit', foreground=ModernStyles.COLORS['type_unit'])
        self.tree.tag_configure('detail', foreground=ModernStyles.COLORS['type_detail'])
        
        # Контекстное меню
        self.tree.bind("<Button-3>", self.show_tree_context_menu)
        self.tree.bind("<Double-Button-1>", lambda e: self.show_tree())
    
    def setup_list_view(self):
        """Настройка табличного просмотра"""
        # Панель поиска
        search_frame = tk.Frame(self.list_frame, bg=ModernStyles.COLORS['bg_medium'])
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text=f"{ModernStyles.ICONS['search']} Поиск:", 
                bg=ModernStyles.COLORS['bg_medium'],
                fg=ModernStyles.COLORS['fg_primary']).pack(side=tk.LEFT, padx=10, pady=8)
        
        self.list_search_var = tk.StringVar()
        self.list_search_var.trace('w', lambda *args: self.filter_list())
        
        search_entry = ModernEntry(search_frame, textvariable=self.list_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Таблица
        list_container = tk.Frame(self.list_frame, bg=ModernStyles.COLORS['bg_dark'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("name", "type")
        self.list_view = ModernTreeview(list_container, columns=columns, show="headings")
        
        self.list_view.heading("name", text="Имя компонента")
        self.list_view.heading("type", text="Тип")
        
        self.list_view.column("name", width=400)
        self.list_view.column("type", width=150)
        
        self.list_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Полосы прокрутки
        v_scroll = ttk.Scrollbar(list_container, orient=tk.VERTICAL, 
                                 command=self.list_view.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_view.configure(yscrollcommand=v_scroll.set)
        
        # Контекстное меню
        self.list_view.bind("<Button-3>", self.show_list_context_menu)
        self.list_view.bind("<Double-Button-1>", lambda e: self.show_tree())
    
    def setup_output_view(self):
        """Настройка области вывода"""
        # Панель с кнопками
        toolbar = tk.Frame(self.output_frame, bg=ModernStyles.COLORS['bg_medium'])
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ModernButton(toolbar, text="Очистить", icon='🧹',
                    command=self.clear_output, style='default').pack(side=tk.LEFT, padx=5, pady=5)
        
        ModernButton(toolbar, text="Копировать", icon='📋',
                    command=self.copy_output, style='default').pack(side=tk.LEFT, padx=5, pady=5)
        
        # Текст вывода
        self.output_text = ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            font=ModernStyles.FONTS['mono'],
            bg=ModernStyles.COLORS['bg_light'],
            fg=ModernStyles.COLORS['fg_primary'],
            insertbackground=ModernStyles.COLORS['fg_primary'],
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Теги
        self.output_text.tag_config("error", foreground=ModernStyles.COLORS['error'])
        self.output_text.tag_config("success", foreground=ModernStyles.COLORS['success'])
        self.output_text.tag_config("info", foreground=ModernStyles.COLORS['info'])
        self.output_text.tag_config("warning", foreground=ModernStyles.COLORS['warning'])
        self.output_text.tag_config("bold", font=ModernStyles.FONTS['bold'])
    
    def setup_statusbar(self):
        """Создание строки состояния"""
        self.statusbar = tk.Frame(self.root, bg=ModernStyles.COLORS['bg_medium'], height=30)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        self.statusbar.pack_propagate(False)
        
        # Статус
        self.status_label = tk.Label(self.statusbar, text="✓ Готов", 
                                     bg=ModernStyles.COLORS['bg_medium'],
                                     fg=ModernStyles.COLORS['success'],
                                     font=ModernStyles.FONTS['small'])
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Информация о файле
        self.file_info_label = tk.Label(self.statusbar, text="📁 Файл не открыт",
                                        bg=ModernStyles.COLORS['bg_medium'],
                                        fg=ModernStyles.COLORS['fg_secondary'],
                                        font=ModernStyles.FONTS['small'])
        self.file_info_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_keyboard_shortcuts(self):
        """Настройка горячих клавиш"""
        self.root.bind('<Control-n>', lambda e: self.create_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-w>', lambda e: self.close_file())
        self.root.bind('<Control-q>', lambda e: self.quit())
        self.root.bind('<Control-Shift-C>', lambda e: self.add_component())
        self.root.bind('<Control-Shift-S>', lambda e: self.add_spec())
        self.root.bind('<Delete>', lambda e: self.delete_item())
        self.root.bind('<Control-Delete>', lambda e: self.delete_spec_link_dialog())
        self.root.bind('<Control-r>', lambda e: self.restore_item())
        self.root.bind('<Control-t>', lambda e: self.truncate())
        self.root.bind('<F5>', lambda e: self.refresh_view())
        self.root.bind('<F1>', lambda e: self.show_help())
    
    def filter_tree(self):
        """Фильтрация дерева по поиску"""
        search = self.search_var.get().lower()
        
        # Очищаем дерево
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search:
            # Если поиск пустой, показываем всё
            for node in self.tree_model.root_nodes:
                self._add_tree_node("", node)
        else:
            # Показываем только совпадения
            for node in self.tree_model.root_nodes:
                if search in node.name.lower():
                    self._add_tree_node("", node)
    
    def filter_list(self):
        """Фильтрация списка по поиску"""
        search = self.list_search_var.get().lower()
        
        for item in self.list_view.get_children():
            self.list_view.delete(item)
        
        for node in self.tree_model.root_nodes:
            if not search or search in node.name.lower():
                self._add_list_items(node)
    
    def _add_tree_node(self, parent, node: ComponentNode):
        """Добавление узла в дерево с цветом"""
        # Определяем тег по типу
        if node.type == "Изделие":
            tag = 'product'
        elif node.type == "Узел":
            tag = 'unit'
        else:
            tag = 'detail'
        
        item_id = self.tree.insert(parent, tk.END, text=node.name, 
                                   values=(node.type,), tags=(tag,))
        
        node.children.sort(key=lambda x: x.name.lower())
        for child in node.children:
            self._add_tree_node(item_id, child)
    
    def _add_list_items(self, node: ComponentNode):
        """Добавление элементов в список"""
        self.list_view.insert("", tk.END, values=(node.name, node.type), iid=str(node.ptr))
        for child in node.children:
            self._add_list_items(child)
    
    def get_selected_component(self) -> Optional[str]:
        """Получить имя выбранного компонента"""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])['text']
        
        selection = self.list_view.selection()
        if selection:
            return self.list_view.item(selection[0])['values'][0]
        
        return None
    
    def show_tree_context_menu(self, event):
        """Контекстное меню для дерева"""
        try:
            item_id = self.tree.identify_row(event.y)
            if not item_id:
                return
            
            self.tree.selection_set(item_id)
            info = self.tree_model.get_item_info(self.tree, item_id)
            
            menu = tk.Menu(self.tree, tearoff=0, bg=ModernStyles.COLORS['bg_medium'],
                          fg=ModernStyles.COLORS['fg_primary'],
                          activebackground=ModernStyles.COLORS['accent_blue'])
            
            if info['is_component']:
                self._add_component_menu_items(menu, info['text'])
            else:
                self._add_spec_link_menu_items(menu, info['parent_text'], info['text'])
            
            menu.add_separator()
            menu.add_command(label=f"{ModernStyles.ICONS['refresh']} Обновить", 
                           command=self.refresh_view)
            
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def show_list_context_menu(self, event):
        """Контекстное меню для списка"""
        try:
            item_id = self.list_view.identify_row(event.y)
            if not item_id:
                return
            
            self.list_view.selection_set(item_id)
            item = self.list_view.item(item_id)
            component_name = item['values'][0]
            
            menu = tk.Menu(self.list_view, tearoff=0, bg=ModernStyles.COLORS['bg_medium'],
                          fg=ModernStyles.COLORS['fg_primary'],
                          activebackground=ModernStyles.COLORS['accent_blue'])
            
            self._add_component_menu_items(menu, component_name)
            
            menu.add_separator()
            menu.add_command(label=f"{ModernStyles.ICONS['refresh']} Обновить", 
                           command=self.refresh_view)
            
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _add_component_menu_items(self, menu, component_name):
        """Пункты меню для компонента"""
        menu.add_command(label=f"{ModernStyles.ICONS['add']} Добавить компонент", 
                        command=self.add_component)
        menu.add_command(label=f"{ModernStyles.ICONS['spec']} Добавить в спецификацию", 
                        command=lambda: self.add_spec_with_parent(component_name))
        menu.add_separator()
        
        references = self.tree_model.find_component_references(component_name)
        
        if references:
            menu.add_command(label=f"{ModernStyles.ICONS['delete']} Удалить компонент", 
                           command=self.delete_item, state=tk.DISABLED)
            menu.add_command(label=f"{ModernStyles.ICONS['info']} Инфо (есть ссылки)", 
                           command=lambda: self.show_component_info_with_name(component_name))
        else:
            menu.add_command(label=f"{ModernStyles.ICONS['delete']} Удалить компонент", 
                           command=self.delete_item)
            menu.add_command(label=f"{ModernStyles.ICONS['info']} Информация", 
                           command=lambda: self.show_component_info_with_name(component_name))
        
        menu.add_command(label=f"{ModernStyles.ICONS['tree']} Показать дерево", 
                        command=lambda: self.show_tree_for_component(component_name))
    
    def _add_spec_link_menu_items(self, menu, parent_name, child_name):
        """Пункты меню для связи"""
        menu.add_command(label=f"{ModernStyles.ICONS['delete']} Удалить связь", 
                        command=lambda: self.delete_spec_link(parent_name, child_name))
        menu.add_command(label=f"{ModernStyles.ICONS['edit']} Изменить кратность", 
                        command=lambda: self.change_quantity(parent_name, child_name))
        menu.add_separator()
        menu.add_command(label=f"{ModernStyles.ICONS['tree']} Дерево родителя", 
                        command=lambda: self.show_tree_for_component(parent_name))
        menu.add_command(label=f"{ModernStyles.ICONS['tree']} Дерево потомка", 
                        command=lambda: self.show_tree_for_component(child_name))
    
    def add_spec_with_parent(self, parent_name):
        """Диалог добавления спецификации"""
        if not self.app.is_open():
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте файл!")
            return
        
        dialog = InputDialog(
            self.root,
            "Добавить в спецификацию",
            [
                ("Родитель", "entry"),
                ("Комплектующее", "entry"),
                ("Кратность", "entry")
            ]
        )
        
        dialog.entries["Родитель"].set(parent_name)
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                parent = dialog.result["Родитель"]
                child = dialog.result["Комплектующее"]
                qty = dialog.result["Кратность"] or "1"
                
                result = self.execute_cmd(f"Input({parent}/{child}, {qty})")
                self.update_state()
                self.status_label.config(text=f"✓ Добавлена связь: {parent} ← {child}")
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def show_tree_for_component(self, component_name):
        """Показать дерево компонента"""
        try:
            result = self.execute_cmd(f"Print({component_name})")
            self.notebook.select(self.output_frame)
        except Exception as e:
            self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def show_component_info(self):
        """Информация о компоненте"""
        selected = self.get_selected_component()
        if selected:
            self.show_component_info_with_name(selected)
        else:
            messagebox.showinfo("Информация", "Выберите компонент")
    
    def show_component_info_with_name(self, component_name):
        """Информация о компоненте по имени"""
        references = self.tree_model.find_component_references(component_name)
        ComponentInfoDialog(self.root, component_name, references)
    
    def delete_spec_link(self, parent: str, child: str):
        """Удаление связи"""
        if messagebox.askyesno("Подтверждение", f"Удалить связь {parent} → {child}?"):
            try:
                result = self.execute_cmd(f"Delete({parent}/{child})")
                self.update_state()
                self.status_label.config(text=f"✓ Удалена связь: {parent}/{child}")
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def delete_spec_link_dialog(self):
        """Диалог удаления связи"""
        selected = self.get_selected_component()
        
        dialog = InputDialog(
            self.root,
            "Удалить связь",
            [
                ("Родитель", "entry"),
                ("Комплектующее", "entry")
            ]
        )
        
        if selected:
            dialog.entries["Комплектующее"].set(selected)
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            parent = dialog.result["Родитель"]
            child = dialog.result["Комплектующее"]
            if parent and child:
                self.delete_spec_link(parent, child)
    
    def change_quantity(self, parent: str, child: str):
        """Изменение кратности"""
        dialog = InputDialog(
            self.root,
            "Изменить кратность",
            [("Новая кратность", "entry")]
        )
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                qty = dialog.result["Новая кратность"]
                self.execute_cmd(f"Delete({parent}/{child})")
                result = self.execute_cmd(f"Input({parent}/{child}, {qty})")
                self.update_state()
                self.status_label.config(text=f"✓ Изменена кратность: {parent}/{child} = {qty}")
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def clear_output(self):
        """Очистка вывода"""
        self.output_text.delete(1.0, tk.END)
    
    def copy_output(self):
        """Копирование вывода в буфер обмена"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        self.status_label.config(text="✓ Скопировано в буфер обмена")
    
    def log_output(self, text: str, tag: str = None):
        """Вывод текста"""
        self.output_text.insert(tk.END, text + "\n")
        if tag:
            last_line_start = self.output_text.index(f"end-2c linestart")
            last_line_end = self.output_text.index("end-1c")
            self.output_text.tag_add(tag, last_line_start, last_line_end)
        self.output_text.see(tk.END)
    
    def execute_cmd(self, cmd: str) -> str:
        """Выполнение команды"""
        self.log_output(f"> {cmd}", "info")
        try:
            result = self.app.execute(cmd)
            if result:
                self.log_output(result, "success")
            return result
        except PSUserError as e:
            self.log_output(f"✗ {e}", "error")
            raise
        except Exception as e:
            self.log_output(f"⚠ Системная ошибка: {e}", "error")
            raise
    
    def update_state(self):
        """Обновление состояния"""
        if self.app.is_open():
            self.file_indicator.config(fg=ModernStyles.COLORS['success'])
            self.file_info_label.config(
                text=f"📁 {os.path.basename(self.current_file or '')}",
                fg=ModernStyles.COLORS['fg_primary'])
        else:
            self.file_indicator.config(fg=ModernStyles.COLORS['error'])
            self.file_info_label.config(text="📁 Файл не открыт", 
                                        fg=ModernStyles.COLORS['fg_secondary'])
        
        self.refresh_view()
    
    def refresh_view(self):
        """Обновление представлений"""
        self.tree_model.rebuild()
        self.filter_tree()
        self.filter_list()
    
    # Обработчики команд
    
    def create_file(self):
        dialog = InputDialog(
            self.root,
            "Создать файл",
            [
                ("Имя файла", "entry"),
                ("Макс. длина имени", "entry"),
                ("Имя файла спецификаций (опц.)", "entry")
            ]
        )
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                name = dialog.result["Имя файла"]
                max_len = dialog.result["Макс. длина имени"]
                prs_name = dialog.result["Имя файла спецификаций (опц.)"]
                
                cmd = f"Create {name}({max_len}"
                if prs_name:
                    cmd += f", {prs_name}"
                cmd += ")"
                
                result = self.execute_cmd(cmd)
                self.current_file = name
                self.update_state()
                self.status_label.config(text=f"✓ Создан файл: {name}")
                
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("PRD файлы", "*.prd"), ("Все файлы", "*.*")]
        )
        
        if filename:
            try:
                base = os.path.splitext(os.path.basename(filename))[0]
                result = self.execute_cmd(f"Open {base}")
                self.current_file = base
                self.update_state()
                self.status_label.config(text=f"✓ Открыт файл: {base}")
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def close_file(self):
        self.app.close()
        self.current_file = None
        self.update_state()
        self.status_label.config(text="✓ Файл закрыт")
    
    def add_component(self):
        if not self.app.is_open():
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте файл!")
            return
        
        dialog = InputDialog(
            self.root,
            "Добавить компонент",
            [
                ("Имя компонента", "entry"),
                ("Тип", {"combobox": ["Изделие", "Узел", "Деталь"]})
            ]
        )
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                name = dialog.result["Имя компонента"]
                type_name = dialog.result["Тип"]
                
                result = self.execute_cmd(f"Input({name}, {type_name})")
                self.update_state()
                self.status_label.config(text=f"✓ Добавлен компонент: {name}")
                
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def add_spec(self):
        if not self.app.is_open():
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте файл!")
            return
        
        selected = self.get_selected_component()
        
        dialog = InputDialog(
            self.root,
            "Добавить в спецификацию",
            [
                ("Родитель", "entry"),
                ("Комплектующее", "entry"),
                ("Кратность", "entry")
            ]
        )
        
        if selected:
            dialog.entries["Родитель"].set(selected)
        
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                parent = dialog.result["Родитель"]
                child = dialog.result["Комплектующее"]
                qty = dialog.result["Кратность"] or "1"
                
                result = self.execute_cmd(f"Input({parent}/{child}, {qty})")
                self.update_state()
                self.status_label.config(text=f"✓ Добавлена связь: {parent} ← {child}")
                
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def delete_item(self):
        if not self.app.is_open():
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте файл!")
            return
        
        selected = self.get_selected_component()
        
        if not selected:
            messagebox.showinfo("Информация", "Выберите компонент для удаления")
            return
        
        references = self.tree_model.find_component_references(selected)
        
        if references:
            msg = f"⚠ Невозможно удалить '{selected}'\n\nИспользуется в:\n"
            for parent, qty in references:
                msg += f"  • {parent} (×{qty})\n"
            msg += "\nСначала удалите эти связи!"
            messagebox.showwarning("Невозможно удалить", msg)
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить компонент '{selected}'?"):
            try:
                result = self.execute_cmd(f"Delete({selected})")
                self.update_state()
                self.status_label.config(text=f"✓ Удален компонент: {selected}")
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def restore_item(self):
        if not self.app.is_open():
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте файл!")
            return
        
        selected = self.get_selected_component()
        
        if not selected:
            if messagebox.askyesno("Подтверждение", "Восстановить все удаленные компоненты?"):
                try:
                    result = self.execute_cmd("Restore(*)")
                    self.update_state()
                    self.status_label.config(text="✓ Восстановлены все компоненты")
                except Exception as e:
                    self.status_label.config(text=f"✗ Ошибка: {e}")
        else:
            if messagebox.askyesno("Подтверждение", f"Восстановить компонент '{selected}'?"):
                try:
                    result = self.execute_cmd(f"Restore({selected})")
                    self.update_state()
                    self.status_label.config(text=f"✓ Восстановлен компонент: {selected}")
                except Exception as e:
                    self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def truncate(self):
        if not self.app.is_open():
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте файл!")
            return
        
        if messagebox.askyesno("Подтверждение", 
                               "⚠ Это действие физически удалит все помеченные записи!\n"
                               "Продолжить?", icon='warning'):
            try:
                result = self.execute_cmd("Truncate")
                self.update_state()
                self.status_label.config(text="✓ Файлы очищены")
            except Exception as e:
                self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def show_tree(self):
        if not self.app.is_open():
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте файл!")
            return
        
        selected = self.get_selected_component()
        
        if not selected:
            messagebox.showinfo("Информация", "Выберите компонент для просмотра")
            return
        
        self.show_tree_for_component(selected)
    
    def show_all(self):
        if not self.app.is_open():
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте файл!")
            return
        
        try:
            result = self.execute_cmd("Print(*)")
            self.notebook.select(self.list_frame)
        except Exception as e:
            self.status_label.config(text=f"✗ Ошибка: {e}")
    
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка")
        help_window.geometry("700x500")
        help_window.configure(bg=ModernStyles.COLORS['bg_dark'])
        
        # Заголовок
        tk.Label(help_window, text=f"{ModernStyles.ICONS['help']} Справка", 
                font=ModernStyles.FONTS['title'],
                bg=ModernStyles.COLORS['bg_dark'],
                fg=ModernStyles.COLORS['fg_bright']).pack(pady=20)
        
        # Текст справки
        text_frame = tk.Frame(help_window, bg=ModernStyles.COLORS['bg_light'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        text = ScrolledText(text_frame, wrap=tk.WORD, 
                           font=ModernStyles.FONTS['mono'],
                           bg=ModernStyles.COLORS['bg_light'],
                           fg=ModernStyles.COLORS['fg_primary'],
                           insertbackground=ModernStyles.COLORS['fg_primary'],
                           relief=tk.FLAT,
                           borderwidth=0,
                           padx=10,
                           pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, HELP_TEXT)
        text.config(state=tk.DISABLED)
        
        # Кнопка закрытия
        ModernButton(help_window, text="Закрыть", icon='❌',
                    command=help_window.destroy).pack(pady=20)
    
    def show_about(self):
        about_text = f"""{ModernStyles.ICONS['info']} PS Manager v2.0

Современный менеджер спецификаций

✨ Особенности:
• Управление компонентами (Изделия/Узлы/Детали)
• Построение иерархических спецификаций
• Визуализация деревьев зависимостей
• Логическое удаление и восстановление
• Физическое уплотнение файлов

🎨 Современный тёмный интерфейс
⚡ Быстрые клавиши для всех операций
🔍 Умный поиск по компонентам

© 2024
        """
        
        messagebox.showinfo("О программе", about_text)
    
    def quit(self):
        if messagebox.askokcancel("Выход", "Завершить работу программы?"):
            self.app.close()
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Запуск приложения"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()


def main():
    app = ModernPSGUI()
    app.run()

    PSGUI = ModernPSGUI


if __name__ == "__main__":
    main()