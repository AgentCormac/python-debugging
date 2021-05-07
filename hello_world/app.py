import json
import os
import debugpy

print("Starting hello_world\n")

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    if os.environ.get("IS_DEBUG") == "true":
        print("IS_DEBUG is true, waiting for debugger on 0.0.0.0:5890\n")
        debugpy.listen(("0.0.0.0", 5890))
        debugpy.wait_for_client()
    else:
        print("IS_DEBUG not active, running without debugpy.\n")
    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    a = 1
    a = a + 1
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world","mark":"higginbottom","a":"{0}".format(a)
            # "location": ip.text.replace("\n", "") 
        })
    }
