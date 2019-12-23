document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("loginForm");
  var inputLogin = document.querySelector("input[name='login']");
  var inputPassword = document.querySelector("input[name='password']");
  var inputPassword1 = document.querySelector("input[name='password1']");
  var inputPassword2 = document.querySelector("input[name='password2']");

  inputLogin && inputLogin.addEventListener("keyup", sendFormByEnterClick);
  inputPassword && inputPassword.addEventListener("keyup", sendFormByEnterClick);
  inputPassword1 && inputPassword1.addEventListener("keyup", sendFormByEnterClick);
  inputPassword2 && inputPassword2.addEventListener("keyup", sendFormByEnterClick);

  function sendFormByEnterClick(e) {
    if ((e.key === "Enter" || e.keyCode === 13) && form !== null && typeof form === "object") {
      form.submit();
    }
  }
});
