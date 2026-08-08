StudentDashboard={
    data(){
        return{
            activeTab:'overview',
            studentId:null,
            studentInfo:{
                year:'',
                cgpa:'',
                dept:'',
                dob:''
            },
            eligibleDrives:[],
            drives:[],
            companies:[],
            applications:[],
            placementHistory:[],
            stats:{
                numApplications:0,
                numDrives:0,
                numCompanies:0,
                numEligible:0
            },
            loading:false,
            error:'',
            success:'',
            searchQuery:'',
            editingProfile:'',
            resumePath:'',
            resumeFile:'',
            filterBranch:'',
            filterCGPA:'',
            exportLoading:false,
            exportTaskId:null,
            exportSuccess:'',
            exportError:'',
        }
    },
    methods:
    {
        async fetchAllDrives(){
            try{
                this.loading=true
                const response=await fetch('/student/all_drives',{
                    'credentials':"include"
                })
                if(response.ok){
                    const data=await response.json()
                        this.drives=data.drives
                        this.error='';
                }
                else{
                    this.error='Failed to fetch company drives'
                }
            }
            catch(err){
                this.error='Something Wrong..Try again!'+err.message
            }
            finally{
                this.loading=false
            } 
        },
        clearSearch(){
            this.searchQuery=''
            this.error=''
            this.success=''
        },
        async fetchDashboard(){
            try{
                this.loading=true
                const response=await fetch('/student/student_dashboard',{
                    'credentials':"include"
                })
                if(response.ok){
                    const data=await response.json()
                        this.stats={
                            numApplications:data.num_applications,
                            numCompanies:data.num_companies,
                            numDrives:data.num_placement_drives
                        }
                        this.error=''
                }
                else{
                    this.error='Failed to fetch dashboard'
                }
            }
            catch(err){
                this.error='Something Wrong..Try again!'+err.message
            }
            finally{
                this.loading=false
            } 
        },
        async fetchStudentId(){
            try{
                const res=await fetch("/auth/check",{
                    credentials:'include'
                })
                if(res.ok){
                    const data=await res.json()
                    this.studentId=data.id
                }
                else{
                    this.error="Not available"
                }
            }
            catch(err){
                this.error="Error:"+err.message
            }
            finally{
                this.loading=false
            }
        },
        async applyDrive(driveId){
            try{
                this.loading=true
                const response=await fetch(`/student/drive/apply/${driveId}`, {
                    'method':'POST',
                    'headers':{ 'Content-Type': 'application/json' },
                    'credentials':'include'
                });
                if (response.ok){
                    this.success="Successfully applied to the drive"
                    await this.fetchApplications()
                    this.error=''
                }
                else{
                    const errData=await response.json();
                    this.error=errData.Message||errData.error||'Failed to apply';
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        async ExportApplication(){
            try{
                this.loading=true
                this.exportLoading=true
                this.exportError=''
                const response=await fetch('/student/export',{
                    'method':'POST',
                    'headers':{ 'Content-Type': 'application/json' },
                    'credentials':'include'
                })
                if(response.ok){
                    const data=await response.json()
                    this.exportTaskId=data.task_id
                    this.exportSuccess="Export queued! Please check your mail later.."
                    this.checkExportStatus()
                }
                else{
                    this.exportError="Failed to export applications"
                }
            }
            catch(e){
                this.exportError="Error"+e.message
            }
            finally{
                this.exportLoading=false
                this.loading=false
            }
        },
        async checkExportStatus(){
            if(!this.exportTaskId){
                return
            }
            try{
                const response=await fetch(`/student/export_csv_status/${this.exportTaskId}`,{
                credentials:'include'
                })
                const data=await response.json() 
                if(data.status==='SUCCESS'){
                    this.exportSuccess='Export ready! Check your email for CSV attachment.'
                    return
                }
                if(data.status==='PENDING'){
                    setTimeout(()=>this.checkExportStatus(),3000)
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
        },
        searchCompanies(){
        if(!this.searchQuery){
            this.fetchAllCompanies()
        }
        else{
            this.companies = this.companies.filter(c => 
                c.name.toLowerCase().includes(this.searchQuery.toLowerCase())
            )
        }
},
        async fetchApplications(){
            if(!this.studentId){
                return
            }
            try{
                this.loading=true
                const response=await fetch(`/student/student/${this.studentId}/applications`, {
                    credentials:'include'
                });
                if(response.ok){
                    const data=await response.json()
                    this.applications=data.applications||[]
                    this.error=''
                }
                else{
                    this.error="Failed to fetch applications.."
                    this.applications=[]
                }      
            }
            catch(err){
                this.error="Error:"+err.message
            }
            finally{
                this.loading=false
            }
        },
        async fetchStudentInfo(){
            if(!this.studentId){
                return 
            }
            try{
                this.loading=true
                const res=await fetch(`/student/${this.studentId}/info`,{
                    credentials:'include'
                })
                if(res.ok){
                    const data=await res.json()
                    if (data.student){
                        this.studentInfo=data.student;
                    }
                    this.error='';
                }
                else{
                    this.error=`Failed to fetch student info ${this.studentId}`
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        async fetchplacementHistory(){
            if(!this.studentId){
                return
            }
            try{
                this.loading=true
                const res=await fetch(`/student/student/${this.studentId}/placement`,{
                    credentials:'include'
                })
                if(res.ok){
                    const data=await res.json()
                    if (data.placement_history){
                        this.placementHistory=data.placement_history;
                    }
                    this.error='';
                }
                else{
                    this.error=`Failed to fetch student placement History`
                    this.placementHistory=[]
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        async fetchEligibleDrives(){
            if(!this.studentId){
                return
            }
            try{
                this.loading=true
                const res=await fetch('/student/drives/eligible',{
                    credentials:'include'
                })
                if(res.ok){
                    const data=await res.json()
                    this.eligibleDrives=data.eligible_drives
                    this.stats.numEligible=data.eligible_drives.length 
                    this.error=''
                }
                else{
                    this.error="Cannot fetch eligible drives"
                    this.eligibleDrives=[]
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        handleResumeupload(event){
            const file=event.target.files[0]
            if(file){
                this.resumeFile=file
                this.resumePath=file.name
            }
        },
        cancelEdit(){
            this.editingProfile=false
            this.fetchStudentInfo()
        },
        switchTab(tab){
            this.activeTab=tab
            this.error=""
            this.success=""
            this.clearSearch()
            if(tab=='drives'){
                this.fetchAllDrives()
            }
            else if(tab=='companies'){
                this.fetchAllCompanies()
            }
            else if(tab=='overview'){}
            else if(tab=='applications'){
                this.fetchApplications()
            }
            else if(tab=='history'){
                this.fetchplacementHistory()
            }
            else if (tab=='eligible'){
                this.fetchEligibleDrives()
            }
            else if(tab=='profile'){
                this.fetchStudentInfo()
            }
        },
        async fetchAllCompanies(){
            try{
                this.loading=true
                const response=await fetch('/student/view_companies',{
                    'credentials':"include"
                })
                if(response.ok){
                    const data=await response.json()
                        this.companies=data.companies
                        this.error='';
                }
                else{
                    this.error='Failed to fetch companies'
                }
            }
            catch(err){
                this.error='Something Wrong..Try again!'+err.message
            }
            finally{
                this.loading=false
            } 
        },
        async updateProfile(){
            if(! this.studentId){
                return
            }
            try{
                this.loading=true
                const form=new FormData()
                form.append('name',this.studentInfo.name)
                form.append('dept',this.studentInfo.dept)
                form.append('cgpa',this.studentInfo.cgpa)
                form.append('year',this.studentInfo.year)
            if (this.resumeFile){
                    form.append('resume',this.resumeFile)
                }
            const res=await fetch(`/student/student/${this.studentId}/edit-profile`,{
                method:'PATCH',
                credentials:'include',
                body:form
            })
            if(res.ok){
                this.success="Profile updated succesfully"
                this.editingProfile=false
                await this.fetchStudentInfo()
                this.error=''
             }
            else{
                this.error="Failed to edit profile"
                }
            }
            catch(err){
                this.error="Error:"+err.message
            }   
            finally{
                this.loading=false
            }     
        },
        checkifApplied(driveId){
            return this.applications.some(app=>app.drive_id===driveId)
        },
        viewResume(){
            window.open('/student/'+this.studentId+'/resume','_blank')
        },
        getApplicationStatus(driveId){
            const app=this.applications.find(a=>a.drive_id===driveId)
            if(app){
                return app.status
            }
            return null
        },
        async withdrawApplication(application_id){
            try{
                this.loading=true
                const res=await fetch(`/student/applications/${application_id}/withdraw`,{
                    'method':'PATCH',
                    'headers':{'Content-Type':'application/json'},
                    'credentials':"include"
                })
                if(res.ok){
                    this.success='Successfully withdrawn application'
                    this.fetchApplications()
                    this.error=''
                }
                else{
                    this.error='failed to withdraw application'
                } 
            }
            catch(e){
                this.error="Error : "+e.message
            }
            finally{
                this.loading=false
            }
        },
        isEligible(drive){
        if(this.studentInfo.cgpa < drive.cgpa_above){
            return false
        }
        if(!drive.branches.split(',').includes(this.studentInfo.dept)){
            return false
        }
        if(this.studentInfo.dob){
            const dob=new Date(this.studentInfo.dob)
            const today=new Date()
            let age=today.getFullYear()-dob.getFullYear()
            if(today.getMonth()<dob.getMonth()||(today.getMonth()==dob.getMonth()&& today.getDate()<=dob.getDate())){
                age-=1
            }
            if(drive.age_cat<age){
                return false
            }
        }
        if(new Date()>new Date(drive.deadline)){
        return false
        }
        return true
        }
    },
    async mounted(){
       await this.fetchStudentId()
       await this.fetchStudentInfo() 
       await this.fetchDashboard()
       await this.fetchEligibleDrives()
       await this.fetchplacementHistory()
    },
    template:`
    <div class="student-dashboard container-fluid p-5">
    <h2 class="mb-5">Student Dashboard</h2>

    <div v-if="success" class="alert alert-success">{{success}}
     <button type="button" class="btn-close" @click="success = ''"></button>
     </div>
    <div v-if="error" class="alert alert-danger">{{error}}
     <button type="button" class="btn-close" @click="error = ''"></button>
    </div>
    <div class="row mb-4">
        <div class="col-md-3 mb-3">
    <div class="card bg-primary text-white" style="height:125px">
        <div class="card-body">
            <h6 class="card-title text-center">My Applications</h6>
            <h3 class="text-center" style="font-size:40px">{{stats.numApplications}}</h3>
        </div>
    </div>
</div>
<div class="col-md-3 mb-3">
    <div class="card bg-success text-white" style="height:125px">
        <div class="card-body">
            <h6 class="card-title text-center">CGPA</h6>
            <h3 class="text-center" style="font-size:40px">{{studentInfo.cgpa}}</h3>
        </div>
    </div>
</div>
<div class="col-md-3 mb-3">
    <div class="card bg-info text-white" style="height:125px">
        <div class="card-body">
            <h6 class="card-title text-center">Department</h6>
            <div class="p-2">
            <h3 class="text-center" style="font-size:25px">{{studentInfo.dept}}</h3>
            </div>
        </div>
    </div>
</div>
<div class="col-md-3 mb-3">
    <div class="card bg-warning text-white" style="height:125px">
        <div class="card-body">
            <h6 class="card-title text-center">Placements</h6>
            <h3 class="text-center" style="font-size:40px">{{placementHistory.length}}</h3>
        </div>
    </div>
</div>
    <ul class="nav nav-tabs mb-4" role="tablist">
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='overview'}" @click="switchTab('overview')" type="button">Overview</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class='nav-link' :class="{active:activeTab=='eligible'}" @click="switchTab('eligible')" type="button">Eligible Drives</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class='nav-link' :class="{active:activeTab=='companies'}" @click="switchTab('companies')" type="button">Companies</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='applications'}" @click="switchTab('applications')" type="button">Applications</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class='nav-link' :class="{active:activeTab=='drives'}" @click="switchTab('drives')" type="button">All Drives</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='history'}" @click="switchTab('history')" type="button">Placement History</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='profile'}" @click="switchTab('profile')" type="button">My profile</button>
    </li>
    </ul>
    <div class="tab-content">
    <div v-if="activeTab=='overview'" class="tab-pane active">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Hello {{studentInfo.name}}! </h5>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <h6>Statistics</h6>
                        <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Eligible Drives</span>
                        <span class="badge bg-primary">{{stats.numEligible}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Total Companies</span>
                        <span class="badge bg-primary">{{stats.numCompanies}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Total Placement Drives</span>
                        <span class="badge bg-primary">{{stats.numDrives}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Total Applications</span>
                        <span class="badge bg-primary">{{stats.numApplications}}</span>
                        </li>
                        </ul>
                    </div>
                <div class="col-md-6">
                <h5>Quick Actions</h5>
                <div class="list-group">
                <button class="list-group-item list-group-item-action" @click="switchTab('eligible')" type="button">View Eligible Drives -></button>
                <button class="list-group-item list-group-item-action" @click="switchTab('companies')" type="button">View Companies -></button>
                <button class="list-group-item list-group-item-action" @click="switchTab('drives')" type="button">View All drives -></button>
                <button class="list-group-item list-group-item-action" @click="switchTab('profile')" type="button">Update/View Profile -></button>
                <button class="list-group-item list-group-item-action" @click="switchTab('applications')" type="button">Track Applications -></button>
                 </div>
            </div>
        </div>
    </div>
</div>
</div>
<div v-if="activeTab=='eligible'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<h5 class="card-title m-3">Drives You Qualify For</h5>
    <div class="table-responsive ms-3 me-3 mb-3">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                <th class="text-center">Drive ID</th>
                <th class="text-center">Company</th>
                <th class="text-center">Job Title</th>
                <th class="text-center">Eligible Branches</th>
                <th class="text-center">CGPA Criteria</th>
                <th class="text-center">Deadline</th>
                <th class="text-center">Status</th>
                <th class="text-center">Actions</th>
            </tr>
        </thead>
        <tbody>
        <tr v-for="drive in eligibleDrives" :key="drive.drive_id">
            <td class="text-center">{{ drive.drive_id }}</td>
            <td class="text-center">{{ drive.company_id }}</td>
            <td class="text-center">{{ drive.jobtitle }}</td>
            <td class="text-center">{{drive.branches}}</td>
            <td class="text-center">{{ drive.cgpa_above }}</td>
            <td class="text-center">{{ drive.deadline }}</td>    
            <td class="text-center">{{drive.status}}</td>
            <td class="text-center">
                <span v-if="getApplicationStatus(drive.drive_id)==='applied'" class="badge bg-info">Applied</span>
                <span v-else-if="getApplicationStatus(drive.drive_id)==='shortlisted'" class="badge bg-warning">Shortlisted</span>
                <span v-else-if="getApplicationStatus(drive.drive_id)==='selected'" class="badge bg-success">Selected</span>
                <span v-else-if="getApplicationStatus(drive.drive_id)==='rejected'" class="badge bg-danger">Rejected</span>
                <span v-else-if="getApplicationStatus(drive.drive_id)==='withdrawn'" class="badge bg-secondary">Withdrawn</span>
                <span v-else class="text-muted">Not Applied</span>
            </td>
            </tr>
            </tbody>
        </table>
    </div>
    <div v-if="eligibleDrives.length===0" class="p-3 text-center text-muted">Sorry! You are not eligible for any of the drives..</div>
</div>
</div>
<div v-if="activeTab=='drives'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<h5 class="card-title m-3">All Drives</h5>
    <div class="table-responsive ms-3 me-3 mb-3">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                <th class="text-center">Drive ID</th>
                <th class="text-center">Company ID</th>
                <th class="text-center">Job Title</th>
                <th class="text-center">Job Description</th>
                <th class="text-center">Eligible Branches</th>
                <th class="text-center">CGPA Criteria</th>
                <th class="text-center">Skills Required</th>
                <th class="text-center">Deadline</th>
                <th class="text-center">Status</th>
                <th class="text-center">Actions</th>
            </tr>
        </thead>
        <tbody>
        <tr v-for="drive in drives" :key="drive.drive_id">
            <td class="text-center">{{ drive.drive_id }}</td>
            <td class="text-center">{{ drive.company_id }}</td>
            <td class="text-center">{{ drive.jobtitle }}</td>
            <td class="text-center">{{ drive.job_desc }}</td>
            <td class="text-center">{{ drive.branches}}</td>
            <td class="text-center">{{ drive.cgpa_above }}</td>
            <td class="text-center">{{ drive.skills }}</td>
            <td class="text-center">{{ drive.deadline }}</td>    
            <td class="text-center">
            <button v-if="!checkifApplied(drive.drive_id) && drive.status!=='closed' && isEligible(drive)" class="btn btn-sm btn-primary" @click="applyDrive(drive.drive_id)">Apply</button>
            <span v-else-if="checkifApplied(drive.drive_id)" class="badge bg-success">Applied</span>
            <span v-else-if="drive.status==='closed'" class="text-muted fw-bold">Closed</span>
            <span v-else class="text-muted">Not Eligible</span>
            </td>
            <td>
                <button v-if="getApplicationStatus(drive.drive_id)==='applied'" @click="withdrawApplication(applications.find(a=>a.drive_id==drive.drive_id).application_id)" class="btn btn-sm btn-secondary">Withdraw</button>
                <span v-else class="text-muted"> No Actions</span>
            </td>
            </tr>
            </tbody>
        </table>
    </div>
    <div v-if="drives.length===0" class="p-3 text-center text-muted">No Drives Found!</div>
</div>
</div>
<div v-if="activeTab=='applications'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<h5 class="card-title m-3">My Applications</h5>
<div v-if="exportSuccess" class="alert alert-success">
    {{exportSuccess}}
    <button type="button" class="btn-close" @click="exportSuccess = ''"></button>
</div>
<div v-if="exportError" class="alert alert-danger">
    {{ exportError }}
    <button type="button" class="btn-close" @click="exportError = ''"></button>
</div>
<button class="btn btn-primary" @click="ExportApplication" :disabled="exportLoading">
    <span v-if="exportLoading" class="spinner-border spinner-border-sm me-2"></span>
    {{exportLoading?'Exporting...' :'Export Applications'}}
</button>
<div class="table-responsive ms-3 me-3 mb-3">
    <table class="table table-hover mb-1">
        <thead class="table-light">
            <tr>
                <th class="text-center">Application ID</th>
                <th class="text-center">Job Title</th>
                <th class="text-center">Job Description</th>
                <th class="text-center">Company Name</th>
                <th class="text-center">Status</th>
            </tr>
        </thead>
        <tbody>
        <tr v-for="app in applications" :key="app.application_id">
            <td class="text-center">{{app.application_id}}</td>
            <td class="text-center">{{app.jobtitle}}</td>
            <td class="text-center">{{app.job_desc}}</td>
            <td class="text-center">{{ app.company_name }}</td>
            <td class="text-center">
                <span v-if="app.status==='applied'" class="badge bg-info">Applied</span>
                <span v-else-if="app.status==='shortlisted'" class="badge bg-warning">Shortlisted</span>
                <span v-else-if="app.status==='selected'" class="badge bg-success">Selected</span>
                <span v-else-if="app.status==='withdrawn'" class="badge bg-secondary">Withdrawn</span>
                <span v-else class="badge bg-danger">Rejected</span>
            </td>
        </tr>
        </tbody>
    </table>
</div>
<div v-if="applications.length===0" class="p-3 text-center text-muted">No Applications Found!</div>
</div>
</div>
<div v-if="activeTab=='companies'" class="tab-pane active">
<div class="card mb-4">
    <div class="card-body">
    <h5 class="card-title">Search Companies</h5>
    <div class="input-group">
    <input v-model="searchQuery" type="text" placeholder="Search for a company..." class="form-control" @keyup.enter="searchCompanies">
    <button class="btn btn-primary" @click="searchCompanies">Search</button>
    <button class="btn btn-secondary" @click="fetchAllCompanies">View All Companies</button>
    <button class="btn btn-outline-secondary" @click="clearSearch">Clear</button>
    </div>
    </div>
</div>
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<div class="table-responsive">
    <table class="table table-hover mb-1">
        <thead class="table-light">
            <tr>
                <th class="text-center">Company ID</th>
                <th class="text-center">Company Name</th>
                <th class="text-center">Industry Field</th>
                <th class="text-center">Location</th>
                <th class="text-center">Website</th>
                <th class="text-center">Status</th>
            </tr>
        </thead>
        <tbody>
        <tr v-for="company in companies" :key="company.company_id">
            <td class="text-center">{{ company.company_id }}</td>
            <td class="text-center">{{ company.name }}</td>
            <td class="text-center">{{ company.field }}</td>
            <td class="text-center">{{ company.location }}</td>
            <td class="text-center"><a :href="company.website" target="_blank">{{company.website}}</a></td>
            <td class="text-center">
                <span v-if="company.approval_status==='approved'" class="badge bg-success">Approved</span>
                <span v-else-if="company.approval_status==='rejected'" class="badge bg-danger">Rejected</span>
                <span v-else class="badge bg-warning">Pending</span>
            </td>
        </tr>
        </tbody>
    </table>
</div>
<div v-if="companies.length===0" class="p-3 text-center text-muted">No Companies Found!</div>
</div>
</div>
<div v-if="activeTab=='history'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<h5 class="card-title m-3">Placement History</h5>
<div class="table-responsive m-3">
    <table class="table table-hover mb-1">
        <thead class="table-light">
            <tr>
                <th class="text-center">Application ID</th>
                <th class="text-center">Company Name</th>
                <th class="text-center">Job Title</th>
                <th class="text-center">Expected Salary</th>
                <th class="text-center">Status</th>
                <th class="text-center">Date</th>
            </tr>
        </thead>
        <tbody>
        <tr v-for="p in placementHistory" :key="p.application_id">
            <td class="text-center">{{ p.application_id }}</td>
            <td class="text-center">{{ p.company}}</td>
            <td class="text-center">{{ p.jobtitle}}</td>
            <td class="text-center">
            <div v-if="p.jobtitle.toLowerCase().includes('intern')">{{ p.salary}} Per Month</div>
            <div v-else>{{ p.salary}} Per Annum</div>
            </td>
            <td class="text-center"><span class="badge bg-success">{{p.status}}</span></td>
            <td class="text-center">{{ p.application_date }}</td>
        </tr>
        </tbody>
    </table>
</div>
<div v-if="placementHistory.length===0" class="p-3 text-center text-muted">You are not yet placed..Please Keep Trying!</div>
</div>
</div>
<div v-if="activeTab=='profile'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<h5 class="card-title ms-3 mt-3">My Profile</h5>
<div v-if="!editingProfile" class="row mt-3">
<div class="col-md-6 m-3">
    <p><strong>Name:</strong> {{ studentInfo.name }}</p>
    <p><strong>Date of Birth:</strong> {{ studentInfo.dob }}</p>
    <p><strong>Department:</strong> {{ studentInfo.dept }}</p>
    <p><strong>Year:</strong> {{ studentInfo.year }}</p>
    <p><strong>CGPA:</strong> {{ studentInfo.cgpa }}</p>
    <p><strong>Resume:</strong> {{ studentInfo.resume_path || 'Not uploaded' }}
    <button v-if="studentInfo.resume_path" @click="viewResume" class="btn btn-sm btn-outline-secondary m-2">View</button></p>
    
</div>
<div class="col-md-6">
    <button class="btn btn-primary ms-4 mb-4" @click="editingProfile=true">Edit Profile</button>
</div>
</div>  
<div v-else class="row m-3">
<div class="col-md-6">
    <div class="mb-3">
        <label class="form-label">Name</label>
        <input v-model="studentInfo.name" type="text" class="form-control">
    </div>
<div class="mb-3">
<label class="form-label">Department</label>
<input v-model="studentInfo.dept" type="text" class="form-control">
</div>
<div class="mb-3">
<label class="form-label">CGPA</label>
<input v-model="studentInfo.cgpa" type="number" step="0.01" class="form-control">
</div>
<div class="mb-3">
<label class="form-label">Resume</label>
<input type="file" @change="handleResumeupload($event)" accept=".pdf,.doc,.docx" class="form-control">
</div>
<button class="btn btn-success me-2" @click="updateProfile">Update Details</button>
<button class="btn btn-secondary me-2" @click="cancelEdit">Cancel Edit</button>
</div>
</div>
</div>
</div>
</div>
</div>
</div>
    `
}