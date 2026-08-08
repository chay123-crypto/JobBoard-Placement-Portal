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
    goRegister(){
        this.$emit('go-register')
    }
  },
  template:`
  <div class="row justify-content-center mt-5">
  <div class="col-md-4">
  <div class="card shadow mt-5">
   <div class="card-body p-4">
    <h3 class="card-title text-center mb-4">Placement Portal</h3>
    <h5 class="text-center text-muted mb-4">Login</h5>
     <div v-if="error" class="alert alert-danger">{{ error }}</div>
     <div class="mb-3">
     <label class="form-label">Email</label>
     <input v-model="email" type="email" class="form-control" placeholder="enter your email" required></div>
    <div class="mb-3">
    <label class="form-label">Password</label>
     <input v-model="password" type="password" class="form-control" placeholder="enter your password" required></div>
     <button class="btn btn-primary w-100 mb-3" @click="handlelogin">Login</button>
     <p class="text-center text-muted mb-0">No account? <a href="#" @click.prevent="goRegister">Register here</a></p>
     </div>
     </div>
     </div>
  </div>
  `
}