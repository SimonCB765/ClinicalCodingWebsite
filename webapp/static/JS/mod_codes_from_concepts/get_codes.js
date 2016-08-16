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
    form.submit(function (event) {
        var form = $("section.conceptDefs form");
        var formData = new FormData(form.get(0));
        $.ajax({
            type: form.attr("method"),
            url: form.attr("action"),
            data: formData,
            processData: false,  // Tell jQuery not to process the data.
            contentType: false,   // Tell jQuery not to set the contentType.
            success: function(data, status, request) {
                console.log(data);
                console.log(status);
            },
            error: function() {
                console.log("Unexpected error");
            }
        });
        console.log("Submitted");

        event.preventDefault();  // Prevent the default submission of the form.
    });
});