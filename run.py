from app import create_app

app = create_app()

if __name__ == '__main__':
    # host='0.0.0.0' を追加することで、同じWi-Fi内のスマホからアクセス可能になります
    app.run(host='0.0.0.0', port=5001, debug=True)