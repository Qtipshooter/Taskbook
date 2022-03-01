
//Function to display tasks in day view
function displayDayTasks(key){
    let taskDesc = "";
    let count = 0;
    //fetches tasks
    api_get_tasks(function(result){
        for(const task of result.tasks){
            //if task matches current day, display it
            if(task.date == key){
                taskDesc = makeDescriptionHTML(task, taskDesc);
                document.getElementById("toast-container-today").innerHTML = taskDesc;
                count++;
            }
        }
        if(count==0){
            let task = {
                date:"-",
                time:"-",
                description:"<h4 class='ms-3'>No tasks for today!<h4>",
            }
            taskDesc = makeDescriptionHTML(task, taskDesc,false);
            document.getElementById("toast-container-today").innerHTML =taskDesc;
        }

    });
}

//Function to display next num tasks
function displayNextTasks(key, num){
    let taskDesc = "";  //building the tasks into this variable
    let count = 0;      //counting up to how many tasks are in this column

    //fetches tasks and stores them into array to be sorted by date
    api_get_tasks(function(result){
        for(const task of result.tasks){
            //Magic number num is how many upcoming tasks can be displayed, may be modified when customization comes in.
            if(count >= num) break;
            if(task.date > key){
                count++;
                taskDesc = makeDescriptionHTML(task, taskDesc);
                document.getElementById("toast-container-upcoming").innerHTML = taskDesc;
            }
        }
        if(count==0){
            let task = {
                date:"-",
                time:"-",
                description:"<h4 class='ms-3'>No upcoming tasks!<h4>",
            }
            taskDesc = makeDescriptionHTML(task, taskDesc, false);
            document.getElementById("toast-container-upcoming").innerHTML =taskDesc;
        }
    });
}

//Function to display next num days
function displayNextDays(key, num) {
    let taskDesc = "";  //building the tasks into this variable
    let empty = true; //keeping track of whether we have a task or not
    end_date = new Date() //varibale to hold end date
    end_date.setDate(new Date(key).getDate() + num + 1) //calculate end date (num days after current date)
    end_date = end_date.getFullYear() + '-' + appendZero(end_date.getMonth() + 1) + '-' + appendZero(end_date.getDate()) //conveert to string for comparison

    //fetches tasks and stores them into array to be sorted by date
    api_get_tasks(function (result) {
        for (const task of result.tasks) {
            if ((task.date > key) && (task.date <= end_date)) {
                taskDesc = makeDescriptionHTML(task, taskDesc);
                document.getElementById("toast-container-upcoming").innerHTML = taskDesc;
                empty = false;
            }
        }
        if (empty) {
            let task = {
                date: "-",
                time: "-",
                description: "<h4 class='ms-3'>No upcoming tasks!<h4>",
            }
            taskDesc = makeDescriptionHTML(task, taskDesc);
            document.getElementById("toast-container-upcoming").innerHTML = taskDesc;
        }
    });
}

// dynamically generate today's date to render in the front-end
// the tricky bit is that, if we are at /task or today then it is the current day but if someone comes to this page from clicking on a date from calendar,
// then, we need to display that date. So I had to look at the URL and then based on that, dynamically generate the date.
// what is does is, if we are at a route /tasks/whatever, then we display that date. If we are at /task then we display today's date.
var urlDate = window.location.href.split("?")[0];
viewDate = (urlDate.split("/").length > 4) ? new Date(urlDate.split("/")[4].replace(/-/g,'/')) : new Date();
document.getElementById("today-date").innerHTML = viewDate.toDateString();

//key variable that represents the current day
let dateKey = viewDate.getFullYear() + '-' + appendZero(viewDate.getMonth()+1) + '-' + appendZero(viewDate.getDate());

//check if path is set to just today

//displays tasks for today
displayDayTasks(dateKey);


//displays upcoming tasks
function api_get_settings(success_function) {

    $.ajax({
        url: '/api/settings', type: "GET",
        success: success_function
    });
}

api_get_settings(function (result) {
    let type = "task";
    let shown = 10;

    for (const setting of result.settings) {
        type = setting.upcoming_type
        shown = setting.upcoming_shown
    }

    if(type === "task") {
        displayNextTasks(dateKey, shown)
    }

    else {
        displayNextDays(dateKey, shown)
    }
})
