#app routes
from flask import Flask, render_template, request, url_for, redirect
from flask import current_app as app
from .models import*
from datetime import datetime

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        uname=request.form.get("username")
        pwd=request.form.get("password")
        usr=User_Info.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0:
            return redirect(url_for("admindash"))
        elif usr and usr.role==1:
            return redirect(url_for("userdash", user_id=usr.id))
        prof = ServiceProfessional.query.filter_by(email=uname, password=pwd).first()
        if prof:
            return redirect(url_for("profdash", professional_id=prof.professional_id))
        else:
            return render_template("login.html",msg="Invalid user credentials...")
    return render_template("login.html")



@app.route("/custosign", methods=["GET", "POST"])
def custosign():
    if request.method=="POST":
        uname=request.form.get("username")
        pwd=request.form.get("password")
        full_name=request.form.get("full_name")
        address=request.form.get("address")
        pincode=request.form.get("pincode")
        new_usr=User_Info(email=uname,password=pwd,full_name=full_name,address=address,pincode=pincode)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration Successful")
    return render_template("custosign.html",msg="")

@app.route("/professional_register", methods=["GET", "POST"])
def professional_register():
    names = db.session.query(Service.service_name).distinct().all()
    enumerated_names=list(enumerate(names,start=1))
    if request.method=="POST":
        uname=request.form.get("username")
        pwd=request.form.get("password")
        full_name=request.form.get("full_name")
        service_type=request.form.get("service_type")
        experience=request.form.get("experience")
        phone_number=request.form.get("phone_number")
        address=request.form.get("address")
        pincode=request.form.get("pincode")
        new_usr=ServiceProfessional(email=uname,password=pwd,full_name=full_name,experience=experience,service_type=service_type,phone_number=phone_number,address=address,profile_status='pending')
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html")
    return render_template("professional_register.html",serv = enumerated_names)




@app.route('/admindash')
def admindash():
    services=Service.query.all()
    professionals = ServiceProfessional.query.all()
    service_requests = ServiceRequest.query.all() 
    customers = User_Info.query.filter_by(role=1).all()
    return render_template("admindash.html", services=services,customers=customers, professionals=professionals, service_requests=service_requests)

@app.route('/new_service', methods=["POST","GET"])
def new_service():
    if request.method=="POST":
        service_name=request.form.get("service_name")
        description=request.form.get("description")
        base_price=request.form.get("base_price")
        time_required=request.form.get("time_required")
        add_service=Service(service_name=service_name, description=description, base_price=base_price, time_required=time_required)
        db.session.add(add_service)
        db.session.commit()
        return redirect(url_for("admindash"))
    return render_template("addservice.html")


@app.route('/userdash/<int:user_id>')
def userdash(user_id):

    user = User_Info.query.get(user_id)
    services = Service.query.all()
    professionals = ServiceProfessional.query.all()
    service_requests = ServiceRequest.query.filter_by(user_id=user_id).order_by(ServiceRequest.date_of_request.desc()).all()
    return render_template('userdash.html', user_id=user_id, services=services, professionals=professionals,service_requests=service_requests,user=user)

@app.route('/profdash/<int:professional_id>', methods=["GET", "POST"])
def profdash(professional_id):
    prof=ServiceProfessional.query.filter_by(professional_id=professional_id).first()

    todays_services = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.service_status.in_(['Requested', 'Accepted'])
    ).all()
    closed_services = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.service_status.in_(['Completed', 'Rejected'])
    ).all()

   
    return render_template('profdash.html',todays_services=todays_services,closed_services=closed_services,professional_id=professional_id, prof=prof)

#edit service and delete service 

@app.route("/editservice/<service_id>",methods=["GET","POST"])
def editservice(service_id):
    v=Service.query.filter_by(service_id=service_id).first()
    if request.method=="POST":
        service_name=request.form.get("service_name")
        description=request.form.get("description")
        base_price=request.form.get("base_price")
        time_required=request.form.get("time_required")
        v.service_name=service_name
        v.description=description
        v.base_price=base_price      
        v.time_required=time_required


        db.session.commit()
        return redirect(url_for("admindash"))
    
    return render_template("editservice.html",service=v)

@app.route("/delete_new_service/<service_id>",methods=["GET","POST"])
def delete_new_service(service_id):
    v=Service.query.filter_by(service_id=service_id).first()
    try:
        db.session.delete(v)
        db.session.commit()
        return redirect(url_for("admindash",s=1))
    except:
        return redirect(url_for("admindash",s=0))


@app.route("/book_service/<int:user_id>/<int:service_id>",methods=["GET","POST"])
def book_service(user_id, service_id):
    if request.method=="POST":
            
        serv_id=request.form.get("service_id")
        usr_id= request.form.get('user_id')
        print(serv_id,usr_id)
        professional = ServiceProfessional.query.filter_by(service_type=serv_id, profile_status='active').first()
        print(professional)
        if not professional:            
            return redirect(url_for("userdash", user_id=user_id))


        new_request=ServiceRequest(service_id=service_id,user_id=user_id,professional_id=professional.professional_id,service_status='Requested')
        db.session.add(new_request)
        db.session.commit()
        
        return redirect(url_for("userdash", user_id=user_id))
    return render_template("book_service.html",user_id=user_id,service_id=service_id)

    


@app.route('/accept_request/<int:professional_id>', methods=['POST'])
def accept_request(professional_id):
    request_id = request.form.get('request_id')
    
    service_request = ServiceRequest.query.get(request_id)
    service_request.service_status = 'Accepted'
    db.session.commit()

    return redirect(url_for('profdash',professional_id=professional_id))

@app.route('/reject_request/<int:professional_id>', methods=['POST'])
def reject_request(professional_id):
    request_id = request.form.get('request_id')
    service_request = ServiceRequest.query.get(request_id)
    service_request.service_status = 'Rejected'
    db.session.commit()

    return redirect(url_for('profdash',professional_id=professional_id))

#searching userdashboard

@app.route("/search/<int:user_id>", methods=["GET","POST"])
def search(user_id):
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        print(search_txt)
        by_services=search_by_services(search_txt)
        user=User_Info.query.filter_by(id=user_id).first()
        if by_services:
            return render_template('userdash.html', services=by_services, user_id=user_id, user=user)

    return redirect(url_for("userdash",user_id=user_id))

def search_by_services(search_txt):
    services = Service.query.filter(Service.service_name.ilike(f"%{search_txt}%")).all()
    
    return services

#searching professional dashboard

@app.route("/prof_search/<int:professional_id>", methods=["GET","POST"])
def prof_search(professional_id):
    if request.method=="POST":
        search_txt=request.form.get("query")
        search_by=request.form.get("column")

        # by_address=search_by_address(search_txt)
        # print(by_address)

    todays_services = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.service_status.in_(['Requested', 'Accepted'])
    ).all()

    closed_services = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.service_status.in_(['Completed', 'Rejected'])
    ).all()

    if search_by == 'address':    
        if search_txt:
            todays_services = [
                service for service in todays_services
                if search_txt.lower() in service.user_info.address.lower()
            ]
            closed_services = [
                service for service in closed_services
                if search_txt.lower() in service.user_info.address.lower()
            ]
    elif search_by == 'status':    
        if search_txt:
            todays_services = [
                service for service in todays_services
                if search_txt.lower() in service.service_status.lower()
            ]
            closed_services = [
                service for service in closed_services
                if search_txt.lower() in service.service_status.lower()
            ]
    prof=ServiceProfessional.query.filter_by(professional_id=professional_id).first()


        # if by_address:
    return render_template('profdash.html',prof=prof, professional_id=professional_id, todays_services=todays_services, closed_services=closed_services)

    # return redirect(url_for("profdash",professional_id=professional_id))

# def search_by_address(search_txt):
#     address = User_Info.query.filter(User_Info.address.ilike(f"%{search_txt}%")).all()
    
#     return address

#searching admin dashboard

@app.route("/admin_search", methods=["GET", "POST"])
def admin_search():
    if request.method == "POST":
        search_txt = request.form.get("query")
        search_by = request.form.get("column")
    print(search_txt)
    print(search_by)
    # Fetching all data from the database
    services = Service.query.all()
    professionals = ServiceProfessional.query.all()
    service_requests = ServiceRequest.query.all()
    customers = User_Info.query.filter_by(role=1).all()

    # Search logic based on the selected column
    if search_by == "Services" and search_txt:
        services = [
            service for service in services
            if search_txt.lower() in service.service_name.lower()
        ]
        print('s')

    elif search_by == "Professionals" and search_txt:
        professionals = [
            professional for professional in professionals
            if search_txt.lower() in professional.full_name.lower()
        ]
        print('s2')


    elif search_by == "Customers" and search_txt:
        customers = [
            customer for customer in customers
            if search_txt.lower() in customer.full_name.lower()
        ]
        print(customers)

    # Returning the filtered data to the template
    return render_template(
        'admindash.html',
        services=services,
        professionals=professionals,
        customers=customers,
        service_requests=service_requests
    )



# def search_by_address(search_txt):
#     address = User_Info.query.filter(User_Info.address.ilike(f"%{search_txt}%")).all()
    
#     return address




@app.route('/close_request/<int:user_id>', methods=['POST'])
def close_request(user_id):
    request_id = request.form.get('request_id')
    service_request = ServiceRequest.query.get(request_id)
    if service_request.service_status == 'Completed':
        service_request.service_status = 'Closed'
        db.session.commit()
        

    return redirect('/userdash/')

@app.route('/complete/<int:user_id>', methods=['POST'])
def complete(user_id):
    request_id = request.form.get('request_id')
    service_request = ServiceRequest.query.get(request_id)
    if service_request.service_status == 'Accepted':
        service_request.service_status = 'Completed'
        service_request.date_of_completion=datetime.today().date()
        db.session.commit()
        

    return redirect(url_for('userdash',user_id=user_id))

@app.route('/accept_professional/<int:professional_id>', methods=['POST'])
def accept_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if professional.profile_status == 'pending':
        professional.profile_status = 'active'
        db.session.commit()

    return redirect(url_for('admindash',professional_id=professional_id))

@app.route('/reject_professional/<int:professional_id>', methods=['POST'])
def reject_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if professional.profile_status == 'pending':
        professional.profile_status = 'blocked'
        db.session.commit()
        
    return redirect(url_for('admindash',professional_id=professional_id))

@app.route('/block_professional/<int:professional_id>', methods=['POST'])
def block_professional(professional_id):
    print(professional_id)
    professional = ServiceProfessional.query.get(professional_id)
    if professional.profile_status == 'active':
        professional.profile_status = 'blocked'
        db.session.commit()
       
    return redirect(url_for('admindash',professional_id=professional_id))

@app.route('/unblock_professional/<int:professional_id>', methods=['POST'])
def unblock_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if professional.profile_status == 'blocked':
        professional.profile_status = 'active'
        db.session.commit()
        
    return redirect(url_for('admindash',professional_id=professional_id))



@app.route("/professional_profile/<int:professional_id>", methods=["GET", "POST"])
def professional_profile(professional_id):
    professional = ServiceProfessional.query.get(professional_id)

    if request.method == "POST":
        # Update profile with form data
        professional.full_name = request.form.get("full_name")
        professional.email = request.form.get("email")
        professional.phone_number = request.form.get("phone_number")
        professional.address = request.form.get("address")
        professional.experience = request.form.get("experience")
        professional.service_type = request.form.get("service_type")
        
        # Commit changes to the database
        db.session.commit()

        # Redirect to the same page to show updated info
        return redirect(url_for('professional_profile', professional_id=professional_id))

    return render_template('professional_profile.html', professional=professional)


#edit and update profile

@app.route("/edit_profile/<int:professional_id>", methods=["GET", "POST"])
def edit_profile(professional_id):
    # Query the profile using the profile_id
    prof = ServiceProfessional.query.filter_by(professional_id=professional_id).first()
    

    
    if request.method == "POST":
        # Get updated values from the form
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        address = request.form.get("address")
        experience = request.form.get("experience")
        service_type = request.form.get("service_type")

        # Update the profile object
        prof.full_name = full_name
        prof.email = email
        prof.phone_number = phone_number
        prof.address = address
        prof.experience = experience
        prof.service_type = service_type
        # Commit changes to the database
        db.session.commit()

        # Redirect to a relevant page (e.g., admin dashboard or profile page)
        return redirect(url_for("profdash", professional_id=professional_id))
    
    # Render the edit profile page with the current profile data
    return render_template("edit_profile.html", prof=prof)

# edit customers

@app.route("/userdash/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    # Query the User_Info table by user_id
    user = User_Info.query.get(user_id)


    if request.method == "POST":
        # Get updated values from the form
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        address = request.form.get("address")
        pincode = request.form.get("pincode")

        # Update the user's details
        user.full_name = full_name
        user.email = email
        user.address = address
        user.pincode = int(pincode) if pincode.isdigit() else user.pincode

        # Save changes to the database
        db.session.commit()

        # Redirect to the user's dashboard
        return redirect(url_for("userdash", user_id=user_id))

    # Render the edit user page with the current user's data
    return render_template("edit_user.html", user=user)

# review professional

@app.route('/userdash/submit_remarks/<int:request_id>', methods=['POST'])
def submit_remarks(request_id):
    service_request = ServiceRequest.query.get(request_id)

    if service_request.service_status != 'Completed':

        return redirect(url_for('userdash',user_id=user_id))  

    remarks = request.form.get('remarks')
    if remarks:
        service_request.remarks = remarks
        db.session.commit()


    return redirect(url_for('userdash',user_id=request.form.get('user_id'))) 

