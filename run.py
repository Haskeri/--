import traceback

try:
    print("Запуск приложения...")
    from app import create_app, db
    app = create_app()
    print("Приложение создано")

    with app.app_context():
        db.create_all()
    print("БД инициализирована")

    print("Запуск Flask на 0.0.0.0:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
except Exception as e:
    print(f"ОШИБКА: {e}")
    traceback.print_exc()
    input("Нажмите Enter для выхода...")
