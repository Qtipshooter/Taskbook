const date = new Date();

//get day of the week for current day
const currentDay = date.getDay();

//array of each month to display the words for it
const month = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];

const weekday = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
];

//number of milliseconds in a day
var dayMilliseconds = 60 * 60 * 24 * 1000;

//will return the first day of the week in milliseconds (Sunday)
const firstDay = new Date(date.getTime() - dayMilliseconds * currentDay);

//will return last day of the week in milliseconds (Saturday)
const lastDay = new Date(firstDay.getTime() + dayMilliseconds * 6);

//sets header to display the start and end day of the week
document.querySelector(".current-week").innerHTML = month[firstDay.getMonth()] + " " + firstDay.getDate() + " - " + month[lastDay.getMonth()] + " " + lastDay.getDate();

//place the tasks in the accord
for (let i = 0; i < 7; i++) {
    let accordData = "";
    let currentDate = new Date(firstDay.getTime() + dayMilliseconds * i)
    let dateKey = currentDate.getFullYear() + "-" + appendZero(currentDate.getMonth() + 1) + "-" + appendZero(currentDate.getDate());
    accordData += `<div class="accordion-body d-flex justify-items-center align-items-center flex-wrap" id="` + dateKey + `">`
    accordData += `</div>`
    document.getElementById("collapse" + weekday[i]).innerHTML = accordData;
    displayWeeklyTasks(dateKey);
}

//Function to display tasks in day view
function displayWeeklyTasks(key){
    let taskDesc = "";
    let count = 0;
    //fetches tasks
    api_get_tasks(function(result){
        for(const task of result.tasks){
            //if task matches current day, display it
            if(task.date == key){
                taskDesc = makeDescriptionHTML(task, taskDesc);
                document.getElementById(key).innerHTML = taskDesc;
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
            document.getElementById(key).innerHTML =taskDesc;
        }
    });
}

