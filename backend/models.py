#Data Models

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db=SQLAlchemy()

class User_Info(db.Model):
    __tablename__='user_info'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,default=1)
    full_name=db.Column(db.String,nullable=False)
    address=db.Column(db.String,nullable=False)
    pincode=db.Column(db.Integer,nullable=False)
    #relationships
    service_requests = db.relationship('ServiceRequest', backref='user_info', lazy=True)


class ServiceProfessional(db.Model):
    __tablename__='service_professional'
    professional_id=db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String, nullable=False)
    password=db.Column(db.String,nullable=False)
    full_name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    experience = db.Column(db.String, nullable=False)
    service_type = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    profile_status = db.Column(db.String, default='pending', nullable=False)
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='service_professional', lazy=True)

# Service Table
class Service(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)  

    # Relationships
    service_professional = db.relationship('ServiceProfessional', backref='services', lazy=True)
    service_requests = db.relationship('ServiceRequest', backref='services', lazy=True)


# Service Request Table
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    request_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.professional_id'), nullable=False)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String, nullable=False)
    remarks = db.Column(db.String)

