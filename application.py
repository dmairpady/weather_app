from flask import Flask,render_template,request,flash,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import requests

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///weather.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']="thi23241"
db=SQLAlchemy(app)

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ city }&appid=9d0e92a088302c50540a48f8ddbb641a"
    r = requests.get(url).json()
    return r


class City(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)


@app.route('/',methods=['POST'])
def index_post():
    err_msg=''
    if request.method=='POST':
        new_city=request.form.get('city')
        if new_city:
            exists = db.session.query(City).filter(City.name == new_city).first()
            if not exists:
                new_city_data=get_weather_data(new_city)
                if new_city_data['cod']==200:
                    new_city_obj=City(name=new_city)
                    db.session.add(new_city_obj)
                    db.session.commit()
                else:
                    err_msg="City doesnt exist in the world"
            else:
                err_msg='City already exists'
    if err_msg:
        flash(err_msg,'error')
    else:
        flash('City added successfully')
    return redirect(url_for('index_get'))


@app.route('/')
def index_get():
    cities=City.query.all()
    weather_data=[]

    for city in cities:
        r=get_weather_data(city.name)
        weather={
            "temperature": r['main']['temp'],
            "city": r['name'],
            "description":r['weather'][0]['description'],
            "icon": r['weather'][0]['icon'],
            }
        weather_data.append(weather)
    return render_template('weather.html',weather_data=weather_data)

@app.route('/delete/<name>')
def delete_city(name):
    city=City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f"Successfully deleted {city.name} ",'success')
    return redirect(url_for('index_get'))

if __name__=='__main__':
    app.run(debug=True)