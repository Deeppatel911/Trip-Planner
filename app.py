import numpy as np
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import requests, json, pandas as pd, os
from datetime import timedelta
from gtts import gTTS
from translate import Translator
import db, mail_config, config

app = Flask(__name__)

app.config['MYSQL_HOST'] = db.mysql_host
app.config['MYSQL_USER'] = db.mysql_user
app.config['MYSQL_PASSWORD'] = db.mysql_password
app.config['MYSQL_DB'] = db.mysql_db

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = mail_config.mail_username
app.config['MAIL_PASSWORD'] = mail_config.mail_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
mysql = MySQL(app)


@app.route('/', methods=['POST', 'GET'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return render_template('login.html')


@app.route('/sign_up', methods=['POST', 'GET'])
def signup():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return render_template('signup.html')


@app.route('/validate_login', methods=['POST', 'GET'])
def validate_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')

        if 'admin' in session:
            cur = mysql.connection.cursor()
            cur.execute("SELECT email, password FROM admin WHERE email=%s ", (email,))
            result = cur.fetchone()
            cur.close()

            if result:
                if password == result[1]:
                    session.permanent = True
                    session['loggedin'] = True
                    session['email'] = email
                    session['password'] = password
                    return redirect(url_for('home'))

                else:
                    error_statement = "Incorrect Password"
                    return render_template('admin.html', error_statement1=error_statement)

            else:
                error_statement = "User Does not Exist..."
                return render_template('admin.html', error_statement=error_statement)

        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT email, password FROM login WHERE email=%s ", (email,))
            result = cur.fetchone()
            cur.close()

            if result:
                if password == result[1]:
                    session.permanent = True
                    session['loggedin'] = True
                    session['email'] = email
                    session['password'] = password
                    return redirect(url_for('home'))

                else:
                    error_statement = "Incorrect Password"
                    return render_template('login.html', error_statement1=error_statement)

            else:
                error_statement = "User Does not Exist..."
                return render_template('login.html', error_statement=error_statement)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password1 = request.form.get('pass')
        password2 = request.form.get('pass1')
        contact = request.form.get('contact')
        gender = request.form.get('gender')
        dob = request.form.get('dob')

        if password1 != password2:
            error_statement = "Password Does not Match"
            return render_template('signup.html', error_statement1=error_statement)

        cur = mysql.connection.cursor()
        cur.execute("SELECT email from login where email LIKE %s", [email])
        result = cur.fetchone()
        cur.close()

        if result:
            error_statement = "Email Already Registered..."
            return render_template('signup.html', error_statement2=error_statement)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(email,first, last, contact, gender, dob) VALUES (%s, %s, %s, %s, %s, %s)",
                    (email, fname, lname, contact, gender, dob))
        cur.execute("INSERT INTO login(email, password) VALUES (%s, %s)",
                    (email, password1))

        mysql.connection.commit()
        cur.close()

        success_statement = "Registered Successfully...  Login to your Account"
        return render_template('login.html', success_statement=success_statement)

    return render_template('login.html')


@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email_fp')

        if 'admin' in session:
            cur = mysql.connection.cursor()
            cur.execute("SELECT email, password FROM admin WHERE email=%s", (email,))
            my_data = cur.fetchone()
            cur.close()

        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM login WHERE email=%s', (email,))
            my_data = cur.fetchone()
            cur.close()

        m1 = ''
        if my_data:
            m1 = my_data[0]

        if email == m1:
            my_password = my_data[1]
            if 'admin' in session:
                cur = mysql.connection.cursor()
                cur.execute('Select first, last from admin where email=%s', (email,))
                name = cur.fetchone()
                cur.close()

            else:
                cur = mysql.connection.cursor()
                cur.execute('Select first, last from users where email=%s', (email,))
                name = cur.fetchone()
                cur.close()

            msg = Message('Hello', sender=mail_config.mail_username, recipients=[m1])
            msg.body = "Hello " + str(name[0]) + " " + str(name[1]) + " your password is " + str(my_password)
            mail.send(msg)
            success_statement = "Email has been sent to your Account..."

            if 'admin' in session:
                return render_template('admin.html', success_statement=success_statement)
            else:
                return render_template('login.html', success_statement=success_statement)

        else:
            error_statement = "Email-Id is not registered..."
            if 'admin' in session:
                return render_template('admin.html', error_statement=error_statement)
            else:
                return render_template('login.html', error_statement2=error_statement)


@app.route('/home', methods=['POST', 'GET'])
def home():
    if 'loggedin' in session:
        if 'admin' in session:
            cur = mysql.connection.cursor()
            cur.execute('Select * from users')
            data = cur.fetchall()
            cur.close()
            return render_template('admin_home.html', data=data)
        else:
            return render_template('home.html')
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/safety', methods=['POST', 'GET'])
def safety():
    if 'loggedin' in session:
        if 'admin' not in session:
            if request.method == 'POST':
                country = request.form.get('country')
                country = str(country)
                country = country.title()

                df = pd.read_csv('datasets/country-codes.csv')

                index = df.index
                try:
                    condition = df['countries'] == country
                    code_index = index[condition].tolist()
                    ci = code_index[0]
                    country_code = df['Alpha-2 code'].iloc[ci]

                    url = "https://www.travel-advisory.info/api"

                    # querystring = {'countrycode':'IND'}
                    querystring = dict()
                    querystring['countrycode'] = country_code

                    response = requests.request("POST", url, params=querystring)

                    r = json.loads(response.text)
                    r2 = r['data'][country_code]['advisory']

                    # return r2['message']

                    # covid statistics
                    headers = dict()
                    headers['x-rapidapi-key'] = config.api_key
                    headers['x-rapidapi-host'] = config.api_host

                    url2 = "https://corona-virus-world-and-india-data.p.rapidapi.com/api"

                    response2 = requests.request("GET", url2, headers=headers)
                    r3 = json.loads(response2.text)
                    r4 = r3['countries_stat']

                    tc = td = tr = ac = ''
                    # print(r2)

                    for i in r4:
                        if country == i['country_name'] or (
                                country == 'United States Of America' and i['country_name'] == 'USA') or (
                                country == 'United Kingdom' and i['country_name'] == 'UK'):
                            tc = 'Total Cases: ' + i['cases']
                            td = 'Total Deaths: ' + i['deaths']
                            tr = 'Total Recoveries: ' + i['total_recovered']
                            ac = 'Active Cases: ' + i['active_cases']

                    # final_output_string = r2['message'] + '<br/>' + st

                    return render_template('safety_result.html', travel_advise=r2['message'], total_cases=tc,
                                           total_deaths=td, total_recoveries=tr, active_cases=ac)  # final_output_string

                except:
                    return render_template('safety.html', travel_advise='Enter the correct country name')

            return render_template('safety.html')

        else:
            return redirect(url_for('home'))

    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/travel_cost', methods=['POST', 'GET'])
def travel_cost():
    if 'loggedin' in session:
        if 'admin' not in session:
            if request.method == 'POST':
                country = request.form.get('country')
                country = str(country)
                country = country.title()

                df = pd.read_csv('datasets/country-codes.csv')

                index = df.index
                try:
                    condition = df['countries'] == country
                    code_index = index[condition].tolist()
                    ci = code_index[0]
                    country_code = df['Alpha-2 code'].iloc[ci]

                    url = "https://widget.budgetyourtrip.com/location-widget-js/"

                    final_url = url + country_code

                    return render_template('travel_cost_result.html', travel_cost_url=final_url)

                except:
                    return render_template('travel_cost.html', message='Enter the correct country name')

            return render_template('travel_cost.html')

        else:
            return redirect(url_for('home'))

    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    # session.pop('password',None)
    if 'admin' in session:
        session.pop('admin', None)
        return render_template('admin.html', message="You've logged out successfully!")
    return render_template('login.html', message="You've logged out successfully!")


@app.route('/attractions_recommendations')
def attractions():
    if 'loggedin' in session:
        if 'admin' not in session:
            return render_template('attraction_preferences.html', showOutput=0)
        else:
            return redirect(url_for('home'))
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


attractions_result = pd.DataFrame(columns=['name', 'province', 'city', 'price', 'rating', 'category'])
@app.route('/get_attractions_recommendations', methods=['POST', 'GET'])
def get_attractions_recommendations():
    if 'loggedin' in session:
        if 'admin' not in session:
            if request.method == 'POST':
                global attractions_result
                email = session.get('email')

                if attractions_result.size != 0:
                    attractions_result = pd.DataFrame(attractions_result, columns=['name', 'province', 'city', 'price', 'rating', 'category', 'ab', 'pq', 'rs'])
                    attractions_result = attractions_result.drop(columns=['ab', 'pq', 'rs'])

                destination = request.form.get('destination')
                budget = request.form.get('budget')

                destination = str(destination)
                destination = destination.lower()
                budget = int(budget)

                choices_list = []
                choices_list.append(request.form.get('rate1'))
                choices_list.append(request.form.get('rate2'))
                choices_list.append(request.form.get('rate3'))
                choices_list.append(request.form.get('rate4'))
                choices_list.append(request.form.get('rate5'))
                choices_list.append(request.form.get('rate6'))
                choices_list.append(request.form.get('rate7'))
                choices_list.append(request.form.get('rate8'))
                choices_list.append(request.form.get('rate9'))
                choices_list.append(request.form.get('rate10'))
                choices_list.append(request.form.get('rate11'))
                choices_list.append(request.form.get('rate12'))
                choices_list.append(request.form.get('rate13'))
                choices_list.append(request.form.get('rate14'))
                choices_list.append(request.form.get('rate15'))
                choices_list.append(request.form.get('rate16'))
                choices_list.append(request.form.get('rate17'))
                choices_list.append(request.form.get('rate18'))
                choices_list.append(request.form.get('rate19'))
                choices_list.append(request.form.get('rate20'))

                df = pd.read_csv('datasets/attractions.csv', index_col=False)
                index = df.index

                try:
                    condition = df['city'].str.contains(destination)
                    destination_index = index[condition].tolist()
                    di = destination_index[0]
                    if di:
                        f_choices_list = []
                        for i in choices_list:
                            if i:
                                f_choices_list.append(i)
                        print(f_choices_list)

                        if len(f_choices_list) >= 1:
                            for i in range(len(f_choices_list)):
                                attractions_result = pd.concat([attractions_result, df[df['category'].str.contains(f_choices_list[i])]],
                                                   ignore_index=True)

                            attractions_result = attractions_result[attractions_result['city'].str.contains(destination)]
                            attractions_result = attractions_result[attractions_result['rating'] >= 3]
                            attractions_result = attractions_result[attractions_result['price'] <= budget]

                            if attractions_result.empty:
                                error_statement = "No attraction found! Try selecting more choices."
                                return render_template('attraction_preferences.html', message=error_statement)
                            else:
                                attractions_result = attractions_result.sort_values(by=['rating', 'name'], ascending=[False, True])
                                attractions_result = attractions_result.drop_duplicates('name')

                                attractions_result['name'] = attractions_result['name'].apply(lambda x: x.capitalize())
                                attractions_result['city'] = attractions_result['city'].apply(lambda x: x.capitalize())
                                attractions_result['province'] = attractions_result['province'].apply(lambda x: x.capitalize())
                                attractions_result['price'] = attractions_result['price'].apply(np.ceil)

                                attractions_result = attractions_result.reset_index()
                                attractions_result = attractions_result.drop(['index'], axis=1)
                                attractions_result = attractions_result.drop(['id'], axis=1)
                                attractions_result.index = attractions_result.index + 1
                                attractions_result['name'] = attractions_result['name'].str.replace('_', ' ')

                                cur = mysql.connection.cursor()
                                cur.execute('Select * from attractions where email=%s', (email,))
                                data = cur.fetchall()
                                cur.close()

                                fav_status = []
                                data = list(data)
                                #print(data)
                                data = list(map(lambda x: x[1], data))
                                #print(data)

                                for i in attractions_result['name']:
                                    if str(i) in data:
                                        fav_status.append('Saved')
                                    else:
                                        fav_status.append('Save to Favourites')

                                attractions_result['fav_status'] = fav_status

                                # print(len(result))
                                # if len(result) == 0:

                                attractions_result = attractions_result.to_numpy()
                                # print(result)

                                for i in attractions_result:
                                    i[0] = i[0].replace("_", " ")
                                    #i[1] = i[1].replace("_", " ")
                                    i[5] = i[5].replace("_", " ")


                                return render_template('attraction_preferences.html', data=attractions_result, showOutput=1)
                            # return render_template('attractions_output.html',data='abc') #index_list#index_list#render_template('get_recommendations.html', form_status="Hotel preferences submitted")
                        else:
                            return render_template('attraction_preferences.html', message='Select at least 1 choice', showOutput=0)

                except:
                    error_statement = "No attraction found! Please enter correct destination name."
                    return render_template('attraction_preferences.html', message=error_statement, showOutput=0)
        else:
            return redirect(url_for('home'))

    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/view_details')
def view_details():
    if 'loggedin' in session:
        if 'admin' not in session:
            email = session.get('email')

            cur = mysql.connection.cursor()
            cur.execute('Select * from users where email=%s', (email,))
            data = cur.fetchone()
            cur.close()

            return render_template('user_profile.html', data=data)

        else:
            return redirect(url_for('home'))

    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/edit_details', methods=['POST'])
def edit_details():
    if 'loggedin' in session and 'admin' not in session:
        if request.method == 'POST':
            email = session.get('email')

            fname = request.form.get('fname')
            lname = request.form.get('lname')
            contact_no = request.form.get('contact')
            dob = request.form.get('dob')

            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE users SET first=%s, last=%s, contact=%s, dob=%s, approval='Yet to be approved' WHERE email=%s",
                (fname, lname, contact_no, dob, email))
            flash('Data updated successfully!')
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('view_details'))
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'loggedin' in session and 'admin' not in session:
        if request.method == 'POST':
            email = session.get('email')
            # current_password=request.form.get('cr_pass')
            new_password = request.form.get('new_pass1')
            new_password2 = request.form.get('new_pass2')

            if new_password != new_password2:
                flash('Password Does not Match!')
                return redirect(url_for('change_password'))

            cur = mysql.connection.cursor()
            cur.execute('UPDATE login SET password=%s WHERE email=%s', (new_password, email))
            flash('Password updated successfully!')
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('view_details'))
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/translator', methods=['POST', 'GET'])
def translator():
    if 'loggedin' in session:
        if 'admin' not in session:
            if request.method == 'POST':
                text = request.form.get('my_text')
                text = str(text)
                target_lang = request.form.get('lang')
                target_lang = str(target_lang)
                target_lang = target_lang.capitalize()

                df = pd.read_csv('datasets/language-codes.csv')
                index = df.index

                if os.path.exists('static/translated_audio_output.mp3'):
                    os.remove('static/translated_audio_output.mp3')

                try:
                    condition = df['language'] == target_lang
                    code_index = index[condition].tolist()
                    ci = code_index[0]
                    lang_code = df['alpha2'].iloc[ci]

                    trans = Translator(to_lang=lang_code)
                    trans_text = trans.translate(text)

                    output = gTTS(text=trans_text, lang=lang_code, slow=False)
                    output.save('static/translated_audio_output.mp3')

                    message = 'done'
                    return render_template('translator.html', message=message)

                except:
                    error_statement = 'Enter correct language name'
                    return render_template('translator.html', error_statement=error_statement)

            return render_template('translator.html')

        else:
            return redirect(url_for('home'))

    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/restaurants_recommendations')
def restaurants():
    if 'loggedin' in session:
        if 'admin' not in session:
            return render_template('restaurant_preferences.html', showOutput=0)
        else:
            return redirect(url_for('home'))
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if 'loggedin' in session:
        session.pop('loggedin', None)
        session.pop('email', None)
    session['admin'] = True
    return render_template('admin.html')


@app.route('/admin_approve_details/<string:email>/<string:approval>', methods=['GET'])
def admin_approve_details(email, approval):
    if 'loggedin' and 'admin' in session:
        flash("Approval status have been updated successfully.")

        if approval == 'Approved':
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET approval='Approved' WHERE email=%s", (email,))
            mysql.connection.commit()

        else:
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE users SET approval='Not Approved. Assure that all the details submitted by you is correct.' WHERE email=%s",
                (email,))
            mysql.connection.commit()

        return redirect(url_for('home'))
    else:
        return redirect(url_for('admin'))


@app.route('/admin_delete_user/<string:email>', methods=['GET'])
def admin_delete_user(email):
    if 'loggedin' and 'admin' in session:
        flash("Record Has Been Deleted Successfully")

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE email=%s", (email,))
        mysql.connection.commit()

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM login WHERE email=%s", (email,))
        mysql.connection.commit()

        return redirect(url_for('home'))
    else:
        return redirect(url_for('admin'))


@app.route('/hotels_recommendations')
def hotels():
    if 'loggedin' in session:
        if 'admin' not in session:
            return render_template('hotel_preferences.html', showOutput=0)
        else:
            return redirect(url_for('home'))
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


hotels_result = pd.DataFrame(columns=['hotel_name', 'hotel_rating', 'amenities', 'address', 'price'])
@app.route('/get_hotels_recommendations', methods=['POST', 'GET'])
def get_hotels_recommendations():
    if 'loggedin' in session:
        if 'admin' not in session:
            if request.method == 'POST':
                global hotels_result
                email = session.get('email')

                if hotels_result.size != 0:
                    hotels_result = pd.DataFrame(hotels_result, columns=['hotel_name', 'hotel_rating', 'amenities', 'address', 'price', 'ab', 'pq', 'rs'])
                    hotels_result = hotels_result.drop(columns=['ab', 'pq', 'rs'])

                destination = request.form.get('destination')
                budget = request.form.get('budget')

                destination = str(destination)
                destination = destination.title()
                budget = int(budget)

                #if count >= 5:
                choices_list=[]
                choices_list.append(request.form.get('rate1'))
                choices_list.append(request.form.get('rate2'))
                choices_list.append(request.form.get('rate3'))
                choices_list.append(request.form.get('rate4'))
                choices_list.append(request.form.get('rate5'))
                choices_list.append(request.form.get('rate6'))
                choices_list.append(request.form.get('rate7'))
                choices_list.append(request.form.get('rate8'))
                choices_list.append(request.form.get('rate9'))
                choices_list.append(request.form.get('rate10'))
                choices_list.append(request.form.get('rate11'))
                choices_list.append(request.form.get('rate12'))
                choices_list.append(request.form.get('rate13'))
                choices_list.append(request.form.get('rate14'))
                choices_list.append(request.form.get('rate15'))

                df = pd.read_csv('datasets/hotel_data.csv', index_col=False)
                index = df.index

                try:
                    condition = df['address'].str.contains(destination)
                    destination_index = index[condition].tolist()
                    di = destination_index[0]
                    if di:
                        f_choices_list = []
                        for i in choices_list:
                            if i:
                                f_choices_list.append(i)
                        print(f_choices_list)

                        if len(f_choices_list) >= 1:
                            for i in range(len(f_choices_list)):
                                hotels_result = pd.concat([hotels_result, df[df['amenities'].str.contains(f_choices_list[i])]],
                                                   ignore_index=True)

                            hotels_result = hotels_result[hotels_result['address'].str.contains(destination)]
                            hotels_result = hotels_result[hotels_result['hotel_rating'] >= 3]
                            hotels_result = hotels_result[hotels_result['price'] <= budget]

                            if hotels_result.empty:
                                error_statement = "No hotel found! Try selecting more choices."
                                return render_template('hotel_preferences.html', message=error_statement)
                            else:
                                hotels_result['price'] = hotels_result['price'].apply(np.ceil)
                                hotels_result = hotels_result.sort_values(by=['hotel_rating', 'hotel_name'], ascending=[False, True])
                                hotels_result = hotels_result.drop_duplicates('hotel_name')

                                hotels_result = hotels_result.reset_index()
                                hotels_result = hotels_result.drop(['index'], axis=1)
                                hotels_result = hotels_result.drop(['id'], axis=1)
                                hotels_result.index = hotels_result.index + 1

                                cur = mysql.connection.cursor()
                                cur.execute('Select * from hotels where email=%s', (email,))
                                data = cur.fetchall()
                                cur.close()

                                fav_status = []
                                data = list(data)
                                # print(data)
                                data = list(map(lambda x: x[1], data))
                                # print(data)

                                for i in hotels_result['hotel_name']:
                                    if str(i) in data:
                                        fav_status.append('Saved')
                                    else:
                                        fav_status.append('Save to Favourites')

                                hotels_result['fav_status'] = fav_status

                                # print(len(hotels_result))
                                # if len(hotels_result) == 0:

                                hotels_result = hotels_result.to_numpy()
                                # print(hotels_result)

                                return render_template('hotel_preferences.html', data=hotels_result, showOutput=1)
                            # return render_template('hotels_output.html',data='abc') #index_list#index_list#render_template('get_recommendations.html', form_status="Hotel preferences submitted")
                        else:
                            return render_template('hotel_preferences.html', message='Select at least 1 choice', showOutput=0)

                except:
                    error_statement = "No hotel found! Please enter correct destination name."
                    return render_template('hotel_preferences.html', message=error_statement, showOutput=0)
            else:
                return redirect(url_for('home'))

    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


restaurants_result = pd.DataFrame(columns=['name', 'address', 'city', 'postal_code', 'stars', 'categories'])
@app.route('/get_restaurants_recommendations', methods=['POST', 'GET'])
def get_restaurants_recommendations():
    if 'loggedin' in session:
        if 'admin' not in session:
            if request.method == 'POST':
                global restaurants_result
                email = session.get('email')

                if restaurants_result.size != 0:
                    restaurants_result = pd.DataFrame(restaurants_result, columns=['name', 'address', 'city', 'postal_code', 'stars', 'categories', 'ab', 'pq', 'rs'])
                    restaurants_result = restaurants_result.drop(columns=['ab', 'pq', 'rs'])

                destination = request.form.get('destination')
                destination = str(destination)
                destination = destination.capitalize()

                choices_list = []
                choices_list.append(request.form.get('rate1'))
                choices_list.append(request.form.get('rate2'))
                choices_list.append(request.form.get('rate3'))
                choices_list.append(request.form.get('rate4'))
                choices_list.append(request.form.get('rate5'))
                choices_list.append(request.form.get('rate6'))
                choices_list.append(request.form.get('rate7'))
                choices_list.append(request.form.get('rate8'))
                choices_list.append(request.form.get('rate9'))
                choices_list.append(request.form.get('rate10'))
                choices_list.append(request.form.get('rate11'))
                choices_list.append(request.form.get('rate12'))
                choices_list.append(request.form.get('rate13'))
                choices_list.append(request.form.get('rate14'))
                choices_list.append(request.form.get('rate15'))
                choices_list.append(request.form.get('rate16'))
                choices_list.append(request.form.get('rate17'))
                choices_list.append(request.form.get('rate18'))
                choices_list.append(request.form.get('rate19'))
                choices_list.append(request.form.get('rate20'))

                df = pd.read_csv('datasets/yelp-dataset.csv', index_col=False)
                index = df.index

                try:
                    condition = df['city'].str.contains(destination)
                    destination_index = index[condition].tolist()
                    di = destination_index[0]
                    if di:
                        f_choices_list = []
                        for i in choices_list:
                            if i:
                                f_choices_list.append(i)
                        print(f_choices_list)

                        if len(f_choices_list) >= 1:
                            for i in range(len(f_choices_list)):
                                restaurants_result = pd.concat([restaurants_result, df[df['categories'].str.contains(f_choices_list[i])]],
                                                   ignore_index=True)

                            restaurants_result = restaurants_result[restaurants_result['city'].str.contains(destination)]
                            restaurants_result = restaurants_result[restaurants_result['stars'] >= 3]

                            if restaurants_result.empty:
                                error_statement = "No restaurant found! Try selecting more choices."
                                return render_template('restaurants_preferences.html', message=error_statement)
                            else:
                                restaurants_result = restaurants_result.sort_values(by=['stars', 'name'], ascending=[False, True])
                                restaurants_result = restaurants_result.drop_duplicates('name')

                                restaurants_result = restaurants_result.reset_index()
                                restaurants_result = restaurants_result.drop(['index'], axis=1)
                                restaurants_result = restaurants_result.drop(['id'], axis=1)
                                restaurants_result.index = restaurants_result.index + 1
                                restaurants_result['name'] = restaurants_result['name'].str.replace('\"', '')

                                cur = mysql.connection.cursor()
                                cur.execute('Select * from restaurants where email=%s', (email,))
                                data = cur.fetchall()
                                cur.close()

                                fav_status = []
                                data = list(data)
                                # print(data)
                                data = list(map(lambda x: x[1], data))
                                # print(data)

                                for i in restaurants_result['name']:
                                    if str(i) in data:
                                        fav_status.append('Saved')
                                    else:
                                        fav_status.append('Save to Favourites')

                                restaurants_result['fav_status'] = fav_status

                                # print(len(restaurants_result))
                                # if len(restaurants_result) == 0:

                                restaurants_result = restaurants_result.to_numpy()
                                # print(restaurants_result)

                                for i in restaurants_result:
                                    i[0] = i[0].replace("\"", "")
                                    i[1] = i[1].replace("\"", "")
                                    i[5] = i[5].replace(";", ", ")

                                return render_template('restaurant_preferences.html', data=restaurants_result, showOutput=1)
                            # return render_template('restaurants_output.html',data='abc') #index_list#index_list#render_template('get_recommendations.html', form_status="Hotel preferences submitted")
                        else:
                            return render_template('restaurant_preferences.html', message='Select at least 1 choice', showOutput=0)

                except:
                    error_statement = "No restaurant found! Please enter correct destination name."
                    return render_template('restaurant_preferences.html', message=error_statement, showOutput=0)
        else:
            return redirect(url_for('home'))

    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/save_attraction_to_favourites/<string:name>/<string:rating>/<string:price>/<string:city>/<string:province>/<string:category>',
           methods=['GET'])
def save_attraction_to_favourites(name, rating, price, city, province, category):
    if 'loggedin' in session:
        if 'admin' not in session:
            global attractions_result
            email = session.get('email')

            cur = mysql.connection.cursor()
            cur.execute('Select * from attractions where email=%s and name=%s', (email, name))
            data = cur.fetchall()

            if not data:
                cur.execute(
                    'INSERT INTO attractions(name, rating, price, city, province, category, email) values(%s,%s,%s,%s,%s,%s,%s)',
                    (name, rating, price, city, province, category, email))
                mysql.connection.commit()

            cur.close()

            return render_template('attraction_preferences.html', data=attractions_result, showOutput=1)
        else:
            return render_template('home.html')
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/save_hotel_to_favourites/<string:name>/<string:rating>/<string:price>/<string:address>/<string:amenities>',
           methods=['GET'])
def save_hotel_to_favourites(name, rating, price, address, amenities):
    if 'loggedin' in session:
        if 'admin' not in session:
            email = session.get('email')

            cur = mysql.connection.cursor()
            cur.execute('Select * from hotels where email=%s and name=%s', (email, name))
            data = cur.fetchall()

            if not data:
                cur = mysql.connection.cursor()
                cur.execute(
                    'INSERT INTO hotels(name, rating, price, address, amenities, email) values(%s,%s,%s,%s,%s,%s)',
                    (name, rating, price, address, amenities, email))
                mysql.connection.commit()

            cur.close()

            global hotels_result
            return render_template('hotel_preferences.html', data=hotels_result, showOutput=1)
        else:
            return render_template('home.html')
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/save_restaurant_to_favourites/<string:name>/<string:rating>/<string:address>/<string:city>/<string:postal_code>/<string:categories>',
           methods=['GET'])
def save_restaurant_to_favourites(name, rating, address, city, postal_code, categories):
    if 'loggedin' in session:
        if 'admin' not in session:
            email = session.get('email')

            cur = mysql.connection.cursor()
            cur.execute('Select * from restaurants where email=%s and name=%s', (email, name))
            data = cur.fetchall()

            if not data:
                cur = mysql.connection.cursor()
                cur.execute(
                    'INSERT INTO restaurants(name, rating, address, city, postal_code, categories, email) values(%s,%s,%s,%s,%s,%s,%s)',
                    (name, rating, address, city, postal_code, categories, email))
                mysql.connection.commit()

            cur.close()

            global restaurants_result
            return render_template('restaurant_preferences.html', data=restaurants_result, showOutput=1)
        else:
            return render_template('home.html')
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/favourites/<string:rec_type>', methods=['GET'])
def favourites(rec_type):
    if 'loggedin' in session:
        if 'admin' not in session:
            email = session.get('email')

            if rec_type == 'attractions':
                cur = mysql.connection.cursor()
                cur.execute('Select * from attractions where email=%s', (email,))
                data = cur.fetchall()
                cur.close()
                return render_template('favourite_attractions.html', data=data)

            elif rec_type == 'hotels':
                cur = mysql.connection.cursor()
                cur.execute('Select * from hotels where email=%s', (email,))
                data = cur.fetchall()
                cur.close()
                return render_template('favourite_hotels.html', data=data)

            elif rec_type == 'restaurants':
                cur = mysql.connection.cursor()
                cur.execute('Select * from restaurants where email=%s', (email,))
                data = cur.fetchall()
                cur.close()
                return render_template('favourite_restaurants.html', data=data)
        else:
            return redirect(url_for('home'))
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/remove_from_favourites/<string:rec_type>/<string:name>', methods=['POST', 'GET'])
def remove_from_favourites(rec_type, name):
    if 'loggedin' in session:
        if 'admin' not in session:
            email = session.get('email')

            if rec_type == 'attractions':
                cur = mysql.connection.cursor()
                cur.execute('Select * from attractions where name=%s and email=%s', (name, email))
                data = cur.fetchone()

                cur.execute('Delete from attractions where id=%s', (data[0],))
                mysql.connection.commit()
                cur.close()

                return redirect('/favourites/attractions')

            elif rec_type == 'hotels':
                cur = mysql.connection.cursor()
                cur.execute('Select * from hotels where name=%s and email=%s', (name, email))
                data = cur.fetchone()

                cur.execute('Delete from hotels where id=%s', (data[0],))
                mysql.connection.commit()
                cur.close()

                return redirect('/favourites/hotels')

            elif rec_type == 'restaurants':
                cur = mysql.connection.cursor()
                cur.execute('Select * from restaurants where name=%s and email=%s', (name, email))
                data = cur.fetchone()

                cur.execute('Delete from restaurants where id=%s', (data[0],))
                mysql.connection.commit()
                cur.close()

                return redirect('/favourites/restaurants')

        else:
            return render_template('home.html')
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


@app.route('/speech_to_text_translator', methods=['POST', 'GET'])
def speech_to_text_translator():
    if 'loggedin' in session:
        if 'admin' not in session:
            if request.method == 'POST':
                lang_name = request.form.get('lang_name2')
                lang_name = str(lang_name)
                lang_name = lang_name.capitalize()
                text = request.form.get('input_text')
                text = str(text)

                #print(lang_name)
                #print(text)

                df = pd.read_csv('datasets/language-codes.csv')
                index = df.index

                try:
                    condition = df['language'] == lang_name
                    code_index = index[condition].tolist()
                    ci = code_index[0]
                    lang_code = df['alpha2'].iloc[ci]

                    #print(lang_code)

                    trans = Translator(from_lang=lang_code, to_lang='en')
                    trans_text = trans.translate(text)

                    return render_template('translator.html', text=trans_text)
                except:
                    return render_template('translator.html', text='Enter correct language name')

            return render_template('translator.html')
        else:
            return render_template('home.html')
    else:
        if 'admin' in session:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.permanent_session_lifetime = timedelta(hours=5, minutes=30)
    app.run(debug=True)
