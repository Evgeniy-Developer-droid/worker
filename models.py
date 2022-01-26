from flask_sqlalchemy import SQLAlchemy
 
db = SQLAlchemy()
 
class Job(db.Model):
    __tablename__ = 'job_stack'
 
    id = db.Column(db.Integer, primary_key = True)
    job_id = db.Column(db.Integer())
    url = db.Column(db.String())
    token = db.Column(db.String())
    priority = db.Column(db.String()) # normal | high
    callback = db.Column(db.String())
    results = db.Column(db.String())  # string object
    creation_date = db.Column(db.Integer())
    processing_time = db.Column(db.String(), default="0.0")
    status = db.Column(db.String(), default="waiting")  # waiting | performed | done
 
 
    def __repr__(self):
        return f"{self.job_id}"



class Statistic(db.Model):
    __tablename__ = "statistic"

    id = db.Column(db.Integer, primary_key = True)
    processed = db.Column(db.Integer(), default=0)
    in_progress = db.Column(db.Integer(), default=0)
    queue = db.Column(db.Integer(), default=0)
    average_processing_time = db.Column(db.String(), default="0.0")
    sum_time = db.Column(db.String(), default="0.0")

    def __repr__(self):
        return f"{self.id}"