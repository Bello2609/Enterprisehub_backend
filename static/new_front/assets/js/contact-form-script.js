!function(e){"use strict";function t(){e("#contactForm").removeClass().addClass("shake animated").one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",function(){e(this).removeClass()})}function a(t,a){if(t)var s="h4 text-center tada animated text-success";else s="h4 text-center text-danger";e("#msgSubmit").removeClass().addClass(s).text(a)}e("#contactForm").validator().on("submit",function(s){var n,i,o,m;s.isDefaultPrevented()?(t(),a(!1,"Did you fill in the form properly?")):(s.preventDefault(),n=e("#name").val(),i=e("#email").val(),o=e("#msg_subject").val(),m=e("#message").val(),e.ajax({type:"POST",url:"assets/php/form-process.php",data:"name="+n+"&email="+i+"&msg_subject="+o+"&message="+m,success:function(s){"success"==s?(e("#contactForm")[0].reset(),a(!0,"Message Submitted!")):(t(),a(!1,s))}}))})}(jQuery);