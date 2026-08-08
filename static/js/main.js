const {createApp}=Vue
const app=createApp({
    data()
    {
        return{
            currentView:'login',
            currentUser:null,
            loading:true
        }
    },
    methods:{
        async checkSession(){
            try{
                const response=await fetch('/auth/check',{
                    credentials:'include'
                })
                if(response.ok){
                    const data=await response.json()
                    this.currentUser=data
                    this.redirectbyRole(data.role)
                }
                else{
                    this.currentView='login'
                }
            }
            catch(error){
                this.currentUser=null
                this.currentView='login'
            }
            finally{
                this.loading=false
            }
        },
        redirectbyRole(role){
            if(role==='admin'){
                this.currentView='adminDashboard'
            }
            else if(role==='student'){
                this.currentView='studentDashboard'
            }
            else if(role==='company'){
                this.currentView='companyDashboard'
            }
        },
        handlelogin(user)
        {
            this.currentUser=user
            this.redirectbyRole(user.role)
        },
        async handlelogout(){
            await fetch('/auth/logout',{
                method:'POST',
                credentials:'include'
            })
            this.currentUser=null
            this.currentView='login'
        }
    },
    mounted(){
        this.checkSession()
    },
    template:`
    <div>
    <div v-if="loading" class="d-flex justify-content-center align-items-center" style="height:100vh">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
     <div v-else>
     <nav class="navbar navbar-dark bg-dark px-6" v-if="currentUser">
     <span class="navbar-brand fw-bold">Placement Portal</span>
     <div class="d-flex align-items-center gap-3">
     <span class="text-white">{{ currentUser.email }}</span>
    <span class="badge bg-primary text-capitalize">{{ currentUser.role }}</span>
    <button class="btn btn-outline-light btn-sm" @click="handlelogout">Logout</button>
    </div>
    </nav>
    <div class="container mt-5">
    <Login v-if="currentView=='login'" @login-success="handlelogin" @go-register="currentView='register'"></Login>
    <Register v-if="currentView === 'register'"@go-login="currentView = 'login'"/>
    <AdminDashboard v-if="currentView==='adminDashboard'"/>
    <CompanyDashboard v-if="currentView==='companyDashboard'"/>
    <StudentDashboard v-if="currentView==='studentDashboard'"/>
     </div>
     </div>
    </div>
`
})
app.component('Login',Login)
app.component('Register',Register)
app.component('AdminDashboard',AdminDashboard)
app.component('CompanyDashboard',CompanyDashboard)
app.component('StudentDashboard',StudentDashboard)
app.mount('#app')