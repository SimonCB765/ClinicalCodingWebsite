"""Handlers for the pages made available by this blueprint."""

# Flask imports.
from flask import jsonify, redirect, render_template, request, url_for

# User imports.
from . import forms
from . import long_task


def get_codes():
    """Render and process the page for extracting codes from concept definitions."""

    # Get the form for displaying or validating.
    uploadForm = forms.ConceptUploadForm()

    if request.method == 'POST':
        # A POST request was made, so validate the form.
        if uploadForm.validate():
            response = jsonify({
                "response": render_template("mod_codes_from_concepts/concept_form.html", form=uploadForm),
                "success": True
            })
        else:
            response = jsonify({
                "response": render_template("mod_codes_from_concepts/concept_form.html", form=uploadForm),
                "success": False
            })
        return response
    else:
        # A GET request was made, so just render the page.
        return render_template("mod_codes_from_concepts/get_codes.html", form=uploadForm)


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
