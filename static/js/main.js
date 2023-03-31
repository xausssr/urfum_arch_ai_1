let TASK_ID = "empty"
let INTERVAL_HOLDER = null;
let MAIN_RESPONSE = "";
let BASE_URL = document.URL
if (BASE_URL.slice(-1) !== "/"){
    BASE_URL = BASE_URL + "/"
}

function switch_layout(state){
    switch (state){
        case "result":
            document.getElementById("applyNetButton").disabled = false;
            document.getElementById("spinner").hidden = true;
            document.getElementById("statusLine").hidden = true;
            document.getElementById("resultHeader").hidden = false;
            document.getElementById("outputArea").hidden = false;
            break;
        case "wait":
            document.getElementById("applyNetButton").disabled = true;
            document.getElementById("spinner").hidden = false;
            document.getElementById("statusLine").hidden = false;
            document.getElementById("resultHeader").hidden = true;
            document.getElementById("outputArea").hidden = true;
            break
        default:
            document.getElementById("applyNetButton").disabled = false;
            document.getElementById("spinner").hidden = true;
            document.getElementById("statusLine").hidden = true;
            document.getElementById("resultHeader").hidden = true;
            document.getElementById("outputArea").hidden = true;
    }
}

function send_data(){
    data = document.getElementById("manuallyInputArea").value;
    if(data === ''){
        alert("Введите текст!")
        return
    }
    
    $.ajax({
        type: "POST",
        url: BASE_URL + "send_text",
        data: data,
        processData: false,
        contentType: "text/plain",
        success: function(response_id) {
            TASK_ID = response_id;
            switch_layout("wait")
            INTERVAL_HOLDER = setInterval(check_result, 5000);
        }
    });

}

function check_result(){
    $.ajax({
        type: "GET",
        url: BASE_URL + 'get_result?id=' + TASK_ID,
        success: function(response, status, code) {
            if (status === "success"){
                document.getElementById("outputArea").value = response;
                TASK_ID = "empty";
                clearInterval(INTERVAL_HOLDER);
                INTERVAL_HOLDER = null;
                switch_layout("result");
                MAIN_RESPONSE = response;
                return;
            }
            else{
                return;
            }
            
        },
        error: function(response, status){
            alert("Error: " + response + " " + status);
        }
    });
}