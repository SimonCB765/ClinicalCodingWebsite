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
                if (data["success"] && data["action"] === "update") {
                    // The form was successfully validated and an update of the concept's codes needs to be performed.

                    //Make ajax call and update the form based on the success of that.
                    // Update the form element. Use .html rather than .replaceWith to preserve handlers.
                    //form.html(data["response"])
                }
            },
            error: function() {
                console.log("Unexpected Error.");
            }
        });

        event.preventDefault();  // Prevent the default submission of the form.
    });
});