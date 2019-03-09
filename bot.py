from flask import Flask, request, make_response, Response
import os
import json
import requests

from slackclient import SlackClient

# Your app's Slack bot user token
SLACK_BOT_TOKEN = "xoxb-562711937057-571650737138-qXL27XiJI0KJAmJtqLdIFYjB"
#SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)
requestor="Larison"
subject="Need a Java resource"
received_data={}
# Flask webserver for incoming traffic from Slack
app = Flask(__name__)
app.config.update(
    TESTING=True,
    ENV="development"
)
# Helper for verifying that requests came from Slack
# def verify_slack_token(request_token):
#     if SLACK_VERIFICATION_TOKEN != request_token:
#         print("Error: invalid verification token!")
#         print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
#         return make_response("Request contains invalid Slack verification token", 403)

def find_missing(received_data):
        missing_data=""
        
        for data in (received_data):
            if (received_data)[data]=="":
                missing_data+=data+", "
        return missing_data[:-2]



def ask_questions(missing_data):
    print("missing "+missing_data)
    if "location" in missing_data.lower():
        attachments_json=[
            {
                "text":"Which location is the job opening for?",
                "fallback":"Question",
                "callback_id":"job_loc",
                "color":"3AA3E3",
                "attachment_type":"default",
                "actions":[
                    {
                        "name":"missing",
                        "text":"Goa",
                        "type":"button",
                        "value":"Goa"
                    },
                    {
                        "name":"missing",
                        "text":"Pune",
                        "type":"button",
                        "value":"Pune"
                    },
                    {
                        "name":"missing",
                        "text":"Nagpur",
                        "type":"button",
                        "value":"Nagpur"
                    },
                    {
                        "name":"missing",
                        "text":"Bangalore",
                        "type":"button",
                        "value":"Bangalore"
                    },
                    {
                        "name":"missing",
                        "text":"Hydrabad",
                        "type":"button",
                        "value":"Hydrabad"
                    },
                    {
                        "name":"missing",
                        "text":"Santa Clara",
                        "type":"button",
                        "value":"Pune"
                    }
                ]
            }
        ]
        slack_client.api_call("chat.postMessage",channel="UGTK5P58S",text="",attachments=attachments_json)
        return

    if "notice_period" in missing_data.lower():
        attachments_json=[
	{
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "How soon would you like this person to join?"
		},
		"accessory": {
			"type": "datepicker",
			"initial_date": "2019-03-10",
			"placeholder": {
				"type": "plain_text",
				"text": "Select a date"
			}
		}
	}
]
        slack_client.api_call("chat.postMessage",channel="UGTK5P58S",text="",blocks=attachments_json)
        return
    return



@app.route("/Slackbot/request_data", methods=["POST"])
def request_data():
    # Parse the request payload
    missing_data=""
    global received_data
    print(request.get_data())
    received_data = json.loads(request.get_data())
    received_data["notice_period"]=""
    missing_data=find_missing(received_data)
    slack_client.api_call("chat.postMessage",channel="UGTK5P58S",text="Hello "+received_data["sender"]+", I noticed that your request with subject \""+received_data["subject"]+"\" did not contain some data ")
    ask_questions(missing_data)

    # Load options dict as JSON and respond to Slack
    return make_response("", 200)


#     # Load options dict as JSON and respond to Slack
#     return Response(json.dumps(menu_options), mimetype='application/json')


# The endpoint Slack will send the user's menu selection to

@app.route("/slack/receive_message", methods=["POST"])
def receive_actions():
    return({"challenge":"3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"},"application/json")


@app.route("/slack/message_actions", methods=["POST"])
def message_actions():

    # Parse the request payload
    form_json = json.loads(request.form["payload"])
    global received_data

    print(form_json)
    if find_missing(received_data)!="notice_period":
        selection = form_json["actions"][0]["value"]

        if(form_json["callback_id"]):
            received_data["location"]=selection
            print(received_data)
        print("missing is not blank")
        ask_questions(find_missing(received_data))
        slack_client.api_call(
        "chat.update",
        channel=form_json["channel"]["id"],
        ts=form_json["message_ts"],
        text="All right {} location then".format(selection),
        attachments=[])
    else:
        print("missing is blank")
        #ask_questions(find_missing(received_data))
        selection=form_json["actions"][0]["selected_date"]
        print (form_json)
        slack_client.api_call(
        "chat.postMessage",
        channel="UGTK5P58S",
        text="Great,I'll find some one who can join by {}.\nThanks!".format(selection),
        attachments=[] # empty `attachments` to clear the existing massage attachments
        )
        requests.get("http://10.244.54.35:4567/setFlag")
    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response("", 200)



# Start the Flask server
if __name__ == "__main__":
    app.run(debug=True)
    