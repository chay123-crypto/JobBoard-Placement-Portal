const Login={
    data(){
        return {
            email:'',
            password:'',
            error:''
        }
    },
    methods:{
        async handlelogin(){
            try{
                const response=await fetch('/auth/login',{
                    'method':'POST',
                    'headers':{'Content-Type':'application/json'},
                    'credentials':'include',
                    'body':JSON.stringify({
                        email:this.email,
                        password:this.password
                    })
                })
                if(response.ok){
                    const data=await response.json()
                    this.$emit('login-success',data)
                }
                else{
                    const error=await response.json()
                    this.error=error.error
                }
            }
        catch(err){
            this.error='Something went wrong.Try again.'
        }
    },
    async loginAsDemo(role){
        const demoAccounts={
            student:{email:'demo.student@placement.in',password:'DemoAccess123!'},
            company:{email:'demo.company@placement.in',password:'DemoAccess123!'}
        }
        const account=demoAccounts[role]
        this.email=account.email
        this.password=account.password
        this.error=''
        await this.handlelogin()
    },
    goRegister(){
        this.$emit('go-register')
    }
  },
  template:`
  <section class="auth-layout auth-layout--login">
    <div class="auth-copy">
      <span class="auth-copy__eyebrow">YOUR NEXT CHAPTER STARTS HERE</span>
      <h1>Find the work that moves you forward.</h1>
      <p>Discover opportunities, connect with employers, and keep your placement journey in one place.</p>
      <div class="auth-highlights">
        <div><span aria-hidden="true">01</span><span>Explore opportunities matched to your goals</span></div>
        <div><span aria-hidden="true">02</span><span>Track every application from one dashboard</span></div>
        <div><span aria-hidden="true">03</span><span>Stay ready for the next step in your career</span></div>
      </div>
    </div>
    <div class="auth-panel">
      <div class="card auth-card">
        <div class="card-body">
          <span class="auth-form__eyebrow">WELCOME BACK</span>
          <h2 class="auth-form__title">Sign in to your account</h2>
          <p class="auth-form__description">Pick up where your career journey left off.</p>
          <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
          <div class="mb-3">
            <label class="form-label" for="login-email">Email address</label>
            <input id="login-email" v-model="email" type="email" class="form-control" placeholder="you@example.com" autocomplete="email" required>
          </div>
          <div class="mb-4">
            <label class="form-label" for="login-password">Password</label>
            <input id="login-password" v-model="password" type="password" class="form-control" placeholder="Enter your password" autocomplete="current-password" required>
          </div>
          <button class="btn btn-primary w-100 auth-submit" @click="handlelogin">Sign in</button>
          <div class="auth-demo">
            <p class="auth-demo__title">Explore with a demo account</p>
            <p class="auth-demo__note">Shared sample accounts; please don't enter personal information.</p>
            <div class="auth-demo__actions">
              <button class="btn btn-outline-primary" type="button" @click="loginAsDemo('company')">Continue as demo company</button>
              <button class="btn btn-outline-secondary" type="button" @click="loginAsDemo('student')">Continue as demo student</button>
            </div>
          </div>
          <p class="auth-switch">New to Career Portal? <a href="#" @click.prevent="goRegister">Create an account</a></p>
        </div>
      </div>
    </div>
  </section>
  `
}
