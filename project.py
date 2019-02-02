from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CatalogItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Web client 1"

engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session.get('username')
    output += '!</h1>'
    output += '<img src="'
    output += login_session.get('picture')
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session.get('username'))
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session.get('username'), email=login_session.get(
                   'email'), picture=login_session.get('picture'))
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session.get('email')).first()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalogs/<int:catalog_id>/item/JSON')
def catalogItemJSON(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).first()
    items = session.query(CatalogItem).filter_by(
        catalog_id=catalog_id).all()
    return jsonify(CatalogItem=[i.serialize for i in items])


# ADD JSON ENDPOINT HERE
@app.route('/catalogs/<int:catalog_id>/item/<int:item_id>/JSON')
def itemItemJSON(catalog_id, item_id):
    itemItem = session.query(CatalogItem).filter_by(id=item_id).first()
    return jsonify(MenuItem=itemItem.serialize)


@app.route('/catalog/JSON')
def catalogsJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(catalogs=[r.serialize for r in catalogs])


@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    if 'username' not in login_session:
        return render_template('publiccatalogs.html', catalogs=catalogs)
    else:
        return render_template('catalogs.html', catalogs=catalogs)


# Task 1: Create route for newMenuItem function here
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCatalog = Catalog(name=request.form.get(
            'name'), user_id=login_session.get('user_id'))
        session.add(newCatalog)
        session.commit()
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newCatalog.html')


@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCatalog = session.query(Catalog).filter_by(id=catalog_id).first()
    if editedCatalog.user_id != login_session.get('user_id'):
        return "<script>function myFunction() {alert('You are not authorized to edit this catalog. Please create your own catalog in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form.get('name'):
            editedCatalog.name = request.form.get('name')
            flash('Catalog Successfully Edited %s' % editedCatalog.name)
            return redirect(url_for('showCatalogs'))
    else:
        return render_template('editCatalog.html', catalog=editedCatalog)


# Delete a catalog
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    catalogToDelete = session.query(Catalog).filter_by(id=catalog_id).first()
    if 'username' not in login_session:
        return redirect('/login')
    if catalogToDelete.user_id != login_session.get('user_id'):
        return "<script>function myFunction() {alert('You are not authorized to delete this catalog. Please create your own catalog in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(catalogToDelete)
        flash('%s Successfully Deleted' % catalogToDelete.name)
        session.commit()
        # why is there a prameter?
        return redirect(url_for('showCatalogs', catalog_id=catalog_id))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete)


@app.route('/catalog/<int:catalog_id>/')
@app.route('/catalogs/<int:catalog_id>/item/')
def catalogItem(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).first()
    creator = getUserInfo(catalog.user_id)
    items = session.query(CatalogItem).filter_by(catalog_id=catalog_id).all()
    # or creator.id != login_session('user_id'):
    if 'username' not in login_session:
        return render_template('publicitem.html', items=items, catalog=catalog, creator=creator)
    else:
        return render_template('item.html', items=items, catalog=catalog, creator=creator)


@app.route('/catalogs/<int:catalog_id>/new', methods=['GET', 'POST'])
def newCatalogItem(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).first()
    if login_session.get('user_id') != catalog.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add menu items to this catalog. Please create your own catalog in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = CatalogItem(name=request.form.get('name'), description=request.form.get('description'), price=request.form.get(
            'price'), family=request.form.get('family'), catalog_id=catalog_id, user_id=catalog.user_id)
        session.add(newItem)
        session.commit()
        flash("new catalog item created!")
        return redirect(url_for('catalogItem', catalog_id=catalog_id))
    else:
        return render_template('newcatalogitem.html', catalog_id=catalog_id)

# Task 2: Create route for editMenuItem function here


@app.route('/catalogs/<int:catalog_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editCatalogItem(catalog_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(id=item_id).first()
    catalog = session.query(Catalog).filter_by(id=catalog_id).first()
    if login_session.get('user_id') != catalog.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this catalog. Please create your own catalog in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form.get('name'):
            editedItem.name = request.form.get('name')
        if request.form.get('description'):
            editedItem.description = request.form.get('description')
        if request.form.get('price'):
            editedItem.price = request.form.get('price')
        if request.form.get('family'):
            editedItem.course = request.form.get('family')
        session.add(editedItem)
        session.commit()
        flash("catalog item eadited!")
        return redirect(url_for('catalogItem', catalog_id=catalog_id))
    else:
        return render_template('editcatalogitem.html', catalog_id=catalog_id, item_id=item_id, item=editedItem)


# Task 3: Create a route for deleteMenuItem function here


@app.route('/catalogs/<int:catalog_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteCatalogItem(catalog_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).first()
    itemToDelete = session.query(CatalogItem).filter_by(id=item_id).first()
    if login_session.get('user_id') != catalog.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete menu items to this catalog. Please create your own catalog in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("catalog item deleted!")
        return redirect(url_for('catalogItem', catalog_id=catalog_id))
    else:
        return render_template('deletecatalogitem.html', item=itemToDelete)


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
       # if login_session['provider'] == 'facebook':
         #   fbdisconnect()
         #   del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalogs'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalogs'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
