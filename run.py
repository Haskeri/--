from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

app.run(debug=True, port=5000, host='0.0.0.0')
