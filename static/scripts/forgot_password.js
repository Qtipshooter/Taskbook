$("#submit_user_email").click(function() {
    var email = $("#user_email").val();
    jQuery.when(jQuery.getJSON("/get_security_question?user_email=" + email)).done(function(data) {

        // checking for NA because NA is returned as the question if the user is not found
        if (data.question == "NA") {
            $("#empty_email_alert").removeClass("hide");
            $("#empty_email_alert").html("User not found or no security question set. Please try again.");
            return;

        } else {
            $("#user_email_div").addClass("hide");
            $("#security_qna").removeClass("hide");
            $(".new_pwd").removeClass("hide");
            $("#email_to_change_password").val(email);
            $("#user_security_question").html("Question: " +data.question);
            // this is a hidden field so send as POST data to /forgot_password. Setting the value once we get the question
            $("#email_to_change_password").val(email);
        }
    });
});