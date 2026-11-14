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
    <div class="portal-shell">
    <div v-if="loading" class="portal-loading" role="status" aria-label="Loading your portal">
        <div class="spinner-border text-primary" aria-hidden="true"></div>
    </div>
    <div v-else>
    <header class="portal-header" v-if="currentUser">
        <div class="portal-header__inner">
            <div class="portal-brand">
                <span class="portal-brand__mark" aria-hidden="true">C</span>
                <span>Career Portal</span>
            </div>
            <div class="portal-user">
                <div class="portal-user__identity">
                    <span class="portal-user__email">{{ currentUser.email }}</span>
                    <span class="portal-user__role">{{ currentUser.role }}</span>
                </div>
                <button class="btn btn-outline-light btn-sm portal-logout" @click="handlelogout">Sign out</button>
            </div>
        </div>
    </header>
    <main class="portal-main">
    <Login v-if="currentView=='login'" @login-success="handlelogin" @go-register="currentView='register'"></Login>
    <Register v-if="currentView === 'register'" @go-login="currentView = 'login'"/>
    <AdminDashboard v-if="currentView==='adminDashboard'"/>
    <CompanyDashboard v-if="currentView==='companyDashboard'"/>
    <StudentDashboard v-if="currentView==='studentDashboard'"/>
    </main>
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