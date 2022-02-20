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

//will return the first day of the week in milliseconds (Sunday)
const firstDay = new Date(date.getTime() - 60*60*24*currentDay*1000);

//will return last day of the week in milliseconds (Saturday)
const lastDay = new Date(firstDay.getTime() + 60*60*24*6*1000);

//sets header to display the start and end day of the week
document.querySelector(".current-week").innerHTML = month[firstDay.getMonth()] + " " + firstDay.getDate() + " - " + month[lastDay.getMonth()] + " " + lastDay.getDate();

let task = {
    "description": "Test",
    "date": "2020-01-01",
    "time": "12:00",
    "important": true,
    "completed": false,
}
let taskDesc = "";
taskDesc = makeDescriptionHTML(task, taskDesc);
$("#tasksForSunday").html(taskDesc);
$("#tasksForSunday").append(taskDesc);
$("#tasksForSunday").append(taskDesc);
$("#tasksForSunday").append(taskDesc);
$("#tasksForSunday").append(taskDesc);

