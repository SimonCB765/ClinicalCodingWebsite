$(document).ready(function() {
    // Setup the CSRF token submission with AJAX.
    var csrftoken = $('meta[name=csrf-token]').attr('content')
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    })

    // Attach a handler to the form submission to deal with form validation and job submission.
    var form = $("section .conceptForm");
    form.submit(function (event) {
        var formData = new FormData(form.get(0));
        $.ajax({
            type: form.attr("method"),
            url: form.attr("action"),
            data: formData,
            processData: false,  // Tell jQuery not to process the data.
            contentType: false,   // Tell jQuery not to set the contentType.
            success: function(data) {
                // Update the form element. Use .html rather than .replaceWith to preserve handlers.
                form.html(data["response"])
                if (data["success"]) {
                    if (data["action"] === "update") {
                        // The form was successfully validated and an update of the concept's codes needs to be
                        // performed.
                        var statusURL = data["pollURL"];
                        get_extraction_progress(statusURL);

                        //Make ajax call and update the form based on the success of that.
                        // Update the form element. Use .html rather than .replaceWith to preserve handlers.
                        //form.html(data["response"])
                    }
                    else if (data["action"] === "extract") {
                        // A code list needs extracting and the download file for it generating.
                        var statusURL = data["pollURL"];
                        get_extraction_progress(statusURL);
                    }
                }
            },
            error: function() {
                console.log("Unexpected Error.");
            }
        });

        event.preventDefault();  // Prevent the default submission of the form.
    });
});

function get_extraction_progress(statusURL)
{
    $.getJSON(statusURL, function(data)
    {
        console.log(data);
        if (data["state"] !== "PENDING" && data["state"] !== "PROGRESS")
        {
            console.log("DONE");
        }
        else
        {
            // Poll the URL again in 2 seconds.
            setTimeout(function() { get_extraction_progress(statusURL); }, 2000);
        }
    });
}
