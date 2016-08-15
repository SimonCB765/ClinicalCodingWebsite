// Begin the polling once the document is ready.
$(document).ready(function() { get_progress(statusURL); });

function get_progress(statusURL)
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
            setTimeout(function() { get_progress(statusURL); }, 2000);
        }
    });
}