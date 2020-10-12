// Global variable to store all problem lists.
var scraped;

// Getting "page number" from form0
(function() {
    'use strict';
    var form0 = document.getElementById('form_0');
    var form0_submit = document.getElementById('form_0_submit');
    form0_submit.addEventListener('click', function (event) {
        if (form0.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        else {
            // Starting the process of scraping problems list
            transaction();
        }
        form0.classList.add('was-validated');
    }, false);
})();

// AJAX call to function in "main.py" script to get scraped problems list.
// In case error occurs, same is displayed or else result is displayed
function transaction() {
    // alert('inside transaction');
    var req = new XMLHttpRequest();
    req.onreadystatechange = function () {
        if (req.readyState == 4 && req.status == 200) {
            scraped = JSON.parse(req.responseText)

            if (scraped['has_error']) {
                html = "<div class='col-md-8 my-3 alert alert-danger text-center font-weight-bold'>" + scraped['error'] + "</div>";
                document.getElementById('prob_table').innerHTML = html;
            }
            else {
                html = "<table class='col-md-9 col-11 my-3 table table-sm table-hover table-striped'>";
                html += "<thead class='thead-dark'> <tr>";
                    html += "<th class='pl-3'><input type='checkbox' value='Select All' id='select_all' onchange='check_all(this)'>";
                        html += "<span class='ml-2' id='select_all_text'>Select All</span>";
                    html += "</th>";
                    html += "<th>Problem ID</th>";
                    html += "<th>Problem Name</th>";
                html += "</tr> </thead>";
                html += "<tbody>";
                for (i = 0; i < scraped['problems'].length; i++) {
                    // html += "<tr onclick=\"document.location = '" + scraped['problems'][i]['link'] + "'\">";
                    html += "<tr>";
                    html += "<td class='pl-3'><input type='checkbox' value='" + i + "' class='checkboxes' id='checkbox" + i + "'></td>";
                    html += "<td><a href='" + scraped['problems'][i]['link'] + "' style='color:black; text-decoration:none;' target='blank'>" + scraped['problems'][i]['id'] + "</td>";
                    html += "<td><a href='" + scraped['problems'][i]['link'] + "' style='color:black; text-decoration:none;' target='blank'>" + scraped['problems'][i]['name'] + "</td>";
                    html += "</tr>";
                }
                html += "</tbody>";
                html += "</table>";

                html += "<div class='col-md-9 col-11 mt-3 mb-1 text-center'><button id='download' class='px-5 btn btn-primary' type='button' onclick='downloadSelected()'>Download</button></div>";
                html += "<div class='col-md-9 col-11 text-center' id='download_loading'></div>";
                html += "<div class='col-md-9 col-11 mb-5 text-center' id='download_error' style='color:red'></div>";

                document.getElementById('prob_table').innerHTML = html;
            }
            // alert('transaction complete');
        }
        else if (req.readyState != 4) {
            html = "<div class='my-3'>";
            html += "<div class='spinner-grow spinner-grow-sm text-secondary' role='status'> <span class='sr-only'>Loading...</span> </div>";
            html += "<span class='p-1'></span>";
            html += "<div class='spinner-grow spinner-grow-sm text-secondary' role='status'> <span class='sr-only'>Loading...</span> </div>";
            html += "<span class='p-1'></span>";
            html += "<div class='spinner-grow spinner-grow-sm text-secondary' role='status'> <span class='sr-only'>Loading...</span> </div>";
            html += "</div>";
            document.getElementById('prob_table').innerHTML = html;
        }
    }

    req.open('POST', '/form-0');
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var page = document.getElementById('pageno').value;
    var postVars = 'pageno=' + page;
    req.send(postVars);
    
    return false;
}

// Utility to check or uncheck all problems
function check_all(SelectAllElement) {
    if (SelectAllElement.checked) {
        for (i = 0; i < scraped['problems'].length; i++) {
            document.getElementById("checkbox"+i).checked = true;
        }
        document.getElementById("select_all_text").innerHTML = "Unselect All";
    }
    else {
        for (i = 0; i < scraped['problems'].length; i++) {
            document.getElementById("checkbox" + i).checked = false;
        }
        document.getElementById("select_all_text").innerHTML = "Select All";
    }
}

// Start the process of downloading and scraping selected problem statements
function downloadSelected() {
    // alert("inside downloadSelected " + scraped['problems'].length);
    var to_send = [];
    for (i = 0; i < scraped['problems'].length; i++) {
        if(document.getElementById("checkbox"+i).checked == true)
            to_send.push(i);
    }

    if (!(Array.isArray(to_send) && to_send.length)) {
        document.getElementById('download_error').innerHTML = "Please select problems to download";
        return;
    }
    else {
        document.getElementById('download_error').innerHTML = "";
    }

    var request = new XMLHttpRequest();
    request.responseType = "blob";
    request.onreadystatechange = function () {
        // alert("state changed to: " + request.readyState);
        if (request.readyState == 4 && request.status == 200) {
            // window.open(URL.createObjectURL(this.response));

            var a = document.createElement("a");
            a.href = URL.createObjectURL(this.response);
            a.download = "zipped_problems.zip";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            document.getElementById('download_loading').innerHTML = "";
        }
        else if (request.readyState != 4) {
            html = "<div class='my-3'>";
            html += "<div class='spinner-border spinner-border-sm text-dark' role='status'> <span class='sr-only'>Loading...</span> </div>";
            html += "<span class='px-2'>Please wait. This may take enough time.</span>";
            html += "</div>";
            document.getElementById('download_loading').innerHTML = html;
        }
    }

    request.open('POST', '/download');
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var postVars = 'prob_indices=' + to_send;
    request.send(postVars);

    return false;
}