from app import app, db 

# DB自動作成
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()