"""H4cknet XSS: intentionally vulnerable, isolated teaching app. NEVER publish to Internet."""
import os, sqlite3, secrets, re
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, session, redirect, url_for, render_template, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
DB = os.getenv('DB_PATH', '/data/foro.db')


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con


def init():
    os.makedirs(os.path.dirname(DB) or '.', exist_ok=True)
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT DEFAULT 'member');
        CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), title TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id), user_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL, created TEXT NOT NULL);
        ''')
        if not c.execute('SELECT 1 FROM users LIMIT 1').fetchone():
            demo = [('lucia','lucia123'),('marcos','marcos123'),('sara','sara123'),('alex','alex123')]
            for name, pw in demo:
                c.execute('INSERT INTO users(username,password_hash) VALUES(?,?)', (name,generate_password_hash(pw)))
            sample = [('lucia','¿Qué distro usáis para el día a día?','Llevo un tiempo con Fedora en el portátil y Debian en el servidor. ¿Qué tal os está yendo con Arch o Mint?'),('marcos','Mi primer teclado mecánico','Estoy buscando uno compacto para programar. Me interesan los switches silenciosos y que sea fácil de reparar. ¿Recomendaciones?'),('sara','Recursos para aprender redes','Abro hilo para compartir vídeos, ejercicios y libros con los que aprender subnetting, routing y protocolos. Dejad vuestros favoritos.'),('alex','Proyecto de fin de semana: un NAS casero','Tengo un ordenador viejo y me gustaría montarme almacenamiento en casa. ¿TrueNAS o Debian con Samba?'),('lucia','¿Qué editor os resulta más cómodo?','Entre VS Code, Neovim e IntelliJ siempre acabo cambiando. ¿Cómo tenéis configurado vuestro entorno?')]
            for name, title, body in sample:
                uid = c.execute('SELECT id FROM users WHERE username=?',(name,)).fetchone()['id']
                c.execute('INSERT INTO posts(user_id,title,body,created) VALUES(?,?,?,?)',(uid,title,body,now()))
            seed_comments=[(1,'marcos','Fedora para trabajar y Debian en una VM para pruebas.'),(1,'sara','Yo sigo con Mint. Lo que más valoro es que no me dé guerra.'),(2,'alex','He probado uno con switches brown y me ha gustado bastante.'),(3,'lucia','Para redes, Packet Tracer me ayudó mucho al principio.'),(4,'marcos','TrueNAS está genial si tienes discos suficientes.') ]
            for pid, author, body in seed_comments:
                uid=c.execute('SELECT id FROM users WHERE username=?',(author,)).fetchone()['id']
                c.execute('INSERT INTO comments(post_id,user_id,body,created) VALUES(?,?,?,?)',(pid,uid,body,now()))


def now(): return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

def current_user():
    uid=session.get('uid')
    if not uid: return None
    with db() as c: return c.execute('SELECT id,username,role FROM users WHERE id=?',(uid,)).fetchone()

def logged_in(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        if not current_user(): return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return inner

@app.context_processor
def inject(): return {'me': current_user()}

@app.after_request
def add_lab_cookie(res):
    # Deliberately readable, non-authenticating DECOY. Never a session/auth credential.
    if current_user() and not request.cookies.get('h4cknet_demo_token'):
        res.set_cookie('h4cknet_demo_token', 'DEMO-'+secrets.token_hex(6), httponly=False, samesite='Lax')
    return res

def member_count():
    with db() as c: return c.execute('SELECT COUNT(*) AS n FROM users').fetchone()['n']

@app.get('/')
def home():
    with db() as c:
        posts=c.execute('SELECT p.*,u.username,(SELECT COUNT(*) FROM comments x WHERE x.post_id=p.id) AS ncomments FROM posts p JOIN users u ON u.id=p.user_id ORDER BY p.id DESC').fetchall()
    return render_template('home.html', posts=posts, members=member_count(), topic_count=len(posts))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('username','').strip().lower(); pwd=request.form.get('password','')
        if not re.fullmatch(r'[a-z0-9_]{3,20}', name): flash('Nombre: 3–20 caracteres (letras, números o _).'); return render_template('auth.html',register=True)
        if len(pwd)<6: flash('La contraseña debe tener al menos 6 caracteres.'); return render_template('auth.html',register=True)
        try:
            with db() as c: c.execute('INSERT INTO users(username,password_hash) VALUES (?,?)',(name,generate_password_hash(pwd)))
        except sqlite3.IntegrityError:
            flash('Ese usuario ya existe.'); return render_template('auth.html',register=True)
        flash('Cuenta creada; inicia sesión.'); return redirect(url_for('login'))
    return render_template('auth.html',register=True)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        name=request.form.get('username','').strip().lower()
        with db() as c: user=c.execute('SELECT * FROM users WHERE username=?',(name,)).fetchone()
        if user and check_password_hash(user['password_hash'], request.form.get('password','')):
            session.clear(); session['uid']=user['id']; return redirect(url_for('home'))
        flash('Usuario o contraseña incorrectos.')
    return render_template('auth.html',register=False)

@app.get('/logout')
def logout():
    session.clear(); res=redirect(url_for('home')); res.delete_cookie('h4cknet_demo_token'); return res

@app.route('/posts/new', methods=['GET','POST'])
@logged_in
def new_post():
    if request.method=='POST':
        title=request.form.get('title','').strip()[:120]
        body=request.form.get('body','').strip()[:6000]
        if title and body:
            with db() as c:
                cur=c.execute('INSERT INTO posts(user_id,title,body,created) VALUES(?,?,?,?)',(session['uid'],title,body,now()))
                pid=cur.lastrowid
            return redirect(url_for('post',pid=pid))
        flash('El título y el contenido son obligatorios.')
    return render_template('new_post.html')

@app.route('/posts/<int:pid>',methods=['GET','POST'])
def post(pid):
    if request.method=='POST':
        if not current_user(): return redirect(url_for('login'))
        body=request.form.get('body','').strip()[:3000]
        if body:
            with db() as c: c.execute('INSERT INTO comments(post_id,user_id,body,created) VALUES(?,?,?,?)',(pid,session['uid'],body,now()))
        return redirect(url_for('post',pid=pid))
    with db() as c:
        p=c.execute('SELECT p.*,u.username FROM posts p JOIN users u ON u.id=p.user_id WHERE p.id=?',(pid,)).fetchone()
        if not p: abort(404)
        comments=c.execute('SELECT x.*,u.username FROM comments x JOIN users u ON u.id=x.user_id WHERE x.post_id=? ORDER BY x.id',(pid,)).fetchall()
    return render_template('post.html',post=p,comments=comments)

if __name__=='__main__':
    init()
    app.run(host='0.0.0.0',port=5000,debug=False)
else: init()
