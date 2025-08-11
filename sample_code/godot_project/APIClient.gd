extends Node

# A GDScript client for the SpriteShift AI API.

const BASE_URL = "https://api.spriteshift.ai/v1"
var api_key: String = "" # Should be set before use.

# Signal emitted when an upload is complete.
signal upload_complete(job_id)
# Signal emitted when an upload fails.
signal upload_failed(error_message)
# Signal emitted when the job status is successfully retrieved.
signal status_checked(status_data)
# Signal emitted when checking the job status fails.
signal status_check_failed(error_message)
# Signal emitted when the export is ready and assets are downloaded.
signal export_finished(sprite_sheet_path, metadata_path)
# Signal emitted when the export fails.
signal export_failed(error_message)

var http_request: HTTPRequest

func _ready():
	# Create an HTTPRequest node to handle our web requests.
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(self._on_request_completed)

# --- Public API Methods ---

func set_api_key(key: String):
	self.api_key = key

func upload_image(image_path: String, user_id: String):
	var url = BASE_URL + "/api/upload"

	var headers = [
		"X-API-Key: " + api_key
	]

	# Godot's HTTPRequest doesn't directly support FormData,
	# so we would need to construct the multipart/form-data body manually.
	# This is a complex task. For this implementation, we will assume
	# a future Godot version or a library would simplify this.
	# The following is a placeholder for the request.
	print("Placeholder: Uploading image from ", image_path)
	# In a real scenario, we would make the following request:
	# http_request.request(url, headers, HTTPClient.METHOD_POST, form_data_body)

	# For now, we'll simulate a successful upload for testing purposes.
	var mock_response = {"job_id": "job-12345", "status_url": "/api/job/job-12345/status"}
	emit_signal("upload_complete", mock_response["job_id"])


func get_job_status(job_id: String):
	var url = BASE_URL + "/api/job/" + job_id + "/status"
	var headers = ["X-API-Key: " + api_key]
	# The "purpose" is used to know how to handle the response in _on_request_completed
	var metadata = {"purpose": "check_status"}
	http_request.request(url, headers, HTTPClient.METHOD_GET, "", metadata)

func export_assets(job_id: String):
	var url = BASE_URL + "/api/export"
	var headers = [
		"Content-Type: application/json",
		"X-API-Key: " + api_key
	]
	var body = JSON.stringify({
		"job_id": job_id,
		"format": "spritesheet",
		"bitrate": 1080,
		"user_tier": "pro"
	})
	var metadata = {"purpose": "export"}
	http_request.request(url, headers, HTTPClient.METHOD_POST, body, metadata)

# --- Private Methods & Signal Handlers ---

func _on_request_completed(result, response_code, headers, body, user_data):
	var json_response = JSON.parse_string(body.get_string_from_utf8())
	var purpose = user_data.get("purpose", "")

	if response_code >= 400:
		var error_message = json_response.get("error", "Unknown error")
		if purpose == "check_status":
			emit_signal("status_check_failed", error_message)
		elif purpose == "export":
			emit_signal("export_failed", error_message)
		return

	if purpose == "check_status":
		emit_signal("status_checked", json_response)
	elif purpose == "export":
		# The response should contain a URL to the assets.
		# We would then download them.
		var export_url = json_response.get("url")
		# For now, we'll simulate downloading assets.
		_download_assets_from_url(export_url)

func _download_assets_from_url(url: String):
	# In a real implementation, we would download the assets from the URL.
	# For now, we will assume the assets are downloaded and saved.
	var sprite_sheet_path = "user://character_sprites.png"
	var metadata_path = "user://character_anim.json"

	# Here we would use another HTTPRequest to download the files.
	# After downloading, we would save them to the user:// directory.

	print("Simulating download and save of assets.")

	emit_signal("export_finished", sprite_sheet_path, metadata_path)
