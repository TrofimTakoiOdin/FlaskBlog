from flask_blog import create_app

app = create_app(environment='development')  # Or 'testing'

if __name__ == '__main__':
    app.run(debug=True)
