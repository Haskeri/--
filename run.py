import traceback
import sys
import os

try:
    print("Запуск приложения...", flush=True)
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'НЕ ЗАДАН')}", flush=True)

    from app import create_app, db
    app = create_app()
    print("Приложение создано", flush=True)

    with app.app_context():
        print("Инициализация БД...", flush=True)
        db.create_all()
    print("БД инициализирована", flush=True)

    print("Запуск Flask на 0.0.0.0:5000", flush=True)
    app.run(debug=True, port=8080, host='0.0.0.0')
except BaseException as e:
    print(f"ОШИБКА: {e}", flush=True)
    traceback.print_exc()
    input("Нажмите Enter для выхода...")
