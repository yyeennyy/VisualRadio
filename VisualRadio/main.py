from __init__ import create_app

app, db = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5001')