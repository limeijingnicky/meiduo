const { createApp,ref } = Vue
    const APP = createApp ({
    setup() {
        // v-model
        let username=ref(" ")
        let password=ref(" ")
        let password2=ref(" ")
        let mobile= ref(" ")
        let allow=ref(" ")
        // v-show
        let error_name = ref(false)
        let error_password = ref(false)
        let error_password2 = ref(false)
        let error_mobile = ref(false)
        let error_allow = ref(false)
        // error_message
        let error_name_message=ref(" ")
        let error_mobile_message=ref(" ")


        function check_username() {
            // 用户名是5-20个字符，[a-zA-Z0-9_-]
            // 定义正则
            let  regex0 = /[a-zA-Z0-9_-]{5,20}$/;
            //使用正则匹配用户名数据
            if ( regex0 .test(username.value)){
                //匹配成功，不展示错误提示信息
                error_name.value = false;
            } else {
                //匹配失败，展示错误提示信息
                error_name_message.value='请输入5-20个字符的用户名';
                error_name.value = true;
            }
        }
        //校验密码
        function check_password(){
            let regex = /[0-9a-zA-Z]{8,20}$/;
            if( regex.test(password.value)){
                error_password.value = false ;
            } else {
                error_password.value = true;
            }
        }
        // 密码确认
        function check_password2(){
            if(password.value != password2.value){
                error_password.value = true ;
            } else {
                error_password.value = false;
            }
        }
        //校验手机号
        function check_mobile(){
            let  regex1 = /1[0-9]\d{9}$/ ;
            if( regex1.test(mobile.value)){
                error_mobile.value = false ;
            } else {
                error_mobile_message.value = "输入的手机号不正确";
                error_mobile.value =true;
            }
        }
        //校验是否勾选
        function check_allow(){
            if(!allow.value){
                allow.value = true ;
            } else {
                allow.value = false;
            }
        }
        //监听表单提交事件
        function on_submit(){
            check_username.value();
            check_password.value();
            check_password2.value();
            check_mobile.value();
            check_allow.value();

            // 前端校验信息，有错误时禁用提交事件
            if (error_name.value == true || error_password.value==true || error_password2.value==true ||  error_mobile.value==true ||  error_allow.value==true)
            {
               //禁止提交表单事件,默认值为true
                window.event.returnValue = false ;

                }
            }
    }
})
APP.mount('#app')