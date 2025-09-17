import requests
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

def get_db_connection():
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@app.route('/main')
def home():
    popular_videos = [
            {"title": "maximka", "thumbnail": "https://img.youtube.com/vi/zFj1nMFmxCo/hqdefault.jpg"},
            {"title": "stas9n", "thumbnail": "https://novate.ru/files/u34476/little-known-04.jpg"},
            {"title": "alexey", "thumbnail": "https://masterpiecer-images.s3.yandex.net/04a1f5cab05311eeaf3456e543f8144e:upscaled"}
            ]
    recommended_videos = [
            {"title": "legenda", "thumbnail": "https://img.youtube.com/vi/lOKASgtr6kU/hqdefault.jpg"}
            ]
    return render_template("main.html",popular_videos=popular_videos,recommended_videos=recommended_videos)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('registered'))

    return render_template("registration.html")

@app.route('/registered')
def registered():
    recommended_videos = [
            {"title": "manuk", "thumbnail": "https://sportishka.com/uploads/posts/2022-11/1667452782_22-sportishka-com-p-koreitsi-kachki-oboi-22.jpg"},
            ]
    popular_videos = [
            {"title": "azul", "thumbnail": "https://famoushustle.com/cdn/shop/products/FamousHustle.com8ujrm1w17gbColor.png?v=1648955518"}
            ]
    return render_template("registered.html",recommended_videos=recommended_videos,popular_videos=popular_videos)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('registered'))
        else:
            return "Неверный логин или пароль"

    return render_template("signin.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    return render_template("profile.html", username=session['username'])


@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    query = request.args.get('query')
    if not query:
        return "Введите ключевые слова"

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&type=video&maxResults=10"
    response = requests.get(url)
    data = response.json()

    videos = []
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    for item in data.get("items", []):
        video_data = {
            "title": item["snippet"]["title"],
            "videoId": item["id"]["videoId"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
        }
        videos.append(video_data)

        cursor.execute(
            "INSERT INTO videos (title, youtube_id, thumbnail_url, user_id) VALUES (?, ?, ?, ?)",
            (video_data["title"], video_data["videoId"], video_data["thumbnail"], user_id)
        )

    conn.commit()
    conn.close()

    return render_template("searchresults.html", videos=videos, query=query)


@app.route('/playlists')
def playlists():
    if 'user_id' not in session:
        return redirect(url_for('signisigninn'))

    user_id = session['user_id']
    conn = get_db_connection()
    videos = conn.execute(
        'SELECT * FROM videos WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    conn.close()

    return render_template("playlists.html", videos=videos)


if __name__ == '__main__':
    app.run(debug=True,port=8000)
