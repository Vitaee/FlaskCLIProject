import datetime, click,threading,asyncio,logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, make_response
from flask.cli import cli, with_appcontext
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema
from flask_migrate import Migrate


# Init Flask App
app = Flask(__name__)

# Init DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create Model
class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    job = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Boolean(), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, job, status):
        self.job = job
        self.status = status

    def __repr__(self):
        return f'{int(self.id)}'

# Define ModelSchema
class JobSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Job
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    job = fields.String(required=True)
    status = fields.Boolean(required=True)


# Get config file
app.config.from_pyfile("./config/app.conf",silent=True)

# DB & Secret Key from config file
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{app.config.get("DB_USER")}:{app.config.get("DB_PASS")}@{app.config.get("DB_URL")}:{app.config.get("DB_PORT")}/{app.config.get("DB_DATABASE")}'
app.config['SECRET_KEY'] = f'{app.config.get("FLASK_SECRET")}'

# Debug method from config file
if app.debug is not True and app.config.get("LOG_METHOD") != "DEBUG":
    file_handler = RotatingFileHandler('jobsflask.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
else:
    logging.basicConfig(level=logging.DEBUG)


# Define command name and create funciton. Creates table named as jobs.
@click.command(name="createdb")
@with_appcontext
def create_db():
    db.create_all()
    app.logger.info("Db created.")

# Changing log method.
@click.command(name="logmethod")
@with_appcontext
def change_log_method():
    print(f"Inside logmethod function: {threading.current_thread().name}")
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(change_log())
    app.logger.info('Log method changed')
    return jsonify({"result": result})


# Adding jobs.
@click.command(name="addjob")
@click.argument('job')
@click.argument('status')
@with_appcontext
def add_job(job,status):
    
    print(f"Inside addjob function: {threading.current_thread().name}")
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(create_it(job,status))
    app.logger.info('Job added.')
    return jsonify({"result": result})

# Get all jobs.
@click.command(name="getjobs")
@with_appcontext
def get_jobs():
    print(f"Inside get jobs function: {threading.current_thread().name}")
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(all_jobs())
    app.logger.info('Jobs are fetched.')
    return jsonify({"result": result})

# Update job by id.
@click.command(name="updatejob")
@click.argument("status")
@click.argument("id")
@with_appcontext
def update_job(id,status):
    print(f"Inside update job function: {threading.current_thread().name}")
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(update_job_status(id,status))
    app.logger.info('Job updated.')
    return jsonify({"result": result})

# Delete job by id.
@click.command(name="deletejob")
@click.argument("id")
@with_appcontext
def deletejob(id):
    print(f"Inside delete job function: {threading.current_thread().name}")
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(delete_job(id))
    app.logger.info("Job deleted.")
    return jsonify({"result": result})

# Adding cli commands.
app.cli.add_command(create_db)
app.cli.add_command(add_job)
app.cli.add_command(get_jobs)
app.cli.add_command(update_job)
app.cli.add_command(change_log_method)


# Define async functions for jobs.
async def create_it(job,status):
    job = str(job.capitalize())
    status = str(status).capitalize()
    data = {
        "job":job,
        "status":bool(status)
    }
    todo_schema = JobSchema()
    todo = todo_schema.load(data)
    result = await todo_schema.dump(todo.create())
    return result

async def all_jobs():
    get_jobs = await Job.query.all()
    job_schema = JobSchema(many=True)
    todos = await job_schema.dump(get_jobs)
    return todos

async def update_job_status(id,status):
    status = str(status).capitalize()
    data = {
        
        "status":bool(status),
    }
    get_job = await Job.query.get(int(id))
    get_job.todo_description = data['status']
    db.session.add(get_job)
    db.session.commit()
    todo_schema = JobSchema(only=['id', 'status'])
    todo = await todo_schema.dump(get_job)
    return todo

async def delete_job(id):
    try:
        get_job = await Job.query.get(int(id))
    except:
        app.logger.error("The job does not exist!")
    

    db.session.delete(get_job)
    db.session.commit()
    return "Job deleted."

async def change_log():
    if app.config.get("LOG_METHOD") == 'Pro':
        app.config.update(LOG_METHOD="DEBUG",APP_DEBUG=True)
    else:
        app.config.update(LOG_METHOD="Pro", APP_DEBUG=False)

    return "Log method changed"



# Sample example of CRUD Api.
@app.route('/create', methods=['POST'])
def create_job():
    data = request.get_json()
    todo_schema = JobSchema()
    todo = todo_schema.load(data)
    result = todo_schema.dump(todo.create())
    return make_response(jsonify({"job": result}), 200)

@app.route('/gets', methods=['GET'])
def index():
    get_todos = Job.query.all()
    todo_schema = JobSchema(many=True)
    todos = todo_schema.dump(get_todos)
    return make_response(jsonify({"jobs": todos}))

@app.route('/get/<id>', methods=['GET'])
def get_job_by_id(id):
    get_todo = Job.query.get(id)
    todo_schema = JobSchema()
    todo = todo_schema.dump(get_todo)
    return make_response(jsonify({"job": todo}))

@app.route('/update/<id>', methods=['PUT'])
def update_job_by_id(id):
    data = request.get_json()
    get_todo = Job.query.get(id)
    if data.get('job'):
        get_todo.title = data['job']
    if data.get('status'):
        get_todo.todo_description = data['status']
    db.session.add(get_todo)
    db.session.commit()
    todo_schema = JobSchema(only=['id', 'job', 'status'])
    todo = todo_schema.dump(get_todo)
    return make_response(jsonify({"job": todo}))

@app.route('/delete/<id>', methods=['DELETE'])
def delete_todo_by_id(id):
    get_todo = Job.query.get(id)
    db.session.delete(get_todo)
    db.session.commit()
    return make_response("", 204)

if __name__ == "__main__":
    app.run(debug=app.config.get("APP_DEBUG"))