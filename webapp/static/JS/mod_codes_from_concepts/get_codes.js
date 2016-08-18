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
    var form = $("section.conceptDefs form");
    form.submit(function (event) {
        var formData = new FormData(form.get(0));
        $.ajax({
            type: form.attr("method"),
            url: form.attr("action"),
            data: formData,
            processData: false,  // Tell jQuery not to process the data.
            contentType: false,   // Tell jQuery not to set the contentType.
            success: function(data) {
                if (data["success"]) {
                    // The form was successfully validated.
                    if (data["action"] === "update") {
                        // Update the form to remove any messages that should no longer be present.
                        // Use .html rather than .replaceWith to preserve handlers.
                        form.html(data["response"])

                        // Submit a job to update the concept definitions.

                        //Make ajax call and update the form based on the success of that.
                        // Update the form element. Use .html rather than .replaceWith to preserve handlers.
                        //form.html(data["response"])
                    }
                    else {
                        // The concept was saved, so update the form element to indicate this.
                        // Use .html rather than .replaceWith to preserve handlers.
                        form.html(data["response"])
                    }
                }
                else {
                    // The submitted form data was invalid in some way, so update the form element.
                    // Use .html rather than .replaceWith to preserve handlers.
                    form.html(data["response"])
                }
            },
            error: function() {
                console.log("Unexpected Error.");
            }
        });

        event.preventDefault();  // Prevent the default submission of the form.
    });
});