from io import BytesIO
from flask import Flask, render_template, redirect, url_for, flash, request, send_file, Response, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.secret_key = "super secret key"
db = SQLAlchemy(app)






class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    prenom = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    contact = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, name, prenom, email, contact, password):
        self.name = name
        self.prenom = prenom
        self.email = email
        self.contact = contact
        self.password = password

class Pic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pic = db.Column(db.LargeBinary)
    name = db.Column(db.String(80), nullable=False )

    def __init__(self, pic, name):
        self.pic = pic
        self.name = name

class Myspace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    namepainter = db.Column(db.String(80))
    price = db.Column(db.Integer)
    #picpaint = db.Column(db.LargeBinary)
    description = db.Column(db.String(200))
    mail = db.Column(db.String(120))
    
    def __init__(self, namepainter, price, description, mail):
        self.namepainter = namepainter
        self.price = price
        #self.picpaint = picpaint
        self.description = description
        self.mail = mail
        


    


with app.app_context():
    db.create_all()

    
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/inscription', methods=['GET'])
def inscript():
    return render_template('inscription.html')

#pour s'inscrire
@app.route('/inscription',methods=['POST'])
def inscription():
    if request.method == 'POST':
        name= request.form.get('nom')
        prenom = request.form.get('prenom')
        email= request.form.get('email')
        contact= request.form.get('contact')
        password= request.form.get('motpass')
        new_user = User(name, prenom, email, contact, password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('seconnecter'))
    else:
        return render_template('inscription.html')



@app.route('/connect', methods=['GET'])
def connex():
    return render_template('seconnecter.html')


#pour se connecter
@app.route('/connect', methods=['POST'])
def seconnecter():
    #new_user = User.query.all()
    if request.method == 'POST':
        email= request.form.get('email')
        password= request.form.get('motpass')
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['email'] = user.email
            session['password'] = user.password
            #flash("Connexion reussie")
            return redirect("/publications")
    return render_template('seconnecter.html')





#Supprimer un user
@app.route('/supprimer/<int:id>')
def supprimer(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('afficher'))


#Supprimer un user Myspace
@app.route('/supprimerspace/<int:id>')
def supprimerspace(id):
    user = Myspace.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('monespace'))




#afficher la db
@app.route('/afficher')
def afficher():
    users = User.query.all()
    return render_template('afficher.html', users=users)


#redirection vers la page de modification
@app.route('/modifierpge/<int:id>')
def modifierpage(id):
    user = User.query.get_or_404(id)
    return render_template('modifier.html', user=user)


#redirection vers la page de modification Mon espace
@app.route('/modifierspace/<int:id>')
def modifierspace(id):
    users = Myspace.query.get_or_404(id)
    return render_template('monespace.html', users=users)



#Modifier un user
@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    user = User.query.get_or_404(id)
    if user:
        if request.method == 'POST':
            user.name = request.form.get('nom')
            user.email = request.form.get('email')
            user.password = request.form.get('motpass')
            db.session.commit()
            return redirect('/afficher')
    else:
        return render_template('modifier.html', user=user)
    

#Modifier un user Myspace
@app.route('/modifierspe/<int:id>', methods=['GET', 'POST'])
def modifierspe(id):
    user = Myspace.query.get_or_404(id)
    if user:
        if request.method == 'POST':
            user.namepainter = request.form.get('nompein')
            user.price = request.form.get('prixtoil')
            user.description = request.form.get('description')
            db.session.commit()
            return redirect('/monespace')
    else:
        return render_template('monespace.html', user=user)




#publications
@app.route('/publications')
def publications():
    pubs = Myspace.query.all()
    return render_template('publications.html',pubs=pubs)



#Inserer image dans la bd
@app.route('/pubmodif', methods=['GET', 'POST'])
def pubmodif():
    pic = request.files['pic']
    print(pic)
    if not pic:
        return "Image non ajoute"
    
    filename = secure_filename(pic.filename)

    img = Pic(pic=pic.read(), name=filename)
    db.session.add(img)
    db.session.commit()          
    #pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic.filename))
    #user = User.query.filter_by(id=1).first()
    #user.pic = pic.filename
    #db.session.commit()   
    return "Image ajoute"

""" @app.route("/imgaff", methods=['GET', 'POST'])
def image():
    img = Pic.query.all()
    return render_template('img.html', imgs=img) """


#Afficher img depuis la bd
@app.route('/img/<int:id>', methods=['GET', 'POST'])
def image(id):
    imgs =Pic.query.filter_by(id=id).first()
    return Response(imgs.pic, mimetype='image/jpg')

# @app.route('/img/<int:id>', methods=['GET', 'POST'])
# def imge(id):
#     imgs = Pic.query.filter_by(id=id).first()
#     return send_file(BytesIO(imgs.pic))


@app.route('/imgaff', methods=['GET'])
def imgaff():
    imgs = Pic.query.all()
    return render_template('img.html', imgs=imgs)
#Python Flask Upload and Display Image | Flask tutorial




#Mon espace
@app.route('/monespace', methods=['GET']) 
def monespace():
    spaces = Myspace.query.filter_by(mail=session['email']).all()
    return render_template('monespace.html', spaces=spaces)

#Soumettre des elements dans la db Myspace
@app.route('/soumettre', methods=['GET', 'POST'])
def soumettre(): 
    if request.method == 'POST':
        namepainter= request.form.get('nompein')
        price = request.form.get('prixtoil')
        #picpaint = request.files['imgtoil']
        description = request.form.get('description')
        mail = session['email']
        new_myspace = Myspace(namepainter, price, description, mail)
        db.session.add(new_myspace)
        db.session.commit()
        return redirect('/monespace')
    return render_template('monespace.html')



@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
		flash('Image successfully uploaded and displayed below')
		return render_template('upload.html', filename=filename)
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)





    
@app.route('/panier', methods=['GET'])
def panier(): 
    return render_template('panier.html')



@app.route('/apropos', methods=['GET'])
def apropos(): 
    return render_template('apropos.html')





if __name__ == "__main__":
    app.run(debug=True)