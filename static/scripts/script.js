
/* general purpose functions */
//function to fix missing 0's (Used for database keys mostly)
function appendZero(num){
  if(num < 10){
    return "0" + num;
  }
  return num;
}

/* Task Interaction functions */
// this will take the data of the task and send it to the modal
function sendDataToModal(id,desc,date,time,important,completed){
  document.getElementById("task_id").value = id;
  document.getElementById("new_description").value=desc;
  document.getElementById("new_date").value=date;
  document.getElementById("new_time").value=time;
  document.getElementById("mark_important").checked = important === 'true';
  if(important === 'true'){
      document.getElementById("label_for_important").innerHTML = "Mark as not important";
  }
  document.getElementById("mark_completed").checked = completed === 'true';
  if(completed === 'true'){
      document.getElementById("label_for_completed").innerHTML = "Mark as incomplete";
  }
}

//Function to display tasks in a box view
function makeDescriptionHTML(task, taskDesc){
  taskDesc += `<div class="toast show mb-3 mt-3 mx-3" role="alert" aria-live="assertive" aria-atomic="true" style="cursor:pointer" onclick="sendDataToModal('${task.id}','${task.description}','${task.date}','${task.time}','${task.important}','${task.completed}')" data-bs-toggle="modal" data-bs-target="#edit_task_modal">`;
      taskDesc += `<div class="toast-header justify-content-between">`;
          taskDesc += (task.important) ? `<strong><i class="bi bi-brightness-high-fill" style="color:red"></i></strong>` : `<span></span>`
          taskDesc += `<span class="fs-6">${task.date} | ${task.time}</span>`;
      taskDesc += `</div>`;
      taskDesc += `<div class="toast-body fs-6 ${task.completed ? "completed" : "" }">`;
          taskDesc += task.description;
      taskDesc += `</div>`;
  taskDesc += `</div>`;
  return taskDesc;
}

/* API CALLS */

function api_get_tasks(success_function) {

  $.ajax({url:$API_PATH, type:"GET", 
          success:success_function});
}

function api_create_task(task, success_function) {
  $.ajax({url:$API_PATH, type:"POST", 
          data:JSON.stringify(task), 
          contentType:"application/json; charset=utf-8",
          success:success_function});
}

function api_update_task(task, success_function) {
  task.id = parseInt(task.id)
  $.ajax({url:$API_PATH, type:"PUT", 
          data:JSON.stringify(task), 
          contentType:"application/json; charset=utf-8",
          success:success_function});
}

function api_delete_task(task, success_function) {
  task.id = parseInt(task.id)
  $.ajax({url:$API_PATH, type:"DELETE", 
          data:JSON.stringify(task), 
          contentType:"application/json; charset=utf-8",
          success:success_function});
}

