const Register={
    data(){
        return{
            role:'student',
            email:'',
            password:'',
            contact_no:'',
            name:'',
            dept:'',
            dob:'',
            year:'',
            cgpa:'',
            company_name:'',
            website:'',
            error:'',
            message:'',
            field:'',
            location:''
        }
    },
    methods:
    {
        gologin(){
            this.$emit('go-login')
        },
        async handleRegister(){
            const payload={
                'role':this.role,
                'email':this.email,
                'password':this.password,
                'contact_no':this.contact_no
            }
            if(this.role=='student')
            {
                payload['name']=this.name
                payload['dept']=this.dept
                payload['cgpa']=this.cgpa
                payload['dob']=this.dob
                payload['year']=this.year
            }
            else if (this.role=='company')
            {
                payload['name']=this.company_name
                payload['location']=this.location
                payload['field']=this.field
                payload['website']=this.website
            }
            try
            {
                const res=await fetch("/auth/register",{
                    'credentials':"include",
                    'method':'POST',
                    'headers':{'Content-Type':'application/json'},
                    'body':JSON.stringify(payload)
                })
                if (res.ok){
                    this.message="Registered Successfully! Please Login.."
                    setTimeout(()=>this.$emit('go-login'),1500)
                }
                else{
                    const errData=await res.json()
                    this.error=errData.error
                }
            }
            catch(err){
                this.error="Something went wrong. Please Try again!"
            }
        }
    },
    template:`
    <section class="auth-layout auth-layout--register">
    <div class="auth-copy">
      <span class="auth-copy__eyebrow">MAKE YOUR NEXT MOVE</span>
      <h1>Good things start with a connection.</h1>
      <p>Create your account to find opportunities, meet employers, and make your next career move.</p>
      <div class="auth-highlights">
        <div><span aria-hidden="true">01</span><span>Set up a profile that represents you</span></div>
        <div><span aria-hidden="true">02</span><span>Find the right path for your next step</span></div>
        <div><span aria-hidden="true">03</span><span>Keep your placement progress together</span></div>
      </div>
    </div>
    <div class="auth-panel">
    <div class="card auth-card">
    <div class="card-body">
    <span class="auth-form__eyebrow">GET STARTED</span>
    <h2 class="auth-form__title">Create your account</h2>
    <p class="auth-form__description">A few details are all you need to get started.</p>

    <div v-if="message" class="alert alert-success">{{message}}</div>
    <div v-if="error" class="alert alert-danger">{{error}}</div>

    <div class="mb-3">
    <label class="form-label">Email</label>
    <input v-model="email" type="email" class="form-control" placeholder="Enter your email" required></div>
    <div class="mb-3">
    <label class="form-label">Password</label>
    <input v-model="password" type="password" class="form-control" placeholder="Enter a password" required></div>
    <div class="mb-3">
    <label class="form-label">Contact Number</label>
    <input v-model="contact_no" type="text" class="form-control" placeholder="Enter your contact number" required></div>
    <div class="mb-3">
    <label class="form-label">Register as</label><br>
    <div class="form-check form-check-inline">
    <input class="form-check-input" v-model="role" type="radio" id="StudentRole" value="student">
    <label class="form-check-label" for="StudentRole">Student</label>
    </div>
    <div class="form-check form-check-inline">
    <input class="form-check-input" v-model="role" type="radio" id="CompanyRole" value="company">
    <label class="form-check-label" for="CompanyRole">Company</label>
    </div>
    </div>
    <div class="mb-3">
    <div v-if="role==='student'">
    <div class="mb-3">
    <label class="form-label">Student Name</label>
    <input v-model="name" type="text" class="form-control" placeholder="Enter student name" required></div>
    <div class="mb-3">
    <label class="form-label">Date of Birth</label>
    <input v-model="dob" type="date" class="form-control" placeholder="Enter Date of Birth" required></div>
    <div class="mb-3">
    <label class="form-label">Cumulative Grade point average (CGPA)</label>
    <input v-model="cgpa" type="text" class="form-control" placeholder="Enter student cgpa" required></div>
    <div class="mb-3">
    <label class="form-label">Department</label>
    <input v-model="dept" type="text" class="form-control" placeholder="Enter student department" required></div>
    <div class="mb-3">
    <label class="form-label">Year</label>
    <input v-model="year" type="text" class="form-control" placeholder="Enter year" required></div>
    </div>
    <div v-if="role=='company'">
    <div class="mb-3">
    <label class="form-label">Company Name</label>
    <input v-model="company_name" type="text" class="form-control" placeholder="Enter company name" required></div>
    <div class="mb-3">
    <label class="form-label">Website</label>
    <input v-model="website" type="text" class="form-control" placeholder="Enter company website" required></div>
    <div class="mb-3">
    <label class="form-label">Location</label>
    <input v-model="location" type="text" class="form-control" placeholder="Enter company location" required></div>
    <div class="mb-3">
    <label class="form-label">Industry</label>
    <input v-model="field" type="text" class="form-control" placeholder="Enter company industry" required></div>
    </div>
    </div>
    <div class="d-flex justify-content-center">
    <button @click="handleRegister" class="btn btn-success w-50 mb-3">Register</button>
    </div>
    <p class="text-center text-muted mb-2">Already Registered? <a href="#" @click.prevent="gologin">Login</a></p>
    </div>
    </div>
    </div>
    </section>`
    
}
