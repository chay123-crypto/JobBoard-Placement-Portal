const AdminDashboard={
    data(){
        return {
            activeTab:'overview',
            stats:{
                numStudents:0,
                numCompanies:0,
                numPlacementDrives:0,
                numPlacedStudents:0,
                numApplications:0,
                minSalary:0,
                maxSalary:0,
                avgSalary:0,
                medianSalary:0,
                AvgStipend:0,
                MedianStipend:0
            },
            students:[],
            companies:[],
            drives:[],
            applications:[],
            applicants:[],
            placementHistory:[],
            searchQuery:'',
            searchType:'student',
            loading:false,
            error:'',
            success:'',
            selectedCompany:'',
            selectedDrive:'',
            selectedDriveTitle:'',
            showStudentDetails:false,
            showCompanyDetails:false,
            showDriveDetails:true
        }
    },
    methods:{
        async fetchAllStudents(){
            try{
                this.loading=true
                const response=await fetch('/admin/view_students',{
                    'credentials':"include"
                })
                if(response.ok){
                    const data=await response.json()
                        this.students=data.students
                        this.error=''
                }
                else{
                    this.error='Failed to fetch students'
                }
            }
            catch(err){
                this.error='Something Wrong..Try again!'+err.message
            }
            finally{
                this.loading=false
            }   
        },
        async fetchAllCompanies(){
            try{
                this.loading=true
                const response=await fetch('/admin/view_companies',{
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
        async fetchDashboard(){
            try{
                this.loading=true
                const response=await fetch('/admin/admin_dashboard',{
                    'credentials':"include"
                })
                if(response.ok){
                    const data=await response.json()
                        this.stats={
                            numStudents:data.num_students,
                            numCompanies:data.num_companies,
                            numPlacementDrives:data.num_placement_drives,
                            numPlacedStudents:data.num_placed,
                            numApplications:data.num_applications,
                            maxSalary:data.maxSalary,
                            minSalary:data.minSalary,
                            medianSalary:data.medianSalary,
                            avgSalary:data.avgSalary,
                            MedianStipend:data.MedianStipend,
                            AvgStipend:data.AvgStipend,

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
        backToDrives(){
            this.showDriveDetails=true
            this.selectedDrive=''
            this.selectedCompany=''
            this.selectedDriveTitle=''
            this.applicants=[]
        },
        async fetchplacementHistory(){
            try{
                this.loading=true
                const res=await fetch('/admin/placement',{
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
        async fetchAllDrives(){
            try{
                this.loading=true
                const response=await fetch('/admin/all_drives',{
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
        async searchStudents(){
            if(!this.searchQuery){
                this.error="Please enter a query to search"
            }
            try{
                this.loading=true;
                const response=await fetch(`/admin/search_student?query=${encodeURIComponent(this.searchQuery)}`, {
                    credentials:'include'
                });
                if(response.ok){
                    const data=await response.json()
                    this.students=data.students
                    this.success=`Found ${data.students.length} results`
                    this.error=''
                }
                else{
                    const errData=await response.json();
                    this.error=errData.error||'No students found';
                    this.students=[];
                }
            }
            catch(err){
                this.error="Error:"+err.message
            }
            finally{
                this.loading=false
            }
        },
        async searchCompanies(){
            if(!this.searchQuery||!this.searchQuery.trim()){
                this.error="Please enter a query to search";
                return;
            }
            try{
                this.loading=true;
                const response=await fetch(`/admin/search_company?query=${encodeURIComponent(this.searchQuery)}`,{
                    credentials:'include'
                });
                if (response.ok){
                    const data=await response.json();
                    this.companies=data.companies;
                    this.success=`Found ${data.companies.length} results`;
                    this.error='';
                }
                else{
                    const errData=await response.json();
                    this.error=errData.error||'No Companies found';
                    this.companies=[];
                }
            }
            catch(err){
                this.error="Error:"+err.message;
            }
            finally{
                this.loading=false;
            }
        },
        async approveCompany(companyId){
            try{
                this.loading=true
                const resp=await fetch(`/admin/company/${companyId}/status`, {
                    method:'PATCH',
                    headers:{ 'Content-Type':'application/json' },
                    credentials:'include',
                    body:JSON.stringify({action:'approve'})
                });
                if (resp.ok){
                    this.success="Company approved successfully"
                    if (this.searchQuery) await this.searchCompanies()
                    else await this.fetchAllCompanies()
                    this.error=""
                }
                else{
                    this.error='Failed to approve company'
                }
            }
            catch(err){
                this.error="Error"+err.message
            }
            finally{
                this.loading=false
            }
        },
        async approveDrive(driveId){
            try{
                this.loading=true
                const resp=await fetch(`/admin/drive/${driveId}/status`, {
                    method:'PATCH',
                    headers:{ 'Content-Type':'application/json' },
                    credentials:'include',
                    body:JSON.stringify({ action: 'approve' })
                });
                if (resp.ok){
                    this.success="Drive approved successfully"
                    await this.fetchAllDrives()
                    this.error=""
                }
                else{
                    this.error='Failed to approve drive'
                }
            }
            catch(err){
                this.error="Error"+err.message
            }
            finally{
                this.loading=false
            }
        },
        async rejectDrive(driveId){
            try{
                this.loading=true
                const resp=await fetch(`/admin/drive/${driveId}/status`, {
                    method:'PATCH',
                    headers:{ 'Content-Type':'application/json' },
                    credentials:'include',
                    body:JSON.stringify({ action:'reject' })
                });
                if (resp.ok){
                    this.success="Drive rejected successfully"
                    await this.fetchAllDrives()
                    this.error=""
                }
                else{
                    this.error='Failed to reject drive'
                }
            }
            catch(err){
                this.error="Error"+err.message
            }
            finally{
                this.loading=false
            }
        },
        viewResume(studentId){
            window.open('/student/'+studentId+'/resume','_blank')
        },
        async rejectCompany(companyId){
            try{
                this.loading=true
                const resp=await fetch(`/admin/company/${companyId}/status`, {
                    method:'PATCH',
                    headers:{ 'Content-Type':'application/json' },
                    credentials:'include',
                    body:JSON.stringify({ action:'reject' })
                });
                if (resp.ok){
                    this.success="Company rejected successfully"
                    if (this.searchQuery) await this.searchCompanies()
                    else await this.fetchAllCompanies()
                    this.error=""
                }
                else{
                    this.error='Failed to reject drive'
                }
            }
            catch(err){
                this.error="Error"+err.message
            }
            finally{
                this.loading=false
            }
        },
        async fetchApplicants(companyId,driveId,jobtitle){
            try{
                this.loading=true
                this.selectedDrive=driveId
                this.selectedCompany=companyId
                this.showDriveDetails=false
                const response=await fetch(`/admin/drives/${driveId}/applicants`, {
                    credentials:'include'
                });
                if(response.ok){
                    const data=await response.json()
                    this.applicants=data.applicants||[]
                    this.selectedDriveTitle=data.jobtitle||jobtitle||''
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
        async deactivateUser(userId,type){
            if(!confirm("Are you sure you want to deactivate the user")){
                return
            }
            try{
                this.loading=true;
                const response=await fetch(`/admin/user/${userId}/deactivate`, {
                    method:'PATCH',
                    headers:{ 'Content-Type': 'application/json' },
                    credentials:'include'
                });
                if (response.ok){
                    const data=await response.json()
                    this.success=`Successfully deactivated user ${userId}`
                    if(type=='company'){
                        await this.fetchAllCompanies()
                    }
                    else{
                        await this.fetchAllStudents()
                    }
                    this.error=''
                }
                else{
                    this.error="failed to deactivate user"
                }
            }
            catch(error){
                this.error="Error"+error.message
            }
            finally{
                this.loading=false
            }
        },
        switchTab(tab){
            this.activeTab=tab
            this.error=""
            this.success=""
            this.clearSearch()
            if (tab=='overview'){
                this.fetchDashboard()
            }
            else if(tab=='students'){
                this.fetchAllStudents()
            }
            else if(tab=='companies'){
                this.fetchAllCompanies()
            }
            else if(tab=='drives'){
                this.fetchAllDrives()
            }
            else if(tab=='placementHistory'){
                this.fetchplacementHistory()
            }
        }
    },
    mounted(){
        this.fetchDashboard()
        this.fetchAllDrives();
    },
    template:`
    <div class="admin-dashboard container-fluid p-5">
    <h2 class="mb-5">Admin Dashboard</h2>
    <div v-if="success" class="alert alert-success">{{success}}
     <button type="button" class="btn-close" @click="success = ''"></button>
     </div>
    <div v-if="error" class="alert alert-danger">{{error}}
     <button type="button" class="btn-close" @click="error = ''"></button>
    </div>
    <div class="row mb-4 justify-content-center">
    <div class="col-md-3">
        <div class="card bg-danger mb-5 text-white">
            <div class="card-body">
                <h5 class="card-title text-center">Total Students</h5>
                <p class="card-text fs-4 text-center">{{stats.numStudents}}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-warning mb-5 text-white">
            <div class="card-body">
                <h5 class="card-title text-center">Total Companies</h5>
                <p class="card-text fs-4 text-center">{{stats.numCompanies}}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-info mb-5 text-white">
            <div class="card-body">
                <h5 class="card-title text-center">Total Placements Drives</h5>
                <p class="card-text fs-4 text-center">{{stats.numPlacementDrives}}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-success mb-5 text-white">
            <div class="card-body">
                <h5 class="card-title text-center">Total Placed Students</h5>
                <p class="card-text fs-4 text-center">{{stats.numPlacedStudents}}</p>
            </div>
        </div>
    </div>
    </div>
    <ul class="nav nav-tabs mb-4" role="tablist">
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='overview'}" @click="switchTab('overview')" type="button">Overview</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='students'}" @click="switchTab('students')" type="button">Students</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='companies'}" @click="switchTab('companies')" type="button">Companies</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='drives'}" @click="switchTab('drives')" type="button">Drives</button>
    </li>
    <li class="nav-item" role="presentation">
    <button class="nav-link" :class="{active:activeTab=='placementHistory'}" @click="switchTab('placementHistory')" type="button">Placements</button>
    </li>
    </ul>
    <div class="tab-content">
    <div v-if="activeTab=='overview'" class="tab-pane active">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Dashboard Overview</h5>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <h6>Statistics</h6>
                        <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Total Students</span>
                        <span class="badge bg-primary m-2">{{stats.numStudents}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Total Companies</span>
                        <span class="badge bg-primary m-2">{{stats.numCompanies}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Total Placement Drives</span>
                        <span class="badge bg-primary m-2">{{stats.numPlacementDrives}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Total Applications</span>
                        <span class="badge bg-primary m-2">{{stats.numApplications}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Median Salary</span>
                        <span class="badge bg-primary m-2">{{stats.medianSalary}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Average Salary</span>
                        <span class="badge bg-primary m-2">{{stats.avgSalary}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Highest Salary</span>
                        <span class="badge bg-primary m-2">{{stats.maxSalary}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Lowest Salary</span>
                        <span class="badge bg-primary m-2">{{stats.minSalary}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Average Stipend for interns</span>
                        <span class="badge bg-primary m-2">{{stats.AvgStipend}}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between m-2">
                        <span>Median Stipend for interns</span>
                        <span class="badge bg-primary m-2">{{stats.MedianStipend}}</span>
                        </li>
                        </ul>
                    </div>
                <div class="col-md-6">
                <h5>Quick Actions</h5>
                <div class="list-group">
                <button class="list-group-item list-group-item-action" @click="switchTab('students')" type="button">Review Students -></button>
                <button class="list-group-item list-group-item-action" @click="switchTab('companies')" type="button">Manage Companies -></button>
                <button class="list-group-item list-group-item-action" @click="switchTab('drives')" type="button">Approve Drives -></button>
                 </div>
            </div>
        </div>
    </div>
</div>
</div>
<div v-if="activeTab=='students'" class="tab-pane active">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Search Students</h5>
            <div class="input-group">
            <input v-model="searchQuery" type="text" class="form-control" placeholder="search by name..." @keyup.enter="searchStudents">
            <button class="btn btn-primary" @click="searchStudents">Search</button>
            <button class="btn btn-secondary" @click="fetchAllStudents">View All</button>
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
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                    <th class="text-center">Student ID</th>
                    <th class="text-center">Name</th>
                    <th class="text-center">Department</th>
                    <th class="text-center">Year</th>
                    <th class="text-center">CGPA</th>
                    <th class="text-center">Actions</th>
                </tr>
            </thead>
            <tbody>
            <tr v-for="student in students" :key="student.student_id">
            <td class="text-center">{{ student.student_id }}</td>
            <td class="text-center">{{ student.name }}</td>
            <td class="text-center">{{ student.dept }}</td>
            <td class="text-center">{{ student.year }}</td>
            <td class="text-center">{{ student.cgpa }}</td>
            <td class="text-center">
            <button class="btn btn-sm btn-danger text-center" v-if="student.is_active" @click="deactivateUser(student.student_id,'student')">Deactivate</button>
            <button class="btn btn-sm btn-success text-center" v-if="!student.is_active" @click="deactivateUser(student.student_id,'student')">Activate</button>
            </td>
            </tr>
            </tbody>
        </table>
    </div>
    <div v-if="students.length===0" class="p-3 text-center text-muted">No students found</div>
</div>
</div>
<div v-if="activeTab=='placementHistory'" class="tab-pane active">
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
            <td class="text-center">{{ p.salary}} LPA</td>
            <td class="text-center"><span class="badge bg-success">{{p.status}}</span></td>
            <td class="text-center">{{ p.application_date }}</td>
        </tr>
        </tbody>
    </table>
</div>
<div v-if="placementHistory.length===0" class="p-3 text-center text-muted">No placement drives started!</div>
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
                <th class="text-center">Industry</th>
                <th class="text-center">Location</th>
                <th class="text-center">Website</th>
                <th class="text-center">Status</th>
                <th class="text-center">Actions</th>
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
            <td class="text-center">
                <button v-if="company.approval_status==='pending'" class="btn btn-sm btn-success m-2" @click="approveCompany(company.company_id)">Approve</button>
                <button v-if="company.approval_status==='pending'"  class="btn btn-sm btn-danger m-2" @click="rejectCompany(company.company_id)">Reject</button>
                <button class="btn btn-sm btn-danger" v-if="company.is_active" @click="deactivateUser(company.user_id,'company')">Deactivate</button>
                <button class="btn btn-sm btn-success" v-if="!company.is_active" @click="deactivateUser(company.user_id,'company')">Activate</button>
            </td>
        </tr>
        </tbody>
    </table>
</div>
</div>
</div>
<div v-if="activeTab=='drives'" class="tab-pane active">
<div v-if="loading" class="text-center">
<div class="spinner-border" role="status">
<span class="visually-hidden">Loading....</span>
</div>
</div>
<div v-else-if="!showDriveDetails" class="card">
<div class="card-body">
<button class="btn btn-sm btn-secondary mb-3" @click="backToDrives">&larr; Back to Drives</button>
<h5 class="card-title">Applicants for {{selectedDriveTitle||'Drive'+selectedDrive}}</h5>
<div class="table-responsive">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                    <th class="text-center">Student ID</th>
                    <th class="text-center">Name</th>
                    <th class="text-center">Department</th>
                    <th class="text-center">Year</th>
                    <th class="text-center">CGPA</th>
                    <th class="text-center">Resume</th>
                    <th class="text-center">Status</th>
                </tr>
            </thead>
            <tbody>
            <tr v-for="applicant in applicants" :key="applicant.student_id">
            <td class="text-center">{{applicant.student_id}}</td>
            <td class="text-center">{{applicant.name}}</td>
            <td class="text-center">{{applicant.dept}}</td>
            <td class="text-center">{{applicant.year}}</td>
            <td class="text-center">{{applicant.cgpa}}</td>
            <td class="text-center"><button v-if="applicant.resume_path" @click="viewResume(applicant.student_id)" class="btn btn-sm btn-outline-secondary m-2">View Resume</button></td>
            <td class="text-center">
                <span v-if="applicant.status==='applied'" class="badge bg-info">Applied</span>
                <span v-else-if="applicant.status==='shortlisted'" class="badge bg-secondary">Shortlisted</span>
                <span v-else-if="applicant.status==='selected'" class="badge bg-danger">Selected</span>
                <span v-else-if="applicant.status==='rejected'" class="badge bg-danger">Rejected</span>
                <span v-else class="badge bg-warning">Pending</span>
            </td>
            </tr>
            </tbody>
        </table>
</div>
</div>
<div v-if="applicants.length===0" class="p-3 text-center text-muted">No applicants found</div>
</div>
<div v-else class="card">
<div class="table-responsive">
    <table class="table table-hover mb-1">
        <thead class="table-light">
            <tr>
                <th class="text-center">Drive ID</th>
                <th class="text-center">Company</th>
                <th class="text-center">Job Title</th>
                <th class="text-center">Eligible Branches</th>
                <th class="text-center">Skill Required</th>
                <th class="text-center">CGPA Criteria</th>
                <th class="text-center">Deadline</th>
                <th class="text-center">Status</th>
                <th class="text-center">Actions</th>
            </tr>
        </thead>
        <tbody>
        <tr v-for="drive in drives" :key="drive.drive_id">
            <td class="text-center">{{drive.drive_id}}</td>
            <td class="text-center">{{drive.company}}</td>
            <td class="text-center">{{drive.jobtitle}}</td>
            <td class="text-center">{{drive.branches}}</td>
            <td class="text-center">{{drive.skills}}</td>
            <td class="text-center">{{drive.cgpa_above}}</td>
            <td class="text-center">{{drive.deadline}}</td> 
            <td>
            <div v-if="drive.status==='approved'" class="badge bg-success">Approved</div>
            <div v-if="drive.status==='rejected'" class="badge bg-warning">Rejected</div>
            <div v-if="drive.status==='closed'" class="badge bg-danger">Closed</div>
            </td>
            <td class="text-center">
                <button v-if="drive.status=='pending'" class="btn btn-sm btn-success m-2" @click="approveDrive(drive.drive_id)">Approve</button>
                <button v-if="drive.status=='pending'"  class="btn btn-sm btn-danger m-2" @click="rejectDrive(drive.drive_id)">Reject</button>
                <button class="btn btn-sm btn-info m-2" @click="fetchApplicants(drive.company_id, drive.drive_id, drive.jobtitle)">View Applicants</button>     
            </td>
        </tr>
        </tbody>
    </table>
</div>
<div v-if="drives.length===0" class="p-3 text-center text-muted">No placement drives found</div>
</div>
</div>
</div>
</div>
`
}