#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Главный модуль программы управления спецификациями.
Поддерживает два режима работы:
- GUI (графический интерфейс) - по умолчанию
- CLI (командная строка) - с флагом --cli
"""

import sys
import argparse
import importlib.util
import os


def check_tkinter() -> bool:
    """Проверка наличия библиотеки tkinter"""
    return importlib.util.find_spec("tkinter") is not None


def check_gui_module() -> bool:
    """Проверка наличия модуля gui_interface"""
    try:
        # Пробуем импортировать модуль GUI
        from ps import gui_interface
        return True
    except ImportError:
        return False


def run_cli():
    """Запуск программы в режиме командной строки (CLI)"""
    from ps.cli import PSApp
    from ps.errors import PSUserError
    from ps.help_text import HELP_TEXT

    # Очищаем экран (опционально)
    os.system('cls' if os.name == 'nt' else 'clear')

    print("=" * 60)
    print("СИСТЕМА УПРАВЛЕНИЯ СПЕЦИФИКАЦИЯМИ (CLI РЕЖИМ)")
    print("=" * 60)
    print(HELP_TEXT)
    print("=" * 60)

    app = PSApp()
    exit_code = 0

    try:
        while True:
            try:
                line = input("\nPS> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nЗавершение работы...")
                break

            if not line:
                continue

            try:
                out = app.execute(line)
                if out:
                    print(out)
            except SystemExit:
                print("Завершение работы...")
                break
            except PSUserError as e:
                print(f"❌ Ошибка: {e}")
            except Exception as e:
                print(f"💥 Системная ошибка: {e}")
                exit_code = 1
    finally:
        app.close()
        print("\n👋 До свидания!")

    sys.exit(exit_code)


def run_gui():
    """Запуск программы в графическом режиме (GUI)"""
    from ps.gui_interface import ModernPSGUI

    try:
        app = ModernPSGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nЗавершение работы GUI...")
    except Exception as e:
        print(f"❌ Критическая ошибка в GUI: {e}")
        return False
    return True


def setup_environment():
    """Настройка окружения перед запуском"""
    # Добавляем текущую директорию в PATH для корректного импорта
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)


def print_banner():
    """Вывод красивого баннера"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║     УПРАВЛЕНИЕ СПЕЦИФИКАЦИЯМИ v1.0                       ║
║     Production System Management                          ║
╠══════════════════════════════════════════════════════════╣
║  Режимы запуска:                                          ║
║    • python main.py     - графический интерфейс (GUI)   ║
║    • python main.py --cli - командная строка (CLI)      ║
║    • python main.py --help - показать справку           ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Главная функция программы"""

    # Настройка окружения
    setup_environment()

    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(
        description="Система управления спецификациями",
        epilog="Примеры использования:\n"
               "  python main.py          # запуск GUI\n"
               "  python main.py --cli    # запуск CLI\n"
               "  python main.py --help   # справка",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--cli",
        action="store_true",
        help="запустить в режиме командной строки (без графического интерфейса)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Управление спецификациями v1.0"
    )

    args = parser.parse_args()

    # Если запрошен CLI режим
    if args.cli:
        run_cli()
        return

    # Иначе пытаемся запустить GUI
    print_banner()
    print("🔍 Проверка компонентов...")

    # Проверяем наличие tkinter
    if not check_tkinter():
        print("⚠️  Tkinter не найден. Запуск в режиме командной строки...")
        run_cli()
        return

    # Проверяем наличие GUI модуля
    if not check_gui_module():
        print("⚠️  Модуль графического интерфейса не найден. Запуск в режиме командной строки...")
        run_cli()
        return

    print("✅ Все компоненты загружены. Запуск графического интерфейса...\n")

    # Запускаем GUI
    success = run_gui()

    # Если GUI не запустился, переключаемся на CLI
    if not success:
        print("\n⚠️  Не удалось запустить графический интерфейс.")
        choice = input("Запустить в режиме командной строки? (д/н): ").strip().lower()
        if choice in ('д', 'да', 'y', 'yes', ''):
            run_cli()
        else:
            print("Программа завершена.")


if __name__ == "__main__":
    main()