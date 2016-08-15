"""Handlers for the pages made available by this blueprint."""

# Flask imports.
from flask import jsonify, redirect, render_template, url_for

# User imports.
from . import forms
from . import long_task


def upload_concepts():
    """Render and process the page for uploading concepts to be defined."""
    uploadForm = forms.ConceptUploadForm()

    if uploadForm.validate_on_submit():
        # A POST request was made and the form was successfully validated, so concept discovery can begin.
        task = long_task.main.apply_async(args=[10, 11])
        return redirect(url_for("conceptDiscovery.view_concepts", taskID=task.id))

    return render_template("mod_codes_from_concepts/upload_concepts.html", form=uploadForm)


def view_concepts(taskID):
    return render_template("mod_codes_from_concepts/view_concepts.html", taskID=taskID)


def task_status(taskID):
    task = long_task.main.AsyncResult(taskID)
    if not task.info:
        # Can't find the task. A proper check for his is saving the task id to the database with the input.
        response = {
            "state": "Can't find task",
            "current": 0,
            "total": 0,
            "status": "Failed"
        }
    elif task.state == "PENDING":
        # The job hasn't started yet.
        response = {
            "state": task.state,
            "current": 0,
            "total": 1,
            "status": "Pending..."
        }
    elif task.state != "FAILURE":
        # The job hasn't failed, and is therefore still going.
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", '')
        }
        if "result" in task.info:
            response["result"] = task.info["result"]
    else:
        # The job failed for some reason.
        response = {
            "state": task.state,
            "current": 1,
            "total": 1,
            "status": str(task.info),  # The exception raised.
        }
    return jsonify(response)
