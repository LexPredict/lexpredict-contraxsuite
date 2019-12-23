document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("loginForm");
  var inputEmail = document.querySelector("input[name='email']");

  inputEmail.addEventListener("keyup", sendFormByEnterClick);

  function sendFormByEnterClick(e) {
    if ((e.key === "Enter" || e.keyCode === 13) && form !== null && typeof form === "object") {
      form.submit();
    }
  }
});
