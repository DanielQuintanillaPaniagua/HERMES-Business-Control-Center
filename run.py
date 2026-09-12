from app import create_app, db

app = create_app()

# Crear las tablas de la base de datos si no existen
with app.app_context():
    db.create_all()
    print("✅ Base de datos inicializada en instance/hermes.db")


if __name__ == '__main__':
    app.run(debug=True, port=5000)