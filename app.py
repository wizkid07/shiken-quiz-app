
# imports

from flask import Flask,render_template,request,redirect,url_for,flash,session,g,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.inspection import inspect



############################################################################

# configuration

app = Flask(__name__)
app.secret_key="Sangimangi"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///quiz.db'
db=SQLAlchemy(app)

#############################################################################


# database model

# class Serializer(object):

#     def serialize(self):
#         return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

#     @staticmethod
#     def serialize_list(l):
#         return [m.serialize() for m in l]

class User(db.Model):
    ID=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(36), nullable=False)
    email=db.Column(db.String(50), nullable=False)
    password=db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return 'User name: {username}'.format(username=self.username)

  
    # covert User object to dictionary
    def toDict(self):
        return{
            'ID':self.ID,
            'username':self.username,
            'email':self.email
        }
    
    #  covert user object list to dictionary
    def toDictlist(list):
        return [item.toDict() for item in list]


class Question(db.Model):
    ID=db.Column(db.Integer, primary_key=True)
    qn=db.Column(db.Text, nullable=False)
    op1=db.Column(db.Text,nullable=False)
    op2=db.Column(db.Text,nullable=False)
    op3=db.Column(db.Text,nullable=False)
    op4=db.Column(db.Text,nullable=False)
    crtans=db.Column(db.Text,nullable=False)
    type=db.Column(db.String(20),nullable=False)
    explanation=db.Column(db.Text,nullable=False)


class Quiz_data(db.Model):
    ID=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(36), nullable=False)
    score=db.Column(db.Integer, nullable=False)
    time=db.Column(db.Integer, nullable=False)
    topic=db.Column(db.String(36), nullable=False)
    date=db.Column(db.DateTime,default=datetime.utcnow)


class Bookmark(db.Model):
    ID=db.Column(db.Integer, primary_key=True)
    qn=db.Column(db.Text, nullable=False)
    op1=db.Column(db.Text,nullable=False)
    op2=db.Column(db.Text,nullable=False)
    op3=db.Column(db.Text,nullable=False)
    op4=db.Column(db.Text,nullable=False)
    crtans=db.Column(db.Text,nullable=False)
    type=db.Column(db.String(20),nullable=False)
    explanation=db.Column(db.Text,nullable=False)
    username=db.Column(db.String(36),primary_key=True)




#####################################################
    

# Routes

#global variable g to check if user is in session

@app.before_request
def before_request():
    g.user=None
    if 'user' in session:
        g.user=session['user']

#########################################################
# index page route and registration
@app.route('/' ,methods=['GET','POST'])
def index():
    # registration 
    if request.method =='POST':
        username = request.form.get("username")
        email =request.form.get("email")
        password=request.form.get("password")
        user = User(username=username,email=email,password=password)
        
        if User.query.filter_by(username=username).first():
            flash("Login already exists",'error')
            return render_template('index.html')
        else:
            db.session.add(user)
            db.session.commit()
            flash("You are now registered",'success')
            return render_template('index.html')

    # OnLoad

    return render_template('index.html')


#####################################################

# Login route 

@app.route('/home',methods=['GET','POST'])
def home():
    # create login session
    if request.method=='POST':
        username=request.form.get("username")
        password=request.form.get("password")
        session.pop('user',None)
        user =User.query.filter_by(username=username,password=password).first()
        if user:
            session['user']=username
            return render_template('homepage.html',username=username)
        else:
            flash("Login not created",'error')
            return redirect(url_for('index'))
    # if already in session
    elif g.user:
        username=session['user']
        return render_template('homepage.html',username=username)

    return redirect(url_for('index'))

#####################################################

# Categories route

@app.route('/output')
def output():
    if g.user:
        return render_template('output.html')
    return redirect(url_for('index'))

@app.route('/database')
def database():
    if g.user:
        return render_template('database.html')
    return redirect(url_for('index'))

@app.route('/aptitude')
def aptitude():
    if g.user:
        return render_template('aptitude.html')
    return redirect(url_for('index'))

########################################################

# quiz template route


@app.route('/quiz/<topic>')
def quiz(topic):
    if g.user:
        session['topic']=topic
        if topic=='random':
            question =Question.query.filter(db.or_(Question.type=='string',Question.type=='array',Question.type=='pointer')).order_by(func.random()).limit(10)
            
        else:
            question =Question.query.filter_by(type=topic).order_by(func.random()).limit(10)
        
        return render_template('quiz.html',question=question)
        
    return redirect(url_for('index'))
            

        
##############################################################################

# Save quizData into database

@app.route('/savedata',methods=['POST'])
def savedata():
    if g.user:
        if request.method=='POST':
            username=session['user']
            score=request.form['score']
            time=request.form['time']
            topic=session['topic']
            if(time !="" and score!=""):
                quiz_data=Quiz_data(username=username,score=score,time=time,topic=topic)
                db.session.add(quiz_data)
                db.session.commit()

            
            return jsonify({'msg':"Go Home"})

        



    return redirect(url_for('index'))



##############################################################################

# TO SHOW PROGRESS

@app.route('/progress')
def progress():

    if g.user:
        username=session['user']

    # FOR STRINGS
        temp=Quiz_data.query.filter(Quiz_data.username==username,Quiz_data.topic=='string').all()
        stringFlag=0
        stringcount=0
        stringaccuracy=0

        if temp:
            stringFlag=1
            string=Quiz_data.query.filter(Quiz_data.topic=='string')
            stringcount=string.filter(Quiz_data.username==username).count()
            accuracy=Quiz_data.query.with_entities(func.avg(Quiz_data.score).label("myavg")).filter(Quiz_data.username==username,Quiz_data.topic=='string').first()
            stringaccuracy=round(accuracy.myavg * 10) 


        
        
        
        # FOR POINTERS
        temp=Quiz_data.query.filter(Quiz_data.username==username,Quiz_data.topic=='pointer').all()
        pointerFlag=0
        pointercount=0
        pointeraccuracy=0

        if temp:
            pointerFlag=1
            pointer=Quiz_data.query.filter(Quiz_data.topic=='pointer')
            pointercount=pointer.filter(Quiz_data.username==username).count()
            accuracy=Quiz_data.query.with_entities(func.avg(Quiz_data.score).label("myavg")).filter(Quiz_data.username==username,Quiz_data.topic=='pointer').first()
            pointeraccuracy=round(accuracy.myavg * 10)

        

        # FOR ARRAYS

        temp = Quiz_data.query.filter(Quiz_data.username==username,Quiz_data.topic=='array').all()
        arrayFlag=0
        arraycount=0
        arrayaccuracy=0
        if temp:
            arrayFlag=1
            array=Quiz_data.query.filter(Quiz_data.topic=='array')
            arraycount=array.filter(Quiz_data.username==username).count()
            accuracy=Quiz_data.query.with_entities(func.avg(Quiz_data.score).label("myavg")).filter(Quiz_data.username==username,Quiz_data.topic=='array').first()
            arrayaccuracy=round(accuracy.myavg * 10) 



        # FOR DATABASE

        temp = Quiz_data.query.filter(Quiz_data.username==username,Quiz_data.topic=='database').all()
        dbFlag=0
        dbcount=0
        dbaccuracy=0
        if temp:
            dbFlag=1
            db=Quiz_data.query.filter(Quiz_data.topic=='database')
            dbcount=db.filter(Quiz_data.username==username).count()
            accuracy=Quiz_data.query.with_entities(func.avg(Quiz_data.score).label("myavg")).filter(Quiz_data.username==username,Quiz_data.topic=='database').first()
            dbaccuracy=round(accuracy.myavg * 10) 



        # SQL

        temp = Quiz_data.query.filter(Quiz_data.username==username,Quiz_data.topic=='SQL').all()
        SQLFlag=0
        SQLcount=0
        SQLaccuracy=0
        if temp:
            SQLFlag=1
            SQL=Quiz_data.query.filter(Quiz_data.topic=='SQL')
            SQLcount=SQL.filter(Quiz_data.username==username).count()
            accuracy=Quiz_data.query.with_entities(func.avg(Quiz_data.score).label("myavg")).filter(Quiz_data.username==username,Quiz_data.topic=='SQL').first()
            SQLaccuracy=round(accuracy.myavg * 10) 



        # AGES

        temp = Quiz_data.query.filter(Quiz_data.username==username,Quiz_data.topic=='ages').all()
        agesFlag=0
        agescount=0
        agesaccuracy=0
        if temp:
            agesFlag=1
            ages=Quiz_data.query.filter(Quiz_data.topic=='ages')
            agescount=ages.filter(Quiz_data.username==username).count()
            accuracy=Quiz_data.query.with_entities(func.avg(Quiz_data.score).label("myavg")).filter(Quiz_data.username==username,Quiz_data.topic=='ages').first()
            agesaccuracy=round(accuracy.myavg * 10) 


        # CALENDAR

        temp = Quiz_data.query.filter(Quiz_data.username==username,Quiz_data.topic=='calendar').all()
        calendarFlag=0
        calendarcount=0
        calendaraccuracy=0
        if temp:
            calendarFlag=1
            calendar=Quiz_data.query.filter(Quiz_data.topic=='calendar')
            calendarcount=calendar.filter(Quiz_data.username==username).count()
            accuracy=Quiz_data.query.with_entities(func.avg(Quiz_data.score).label("myavg")).filter(Quiz_data.username==username,Quiz_data.topic=='calendar').first()
            calendaraccuracy=round(accuracy.myavg * 10) 




        # oddman

        temp = Quiz_data.query.filter(Quiz_data.username==username,Quiz_data.topic=='oddman').all()
        oddmanFlag=0
        oddmancount=0
        oddmanaccuracy=0
        if temp:
            oddmanFlag=1
            oddman=Quiz_data.query.filter(Quiz_data.topic=='oddman')
            oddmancount=oddman.filter(Quiz_data.username==username).count()
            accuracy=Quiz_data.query.with_entities(func.avg(Quiz_data.score).label("myavg")).filter(Quiz_data.username==username,Quiz_data.topic=='oddman').first()
            oddmanaccuracy=round(accuracy.myavg * 10) 


        flaglist=[stringFlag,arrayFlag,pointerFlag,dbFlag,SQLFlag,agesFlag,calendarFlag,oddmanFlag]
        countlist=[stringcount,arraycount,pointercount,dbcount,SQLcount,agescount,calendarcount,oddmancount]
        accuracylist=[stringaccuracy,arrayaccuracy,pointeraccuracy,dbaccuracy,SQLaccuracy,agesaccuracy,calendaraccuracy,oddmanaccuracy]



    
        
        

        return render_template('progress.html',flaglist=flaglist,countlist=countlist,accuracylist=accuracylist)

    return render_template('index.html')
        
##############################################################################


# TO SHOW LEADERBOARD

@app.route('/leaderboard')
def leaderboard():

    string=Quiz_data.query.filter_by(topic='string').order_by(Quiz_data.score.desc(),Quiz_data.time.desc()).limit(5).all()

    array=Quiz_data.query.filter_by(topic='array').order_by(Quiz_data.score.desc(),Quiz_data.time.desc()).limit(5).all()

    pointer=Quiz_data.query.filter_by(topic='pointer').order_by(Quiz_data.score.desc(),Quiz_data.time.desc()).limit(5).all()

    database=Quiz_data.query.filter_by(topic='database').order_by(Quiz_data.score.desc(),Quiz_data.time.desc()).limit(5).all()
    
    SQL = Quiz_data.query.filter_by(topic='SQL').order_by(Quiz_data.score.desc(),Quiz_data.time.desc()).limit(5).all()

    ages = Quiz_data.query.filter_by(topic='ages').order_by(Quiz_data.score.desc(),Quiz_data.time.desc()).limit(5).all()

    calender = Quiz_data.query.filter_by(topic='calendar').order_by(Quiz_data.score.desc(),Quiz_data.time.desc()).limit(5).all()

    oddman = Quiz_data.query.filter_by(topic='oddman').order_by(Quiz_data.score.desc(),Quiz_data.time.desc()).limit(5).all()
  
    
        

    return render_template('leaderboard.html',string=string,array=array,pointer=pointer,database=database,SQL=SQL,ages=ages,calender=calender,oddman=oddman)



##############################################################################

# TO show game history

@app.route('/gamehistory/<topic>' ,methods=['GET','POST'])
def gamehistory(topic):
    username=session['user']
    result=Quiz_data.query.filter(Quiz_data.username==username)
    history=result.filter(Quiz_data.topic==topic).order_by(Quiz_data.ID.desc()).limit(50).all()
    if request.method=="POST":
        sortby=request.form.get("sort")
        if sortby=="score":
            history=result.filter(Quiz_data.topic==topic).order_by(Quiz_data.score.desc()).limit(50).all()
            return render_template('gamehistory.html',history=history,topic=topic)
        else:
            history=result.filter(Quiz_data.topic==topic).order_by(Quiz_data.time.desc()).limit(50).all()
            return render_template('gamehistory.html',history=history,topic=topic)

    return render_template('gamehistory.html',history=history,topic=topic)
        


    
##############################################################################

#logout route

@app.route('/logout')
def logout():
    session.pop('user',None)
    session.pop('topic',None)
    return redirect(url_for('index'))



@app.route('/practice/<int:page_num>')
def practice(page_num):
    
    result=Question.query.paginate(per_page=10,page=page_num)
    return render_template('practice.html',questions=result,current_page=page_num)



@app.route('/bookmark',methods=['GET','POST'])
def bookmark():
    username=session['user']
    if request.method=='POST':
        ID=request.form.get('ID')
        alreadyBookmarked=Bookmark.query.filter_by(ID=ID,username=username).first()
        if alreadyBookmarked:
            return jsonify({'msg':"Already Bookmarked"})
        result=Question.query.filter_by(ID=ID).first()
        bookmark=Bookmark(ID=ID,qn=result.qn,op1=result.op1,op2=result.op2,op3=result.op3,op4=result.op4,crtans=result.crtans,type=result.type,explanation=result.explanation,username=username)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({'msg':"Bookmarked"})


@app.route('/bookmarks')
def bookmarks():
    username=session['user']
    bookmarks=Bookmark.query.filter_by(username=username).all()
    if bookmarks:
        return render_template('bookmarks.html',bookmarks=bookmarks)
    else:
        return render_template('bookmarks.html',bookmarks="No Bookmarks")
    








@app.route('/testing',methods=['GET','POST'])
def testing():
    # result=['string','database','coutput']
    if request.method=='POST':
        username=request.form.get("username")
        user=User.query.filter_by(username=username).first()
        user=User.toDict(user)
        
        return jsonify(user)
    
    
    result=User.query.all()
    userlist=[user.username for user in result]
    return render_template('testing.html',userlist=userlist)
    

@app.route('/adduser',methods=['GET','POST'])
def adduser():
    if request.method=='POST':
        # retrieve data from form
        username=request.form.get("username")
        password=request.form.get("password")
        email=request.form.get("email")

        # create user object and add to database
        user=User(username=username,email=email,password=password)
        db.session.add(user)
        db.session.commit()

        # get user who was inserted
        user=User.query.filter_by(username=username).first()

        # covert user object to dictionary datatype
        user=User.toDict(user)

        # return user as json to frontend
        return jsonify(user)
        

    
    
        



##########################################################

# run app
if __name__=="__main__":
    # Quiz_data.__table__.create(db.session.bind)
    app.run(debug=True)

