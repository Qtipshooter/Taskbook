//progress bar functionality
function displayProgress(key) {
    let total = 0;
    let completed = 0;
    //fetches tasks
    api_get_tasks(function (result) {
        for (const task of result.tasks) {
            //if task matches current day, count it
            if (task.date == key) {
                total++;
                if(task.completed) {
                    completed++;
                }
            }
        }
        if (total != 0) {
            //change the fraction count
            taskFraction = completed + "/" + total + " tasks";
            document.getElementById("progress-fraction").innerHTML = taskFraction;

            //change percentage displayed
            taskPercentage = (completed * 100) / total + "%";
            document.getElementById("progress-percent").innerHTML = taskPercentage;
            document.querySelector(":root").style.setProperty("--progress-size", taskPercentage);


        }

    });
}


//Function to display tasks
function displayDayTasks(key) {
    let taskDesc = "";
    let count = 0;
    //fetches tasks
    api_get_tasks(function (result) {
        for (const task of result.tasks) {
            //if task matches current day, display it
            if (task.date == key) {
                taskDesc = makeDescriptionHTML(task, taskDesc);
                document.getElementById("today_dashboard").innerHTML = taskDesc;
                count++;
            }
        }
        if (count == 0) {
            let task = {
                date: "-",
                time: "-",
                description: "<h4 class='ms-3'>No tasks for today!<h4>",
            }
            taskDesc = makeDescriptionHTML(task, taskDesc);
            document.getElementById("today_dashboard").innerHTML = taskDesc;
        }

    });
}

//get current day
let viewDate = new Date()
let dateKey = viewDate.getFullYear() + '-' + appendZero(viewDate.getMonth() + 1) + '-' + appendZero(viewDate.getDate());

//displays tasks for today
displayDayTasks(dateKey);
displayProgress(dateKey)
