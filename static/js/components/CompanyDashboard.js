CompanyDashboard={
    data(){
        return{
            activeTab:'overview',
            companyId:null,
            companyInfo:{
                name:'',
                website:'',
                location:'',
                field:'',
                approval_status:''
            },
            drives:[],
            applicants:[],
            applications:[],
            selectedDrive:null,
            selectedDriveTitle:'',
            selectedStudent:null,
            showStudentProfile:false,
            stats:{
                numApplications:0,
                numDrives:0
            },
            newDrive:{
                jobtitle:'',
                job_desc:'',
                branches:'',
                cgpa_above:'',
                open_postings:'',
                skills:'',
                deadline:'',
                age_cat:'',
                salary:null
            },
            loading:false,
            error:'',
            success:'',
            searchQuery:'',
            exportLoading:false,
            exportTaskId:null,
            exportSuccess:'',
            exportError:'',
            showInterviewBook:false,
            selectedAppID:null,
            interviewScheduled:false,
            interview:{
                job_title:'',
                interview_date:'',
                interview_time:'',
                location:''
            }
        }
    },
    methods:
    {
        async fetchAllDrives(companyId){
            if(!this.companyId){
                return
            }
            try{
                this.loading=true
                const response=await fetch(`/company/${companyId}/drives`,{
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
        async fetchAllApplicants(){
            try{
                this.loading=true
                const res=await fetch('/company/drives/applicants',{
                    'credentials':"include"
                })
                if(res.ok){
                    const data=await res.json()
                        this.applicants=data.applicants
                        this.selectedDriveTitle=''
                        this.selectedDrive=null
                        this.error='';
                }
                else{
                    const err=await res.json()
                    this.error=err.error
                }
            }
            catch(e){
                this.error="error:"+e
            }
            finally{
                this.loading=false
            }
        },
        async fetchDashboard(){
            try{
                this.loading=true
                const response=await fetch('/company/dashboard',{
                    'credentials':"include"
                })
                if(response.ok){
                    const data=await response.json()
                        this.companyInfo.name=data.company_name
                        this.companyInfo.website=data.website
                        this.companyInfo.field=data.field
                        this.companyInfo.location=data.location
                        this.companyInfo.approval_status=data.approval_status
                        this.drives=data.drives
                        this.stats={
                            numApplications:data.num_applications,
                            numDrives:data.num_placement_drives
                        }
                        this.error=''
                }
                else{
                    this.error='Your company is waiting for admin approval. Please check back later..'
                }
            }
            catch(err){
                this.error='Something Wrong..Try again!'+err.message
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
                const response=await fetch('/company/export',{
                    'method':'POST',
                    headers:{ 'Content-Type': 'application/json' },
                    credentials:'include'
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
        async scheduleInterview(){
            try{
                this.loading=true
                const res=await fetch(`/company/schedule_interview/${this.selectedAppID}`,{
                    'method':'POST',
                    'headers':{'Content-Type':'application/json'},
                    'credentials':'include',
                    'body':JSON.stringify(this.interview)
                })
                if(res.ok){
                    this.success="Interview Scheduled!!"
                    this.showInterviewBook=false
                    this.interviewScheduled=true
                }
                else{
                    const err=await res.json()
                    this.error=err.error
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        async checkExportStatus(){
            if(!this.exportTaskId){
                return
            }
            try{
                const response=await fetch(`/company/exported_csv_status/${this.exportTaskId}`,{
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
        async fetchCompanyId(){
            try{
                const res=await fetch("/auth/check",{
                    credentials:'include'
                })
                if(res.ok){
                    const data=await res.json()
                    this.companyId=data.id
                }
                else{
                    this.error="Not available"
                }
            }
            catch(err){
                this.error="Error:"+err.message
            }
        },
        async updateStatus(applicationId,status){
            try {
                this.loading=true
                const res=await fetch(`/company/application/${applicationId}/status`, {
                    method:'PATCH',
                    headers:{ 'Content-Type':'application/json'},
                    credentials:'include',
                    body:JSON.stringify({ action: status })
                })
                if(res.ok){
                    this.success=`Application ${status} successfully.`
                    await this.fetchApplicants(this.selectedDrive)
                    this.error=''
                }
                else{
                    const err=await res.json()
                    this.error=err.Message||err.error||'Something went wrong'
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        async createDrive(){
            if(!this.companyId){
                return
            }
            try{
                this.loading=true
                const payload={
                    jobtitle:this.newDrive.jobtitle,
                    job_desc:this.newDrive.job_desc,
                    branches:this.newDrive.branches,
                    cgpa_above:this.newDrive.cgpa_above,
                    open_postings:this.newDrive.open_postings,
                    deadline:this.newDrive.deadline,
                    age_cat:this.newDrive.age_cat,
                    skills:this.newDrive.skills,
                    salary:this.newDrive.salary
                }
                const response=await fetch('/company/create_drive', {
                    method:'POST',
                    headers:{ 'Content-Type':'application/json' },
                    credentials:'include',
                    body:JSON.stringify(payload)
                });
                if (response.ok){
                    this.success="Successfully created the drive"
                    this.newDrive={}
                    await this.fetchAllDrives(this.companyId)
                    this.error=''
                }
                else{
                    const errData=await response.json();
                    this.error=errData.Message||errData.error||'Failed to create drive';
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        async fetchApplicants(driveId){
            if(!this.companyId){
                return
            }
            try{
                this.loading=true
                this.selectedDrive=driveId
                const response=await fetch(`/company/drives/${driveId}/applicants`, {
                    credentials:'include'
                });
                if(response.ok){
                    const data=await response.json()
                    this.applicants=data.applicants||[]
                    this.selectedDriveTitle=data.jobtitle || ''
                    this.error=''
                }
                else{
                    this.error="Failed to fetch applicants.."
                    this.applicants=[]
                }      
            }
            catch(err){
                this.error="Error:"+err.message
            }
            finally{
                this.loading=false
            }
        },
        async fetchCompanyInfo(){
            if(!this.companyId){
                return 
            }
            try{
                this.loading=true
                const res=await fetch(`/company/${this.companyId}/info`,{
                    credentials:'include'
                })
                if(res.ok){
                    const data=await res.json()
                    if (data.company){
                        this.companyInfo=data.company;
                    }
                    this.drives=data.drives
                    this.error='';
                }
                else{
                    this.error=`Failed to fetch company info ${this.companyId}`
                }
            }
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        async closeDrive(driveId){
            try{
                this.loading=true
                const res=await fetch(`/company/drive/${driveId}/close`, {
                    method:'PATCH',
                    credentials:'include'
                })
                if(res.ok){
                    this.success="Successfully closed the drive"
                    await this.fetchDashboard()
                    this.error=""
                }
                else{
                    err=await res.json()
                    this.error=err.message||err.error||"Something went wrong"
                }
            }
            catch(e){
                this.error='Something went wrong: '+ e.message
            }
            finally{
                this.loading=false
            }
        },
        async viewApplicantProfile(studentId){
            try{
                this.loading=true
                const res=await fetch(`/company/student/${studentId}/info`, {
                    credentials:'include'
                })
                if(res.ok){
                    const data=await res.json()
                    this.showStudentProfile=true
                    this.selectedStudent=data.student
                    this.error='';
                }
                else{
                    const errData=await res.json()
                    this.error=`Failed to fetch student info ${studentId}`
                }
            } 
            catch(e){
                this.error="Error:"+e.message
            }
            finally{
                this.loading=false
            }
        },
        viewApplicants(driveId){
            this.activeTab='applicants'
            this.fetchApplicants(driveId)
        },
        backToApplicants(){
        this.showStudentProfile=false
        this.selectedStudent=null
        },
        viewResume(){
            window.open('/student/'+this.selectedStudent.user_id+'/resume','_blank')
        },
        clearSearch(){
        this.searchQuery=''
        this.error=''
        this.success=''
        },
        switchTab(tab){
            this.activeTab=tab
            this.error=""
            this.success=""
            this.clearSearch()
            if(tab=='drives'){
                this.fetchAllDrives(this.companyId)
            }
            else if(tab=='applicants'){  
                this.fetchAllApplicants()
            }
            else if(tab=='overview'){
                this.fetchDashboard()
            }
            else if(tab=='create'){}
            else if(tab=='profile'){
                this.fetchCompanyInfo()
            }
        }
    },
    mounted(){
        this.fetchCompanyId()
        this.fetchDashboard()
    },
    template:`
    <div class="company-dashboard container-fluid p-5">
    <h2 class="mb-5">Company Dashboard</h2>

    <div v-if="success" class="alert alert-success">{{success}}
     <button type="button" class="btn-close" @click="success= ''"></button>
     </div>
    <div v-if="error" class="alert alert-danger">{{error}}
     <button type="button" class="btn-close" @click="error = ''"></button>
    </div>
    <div class="row mb-4">
     <div class="col-md-3 mb-3">
        <div class="card bg-info text-white">
            <div class="card-body">
                <h6 class="card-title">Company name</h6>
                <h3>{{companyInfo.name}}</h3>
            </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card bg-dark text-white">
            <div class="card-body">
                <h6 class="card-title">Total Drives</h6>
                <h3>{{stats.numDrives}}</h3>
            </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card bg-secondary text-white">
            <div class="card-body">
                <h6 class="card-title">Total Applications</h6>
                <h3>{{stats.numApplications}}</h3>
            </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <h6 class="card-title">Approval Status</h6>
                <h3>{{companyInfo.approval_status}}</h3>
            </div>
        </div>
      </div>
    </div>
    <ul class="nav nav-tabs mb-4" role="tablist">
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='overview'}" @click="switchTab('overview')" type="button">Overview</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='drives'}" @click="switchTab('drives')" type="button">All Drives</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='applicants'}" @click="switchTab('applicants')" type="button">Applications</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='create'}" @click="switchTab('create')" type="button">Create</button>
    </li>
    </ul>
    <div class="tab-content">
    <div v-if="activeTab=='overview'" class="tab-pane active">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Hello {{companyInfo.name}}! </h5>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <h6>Statistics</h6>
                        <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Applications</span>
                        <span class="badge bg-primary">{{stats.numApplications}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Total Drives</span>
                        <span class="badge bg-primary">{{stats.numDrives}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Approval Status</span>
                        <span class="badge" :class="{'bg-success': companyInfo.approval_status==='approved', 'bg-warning': companyInfo.approval_status!=='approved'}">{{ companyInfo.approval_status }}</span>
                        </li>
                        </ul>
                    </div>
                <div class="col-md-6">
                <h5>Quick Actions</h5>
                <div class="list-group">
                <button class="list-group-item list-group-item-action" @click="switchTab('drives')" type="button">View All drives -></button>
                <button class="list-group-item list-group-item-action" @click="switchTab('profile')" type="button">View Profile -></button>
                 </div>
            </div>
        </div>
    </div>
</div>
</div>
<div v-if="activeTab=='drives'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<h5 class="card-title m-3">Created Drives</h5>
    <div class="table-responsive ms-3 me-3 mb-3">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                <th class="text-center">Drive ID</th>
                <th class="text-center">Job Title</th>
                <th class="text-center">Job Description</th>
                <th class="text-center">Eligible Branches</th>
                <th class="text-center">CGPA Criteria</th>
                <th class="text-center">Skill Required</th>
                <th class="text-center">Deadline</th>
                <th class="text-center">Status</th>
                <th class="text-center">Actions</th>
            </tr>
        </thead>
        <tbody>
        <tr v-for="drive in drives" :key="drive.drive_id">
            <td class="text-center">{{drive.drive_id}}</td>
            <td class="text-center">{{drive.jobtitle}}</td>
            <td class="text-center">{{drive.job_desc}}</td>
            <td class="text-center">{{drive.branches}}</td>
            <td class="text-center">{{drive.cgpa_above}}</td>
            <td class="text-center">{{drive.skills}}</td>
            <td class="text-center">{{drive.deadline}}</td>  
            <td class="text-center">
               <div v-if='drive.status==="pending"' class="badge bg-info">Pending</div>
               <div v-if='drive.status==="approved"' class="badge bg-success">Approved</div>
               <div v-if='drive.status==="rejected"' class="badge bg-danger">Rejected</div>
               <div v-if='drive.status==="closed"'class="badge bg-warning">Closed</div>
            </td>
            <td class="text-center"><button class="btn btn-sm btn-info m-2" @click="viewApplicants(drive.drive_id)">View Applicants</button>
            <button v-if='drive.status!=="closed"' class="btn btn-sm btn-danger m-1" @click="closeDrive(drive.drive_id)">Close</button>
            </td>
            </tr>
            </tbody>
        </table>
    </div>
    <div v-if="drives.length===0" class="p-3 text-center text-muted">No drives created..</div>
</div>
</div>
<div v-if="activeTab=='applicants'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else-if="!showStudentProfile" class="card">
<h5 v-if="selectedDriveTitle" class="card-title m-3">{{selectedDriveTitle ? 'Applicants for: ' + selectedDrive+" "+selectedDriveTitle : 'All Applicants'}}</h5>
<div v-if="exportSuccess" class="alert alert-success">
    {{ exportSuccess }}
    <button type="button" class="btn-close" @click="exportSuccess=''"></button>
</div>
<div v-if="exportError" class="alert alert-danger">
    {{ exportError }}
    <button type="button" class="btn-close" @click="exportError=''"></button>
</div>
<button class="btn btn-primary" @click="ExportApplication" :disabled="exportLoading">
    <span v-if="exportLoading" class="spinner-border spinner-border-sm me-2"></span>
    {{ exportLoading ? 'Exporting...' : 'Export Applications' }}
</button>
    <div class="table-responsive ms-3 me-3 mb-3">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                <th class="text-center">Student ID</th>
                <th class="text-center">Name</th>
                <th class="text-center">CGPA</th>
                <th class="text-center">Department</th>
                <th class="text-center">Status</th>
                <th class="text-center">Actions</th>
            </tr>
        </thead>
        <tbody>
        <tr v-for="applicant in applicants" :key="applicant.student_id">
            <td class="text-center">{{applicant.student_id}}</td>
            <td class="text-center">{{applicant.student_name}}</td>
            <td class="text-center">{{applicant.cgpa}}</td>
            <td class="text-center">{{applicant.dept}}</td>
            <td class="text-center"><span class="badge bg-info">{{ applicant.status }}</span></td>   
            <td class="text-center">
                <button v-if="applicant.status==='applied'" class="btn btn-sm btn-success me-2" @click="updateStatus(applicant.application_id,'shortlisted')">Shortlist</button>
                <button v-if="applicant.status==='applied' || applicant.status==='shortlisted'" class="btn btn-sm btn-primary m-2" @click="updateStatus(applicant.application_id,'selected')">Select</button>
                <button v-if="applicant.status==='applied' || applicant.status==='shortlisted'" class="btn btn-sm btn-danger m-2" @click="updateStatus(applicant.application_id,'rejected')">Reject</button>
                <button v-if="applicant.status!=='rejected'" class="btn btn-sm btn-info m-2" @click="viewApplicantProfile(applicant.student_id)">Student Profile</button>
                <button v-if="applicant.status==='shortlisted'" class="btn btn-sm btn-dark text-white m-2" @click="selectedAppID=applicant.application_id;interview.job_title=applicant.jobtitle||selectedDriveTitle;showInterviewBook=true">Schedule Interview</button>
                <span v-if="applicant.status==='rejected'" class="text-muted">No actions available</span>
            </td>
            </tr>
            </tbody>
        </table>
        <div v-if="showInterviewBook" class="card mt-3 p-3">
        <h6 class="card-title">Schedule Interview for {{interview.job_title}}</h6>
        <div class="mb-2">
        <label><strong>Date of Interview</strong></label>
        <input v-model="interview.interview_date" type="date" class="form-control">
        </div>
        <div class="mb-2">
        <label><strong>Time of Interview</strong></label>
        <input v-model="interview.interview_time" type="time" class="form-control">
        </div>
        <div class="mb-2">
        <label><strong>Location</strong></label>
        <input v-model="interview.location" type="text" class="form-control">
        </div>
        <span class="mt-2"><button class="btn btn-sm btn-success" @click="scheduleInterview" :disabled="interviewScheduled">
        {{interviewScheduled ?'Interview Scheduled':'Schedule'}}</button></span>
        <span class="mt-2"><button class="btn btn-sm btn-danger" @click="showInterviewBook=false">Cancel</button></span>
    </div>
    <div v-if="applicants.length===0" class="p-3 text-center text-muted">No Applicants Found!</div>
</div>
</div>
<div v-else class="card">
<div class="card-body" v-if="selectedStudent">
    <button class="btn btn-sm btn-secondary mb-3" @click="showStudentProfile=false">&larr; Back to Applicants</button>
    <h5 class="card-title">{{ selectedStudent.name }}</h5>
    <p><strong>Department:</strong> {{ selectedStudent.dept }}</p>
    <p><strong>CGPA:</strong> {{ selectedStudent.cgpa }}</p>
    <p><strong>Year:</strong> {{ selectedStudent.year }}</p>
    <p><strong>Date of Birth:</strong> {{ selectedStudent.dob }}</p>
    <p v-if="selectedStudent.resume_path"><strong>Resume:</strong> <button v-if="selectedStudent.resume_path" @click="viewResume" class="btn btn-sm btn-outline-secondary m-2">View</button></p>
    
</div>
</div>
</div>
<div v-if="activeTab=='profile'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<h5 class="card-title">Company Profile</h5>
<div class="row mt-3">
<div class="col-md-6">
    <p><strong>Name:</strong> {{ companyInfo.name }}</p>
    <p><strong>Industry:</strong> {{ companyInfo.field}}</p>
    <p><strong>Location:</strong> {{ companyInfo.location }}</p>
    <p><strong>Website:</strong> <a :href="companyInfo.website" target="_blank">{{ companyInfo.website }}</a></p>
    <p><strong>Approval Status:</strong> {{ companyInfo.approval_status }}</p>
</div>
</div>
</div>
</div>
<div v-if="activeTab=='create'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else class="card">
<h5 class="card-title m-3">Create New Drive</h5>
<div class="row m-3">
    <div class="col-md-6">
        <div class="mb-3">
        <label class="form-label">Job Title</label>
        <input v-model="newDrive.jobtitle" type="text" placeholder="Enter job title.." class="form-control">
        </div>
        <div class="mb-3">
        <label class="form-label">Job Description</label>
        <textarea v-model="newDrive.job_desc" type="text" placeholder="Enter job description.."  class="form-control" required></textarea>
        </div>
        <div class="mb-3">
        <label class="form-label">Eligible Branches</label>
        <input v-model="newDrive.branches" type="text" placeholder="Eg., CSE,AIML,Data Science"  class="form-control"required>
        </div>
        <div class="mb-3">
        <label class="form-label">Skills Required</label>
        <textarea v-model="newDrive.skills" type="text" placeholder="Enter skills required.."  class="form-control" required></textarea>
        </div>
        <div class="mb-3">
        <label class="form-label">CGPA Criteria</label>
        <input v-model="newDrive.cgpa_above" type="number" placeholder="Enter cgpa threshold.." step="0.01" class="form-control" required>
        </div>
        <div class="mb-3">
        <label class="form-label">Open Postings</label>
        <input v-model="newDrive.open_postings" type="number" placeholder="Enter open postings.."  class="form-control" required>
        </div>
        <div class="mb-3">
        <label class="form-label">Expected Salary (per month for interns and LPA for jobs)</label>
        <input v-model="newDrive.salary" type="number" placeholder="Enter salary.." class="form-control" required>
        </div>
        <div class="mb-3">
        <label class="form-label">Deadline</label>
        <input v-model="newDrive.deadline" type="date" class="form-control" required>
        </div>
        <div class="mb-3">
        <label class="form-label">Minimum Age</label>
        <input v-model="newDrive.age_cat" type="number" class="form-control" required>
        </div>
        <button class="btn btn-success" @click="createDrive">Create Drive</button>
        </div>
    </div>
</div>
</div>
</div>
</div>
    `
}