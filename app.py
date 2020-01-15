from flask import Flask, render_template, request, redirect, url_for, session

from source.dao.orm.populate import populate
from source.dao.db import PostgresDb
from source.dao.data import *
from source.dao.orm.entities import *
from source.forms.plan_exercises_form import PlanExercisesForm
from source.forms.training_form import TrainingForm
from source.forms.admin_form import AdminForm
from source.forms.exercise_form import ExerciseForm
from source.forms.user_form import UserForm
from source.forms.plan_form import PlanForm

import os

app = Flask(__name__)


app.secret_key = os.getenv("SECRET_KEY", "jkm-vhnej9l-vm9sqm3:lmve")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL",
                                                  "postgresql://{}:{}@{}:{}/{}".format(username, password, host, port,
                                                                                       database))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def check(admin_page):
    if not session["log_in"] or (admin_page and not session["admin"]) or (not admin_page and session["admin"]):
        return 1
    else:
        return 0


@app.route('/training', methods=['GET'])
def index_training():
    if check(admin_page=False):
        return render_template('login.html', error="no rights, login another way")

    db = PostgresDb()

    show = bool(request.args.get("show"))
    if not show:
        train_query = db.sqlalchemy_session.query(Training).filter(Training.user_id == session['user_id'],
                                                                   Training.date >= datetime.date.today()).all()
    else:
        train_query = db.sqlalchemy_session.query(Training).filter(Training.user_id == session['user_id']).all()

    train = {}
    for item in train_query:

        if item.date not in train:
            train[item.date] = [item]
        else:
            train[item.date].append(item)

    if request.args.get("msg"):
        return render_template('training.html', trainings=train, msg=str(request.args.get("msg")), show=show)
    else:
        return render_template('training.html', trainings=train, msg=0, show=show)


@app.route('/new_training', methods=['GET', 'POST'])
def new_training():
    if check(admin_page=False):
        return render_template('login.html', error="no rights, login another way")

    db = PostgresDb()
    form = TrainingForm(user_id=session['user_id'])

    if request.method == 'POST':
        if not form.validate():
            return render_template('training_form.html', form=form, action="new_training",
                                   form_name="New training with plan name: {}".format(form.new_plan_name.data))
        else:
            plan_obj = Plan(title=form.new_plan_name.data, user_created=True)
            db.sqlalchemy_session.add(plan_obj)
            db.sqlalchemy_session.commit()

            exercises = db.sqlalchemy_session.query(Plan_exercises).filter(
                Plan_exercises.plan_fk == form.plan_id.data).all()

            plan_obj = db.sqlalchemy_session.query(Plan).filter(Plan.title == form.new_plan_name.data).one()
            for exercise in exercises:
                plan_exercise = Plan_exercises(
                    plan_fk=plan_obj.id,
                    exercise_id=exercise.exercise_id,
                    weight=exercise.weight,
                    count=exercise.count
                )
                db.sqlalchemy_session.add(plan_exercise)

            training_obj = Training(
                user_id=session['user_id'],
                plan_id=plan_obj.id,
                date=form.date.data.strftime("%d-%b-%y"),
            )

            db.sqlalchemy_session.add(training_obj)
            db.sqlalchemy_session.commit()

            return redirect(url_for('index_training'))

    user = db.sqlalchemy_session.query(User).filter(User.id == session['user_id']).one()
    new_plan_name = "{}_{}".format(user.login, datetime.datetime.now().strftime("%d/%m/%Y_%H:%M:%S"))
    form.new_plan_name.data = new_plan_name

    return render_template('training_form.html', form=form,
                           form_name="New training with plan name: {}".format(new_plan_name), action="new_training")


@app.route('/edit_training', methods=['GET', 'POST'])
def edit_training():
    if check(admin_page=False):
        return render_template('login.html', error="no rights, login another way")

    form = TrainingForm(user_id=session['user_id'], edit=True)

    if request.method == 'GET':

        id = request.args.get('id')
        db = PostgresDb()

        training_obj = db.sqlalchemy_session.query(Training).filter(Training.id == id).one()

        # fill form
        form.id.data = id
        form.plan_id.data = training_obj.plan_id
        form.date.data = training_obj.date

        return render_template('training_form.html', form=form, form_name="Edit training",
                               action="edit_training")

    else:
        if not form.validate():
            return render_template('training_form.html', form=form, form_name="Edit training",
                                   action="edit_training")
        else:
            db = PostgresDb()
            # find discipline
            training_obj = db.sqlalchemy_session.query(Training).filter(Training.id == int(form.id.data)).one()

            # update fields from form data
            training_obj.id = int(form.id.data)
            training_obj.plan_id = form.plan_id.data
            training_obj.date = form.date.data
            training_obj.user_id = session['user_id']

            db.sqlalchemy_session.commit()

            return redirect(url_for('index_training'))


@app.route('/delete_training')
def delete_training():
    if check(admin_page=False):
        return render_template('login.html', error="no rights, login another way")

    id = request.args.get('id')

    db = PostgresDb()

    result = db.sqlalchemy_session.query(Training).filter(Training.id == id).one()

    db.sqlalchemy_session.delete(result)
    db.sqlalchemy_session.commit()

    return redirect(url_for('index_training'))


@app.route('/open_training')
def open_training():
    if check(admin_page=False):
        return render_template('login.html', error="no rights, login another way")

    id = request.args.get('id')

    db = PostgresDb()
    train = db.sqlalchemy_session.query(Training).filter(Training.id == id).one()
    exercises = db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.plan_fk == train.plan_id).all()

    if request.args.get("msg"):
        return render_template('open_training.html', plan_exercises=exercises, msg=str(request.args.get("msg")),
                               plan_title=train.plan_entity.title)
    else:
        return render_template('open_training.html', plan_exercises=exercises, msg=0,
                               plan_title=train.plan_entity.title)


@app.route('/change_plan_properties', methods=['GET', 'POST'])
def change_plan_properties():
    if check(admin_page=False):
        return render_template('login.html', error="no rights, login another way")

    form = PlanExercisesForm()
    del form.plan_fk
    del form.exercise_id

    db = PostgresDb()

    if request.method == 'GET':

        id = request.args.get('id')

        plan_obj = db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.id == id).one()
        # fill form
        form.id.data = id
        form.weight.data = plan_obj.weight
        form.count.data = plan_obj.count

        return render_template('change_plan_properties.html', form=form,
                               form_name="Edit plan exercise: {}".format(plan_obj.exercise_entity.title),
                               action="change_plan_properties")

    else:
        plan_obj = db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.id == int(form.id.data)).one()

        if not form.validate():
            return render_template('change_plan_properties.html', form=form,
                                   form_name="EEdit plan exercise: {}".format(plan_obj.exercise_entity.title),
                                   action="change_plan_properties")
        else:
            # update fields from form data
            plan_obj.weight = form.weight.data
            plan_obj.count = form.count.data

            db.sqlalchemy_session.commit()

            return redirect(url_for('index_training'))


@app.route('/')
def hello():
    return render_template('login.html', error=False)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('log_in', None)
    session.pop('admin', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = PostgresDb()

        login = request.form['login']
        password = request.form['password']
        admin = db.sqlalchemy_session.query(Admin).filter(Admin.login == login, Admin.password == password).all()

        if admin:

            session['admin'] = True
            session['log_in'] = True

            return redirect(url_for('index'))
        else:
            user = db.sqlalchemy_session.query(User).filter(User.login == login,
                                                            User.password == password).all()
            if user:

                if len(user) > 1:
                    raise Exception('more than 2 user have same login')

                session['admin'] = False
                session['log_in'] = True

                session['user_id'] = user[0].id
                return redirect(url_for('index_training'))
            else:

                session['admin'] = False
                session['log_in'] = False

                return render_template('login.html', error="Wrong login or password")
    return render_template('login.html', error=False)


# ADMIN  -------------------------------------------------------------------------------------------------------------


@app.route('/index')
def index():
    return render_template('index.html')


# user ORIENTED QUERIES ------------------------------------------------------------------------------------------


@app.route('/user', methods=['GET'])
def index_user():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    db = PostgresDb()

    result = db.sqlalchemy_session.query(User).all()

    if request.args.get("msg"):
        return render_template('user.html', users=result, msg=str(request.args.get("msg")))
    else:
        return render_template('user.html', users=result, msg=0)


@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = UserForm()

    if request.method == 'POST':
        form.strip()
        if not form.validate():
            return render_template('user_form.html', form=form, form_name="New user", action="new_user")
        else:
            db = PostgresDb()

            if db.sqlalchemy_session.query(User).filter(User.login == form.login.data).all():
                return render_template('user_form.html', form=form, form_name="New user",
                                       action="new_user",
                                       msg="Cant add this record. Use another login")
            user_obj = User(
                name=form.name.data,
                surname=form.surname.data,
                login=form.login.data,
                password=form.password.data)

            db.sqlalchemy_session.add(user_obj)
            db.sqlalchemy_session.commit()

            return redirect(url_for('index_user'))

    return render_template('user_form.html', form=form, form_name="New user", action="new_user")


@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = UserForm()

    if request.method == 'GET':

        id = request.args.get('id')
        db = PostgresDb()
        user_obj = db.sqlalchemy_session.query(User).filter(User.id == id).one()

        # fill form and send to user
        form.id.data = user_obj.id
        form.name.data = user_obj.name
        form.surname.data = user_obj.surname
        form.login.data = user_obj.login
        form.password.data = user_obj.password

        return render_template('user_form.html', form=form, form_name="Edit user", action="edit_user")

    else:
        form.strip()

        if not form.validate():
            return render_template('user_form.html', form=form, form_name="Edit user",
                                   action="edit_user")
        else:
            db = PostgresDb()

            if db.sqlalchemy_session.query(User).filter(User.login == form.login.data, User.id != form.id.data).all():
                return render_template('user_form.html', form=form, form_name="Edit user",
                                       action="edit_user",
                                       msg="Cant edit this record. Use another login")
            # find professor
            user_obj = db.sqlalchemy_session.query(User).filter(User.id == form.id.data).one()

            # update fields from form data
            user_obj.professor_id = form.id.data
            user_obj.login = form.login.data
            user_obj.password = form.password.data
            user_obj.name = form.name.data
            user_obj.surname = form.surname.data

            db.sqlalchemy_session.commit()

            return redirect(url_for('index_user'))


@app.route('/delete_user')
def delete_user():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    id = request.args.get('id')

    db = PostgresDb()

    if db.sqlalchemy_session.query(Training).filter(Training.user_id == id).all():
        return redirect(url_for('index_user', msg="Cant delete this record. Use this record at training entity"))

    result = db.sqlalchemy_session.query(User).filter(User.id == id).one()

    db.sqlalchemy_session.delete(result)
    db.sqlalchemy_session.commit()

    return redirect(url_for('index_user'))


# END user ORIENTED QUERIES --------------------------------------------------------------------------------------

# exercise ORIENTED QUERIES --------------------------------------------------------------------------------------------


@app.route('/exercise', methods=['GET'])
def index_exercise():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    db = PostgresDb()

    result = db.sqlalchemy_session.query(Exercise).all()

    if request.args.get("msg"):
        return render_template('exercise.html', exercises=result, msg=str(request.args.get("msg")))
    else:
        return render_template('exercise.html', exercises=result, msg=0)


@app.route('/new_exercise', methods=['GET', 'POST'])
def new_exercise():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = ExerciseForm()

    if request.method == 'POST':
        form.strip()
        if not form.validate():
            return render_template('exercise_form.html', form=form, form_name="New exercise", action="new_exercise")
        else:
            db = PostgresDb()
            if db.sqlalchemy_session.query(Exercise).filter(Exercise.title == form.title.data).all():
                return render_template('exercise_form.html', form=form, form_name="New exercise", action="new_exercise",
                                       msg="Cant add this record. Use another title")

            exercise_obj = Exercise(
                title=form.title.data,
                muscle_type=form.muscle_type.data,
                description=form.description.data)

            db.sqlalchemy_session.add(exercise_obj)
            db.sqlalchemy_session.commit()

            return redirect(url_for('index_exercise'))

    return render_template('exercise_form.html', form=form, form_name="New exercise", action="new_exercise")


@app.route('/edit_exercise', methods=['GET', 'POST'])
def edit_exercise():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = ExerciseForm()

    if request.method == 'GET':

        id = request.args.get('id')
        db = PostgresDb()
        exercise = db.sqlalchemy_session.query(Exercise).filter(Exercise.id == id).one()

        # fill form and send to student
        form.id.data = exercise.id
        form.title.data = exercise.title
        form.muscle_type.data = exercise.muscle_type
        form.description.data = exercise.description

        return render_template('exercise_form.html', form=form, form_name="Edit exercise", action="edit_exercise")

    else:
        form.strip()
        if not form.validate():
            return render_template('exercise_form.html', form=form, form_name="Edit exercise", action="edit_exercise")
        else:
            db = PostgresDb()
            if db.sqlalchemy_session.query(Exercise).filter(Exercise.title == form.title.data,
                                                            Exercise.id != form.id.data).all():
                return render_template('exercise_form.html', form=form, form_name="Edit exercise",
                                       action="edit_exercise",
                                       msg="Cant edit this record. Use another title")

            exercise = db.sqlalchemy_session.query(Exercise).filter(Exercise.id == form.id.data).one()

            # update fields from form data
            exercise.id = form.id.data
            exercise.title = form.title.data
            exercise.muscle_type = form.muscle_type.data
            exercise.description = form.description.data

            db.sqlalchemy_session.commit()

            return redirect(url_for('index_exercise'))


@app.route('/delete_exercise')
def delete_exercise():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    id = request.args.get('id')

    db = PostgresDb()

    if db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.exercise_id == id).all():
        return redirect(url_for('index_exercise', msg="Cant delete this record. Use this record at "
                                                      "Plan_exercises entity"))

    result = db.sqlalchemy_session.query(Exercise).filter(Exercise.id == id).one()

    db.sqlalchemy_session.delete(result)
    db.sqlalchemy_session.commit()

    return redirect(url_for('index_exercise'))


# END exercise ORIENTED QUERIES ----------------------------------------------------------------------------------------

# ADMIN ORIENTED QUERIES --------------------------------------------------------------------------------------------

@app.route('/populate', methods=['GET'])
def populate():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    populate()

    return redirect(url_for('index_admin'))


@app.route('/admin', methods=['GET'])
def index_admin():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    db = PostgresDb()

    result = db.sqlalchemy_session.query(Admin).all()

    return render_template('admin.html', admins=result)


@app.route('/new_admin', methods=['GET', 'POST'])
def new_admin():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = AdminForm()
    if request.method == 'POST':
        form.strip()
        if not form.validate():
            return render_template('admin_form.html', form=form, form_name="New admin", action="new_admin")
        else:
            admin_obj = Admin(
                login=form.login.data,
                password=form.password.data)

            db = PostgresDb()
            db.sqlalchemy_session.add(admin_obj)
            db.sqlalchemy_session.commit()

            return redirect(url_for('index_admin'))

    return render_template('admin_form.html', form=form, form_name="New admin", action="new_admin")


@app.route('/edit_admin', methods=['GET', 'POST'])
def edit_admin():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = AdminForm()

    if request.method == 'GET':

        admin_id = request.args.get('admin_id')
        db = PostgresDb()
        admin = db.sqlalchemy_session.query(Admin).filter(Admin.id == admin_id).one()

        # fill form and send to student
        form.id.data = admin.id
        form.login.data = admin.login
        form.password.data = admin.password

        return render_template('admin_form.html', form=form, form_name="Edit admin", action="edit_admint")

    else:
        form.strip()
        if not form.validate():
            return render_template('admin_form.html', form=form, form_name="Edit admin", action="edit_admin")
        else:
            db = PostgresDb()
            # find student
            admin = db.sqlalchemy_session.query(Admin).filter(Admin.id == form.id.data).one()

            # update fields from form data
            admin.id = form.id.data
            admin.login = form.login.data
            admin.password = form.password.data

            db.sqlalchemy_session.commit()

            return redirect(url_for('index_admin'))


@app.route('/delete_admin')
def delete_admin():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    admin_id = request.args.get('admin_id')

    db = PostgresDb()

    result = db.sqlalchemy_session.query(Admin).filter(Admin.id == admin_id).one()

    db.sqlalchemy_session.delete(result)
    db.sqlalchemy_session.commit()

    return redirect(url_for('index_admin'))


# END ADMIN ORIENTED QUERIES ----------------------------------------------------------------------------------------

# plan ORIENTED QUERIES ---------------------------------------------------------------------------------------

@app.route('/plan', methods=['GET'])
def index_plan():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    db = PostgresDb()

    plan = db.sqlalchemy_session.query(Plan).all()

    if request.args.get("msg"):
        return render_template('plan.html', plans=plan, msg=str(request.args.get("msg")))
    else:
        return render_template('plan.html', plans=plan, msg=0)


@app.route('/new_plan', methods=['GET', 'POST'])
def new_plan():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = PlanForm()
    if request.method == 'POST':
        form.strip()
        if not form.validate():
            return render_template('plan_form.html', form=form, form_name="New plan",
                                   action="new_plan")
        else:
            db = PostgresDb()
            if db.sqlalchemy_session.query(Plan).filter(Plan.title == form.title.data).all():
                return render_template('plan_form.html', form=form, form_name="New plan",
                                       action="new_plan", msg="Cant add this record. Use another title")
            plan_obj = Plan(title=form.title.data, user_created=False)

            db.sqlalchemy_session.add(plan_obj)
            db.sqlalchemy_session.commit()

            return redirect(url_for('index_plan'))

    return render_template('plan_form.html', form=form, form_name="New plan", action="new_plan")


@app.route('/edit_plan', methods=['GET', 'POST'])
def edit_plan():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = PlanForm()

    if request.method == 'GET':

        id = request.args.get('id')
        db = PostgresDb()

        discipline = db.sqlalchemy_session.query(Plan).filter(Plan.id == id).one()

        # fill form and send to discipline
        form.id.data = id
        form.title.data = discipline.title

        return render_template('plan_form.html', form=form, form_name="Edit plan", action="edit_plan")

    else:
        form.strip()
        if not form.validate():
            return render_template('plan_form.html', form=form, form_name="Edit plan",
                                   action="edit_plan")
        else:
            db = PostgresDb()

            if db.sqlalchemy_session.query(Plan).filter(Plan.title == form.title.data,
                                                        Plan.id != form.id.data).all():
                return render_template('plan_form.html', form=form, form_name="Edit plan",
                                       action="edit_plan", msg="Cant edit this record. Use another title")

            # find
            plan = db.sqlalchemy_session.query(Plan).filter(Plan.id == int(form.id.data)).one()

            # update fields from form data
            plan.id = int(form.id.data)
            plan.title = form.title.data

            db.sqlalchemy_session.commit()

            return redirect(url_for('index_plan'))


@app.route('/delete_plan')
def delete_plan():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    id = request.args.get('id')

    db = PostgresDb()

    if db.sqlalchemy_session.query(Training).filter(Training.plan_id == id).all():
        return redirect(url_for('index_plan', msg="Cant delete this record. Use this record at Training entity"))

    if db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.plan_fk == id).all():
        db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.plan_fk == id).delete()

    result = db.sqlalchemy_session.query(Plan).filter(Plan.id == id).one()
    db.sqlalchemy_session.delete(result)

    db.sqlalchemy_session.commit()

    return redirect(url_for('index_plan'))


# END plan ORIENTED QUERIES ----------------------------------------------------------------------------------------

# plan_exercises ORIENTED QUERIES -----------------------------------------------------------------------------------


@app.route('/plan_exercises', methods=['GET'])
def index_plan_exercises():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    db = PostgresDb()

    plan = db.sqlalchemy_session.query(Plan_exercises).order_by(Plan_exercises.plan_fk).all()

    if request.args.get("msg"):
        return render_template('plan_exercises.html', plan_exercises=plan, msg=str(request.args.get("msg")))
    else:
        return render_template('plan_exercises.html', plan_exercises=plan, msg=0)


@app.route('/new_plan_exercises', methods=['GET', 'POST'])
def new_plan_exercises():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = PlanExercisesForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('plan_exercises_form.html', form=form, form_name="New plan exercise",
                                   action="new_plan_exercises")
        else:
            plan_obj = Plan_exercises(
                plan_fk=form.plan_fk.data,
                exercise_id=form.exercise_id.data,
                weight=form.weight.data,
                count=form.count.data
            )

            db = PostgresDb()
            db.sqlalchemy_session.add(plan_obj)
            db.sqlalchemy_session.commit()

            return redirect(url_for('index_plan_exercises'))

    return render_template('plan_exercises_form.html', form=form, form_name="New plan exercise",
                           action="new_plan_exercises")


@app.route('/edit_plan_exercises', methods=['GET', 'POST'])
def edit_plan_exercises():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    form = PlanExercisesForm()
    db = PostgresDb()

    if request.method == 'GET':

        id = request.args.get('id')
        db = PostgresDb()

        plan_obj = db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.id == id).one()

        # fill form
        form.id.data = id
        form.plan_fk.data = plan_obj.plan_fk
        form.exercise_id.data = plan_obj.exercise_id
        form.weight.data = plan_obj.weight
        form.count.data = plan_obj.count

        return render_template('plan_exercises_form.html', form=form, form_name="Edit plan exercise",
                               action="edit_plan_exercises")

    else:
        if not form.validate():
            return render_template('plan_exercises_form.html', form=form, form_name="Edit plan exercise",
                                   action="edit_plan_exercises")
        else:
            # find discipline
            plan_obj = db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.id == int(form.id.data)).one()

            # update fields from form data
            plan_obj.id = int(form.id.data)
            plan_obj.plan_fk = form.plan_fk.data
            plan_obj.exercise_id = form.exercise_id.data
            plan_obj.weight = form.weight.data
            plan_obj.count = form.count.data

            db.sqlalchemy_session.commit()

            return redirect(url_for('index_plan_exercises'))


@app.route('/delete_plan_exercises')
def delete_plan_exercises():
    if check(admin_page=True):
        return render_template('login.html', error="no rights, login another way")

    id = request.args.get('id')

    db = PostgresDb()

    result = db.sqlalchemy_session.query(Plan_exercises).filter(Plan_exercises.id == id).one()

    db.sqlalchemy_session.delete(result)
    db.sqlalchemy_session.commit()

    return redirect(url_for('index_plan_exercises'))


# END plan_exercises ORIENTED QUERIES ---------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
