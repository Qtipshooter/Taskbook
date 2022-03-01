//----------Password Reset----------//


// get the user_email from the hideen input from the form
let current_user_email = $("#current_user").val();

// get the user's security question from the database
jQuery.when(jQuery.getJSON("/get_security_question?user_email=" + current_user_email)).done(function(data) {

    // checking for NA because NA is returned as the question if the user is not found
    if (data.question == "NA") {
        $("#current_question").val("No security question set");
        $("#current_answer").hide();
        return;

    } else {
        $("#current_question").val(data.question);
    }
});

document.getElementById('verify').addEventListener("click", function() {
    us_email = $("#verify_user_email").val();
    us_pass = $("#verify_user_password").val();
    del_type = $("#delete_type").val();
    
    data = {
        "email":us_email,
        "passwd":us_pass,
        "del_type":del_type
    }
    
    api_delete_account(data, function(){ window.location = window.location.origin }, function(result) {    
        $('#verify_error').removeClass('hide');
        document.getElementById('verify_alerts').innerHTML = result.responseText;
        console.log(result);
    });
});


//----------Task View Customization----------//



//check database to see what customization options the user set, display the current settings
function api_get_settings(success_function) {

    $.ajax({
        url: '/api/settings', type: "GET",
        success: success_function
    });
}

api_get_settings(function(result){
    let type = "task";
    let shown = 10;
    let view = "dashboard"

    for(const setting of result.settings) {
        type = setting.upcoming_type
        shown = setting.upcoming_shown
        view = setting.view
    }

    document.getElementById("upcoming_shown").value = shown;
    document.getElementById("upcoming_type").value = type;
    
    if(view === "dashboard") {
        document.getElementById("default_view_dashboard").checked = true;
    }
    else if(view === "calendar") {
        document.getElementById("default_view_monthly").checked = true;
    }
    else if (view === "weekly") {
        document.getElementById("default_view_weekly").checked = true;
    }
    else {
        document.getElementById("default_view_task").checked = true;
    }

})
